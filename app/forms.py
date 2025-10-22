from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, FloatField, DateField, SubmitField, PasswordField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesion')


class RegistroForm(FlaskForm):
    nombre = StringField('Nombre completo', validators=[DataRequired(), Length(min=3, max=50)])
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=30)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Registrar')


class EditarClienteForm(FlaskForm):
    nombre = StringField('Nombre completo', validators=[DataRequired(), Length(min=3, max=50)])
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=30)])
    password = PasswordField('Contraseña')
    submit = SubmitField('Registrar')



class MedicionForm(FlaskForm):
    alumno = SelectField('Alumno', coerce=int, validators=[DataRequired()])
    fecha = DateField('Fecha de Medicion', validators=[DataRequired()])

    #modo: manual o balanza
    modo = RadioField("Modo de carga", choices=[("manual", "Carga manual"), ("balanza","Desde balanza")], default="manual")

     #campos que aparecen primero (Visibles)
    altura = FloatField('Altura (cm)', validators=[DataRequired()])
    cadera = FloatField('Cadera (cm)', validators=[DataRequired()])
    cintura = FloatField('Cintura (cm)', validators=[DataRequired()])
    brazo = FloatField('Brazo (cm)', validators=[DataRequired()])
    pecho = FloatField('Pecho (cm)', validators=[DataRequired()])
    muslo = FloatField('Muslo (cm)', validators=[DataRequired()])
    peso = FloatField('Peso (kg)', validators=[DataRequired()])
    
    
    #campos que se ingresan desde balanza
    grasa_corporal = FloatField('Grasa Corporal (%)', validators=[Optional()])
    musculo = FloatField('Musculo', validators=[Optional()])
    agua_corporal = FloatField('Agua Corporal (%)', validators=[Optional()])
    metabolismo_basal = FloatField('Metabolismo Basal (kcal)', validators=[Optional()])


    submit = SubmitField('Guardar')

    
    

class AlumnoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    edad = IntegerField('Edad')
    genero = SelectField('Genero', choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino')])
    submit = SubmitField('Agregar Alumno')



class EditarMedicionForm(FlaskForm):
    fecha = DateField('Fecha', validators=[DataRequired()])
    #modo: manual o balanza
    modo = RadioField("Modo de carga", choices=[("manual", "Carga manual"), ("balanza","Desde balanza")], default="manual")

     #campos que aparecen primero (Visibles)
    altura = FloatField('Altura (cm)', validators=[DataRequired()])
    cadera = FloatField('Cadera (cm)', validators=[DataRequired()])
    cintura = FloatField('Cintura (cm)', validators=[DataRequired()])
    brazo = FloatField('Brazo (cm)', validators=[DataRequired()])
    pecho = FloatField('Pecho (cm)', validators=[DataRequired()])
    muslo = FloatField('Muslo (cm)', validators=[DataRequired()])
    peso = FloatField('Peso (kg)', validators=[DataRequired()])
    
    
    #campos que se ingresan desde balanza
    grasa_corporal = FloatField('Grasa Corporal (%)', validators=[Optional()])
    musculo = FloatField('Musculo', validators=[Optional()])
    agua_corporal = FloatField('Agua Corporal (%)', validators=[Optional()])
    metabolismo_basal = FloatField('Metabolismo Basal (kcal)', validators=[Optional()])