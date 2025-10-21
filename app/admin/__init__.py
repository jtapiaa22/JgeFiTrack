from flask import Blueprint

#blueprint del admin
admin = Blueprint('admin', __name__, template_folder='../templates')

#importamos rutas al final para evitar referencias circulares
from app.admin import routes
