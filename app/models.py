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
        if not (self.cintura and self.cadera and self.altura):
            self.grasa_corporal = None
            return

        try:
            # Convertir altura a cm si viene en metros (por seguridad)
            altura = self.altura
            if altura < 10:  # por si el usuario la ingresó en metros
                altura *= 100

            # ===== US NAVY (ajustada sin cuello) =====
            if genero.lower() == "masculino":
                # Fórmula adaptada para hombres (sin cuello)
                bf = (86.010 * math.log10(self.cintura - self.cintura * 0.25)) \
                    - (70.041 * math.log10(altura)) + 36.76
            else:
                # Fórmula adaptada para mujeres (sin cuello)
                bf = (163.205 * math.log10(self.cintura + self.cadera - self.cintura * 0.2)) \
                    - (97.684 * math.log10(altura)) - 78.387
                
            # Calcular masa grasa en kg
            if self.grasa_corporal and self.peso:
                self.masa_grasa = round(self.peso * (self.grasa_corporal / 100), 2)
            else:
                self.masa_grasa = None


            # Limitar a rango fisiológico normal
            self.grasa_corporal = round(max(2, min(bf, 60)), 2)

        except (ValueError, ZeroDivisionError):
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
        """
        Calcula el porcentaje de masa muscular estimada
        en función del porcentaje de grasa corporal.
        Basado en la proporción fisiológica promedio:
        - Hombres: músculo ≈ 50 – 60% del peso magro
        - Mujeres: músculo ≈ 45 – 55% del peso magro
        """
        if self.grasa_corporal is None:
            self.musculo = None
            return

        # Calcular masa magra (100 - grasa)
        masa_magra = 100 - self.grasa_corporal

        # Ajuste por género
        if hasattr(self, "alumno") and self.alumno and self.alumno.genero:
            genero = self.alumno.genero.lower()
        else:
            genero = "masculino"

        if genero == "femenino":
            self.musculo = round(masa_magra * 0.50, 2)  # mujeres: ~50% masa magra
        else:
            self.musculo = round(masa_magra * 0.55, 2)  # hombres: ~55% masa magra

        # Limitar rango 0–100
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
