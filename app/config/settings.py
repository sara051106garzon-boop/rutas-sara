"""
ParkLink - Configuración centralizada de la aplicación.

Carga variables de entorno desde el archivo .env (python-dotenv).
Si no existe .env, usa valores por defecto seguros para desarrollo local con XAMPP.

Variables de entorno recomendadas en .env:
    SECRET_KEY=<cadena aleatoria larga>
    JWT_SECRET_KEY=<cadena aleatoria larga>
    MYSQL_USER=root
    MYSQL_PASSWORD=
    MYSQL_HOST=localhost
    MYSQL_PORT=3306
    MYSQL_DATABASE=parklink
    ADMIN_EMAILS=admin@redeban.com
    EMAIL_VIGILANTE_DOMINIO=@vigilancia.redeban.com
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Carga el archivo .env ubicado junto a este archivo (o en la raíz del proyecto)
load_dotenv()


class Config:
    # ── Claves secretas ───────────────────────────────────────────────────────
    # IMPORTANTE: en producción SIEMPRE usa variables de entorno con valores
    # largos y aleatorios — nunca los valores por defecto de abajo.
    SECRET_KEY = os.getenv("SECRET_KEY", "parklink_secret_key_cambia_esto_en_produccion")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "parklink_jwt_key_cambia_esto_en_produccion")

    # Tiempo de vida del token JWT (8 horas de sesión de trabajo)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    # ── Conexión MySQL / XAMPP ────────────────────────────────────────────────
    # Tu instalación de XAMPP no tiene contraseña de root — el campo queda vacío.
    # Si en algún momento le asignas contraseña a root en phpMyAdmin, actualiza
    # únicamente la variable MYSQL_PASSWORD en tu archivo .env.
    MYSQL_USER     = os.getenv("MYSQL_USER",     "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")        # Sin contraseña en XAMPP por defecto
    MYSQL_HOST     = os.getenv("MYSQL_HOST",     "localhost")
    MYSQL_PORT     = os.getenv("MYSQL_PORT",     "3306")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "parklink")

    # URI de SQLAlchemy con el driver PyMySQL (puro Python, sin depender de mysqlclient C).
    # Formato: mysql+pymysql://usuario:contraseña@host:puerto/basededatos
    # Con contraseña vacía la URI queda: mysql+pymysql://root:@localhost:3306/parklink
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        "?charset=utf8mb4"          # Soporte completo de Unicode (emojis, tildes, etc.)
    )

    # Desactiva el sistema de seguimiento de cambios de SQLAlchemy (consume memoria extra
    # y Flask mostrará una advertencia si lo dejas en True sin usarlo explícitamente).
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Opciones del pool de conexiones ──────────────────────────────────────
    # XAMPP/MySQL cierra conexiones inactivas después de ~8 horas (wait_timeout).
    # Sin pool_pre_ping, la primera petición después de ese tiempo falla con
    # "MySQL server has gone away". Con pool_pre_ping=True SQLAlchemy verifica
    # la conexión antes de usarla y la renueva si está muerta.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,       # Verifica la conexión antes de cada uso
        "pool_recycle": 1800,        # Renueva conexiones cada 30 min (antes del timeout de MySQL)
        "pool_size": 5,              # Conexiones simultáneas en el pool
        "max_overflow": 10,          # Conexiones extra permitidas en picos de tráfico
        "connect_args": {
            "connect_timeout": 10,   # Falla rápido si MySQL no responde en 10 s
        },
    }

    # ── Configuración de roles por correo ────────────────────────────────────
    # Los usuarios se auto-asignan rol según su correo al registrarse.
    # Edita estas variables (o ponlas en .env) según el dominio real de tu organización.

    # Correos que TERMINAN con este dominio → rol VIGILANTE
    EMAIL_VIGILANTE_DOMINIO = os.getenv(
        "EMAIL_VIGILANTE_DOMINIO", "guardia1@redeban.com"
    )

    # Correos EXACTOS (separados por coma en .env) → rol ADMINISTRADOR
    EMAIL_ADMIN_EXACTOS = [
        correo.strip().lower()
        for correo in os.getenv("ADMIN_EMAILS", "admin@redeban.com").split(",")
        if correo.strip()
    ]
