from app.extensions import db
from flask_login import UserMixin
from datetime import datetime
import math

# =========================================================
# 👤 USUARIO / CLIENTE
# =========================================================
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    pagos = db.relationship(
        'PagoCliente',
        backref='cliente',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    alumnos = db.relationship(
        'Alumno',
        backref='cliente',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

# =========================================================
# 🧍 ALUMNO
# =========================================================
class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer)
    genero = db.Column(db.String(10))
    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    mediciones = db.relationship(
        'MedicionCorporal',
        backref='alumno',
        cascade='all, delete-orphan',
        passive_deletes=True,
        lazy=True
    )

# =========================================================
# 📊 MEDICIÓN CORPORAL
# =========================================================
class MedicionCorporal(db.Model):
    __table_args__ = (
        db.UniqueConstraint('alumno_id', 'fecha', name='uq_alumno_fecha'),
    )

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    peso = db.Column(db.Float, nullable=False)
    altura = db.Column(db.Float, nullable=False)
    cintura = db.Column(db.Float)
    cadera = db.Column(db.Float)
    pecho = db.Column(db.Float)
    brazo = db.Column(db.Float)
    muslo = db.Column(db.Float)
    musculo = db.Column(db.Float)
    imc = db.Column(db.Float)
    metabolismo_basal = db.Column(db.Float)
    grasa_corporal = db.Column(db.Float)
    masa_grasa = db.Column(db.Float)
    agua_corporal = db.Column(db.Float)
    rcc = db.Column(db.Float)
    rca = db.Column(db.Float)

    alumno_id = db.Column(
        db.Integer,
        db.ForeignKey('alumno.id', ondelete='CASCADE'),
        nullable=False
    )

    # =============================
    # FUNCIONES DE CÁLCULO MEJORADAS
    # =============================
    def genero_y_edad(self):
        # Consigue genero y edad preferentemente del objeto alumno relacionado
        genero = getattr(self.alumno, "genero", None)
        edad = getattr(self.alumno, "edad", None)
        # Si falta o está vacío, usar por defecto
        if not genero:
            genero = "masculino"
        if not edad:
            edad = 25
        return genero.lower(), edad

    def calcular_imc(self):
        if self.peso and self.altura and self.altura > 0:
            try:
                self.imc = round(self.peso / ((self.altura / 100) ** 2), 2)
            except Exception:
                self.imc = None
        else:
            self.imc = None
        return self.imc

    def calcular_metabolismo_basal(self):
        genero, edad = self.genero_y_edad()
        if self.peso and self.altura:
            if genero == "femenino":
                self.metabolismo_basal = round(10 * self.peso + 6.25 * self.altura - 5 * edad - 161, 2)
            else:
                self.metabolismo_basal = round(10 * self.peso + 6.25 * self.altura - 5 * edad + 5, 2)
        else:
            self.metabolismo_basal = None
        return self.metabolismo_basal

    def calcular_grasa_corporal(self):
        genero, edad = self.genero_y_edad()
        altura = self.altura
        # Convertir alturas anómalas (ejemplo ingresada en metros)
        if altura and altura < 10:
            altura = altura * 100
        if not (self.cintura and self.cadera and altura):
            self.grasa_corporal = None
            return self.grasa_corporal

        try:
            if genero == "masculino":
                bf = (86.010 * math.log10(self.cintura - self.cintura * 0.25)) \
                   - (70.041 * math.log10(altura)) + 36.76
            else:
                bf = (163.205 * math.log10(self.cintura + self.cadera - self.cintura * 0.2)) \
                   - (97.684 * math.log10(altura)) - 78.387

            self.grasa_corporal = round(max(2, min(bf, 60)), 2)

            # Masa grasa absoluta en kg:
            if self.peso:
                self.masa_grasa = round(self.peso * (self.grasa_corporal / 100), 2)
            else:
                self.masa_grasa = None
        except (ValueError, ZeroDivisionError):
            self.grasa_corporal = None
            self.masa_grasa = None
        return self.grasa_corporal

    def calcular_agua_corporal(self):
        genero, edad = self.genero_y_edad()
        if self.peso and self.altura:
            if genero == "femenino":
                tbw = -2.097 + (0.1069 * self.altura) + (0.2466 * self.peso)
            else:
                tbw = 2.447 - (0.09156 * edad) + (0.1074 * self.altura) + (0.3362 * self.peso)
            self.agua_corporal = round((tbw / self.peso) * 100, 2)
        else:
            self.agua_corporal = None
        return self.agua_corporal

    def calcular_rcc(self):
        if self.cintura and self.cadera and self.cadera > 0:
            try:
                self.rcc = round(self.cintura / self.cadera, 2)
            except Exception:
                self.rcc = None
        else:
            self.rcc = None
        return self.rcc

    def calcular_rca(self):
        if self.cintura and self.altura and self.altura > 0:
            try:
                self.rca = round(self.cintura / self.altura, 2)
            except Exception:
                self.rca = None
        else:
            self.rca = None
        return self.rca

    def calcular_musculo(self):
        genero, _ = self.genero_y_edad()
        if self.grasa_corporal is not None:
            masa_magra = 100 - self.grasa_corporal
            if genero == "femenino":
                self.musculo = round(masa_magra * 0.50, 2)
            else:
                self.musculo = round(masa_magra * 0.55, 2)
            self.musculo = max(0, min(self.musculo, 100))
        else:
            self.musculo = None
        return self.musculo

    def calcular_relaciones(self):
        self.calcular_rcc()
        self.calcular_rca()

    def calcular_todo(self):
        self.calcular_imc()
        self.calcular_metabolismo_basal()
        self.calcular_grasa_corporal()
        self.calcular_agua_corporal()
        self.calcular_relaciones()
        self.calcular_musculo()

# =========================================================
# 💰 PAGO CLIENTE
# =========================================================
class PagoCliente(db.Model):
    __tablename__ = 'pagos_clientes'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )
    monto = db.Column(db.Float, nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
    mes_correspondiente = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), default='Pendiente')  # Pendiente / Aprobado / Rechazado
