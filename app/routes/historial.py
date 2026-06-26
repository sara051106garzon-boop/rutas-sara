# app/routes/historial.py
"""
ParkLink - Vista 31: Historial Personal de Uso
Blueprint: historial_bp
Permite al empleado revisar los días y horas en que ha parqueado.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.database import db
from app.models.acceso import Acceso
from app.models.vehiculo import Vehiculo

historial_bp = Blueprint("historial", __name__)


# ── HISTORIAL PERSONAL DE PARQUEO (GET) ──────────────────────────────────────
@historial_bp.route("/historial", methods=["GET"])
@jwt_required()
def get_historial():
    """
    Retorna todos los registros de entrada/salida de los vehículos del empleado.
    Soporta filtros opcionales por mes y año via query params:
      ?mes=6&anio=2025
    """
    try:
        datos_token = get_jwt_identity()
        if not datos_token:
            return jsonify({"error": "No se pudo validar la identidad corporativa."}), 401

        usuario_id = datos_token.get("id")

        # Obtener IDs de vehículos del empleado
        vehiculos = Vehiculo.query.filter_by(usuario_id=usuario_id).all()
        ids_vehiculos = [v.id for v in vehiculos]

        if not ids_vehiculos:
            return jsonify({
                "registros": [],
                "total": 0,
                "mensaje": "No tienes vehículos registrados."
            }), 200

        # Filtros opcionales de fecha
        mes = request.args.get("mes", type=int)
        anio = request.args.get("anio", type=int)

        query = Acceso.query.filter(Acceso.vehiculo_id.in_(ids_vehiculos))

        if mes:
            if mes < 1 or mes > 12:
                return jsonify({"error": "El mes debe estar entre 1 y 12."}), 400
            query = query.filter(db.extract("month", Acceso.fecha_hora) == mes)

        if anio:
            query = query.filter(db.extract("year", Acceso.fecha_hora) == anio)

        registros = query.order_by(Acceso.fecha_hora.desc()).all()

        resultado = []
        for a in registros:
            resultado.append({
                "id": a.id,
                "placa": a.placa,
                "tipo_movimiento": a.tipo_movimiento,    # "Entrada" o "Salida"
                "tipo_vehiculo": a.tipo_vehiculo,
                "celda_asignada": a.celda_asignada,
                "fecha_hora": a.fecha_hora.strftime("%Y-%m-%d %H:%M:%S") if a.fecha_hora else None,
                "observaciones": a.observaciones_salida,
            })

        return jsonify({
            "registros": resultado,
            "total": len(resultado)
        }), 200

    except Exception as e:
        print(f"❌ Error en GET /historial: {str(e)}")
        return jsonify({"error": f"Error interno en el servidor: {str(e)}"}), 500