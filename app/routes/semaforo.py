# app/routes/semaforo.py
"""
ParkLink - Vista 29: Semáforo de Disponibilidad
Blueprint: semaforo_bp
Permite al empleado consultar cupos libres antes de conducir hacia la empresa.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.database import db
from app.models.celda import Celda

semaforo_bp = Blueprint("semaforo", __name__)


# ── DISPONIBILIDAD GENERAL DEL PARQUEADERO (GET) ─────────────────────────────
@semaforo_bp.route("/disponibilidad", methods=["GET"])
@jwt_required()
def get_disponibilidad():
    """
    Retorna cupos totales, ocupados y libres por tipo de celda.
    El frontend usa esta info para mostrar el semáforo (verde / amarillo / rojo).
    """
    try:
        datos_token = get_jwt_identity()
        if not datos_token:
            return jsonify({"error": "No se pudo validar la identidad corporativa."}), 401

        celdas = Celda.query.all()

        # Agrupar por tipo de celda
        resumen_por_tipo = {}
        for celda in celdas:
            tipo = celda.tipo_celda
            if tipo not in resumen_por_tipo:
                resumen_por_tipo[tipo] = {"total": 0, "ocupadas": 0, "libres": 0}
            resumen_por_tipo[tipo]["total"] += 1
            if celda.ocupada:
                resumen_por_tipo[tipo]["ocupadas"] += 1
            else:
                resumen_por_tipo[tipo]["libres"] += 1

        total = len(celdas)
        ocupadas = sum(1 for c in celdas if c.ocupada)
        libres = total - ocupadas

        # Lógica del semáforo general
        if total == 0:
            estado = "sin_datos"
        elif libres == 0:
            estado = "rojo"        # Sin cupos
        elif libres <= total * 0.2:
            estado = "amarillo"    # Menos del 20% disponible
        else:
            estado = "verde"       # Hay cupos disponibles

        return jsonify({
            "total": total,
            "ocupadas": ocupadas,
            "libres": libres,
            "estado": estado,
            "por_tipo": resumen_por_tipo
        }), 200

    except Exception as e:
        print(f"❌ Error en GET /disponibilidad: {str(e)}")
        return jsonify({"error": f"Error interno en el servidor: {str(e)}"}), 500