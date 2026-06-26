# app/routes/notificaciones.py
"""
ParkLink - Vista 32: Centro de Notificaciones
Blueprint: notificaciones_bp
Bandeja de avisos del sistema (aprobación de cuenta, alertas de tiempo).
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.alertas import Alerta

notificaciones_bp = Blueprint("notificaciones", __name__)

SEVERIDADES_VALIDAS = {"informativo", "advertencia", "urgente"}


# ── 1. LISTAR NOTIFICACIONES (GET) ───────────────────────────────────────────
@notificaciones_bp.route("/notificaciones", methods=["GET"])
@jwt_required()
def get_notificaciones():
    """
    Retorna todas las alertas/avisos del sistema para el empleado.
    Soporta filtro opcional por severidad via query param:
      ?severidad=urgente
    """
    try:
        datos_token = get_jwt_identity()
        if not datos_token:
            return jsonify({"error": "No se pudo validar la identidad corporativa."}), 401

        severidad = request.args.get("severidad", "").strip().lower() or None

        if severidad and severidad not in SEVERIDADES_VALIDAS:
            return jsonify({
                "error": f"Severidad inválida. Opciones: {list(SEVERIDADES_VALIDAS)}"
            }), 400

        query = Alerta.query
        if severidad:
            query = query.filter(Alerta.severidad == severidad)

        alertas = query.order_by(Alerta.fecha_publicacion.desc()).all()

        resultado = []
        for a in alertas:
            resultado.append({
                "id": a.id,
                "titulo": a.titulo,
                "severidad": a.severidad,
                "contenido": a.contenido,
                "fecha_publicacion": a.fecha_publicacion.strftime("%Y-%m-%d %H:%M:%S") if a.fecha_publicacion else None
            })

        return jsonify(resultado), 200

    except Exception as e:
        print(f"❌ Error en GET /notificaciones: {str(e)}")
        return jsonify({"error": f"Error interno en el servidor: {str(e)}"}), 500


# ── 2. RESUMEN DE CONTEOS (GET) ───────────────────────────────────────────────
@notificaciones_bp.route("/notificaciones/resumen", methods=["GET"])
@jwt_required()
def get_resumen_notificaciones():
    """
    Retorna conteo por severidad. Útil para los badges/contadores en la UI.
    """
    try:
        datos_token = get_jwt_identity()
        if not datos_token:
            return jsonify({"error": "No se pudo validar la identidad corporativa."}), 401

        total = Alerta.query.count()
        urgentes = Alerta.query.filter_by(severidad="urgente").count()
        advertencias = Alerta.query.filter_by(severidad="advertencia").count()
        informativos = Alerta.query.filter_by(severidad="informativo").count()

        return jsonify({
            "total": total,
            "urgentes": urgentes,
            "advertencias": advertencias,
            "informativos": informativos
        }), 200

    except Exception as e:
        print(f"❌ Error en GET /notificaciones/resumen: {str(e)}")
        return jsonify({"error": f"Error interno en el servidor: {str(e)}"}), 500