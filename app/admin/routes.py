from flask import Blueprint, abort, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import User, Alumno, MedicionCorporal, PagoCliente
from app.forms import RegistroForm,EditarClienteForm
from app.extensions import db
from app.admin import admin
from datetime import datetime, timedelta



# ============================================================
# DASHBOARD PRINCIPAL (ADMIN)
# ============================================================
@admin.route("/dashboard")
@login_required
def dashboard():
    if not current_user.is_admin:
        flash("Acceso denegado.")
        return redirect(url_for("main.inicio"))

    total_clientes = User.query.filter_by(is_admin=False).count()
    total_alumnos = Alumno.query.count()
    total_mediciones = MedicionCorporal.query.count()

    clientes_recientes = User.query.filter_by(is_admin=False).order_by(User.id.desc()).limit(3).all()

    grafico_labels = ["Clientes", "Alumnos", "Mediciones"]
    grafico_datos = [total_clientes, total_alumnos, total_mediciones]

    return render_template(
        "admin/dashboard.html",
        total_clientes=total_clientes,
        total_alumnos=total_alumnos,
        total_mediciones=total_mediciones,
        grafico_labels=grafico_labels,
        grafico_datos=grafico_datos,
        clientes_recientes=clientes_recientes
    )


# ============================================================
# LISTAR CLIENTES
# ============================================================
@admin.route("/clientes")
@login_required
def admin_clientes():
    if not current_user.is_admin:
        flash("Acceso denegado.")
        return redirect(url_for("main.inicio"))

    clientes = User.query.filter_by(is_admin=False).all()
    clientes_info = []

    for cliente in clientes:
        alumnos = Alumno.query.filter_by(cliente_id=cliente.id).all()
        total_mediciones = sum(len(a.mediciones) for a in alumnos)
        clientes_info.append({
            "id": cliente.id,
            "username": cliente.username,
            "alumnos": alumnos,
            "total_alumnos": len(alumnos),
            "total_mediciones": total_mediciones
        })

    return render_template("admin/clientes.html", clientes=clientes_info)


# ============================================================
# VER CLIENTE ESPECÍFICO
# ============================================================
@admin.route("/cliente/<int:cliente_id>")
@login_required
def ver_cliente(cliente_id):
    if not current_user.is_admin:
        flash("Acceso no autorizado.")
        return redirect(url_for("main.inicio"))

    cliente = User.query.get_or_404(cliente_id)
    alumnos = cliente.alumnos
    total_alumnos = len(alumnos)
    total_mediciones = sum(len(a.mediciones) for a in alumnos)

    return render_template(
        "admin/dashboard_cliente.html",
        cliente=cliente,
        alumnos=alumnos,
        total_alumnos=total_alumnos,
        total_mediciones=total_mediciones
    )


# ============================================================
# CREAR NUEVO CLIENTE
# ============================================================
@admin.route("/cliente/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_cliente():
    if not current_user.is_admin:
        flash("Acceso restringido.")
        return redirect(url_for("main.inicio"))

    form = RegistroForm()
    if form.validate_on_submit():
        nombre = form.nombre.data.title().strip()
        if User.query.filter_by(username=form.username.data).first():
            flash("Ese nombre de usuario ya existe.", "warning")
        else:
            nuevo = User(
                nombre=form.nombre.data,
                username=form.username.data,
                password=generate_password_hash(form.password.data),
                is_admin=False
            )
            db.session.add(nuevo)
            db.session.commit()
            flash("Cliente creado exitosamente.", "success")
            return redirect(url_for("admin.admin_clientes"))

    return render_template("admin/nuevo_cliente.html", form=form)


# ============================================================
# EDITAR CLIENTE
# ============================================================
@admin.route("/cliente/<int:cliente_id>/editar", methods=["GET", "POST"])
@login_required
def editar_cliente(cliente_id):
    if not current_user.is_admin:
        flash("Acceso no autorizado.")
        return redirect(url_for("main.inicio"))

    cliente = User.query.get_or_404(cliente_id)
    form = EditarClienteForm(obj=cliente)


    if form.validate_on_submit():
        cliente.nombre = form.nombre.data
        cliente.username = form.username.data
        if form.password.data:
            cliente.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash("Cliente actualizado correctamente.", "success")
        return redirect(url_for("admin.admin_clientes"))

    return render_template("admin/editar_cliente.html", form=form, cliente=cliente)


# ============================================================
# 🗑️ ELIMINAR CLIENTE (ADMIN)
# ============================================================
@admin.route('/admin/cliente/<int:cliente_id>/eliminar', methods=['POST'])
@login_required
def eliminar_cliente(cliente_id):
    if not current_user.is_admin:
        flash("Acceso no autorizado.", "danger")
        return redirect(url_for("main.inicio"))

    cliente = User.query.get_or_404(cliente_id)

    # 🔁 Elimina pagos, alumnos y mediciones en cascada automáticamente
    db.session.delete(cliente)
    db.session.commit()

    flash(f"✅ Cliente '{cliente.username}' eliminado correctamente.", "success")
    return redirect(url_for('admin.admin_clientes'))  # ✅ usa tu endpoint real



# ============================================================
# APROBAR PAGO
# ============================================================
@admin.route('/pagos/aprobar/<int:id>', methods=['POST'])
@login_required
def aprobar_pago(id):
    if not current_user.is_admin:
        abort(403)

    pago = PagoCliente.query.get_or_404(id)
    pago.estado = 'Aprobado'
    db.session.commit()

    flash(f"Pago de {pago.cliente.nombre} ({pago.mes_correspondiente}) aprobado correctamente.", "success")
    return redirect(url_for('admin.pagos'))


# ============================================================
# REGISTRAR PAGO AUTOMATICO (ADMIN)
# ============================================================

@admin.route('/cliente/<int:cliente_id>/pago', methods=['POST'])
@login_required
def registrar_pago(cliente_id):
    if not current_user.is_admin:
        abort(403)

    cliente = User.query.get_or_404(cliente_id)
    mes_actual = datetime.now().strftime("%B %Y")

    # Verifica si ya tiene pago de este mes
    pago_existente = PagoCliente.query.filter_by(cliente_id=cliente.id, mes_correspondiente=mes_actual).first()
    if pago_existente:
        flash(f"Ya existe un pago registrado para {cliente.nombre} ({mes_actual}).", "warning")
        return redirect(url_for('admin.admin_clientes'))

    # Crea nuevo pago pendiente
    nuevo_pago = PagoCliente(
        cliente_id=cliente.id,
        monto=15000.00,  # 💰 podés cambiar el valor del abono mensual
        mes_correspondiente=mes_actual,
        estado="Pendiente"
    )
    db.session.add(nuevo_pago)
    db.session.commit()

    flash(f"Pago registrado para {cliente.nombre} ({mes_actual}).", "info")
    return redirect(url_for('admin.admin_clientes'))


# ============================================================
# REGISTRAR NUEVO PAGO MANUAL (ADMIN)
# ============================================================

@admin.route('/pagos/nuevo', methods=['GET', 'POST'])
@login_required
def registrar_pago_manual():
    if not current_user.is_admin:
        flash("Acceso no autorizado.", "danger")
        return redirect(url_for("main.inicio"))

    clientes = User.query.filter_by(is_admin=False).all()

    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        monto = request.form.get('monto')
        estado = request.form.get('estado')  # 🔹 Nuevo campo
        mes_correspondiente = datetime.now().strftime("%B %Y")

        # Validaciones básicas
        if not cliente_id or not monto:
            flash("Debe seleccionar un cliente y un monto válido.", "warning")
            return redirect(url_for('admin.registrar_pago_manual'))

        if estado not in ["Pendiente", "Aprobado"]:
            flash("Debe seleccionar un estado válido para el pago.", "warning")
            return redirect(url_for('admin.registrar_pago_manual'))

        cliente = User.query.get(cliente_id)
        if not cliente:
            flash("Cliente no encontrado.", "danger")
            return redirect(url_for('admin.registrar_pago_manual'))

        # Solo verifica duplicados si el pago es aprobado
        if estado == "Aprobado":
            pago_existente = PagoCliente.query.filter_by(
                cliente_id=cliente.id,
                mes_correspondiente=mes_correspondiente,
                estado='Aprobado'
            ).first()
            if pago_existente:
                flash(f"⚠️ Ya existe un pago aprobado para {cliente.nombre} correspondiente a {mes_correspondiente}.", "warning")
                return redirect(url_for('admin.registrar_pago_manual'))

        # Crear nuevo pago
        pago = PagoCliente(
            cliente_id=cliente.id,
            monto=float(monto),
            mes_correspondiente=mes_correspondiente,
            estado=estado,  # 🔹 Usa el estado seleccionado
            fecha_pago=datetime.utcnow()
        )

        db.session.add(pago)
        db.session.commit()

        if estado == "Aprobado":
            flash(f"✅ Pago de {cliente.nombre} registrado y aprobado correctamente.", "success")
        else:
            flash(f"💬 Pago de {cliente.nombre} registrado como pendiente.", "info")

        return redirect(url_for('admin.pagos'))

    return render_template('admin/nuevo_pago.html', clientes=clientes, now=datetime.utcnow())

# ===========================================================
# 💰 LISTAR TODOS LOS PAGOS (ADMIN)
# ===========================================================
@admin.route('/pagos')
@login_required
def pagos():
    if not current_user.is_admin:
        abort(403)

    pagos = PagoCliente.query.order_by(PagoCliente.fecha_pago.desc()).all()
    return render_template('admin/pagos.html', pagos=pagos, now=datetime.utcnow, timedelta=timedelta)





# ============================================================
# ELIMINAR PAGO
# ============================================================
@admin.route('/pagos/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_pago(id):
    if not current_user.is_admin:
        abort(403)

    pago = PagoCliente.query.get_or_404(id)
    
    # Guardamos datos antes de borrar
    nombre_cliente = pago.cliente.nombre if pago.cliente else "Desconocido"
    mes_pago = pago.mes_correspondiente

    db.session.delete(pago)
    db.session.commit()

    flash(f"Pago de {nombre_cliente} ({mes_pago}) eliminado correctamente.", "danger")
    return redirect(url_for('admin.pagos'))




# ============================================================
# RESUMEN DE INGRESOS CON FILTRO DE MES Y AÑO
# ============================================================
from sqlalchemy import extract, func

@admin.route('/ingresos', methods=['GET', 'POST'])
@login_required
def resumen_ingresos():
    if not current_user.is_admin:
        flash("Acceso no autorizado.", "danger")
        return redirect(url_for("main.inicio"))

    hoy = datetime.utcnow()

    # 🔹 Obtener mes y año seleccionados desde el formulario
    mes = request.form.get('mes', hoy.month, type=int)
    anio = request.form.get('anio', hoy.year, type=int)

    # 🔹 Lista de meses (en español)
    meses = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
        (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
        (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
    ]

    # 🔹 Total del mes filtrado
    total_mes = db.session.query(func.sum(PagoCliente.monto))\
        .filter(
            extract('month', PagoCliente.fecha_pago) == mes,
            extract('year', PagoCliente.fecha_pago) == anio,
            PagoCliente.estado == "Aprobado"
        ).scalar() or 0

    # 🔹 Total histórico general
    total_general = db.session.query(func.sum(PagoCliente.monto))\
        .filter(PagoCliente.estado == "Aprobado")\
        .scalar() or 0

    # 🔹 Totales por cliente (solo del mes filtrado)
    pagos_clientes = db.session.query(
        User.nombre, func.sum(PagoCliente.monto).label('total')
    ).join(PagoCliente).filter(
        extract('month', PagoCliente.fecha_pago) == mes,
        extract('year', PagoCliente.fecha_pago) == anio,
        PagoCliente.estado == "Aprobado"
    ).group_by(User.id).order_by(func.sum(PagoCliente.monto).desc()).all()

    # 🔹 Generar texto descriptivo del mes
    nombre_mes = dict(meses).get(mes, "Mes desconocido")
    periodo = f"{nombre_mes} {anio}"

    return render_template(
        'admin/ingresos.html',
        total_mes=total_mes,
        total_general=total_general,
        pagos_clientes=pagos_clientes,
        meses=meses,
        mes=mes,
        anio=anio,
        periodo=periodo,
        hoy=hoy
    )
