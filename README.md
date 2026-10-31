<div align="center">

# ParkLink — Rutas del Back-End

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](LICENSE)

Ejercicio de construcción del back-end de **ParkLink**: definición de rutas,
controladores, servicios y modelos sobre Flask + SQLAlchemy.

</div>

---

## Descripción

Este repositorio reúne la capa de rutas del sistema de parqueaderos ParkLink. Cada
módulo del negocio tiene su propio blueprint, un controlador y los modelos que
necesita, de modo que la API queda separada por responsabilidades.

## Módulos

| Grupo | Blueprints |
| :--- | :--- |
| **Acceso** | `auth`, `admin`, `accesos`, `vehiculosUsuario` |
| **Operación** | `celdas`, `turnos`, `novedades`, `alertas`, `semaforo` |
| **Análisis** | `kpis`, `tendencias`, `historial`, `logs`, `panelControl` |
| **Configuración** | `configuraciones`, `notificaciones` |

## Estructura

```
app/
├── config/settings.py        Configuración por entorno
├── database/database.py      Conexión e inicialización
├── controllers/              Lógica de los endpoints
├── middlewares/roles.py      Validación de permisos por rol
├── models/                   Usuario, vehículo, celda, turno, acceso, novedad, alerta…
├── routes/                   Un blueprint por módulo
└── services/                 Reglas de negocio (auth, vehículos)
migrations/                   Migraciones de Alembic
run.py                        Punto de entrada
seed.py                       Datos de prueba
```

## Cómo ejecutarlo

```bash
python -m venv venv
venv\Scripts\activate         # Windows
pip install -r requirements.txt
python seed.py
python run.py
```

La API queda disponible en `http://127.0.0.1:5000`.

## Repositorios relacionados

- Versión final del back-end: [parklink-backend](https://github.com/sara051106garzon-boop/parklink-backend)
- App móvil: [parklink-app](https://github.com/sara051106garzon-boop/parklink-app)

## Autor

**Sara Garzón** · [github.com/sara051106garzon-boop](https://github.com/sara051106garzon-boop)

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).
