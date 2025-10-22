# JgeFiTrack - Setup, Mantenimiento y Administración

Proyecto: **JgeFiTrack**  
Backend: Flask + SQLAlchemy  
Base de datos: PostgreSQL (local/desarrollo y producción en Render)

---

## 🚀 Requisitos previos

- Python 3.x
- PostgreSQL instalado (https://www.postgresql.org/download/)
- pgAdmin o DBeaver (opcional, para administrar la base visualmente)
- pip, virtualenv

---

## ⚙️ Instalación y configuración inicial

1. **Clona el repositorio y crea el entorno virtual**

git clone <URL-del-repo>
cd JgeFiTrack
python -m venv venv
.\venv\Scripts\activate # Windows
source venv/bin/activate # Mac/Linux
pip install -r requirements.txt


2. **Configura el archivo `.env` en la raíz**

Base local para desarrollo
DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA@localhost:5432/jgefitrack_test
SECRET_KEY=clave-secreta-random

Usuario admin por defecto (ajusta lo que desees)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_NOMBRE=Administrador


3. **Crea la base de datos en PostgreSQL local**

- Usa pgAdmin: click derecho en "Databases" → "Create" → `jgefitrack_test`.
- En terminal:  
  ```
  createdb -U postgres jgefitrack_test
  ```

4. **Inicializa y migra la base (migraciones SQLAlchemy/Alembic/Flask-Migrate)**

flask db init # Solo la primera vez (crea carpeta migrations/)
flask db migrate -m "init" # Genera archivo de migración según modelos
flask db upgrade # Aplica migraciones y crea tablas


5. **Levanta la aplicación**

flask run

---

## 🐘 Migraciones y cambios de estructura

- Al agregar/modificar modelos:
flask db migrate -m "Nueva tabla/campo"
flask db upgrade
- Si hay problemas de duplicados/errores, puedes:
- Borrar la carpeta `migrations/` (solo en desarrollo/local).
- Borrar tablas manualmente en pgAdmin.
- Reiniciar el flujo `init → migrate → upgrade`.

---

## 📀 Backup y restauración

### **Backup local**
- Usa pgAdmin/DBeaver:
- Click derecho sobre la base → "Backup"
- Formato: `.backup` o `.sql`

### **Restaurar en local**
- Desde pgAdmin:
- Click derecho sobre la base → "Restore"
- Selecciona el archivo backup.

### **Backup en producción (Render)**
- El plan gratuito **no habilita conexión ni backup externo**.  
- Alternativas:
- Exporta datos por script Python/Flask dentro de la app (ejemplo: exportar a CSV/JSON/SQL).
- Consulta el dashboard de Render por opción de “snapshot”.

---

## ⚡ Fixes y errores frecuentes

- **No conecta a base de Render:**  
Probablemente el plan gratuito no habilita acceso externo.
- **Migración con columna duplicada:**  
Borrar la carpeta `migrations/`, eliminar tablas a mano y reiniciar el flujo.
- **Error de codificación (UTF-8):**  
Revisa que el `.env` y todas tus contraseñas/datos solo tengan caracteres ASCII.
- **No se crea la carpeta migrations:**  
Puede ser permisos de carpeta, reiniciar terminal o crear manualmente.

---

## 📝 Notas para el futuro

- Mantén este README siempre actualizado con nuevos comandos o fixes.
- Guarda todos los backups y exportaciones importantes en una carpeta separada, versionada.
- Documenta los scripts personalizados en una sección aparte si haces export/import no estándar.
- Si migras el proyecto a otro equipo/servidor, esta guía te permitirá instalar y restaurar todo en minutos.

---

## 👨‍💻 Uso en producción y despliegue

- Render gestiona la conexión y autenticación vía variables de entorno (`DATABASE_URL`).
- Para debugging, usar logs del servidor o exportar automáticamente los errores bajo demanda.
- No olvides eliminar endpoints de exportación pública una vez usado.

---

## ✨ Créditos y autor

- Proyecto probado/desarrollado por **Jorge Alejandro Tapia Ahumada**
- Última actualización: 2025-10-22

