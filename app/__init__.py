# app/__init__.py

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate  
from app.config.settings import Config
from app.database.database import db, bcrypt, jwt

# ── Inicialización de la instancia global de Migrate ────────────────────────
migrate = Migrate()

def create_app():
    """
    Crea y configura la aplicación Flask de ParkLink.
    Devuelve la instancia lista para ser ejecutada por run.py o Gunicorn.
    """
    app = Flask(__name__)

    # ── 1. Configuración ──────────────────────────────────────────────────────
    app.config.from_object(Config)

    # ── 2. CORS (una sola vez) ────────────────────────────────────────────────
    # Permite solicitudes desde el frontend React en desarrollo.
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True,
    )

    # ── 3. Inicialización de extensiones ──────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # 🛠️ Inicializa y vincula Flask-Migrate con la App y SQLAlchemy
    migrate.init_app(app, db)

    # ── 4. Manejadores de errores JWT ─────────────────────────────────────────
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "mensaje": "El token ha expirado. Inicia sesión nuevamente.",
            "error": "token_expired"
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "mensaje": "Token inválido o corrupto.",
            "error": "invalid_token"
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "mensaje": "Se requiere autenticación. No se encontró un token de acceso.",
            "error": "authorization_required"
        }), 401

    # ── 5. Registro de Blueprints ─────────────────────────────────────────────
    # Se importan aquí dentro para prevenir referencias circulares en Python.
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.accesos import accesos_bp 
    from app.routes.celdas import celdas_bp
    from app.routes.alertas import alertas_bp
    from app.routes.kpis import kpis_bp
    from app.routes.logs import logs_bp
    from app.routes.configuraciones import config_bp
    from app.routes.tendencias import tendencias_bp
    from app.routes.semaforo import semaforo_bp
    from app.routes.vehiculosUsuario import vehiculos_usuario_bp
    from app.routes.historial import historial_bp
    from app.routes.notificaciones import notificaciones_bp
    from app.routes.panelControl import panel_control_bp

    # Registro limpio y obligatorio de los controladores de ParkLink
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(accesos_bp, url_prefix="/api/admin")
    app.register_blueprint(celdas_bp, url_prefix="/api/admin")
    app.register_blueprint(alertas_bp, url_prefix="/api/admin")
    app.register_blueprint(kpis_bp, url_prefix="/api/admin")
    app.register_blueprint(logs_bp)
    app.register_blueprint(config_bp, url_prefix="/api/admin")
    app.register_blueprint(tendencias_bp)
    app.register_blueprint(semaforo_bp, url_prefix="/api/user")
    app.register_blueprint(vehiculos_usuario_bp, url_prefix="/api/user")
    app.register_blueprint(historial_bp, url_prefix="/api/user")
    app.register_blueprint(notificaciones_bp, url_prefix="/api/user")
    app.register_blueprint(panel_control_bp, url_prefix="/api/user")

    # ── 6. Ruta de salud ──────────────────────────────────────────────────────
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "online",
            "project": "ParkLink",
            "version": "1.0.0"
        }), 200

    return app