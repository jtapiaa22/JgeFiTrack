from datetime import datetime
from flask import Flask, flash, redirect, url_for
from flask_login import LoginManager, current_user, logout_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
from config import Config
from app.extensions import db, login_manager, migrate
from app.models import PagoCliente, User
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # -----------------------------------------------------------------
    # Registrar Blueprints
    # -----------------------------------------------------------------
    from app.main import main
    from app.cliente import cliente
    from app.admin import admin

    app.register_blueprint(main)
    app.register_blueprint(cliente, url_prefix="/cliente")
    app.register_blueprint(admin, url_prefix="/admin")

    # -----------------------------------------------------------------
    # Cargar usuario (para Flask-Login)
    # -----------------------------------------------------------------
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # =========================================================
    # CREAR USUARIO ADMIN PERSONAL (SOLO SI NO EXISTE NINGUNO)
    # =========================================================
    with app.app_context():
        try:
            # Crear tablas si no existen antes de buscar admin
            db.create_all()

            admin_existente = User.query.filter_by(is_admin=True).first()

            if not admin_existente:
                admin_user = os.environ.get("ADMIN_USERNAME")
                admin_pass = os.environ.get("ADMIN_PASSWORD")
                admin_nombre = os.environ.get("ADMIN_NOMBRE", "Administrador")

                if admin_user and admin_pass:
                    nuevo_admin = User(
                        username=admin_user,
                        password=generate_password_hash(admin_pass),
                        nombre=admin_nombre,
                        is_admin=True
                    )
                    db.session.add(nuevo_admin)
                    db.session.commit()
                    print(f">>Admin '{admin_user}' creado correctamente.")
                else:
                    print("No se creó ningún admin (faltan variables de entorno).")
            else:
                print(f">>Ya existe un administrador: {admin_existente.username}")

        except Exception as e:
            print(f">>No se pudo crear el usuario admin: {e}")

    # =========================================================
    # Context processors
    # =========================================================
    @app.context_processor
    def inject_version():
        return dict(config=app.config)

    @app.context_processor
    def override_url_for():
        def dated_url_for(endpoint, **values):
            if endpoint == 'static':
                filename = values.get('filename')
                if filename:
                    file_path = os.path.join(app.root_path, endpoint, filename)
                    if os.path.exists(file_path):
                        values['v'] = int(os.path.getmtime(file_path))
            return url_for(endpoint, **values)
        return dict(url_for=dated_url_for)

    # =========================================================
    # BLOQUEAR USUARIO SI NO TIENE PAGO DEL MES
    # =========================================================
    @app.before_request
    def verificar_pago_activo():
        if current_user.is_authenticated and not current_user.is_admin:
            pago = (PagoCliente.query
                    .filter_by(cliente_id=current_user.id, estado='Aprobado')
                    .order_by(PagoCliente.fecha_pago.desc())
                    .first())

            mes_actual = datetime.now().strftime("%B %Y")

            if not pago or pago.mes_correspondiente != mes_actual:
                flash("Tu cuenta no esta activada, contactate con el creador para solucionarlo", "danger")
                logout_user()
                return redirect(url_for('main.login'))

    
    # =========================================================
    # Ejecutar migraciones pendientes utilizando Flask-Migrate
    # =========================================================
    with app.app_context():
        try:
            from flask_migrate import upgrade
            upgrade()
            print("Migraciones Alembic (flask db upgrade) aplicadas automáticamente.")
        except Exception as e:
            print(f"Error al aplicar migraciones: {e}")



    
    return app
