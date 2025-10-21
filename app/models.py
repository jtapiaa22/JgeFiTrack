from app.extensions import db
from flask_login import UserMixin
from datetime import datetime


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

    # Relaciones en cascada
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
    agua_corporal = db.Column(db.Float)
    rcc = db.Column(db.Float)
    rca = db.Column(db.Float)

    alumno_id = db.Column(
        db.Integer,
        db.ForeignKey('alumno.id', ondelete='CASCADE'),
        nullable=False
    )

    # =============================
    # FUNCIONES DE CÁLCULO
    # =============================
    def calcular_imc(self):
        if self.peso and self.altura:
            self.imc = round(self.peso / ((self.altura / 100) ** 2), 2)

    def calcular_metabolismo_basal(self, genero="masculino", edad=25):
        if self.peso and self.altura:
            if genero.lower() == "femenino":
                self.metabolismo_basal = round(10 * self.peso + 6.25 * self.altura - 5 * edad - 161, 2)
            else:
                self.metabolismo_basal = round(10 * self.peso + 6.25 * self.altura - 5 * edad + 5, 2)

    def calcular_grasa_corporal(self, genero="masculino", edad=25):
        if self.imc and edad:
            if genero.lower() == "femenino":
                self.grasa_corporal = round(1.29579 * self.imc + 0.23 * edad - 5.4, 2)
            else:
                self.grasa_corporal = round(1.29579 * self.imc + 0.23 * edad - 16.2, 2)

            if self.cintura and self.cadera:
                ajuste = min((self.cintura / self.cadera) * 2, 3)
                self.grasa_corporal = round(self.grasa_corporal + ajuste, 2)
        else:
            self.grasa_corporal = None

    def calcular_agua_corporal(self, genero="masculino", edad=25):
        if self.peso and self.altura:
            if genero.lower() == "femenino":
                tbw = -2.097 + (0.1069 * self.altura) + (0.2466 * self.peso)
            else:
                tbw = 2.447 - (0.09156 * edad) + (0.1074 * self.altura) + (0.3362 * self.peso)
            self.agua_corporal = round((tbw / self.peso) * 100, 2)
        else:
            self.agua_corporal = None

    def calcular_relaciones(self):
        if self.cintura and self.cadera:
            self.rcc = round(self.cintura / self.cadera, 2)
        if self.cintura and self.altura:
            self.rca = round(self.cintura / self.altura, 2)

    def calcular_musculo(self):
        if self.grasa_corporal is not None and self.agua_corporal is not None:
            masa_magra = 100 - self.grasa_corporal
            self.musculo = round(masa_magra * 0.8, 2)
        elif self.grasa_corporal is not None:
            self.musculo = round((100 - self.grasa_corporal) * 0.8, 2)
        else:
            self.musculo = None

        if self.musculo is not None:
            self.musculo = max(0, min(self.musculo, 100))

    def calcular_todo(self, genero="masculino", edad=25):
        self.calcular_imc()
        self.calcular_metabolismo_basal(genero, edad)
        self.calcular_grasa_corporal(genero, edad)
        self.calcular_agua_corporal(genero, edad)
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
