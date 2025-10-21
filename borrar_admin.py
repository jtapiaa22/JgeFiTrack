from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    u = User.query.filter_by(username="jgefitrack").first()
    if u:
        db.session.delete(u)
        db.session.commit()
        print("✅ Usuario admin eliminado correctamente.")
    else:
        print("⚠️ No se encontró el usuario admin.")
