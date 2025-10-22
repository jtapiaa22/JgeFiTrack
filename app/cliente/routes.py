import os
from flask import Blueprint, json, jsonify, render_template, redirect, request, url_for, flash, make_response
from flask_login import login_required, current_user
from app.forms import MedicionForm, AlumnoForm, EditarMedicionForm
from app.models import MedicionCorporal, Alumno
from app.extensions import db
from app.cliente import cliente
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io
from datetime import datetime, date
from reportlab.platypus import Image
import base64
from config import BASE_DIR


# -------------------------------------------------------------------
# DASHBOARD DEL CLIENTE
# -------------------------------------------------------------------
@cliente.route('/dashboard')
@login_required
def home():
    alumnos = Alumno.query.filter_by(cliente_id=current_user.id).all()
    total_alumnos = len(alumnos)

    mediciones = MedicionCorporal.query.filter(
        MedicionCorporal.alumno_id.in_([a.id for a in alumnos])
    ).all()
    total_mediciones = len(mediciones)

    ultima = max([m.fecha for m in mediciones], default=None)
    ultima_medicion = ultima.strftime('%d/%m/%Y') if ultima else "Sin registros"

    alumnos_recientes = Alumno.query.filter_by(cliente_id=current_user.id)\
        .order_by(Alumno.fecha_creacion.desc()).limit(3).all()
    for a in alumnos_recientes:
        ultima_m = MedicionCorporal.query.filter_by(alumno_id=a.id)\
            .order_by(MedicionCorporal.fecha.desc()).first()
        a.ultima_medicion = ultima_m.fecha.strftime('%d/%m/%Y') if ultima_m else "Sin datos"

    fechas = [m.fecha.strftime('%d-%m') for m in mediciones]
    pesos = [m.peso for m in mediciones]

    return render_template(
        "cliente/dashboard.html",
        titulo="Inicio - GymApp",
        total_alumnos=total_alumnos,
        total_mediciones=total_mediciones,
        ultima_medicion=ultima_medicion,
        alumnos_recientes=alumnos_recientes,
        fechas=fechas,
        pesos=pesos
    )


# -------------------------------------------------------------------
# REGISTRAR NUEVA MEDICIÓN (con control de duplicado por fecha)
# -------------------------------------------------------------------
from datetime import date

@cliente.route('/medicion', methods=['GET', 'POST'])
@login_required
def medicion():
    form = MedicionForm()

    #capturar alumno para que no tengas que elegir de nuevo
    alumno_id = request.args.get('alumno_id', type=int)

    #listar alumnos
    form.alumno.choices = [
        (a.id, a.nombre)
        for a in Alumno.query.filter_by(cliente_id=current_user.id).all()
    ]

    alumno_fijo = None
    if alumno_id:
        alumno_fijo = Alumno.query.get_or_404(alumno_id)
        form.alumno.data = alumno_fijo.id
   
    if form.validate_on_submit():
        alumno = Alumno.query.get_or_404(form.alumno.data)
        f = form.fecha.data

        #bloquear duplicado
        ya_existe = MedicionCorporal.query.filter_by(alumno_id=alumno.id, fecha=f).first()
        if ya_existe:
            flash(f'⚠️ Ya existe una medición para {alumno.nombre} el {f.strftime("%d/%m/%Y")}.', 'warning')
            if alumno_fijo:
                return redirect(url_for('cliente.medicion', alumno_id=alumno.id))
            return redirect(url_for('cliente.medicion'))

        # 🆕 Crear nueva medición
        nueva = MedicionCorporal(
            fecha=f,
            peso=form.peso.data if form.peso.data else None,
            altura=form.altura.data if form.altura.data else None,
            cintura=form.cintura.data if form.cintura.data else None,
            cadera=form.cadera.data if form.cadera.data else None,
            pecho=form.pecho.data if form.peso.data else None,
            muslo=form.muslo.data if form.muslo.data else None,
            brazo=form.brazo.data if form.brazo.data else None,
            grasa_corporal=form.grasa_corporal.data if form.grasa_corporal.data else None,
            musculo=form.musculo.data if form.musculo.data else None,
            agua_corporal=form.agua_corporal.data if form.agua_corporal.data else None,
            metabolismo_basal=form.metabolismo_basal.data if form.metabolismo_basal.data else None,
            alumno_id=alumno.id
        )

        nueva.calcular_todo()
        db.session.add(nueva)
        db.session.commit()

        flash('✅ Medición guardada correctamente y datos recalculados.', 'success')
        return redirect(url_for('cliente.mediciones_alumno', id=alumno.id))

    return render_template('cliente/medicion.html', form=form, alumno_fijo=alumno_fijo)

# -------------------------------------------------------------------
# AJAX: chequear si existe medición para (alumno, fecha)
# -------------------------------------------------------------------


@cliente.route('/check-medicion', methods=['GET'])
@login_required
def check_medicion():
    alumno_id = request.args.get('alumno_id', type=int)
    fecha_str = request.args.get('fecha')

    if not alumno_id or not fecha_str:
        return jsonify({"exists": False})

    # fecha viene como 'YYYY-MM-DD' del input type="date"
    try:
        year, month, day = map(int, fecha_str.split('-'))
        f = date(year, month, day)
    except Exception:
        return jsonify({"exists": False})

    existe = MedicionCorporal.query.filter_by(alumno_id=alumno_id, fecha=f).first() is not None
    return jsonify({"exists": existe})



# -------------------------------------------------------------------
# CREAR NUEVO ALUMNO
# -------------------------------------------------------------------
@cliente.route('/alumno/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_alumno():
    form = AlumnoForm()
    if form.validate_on_submit():
        nombre = form.nombre.data.title().strip()
        alumno = Alumno(
            nombre=nombre,
            edad=form.edad.data,
            genero=form.genero.data,
            cliente_id=current_user.id
        )
        db.session.add(alumno)
        db.session.commit()
        flash('Alumno agregado exitosamente.')
        return redirect(url_for('cliente.listar_alumnos'))
    return render_template('cliente/nuevo_alumno.html', form=form)


# -------------------------------------------------------------------
# LISTAR ALUMNOS
# -------------------------------------------------------------------
@cliente.route('/alumnos')
@login_required
def listar_alumnos():
    alumnos = Alumno.query.filter_by(cliente_id=current_user.id).all()
    return render_template('cliente/alumnos.html', alumnos=alumnos)


# -------------------------------------------------------------------
# VER MEDICIONES DE UN ALUMNO
# -------------------------------------------------------------------
@cliente.route('/alumno/<int:id>/mediciones')
@login_required
def mediciones_alumno(id):
    alumno = Alumno.query.get_or_404(id)

    mediciones = (
        MedicionCorporal.query
        .filter_by(alumno_id=alumno.id)
        .order_by(MedicionCorporal.fecha.asc())
        .all()
    )

    fechas = [m.fecha.strftime('%d-%m') for m in mediciones]
    pesos = [m.peso for m in mediciones]
    imcs = [m.imc for m in mediciones]
    metabolismo = [m.metabolismo_basal for m in mediciones]
    grasas = [m.grasa_corporal for m in mediciones]
    musculos = [m.musculo for m in mediciones]
    aguas = [m.agua_corporal for m in mediciones]

    resumen = []
    estado_progreso = "neutral"  # default

    if len(mediciones) >= 2:
        anterior = mediciones[-2]
        actual   = mediciones[-1]

        dif_peso   = round(actual.peso - anterior.peso, 2)
        dif_imc    = round(actual.imc - anterior.imc, 2)
        dif_musc   = round(actual.musculo - anterior.musculo, 2)
        dif_grasa  = round(actual.grasa_corporal - anterior.grasa_corporal, 2)
        dif_agua   = round(actual.agua_corporal - anterior.agua_corporal, 2)

        # Mensajes (no definen el estado)
        if dif_peso > 0:
            resumen.append(f"⚖️ Subió {dif_peso} kg de peso.")
        elif dif_peso < 0:
            resumen.append(f"⚖️ Bajó {abs(dif_peso)} kg de peso.")

        if dif_imc > 0:
            resumen.append(f"📈 El IMC subió {dif_imc} puntos.")
        elif dif_imc < 0:
            resumen.append(f"📉 El IMC bajó {abs(dif_imc)} puntos.")

        if dif_musc > 0:
            resumen.append(f"💪 La masa muscular aumentó {dif_musc} puntos.")
        elif dif_musc < 0:
            resumen.append(f"💤 La masa muscular bajó {abs(dif_musc)} puntos.")

        if dif_grasa > 0:
            resumen.append(f"⚠️ El porcentaje de grasa aumentó {dif_grasa} puntos.")
        elif dif_grasa < 0:
            resumen.append(f"🔥 Redujo la grasa corporal en {abs(dif_grasa)} puntos.")

        if dif_agua > 0:
            resumen.append(f"💧 Aumentó la hidratación en {dif_agua} %.")
        elif dif_agua < 0:
            resumen.append(f"💧 Bajó el nivel de agua corporal {abs(dif_agua)} %.")

        # --------- DECISIÓN DEL ESTADO (score simple) ----------
        score = 0
        if dif_musc > 0: score += 1
        if dif_grasa < 0: score += 1
        if dif_grasa > 0: score -= 1
        if dif_musc < 0: score -= 1
        # (opcional) peso ayuda si acompaña grasa ↓
        if dif_peso < 0 and dif_grasa < 0: score += 1

        if score >= 1:
            estado_progreso = "positivo"
            resumen.insert(0, "💪 El progreso es excelente, ¡seguí así!")
        elif score <= -1:
            estado_progreso = "negativo"
            resumen.insert(0, "⚠️ Algunos indicadores empeoraron, revisá entrenamiento y/o dieta.")
        else:
            estado_progreso = "neutral"
            resumen.insert(0, "💧 Progreso estable entre las últimas mediciones.")
    else:
        resumen = ["🩺 Aún no hay suficientes mediciones para mostrar evolución."]
        estado_progreso = "neutral"

    return render_template(
        'cliente/datos_de_alumno.html',
        alumno=alumno,
        mediciones=mediciones,
        fechas=fechas,
        pesos=pesos,
        imcs=imcs,
        metabolismo=metabolismo,
        grasas=grasas,
        musculos=musculos,
        aguas=aguas,
        resumen=resumen,
        estado_progreso=estado_progreso,  # <- clave
        alumno_id=alumno.id
    )








@cliente.route("/alumno/<int:id>/exportar_pdf", methods=["GET", "POST"])
@login_required
def exportar_pdf(id):
    # 🧩 Recibir los gráficos desde el frontend
    graficos_json = request.form.get("graficos")
    graficos = json.loads(graficos_json) if graficos_json else {}

    alumno = Alumno.query.get_or_404(id)
    mediciones = alumno.mediciones

    # 🧾 Configuración del PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # 🏋️ Encabezado
    titulo = Paragraph(f"<b>Reporte de Mediciones - {alumno.nombre}</b>", styles['Title'])
    fecha = Paragraph(f"<b>Fecha de emisión:</b> {datetime.now().strftime('%d/%m/%Y')}", styles['Normal'])
    elements.extend([titulo, Spacer(1, 12), fecha, Spacer(1, 20)])

    # 📋 Tabla de mediciones
    data = [["Fecha", "Peso (kg)", "Altura (cm)", "IMC", "Metabolismo", "Grasa (%)", "Músculo (%)", "Agua (%)"]]
    for m in mediciones:
        data.append([
            m.fecha.strftime('%d/%m/%Y'),
            m.peso, m.altura, m.imc,
            m.metabolismo_basal, m.grasa_corporal,
            m.musculo, m.agua_corporal
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    # 🧱 Separador antes de los gráficos
    elements.append(Spacer(1, 25))
    elements.append(Paragraph("<b>Evolución del Progreso</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))

    # 🖼️ Agregar todos los gráficos recibidos
    for nombre, grafico_base64 in graficos.items():
        if grafico_base64 and grafico_base64.startswith("data:image/png;base64,"):
            grafico_bytes = base64.b64decode(grafico_base64.split(",")[1])
            grafico_path = os.path.join(BASE_DIR, f"grafico_{nombre}.png")

            with open(grafico_path, "wb") as f:
                f.write(grafico_bytes)

            # Subtítulo con el nombre del gráfico
            titulo_grafico = Paragraph(f"<b>{nombre.capitalize()}</b>", styles['Heading3'])
            elements.append(titulo_grafico)
            elements.append(Spacer(1, 8))
            elements.append(Image(grafico_path, width=500, height=250))
            elements.append(Spacer(1, 15))

    # 🧾 Construir PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    # 📤 Enviar PDF al navegador
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Reporte_{alumno.nombre}.pdf'
    return response


# -------------------------------------------------------------------
# EDITAR ALUMNO
# -------------------------------------------------------------------
@cliente.route('/alumno/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_alumno(id):
    alumno = Alumno.query.get_or_404(id)

    if alumno.cliente_id != current_user.id:
        flash("No tenés permiso para editar a este alumno.")
        return redirect(url_for('cliente.listar_alumnos'))
    
    form = AlumnoForm(obj=alumno)

    if form.validate_on_submit():
        alumno.nombre = form.nombre.data.title().strip()
        alumno.edad = form.edad.data
        alumno.genero = form.genero.data
        db.session.commit()
        flash("Alumno actualizado correctamente.")
        return redirect(url_for('cliente.listar_alumnos'))
    
    return render_template('cliente/editar_alumno.html', form=form, alumno=alumno)


# -------------------------------------------------------------------
# ELIMINAR ALUMNO
# -------------------------------------------------------------------
@cliente.route('/alumno/<int:id>/eliminar')
@login_required
def eliminar_alumno(id):
    alumno = Alumno.query.get_or_404(id)

    if alumno.cliente_id != current_user.id:
        flash("No tenés permiso para eliminar este alumno.")
        return redirect(url_for('cliente.listar_alumnos'))

    db.session.delete(alumno)
    db.session.commit()
    flash("Alumno eliminado correctamente.")
    return redirect(url_for('cliente.listar_alumnos'))


# -------------------------------------------------------------------
# EDITAR MEDICIÓN
# -------------------------------------------------------------------
@cliente.route('/alumno/<int:id_alumno>/medicion/<int:id_medicion>/editar', methods=['GET', 'POST'])
@login_required
def editar_medicion(id_alumno, id_medicion):
    alumno = Alumno.query.get_or_404(id_alumno)
    medicion = MedicionCorporal.query.get_or_404(id_medicion)

    if alumno.cliente_id != current_user.id:
        flash("No tenés permiso para editar esta medición.", "danger")
        return redirect(url_for('cliente.mediciones_alumno', id=id_alumno))

    form = MedicionForm(obj=medicion)
    form.alumno.choices = [(alumno.id, alumno.nombre)]
    form.alumno.data = alumno.id

    if request.method == "GET":
        any_balanza = any([
            medicion.grasa_corporal,
            medicion.musculo,
            medicion.agua_corporal,
            medicion.metabolismo_basal
                           ])
        form.modo.data = "balanza" if any_balanza else "manual"


    if form.validate_on_submit():
        medicion.fecha = form.fecha.data
        medicion.peso = form.peso.data
        medicion.altura = form.altura.data
        medicion.cintura = form.cintura.data
        medicion.cadera = form.cadera.data
        medicion.brazo = form.brazo.data
        medicion.pecho = form.pecho.data
        medicion.muslo = form.muslo.data

        #datos de modo balanza:
        medicion.grasa_corporal = form.grasa_corporal.data if form.grasa_corporal.data else None
        medicion.musculo = form.musculo.data if form.musculo.data else None
        medicion.agua_corporal = form.agua_corporal.data if form.agua_corporal.data else None
        medicion.metabolismo_basal = form.metabolismo_basal.data if form.metabolismo_basal.data else None

        #reiniciar/ajustar los valores calculados
        medicion.calcular_todo()
        db.session.commit()
        flash("Medición actualizada correctamente.", "success")
        return redirect(url_for('cliente.mediciones_alumno', id=id_alumno))

    return render_template('cliente/editar_medicion.html', form=form, alumno=alumno, medicion=medicion)



# -------------------------------------------------------------------
# ELIMINAR MEDICIÓN
# -------------------------------------------------------------------
@cliente.route("/alumno/<int:id_alumno>/medicion/<int:id_medicion>/eliminar")
@login_required
def eliminar_medicion(id_alumno, id_medicion):
    medicion = MedicionCorporal.query.get_or_404(id_medicion)

    if medicion.alumno_id != id_alumno:
        flash("No tenés permiso para eliminar esta medición.", "danger")
        return redirect(url_for("cliente.mediciones_alumno", id=id_alumno))

    db.session.delete(medicion)
    db.session.commit()
    flash("Medición eliminada correctamente.", "success")
    return redirect(url_for("cliente.mediciones_alumno", id=id_alumno))
