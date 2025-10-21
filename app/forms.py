from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, SubmitField, PasswordField, IntegerField, SelectField
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
    fecha = DateField('Fecha', validators=[DataRequired()])
    peso = FloatField('Peso (kg)', validators=[DataRequired()])
    altura = FloatField('Altura (cm)', validators=[DataRequired()])
    grasa_corporal = FloatField('Grasa Corporal (%)')
    musculo = FloatField('Musculo')
    cintura = FloatField('Cintura (cm)')
    cadera = FloatField('Cadera (cm)')
    pecho = FloatField('Pecho (cm)')
    brazo = FloatField('Brazo (cm)')
    muslo = FloatField('Muslo (cm)')
    submit = SubmitField('Guardar')



class AlumnoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    edad = IntegerField('Edad')
    genero = SelectField('Genero', choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino')])
    submit = SubmitField('Agregar Alumno')



class EditarMedicionForm(FlaskForm):
    fecha = DateField('Fecha', validators=[DataRequired()])
    peso = FloatField('Peso (kg)', validators=[DataRequired()])
    altura = FloatField('Altura (cm)', validators=[DataRequired()])
    musculo = FloatField('Musculo')
    cintura = FloatField('Cintura (cm)')
    cadera = FloatField('Cadera (cm)')
    pecho = FloatField('Pecho (cm)')
    brazo = FloatField('Brazo (cm)')
    muslo = FloatField('Muslo (cm)')
    submit = SubmitField('Actualizar')