# app/routes/celdas.py
"""
ParkLink - Rutas para la gestión y auditoría del estado de las celdas del parqueadero.
Blueprint: celdas_bp
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.database import db
from app.models.celda import Celda
from app.models.usuario import Usuario

celdas_bp = Blueprint("celdas", __name__)

# ── 1. OBTENER TODAS LAS CELDAS (Para el mapa visual de Celdas.jsx) ──────────
@celdas_bp.route("/celdas", methods=["GET"])
@jwt_required()
def obtener_mapa_celdas():
    """
    Retorna el estado actual de todas las celdas registradas en el sistema corporativo.
    """
    try:
        datos_token = get_jwt_identity()
        if not datos_token:
            return jsonify({"error": "No se pudo validar la identidad corporativa."}), 401

        # Traer todas las celdas ordenadas por su código alfanumérico
        celdas = Celda.query.order_by(Celda.codigo_celda.asc()).all()
        
        resultado = []
        for c in celdas:
            resultado.append({
                "id": c.id,
                "codigo_celda": c.codigo_celda,
                "tipo_celda": c.tipo_celda,
                "ocupada": c.ocupada
            })

        return jsonify(resultado), 200

    except Exception as e:
        print(f"❌ Error en GET /celdas: {str(e)}")
        return jsonify({"error": f"Error interno al recuperar el mapa de celdas: {str(e)}"}), 500


# ── 2. CAMBIAR ESTADO DE UNA CELDA (Para liberar o bloquear manualmente) ───
@celdas_bp.route("/celdas/<int:celda_id>/estado", methods=["PUT"])
@jwt_required()
def cambiar_estado_celda(celda_id):
    """
    Permite al administrador o vigilante conmutar el estado de ocupación de una celda.
    """
    try:
        data = request.get_json(silent=True) or {}
        # Esperamos un booleano en el JSON corporativo (True = Ocupada, False = Disponible)
        nuevo_estado = data.get('ocupada') 

        if nuevo_estado is None:
            return jsonify({"error": "El campo 'ocupada' (booleano) es obligatorio."}), 400

        celda = Celda.query.get(celda_id)
        if not celda:
            return jsonify({"error": "La celda especificada no existe."}), 404

        # Cambiar estado y persistir en la base de datos
        celda.ocupada = bool(nuevo_estado)
        db.session.commit()

        accion = "ocupada" if celda.ocupada else "liberada"
        return jsonify({
            "message": f"La celda {celda.codigo_celda} ha sido {accion} con éxito.",
            "celda": {
                "id": celda.id,
                "codigo_celda": celda.codigo_celda,
                "ocupada": celda.ocupada
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en PUT /celdas/estado: {str(e)}")
        return jsonify({"error": f"Error al actualizar la celda: {str(e)}"}), 500
    
    # Al final de app/routes/celdas.py

# ── 3. REGISTRAR NUEVA CELDA (POST) ─────────────────────────────────────────
@celdas_bp.route("/celdas", methods=["POST"])
@jwt_required()
def registrar_celda():
    """
    Permite al administrador dar de alta una nueva celda en el sistema ParkLink.
    """
    try:
        datos_token = get_jwt_identity()
        # (Opcional) Puedes añadir aquí tu validación de rol de administrador si lo requieres

        data = request.get_json(silent=True) or {}
        codigo_celda = data.get('codigo_celda')
        tipo_celda = data.get('tipo_celda') # Esperamos "eléctricos" o "movilidad"

        if not codigo_celda or not tipo_celda:
            return jsonify({"error": "El código y el tipo de celda son obligatorios."}), 400

        # Sanitizar y normalizar strings para que coincidan con los filtros del front
        codigo_limpio = codigo_celda.strip().upper()
        tipo_limpio = tipo_celda.strip().lower()

        # Validar que no exista duplicada
        existe = Celda.query.filter_by(codigo_celda=codigo_limpio).first()
        if existe:
            return jsonify({"error": f"La celda {codigo_limpio} ya se encuentra registrada."}), 400

        # Crear y persistir la nueva celda en la BD
        nueva_celda = Celda(
            codigo_celda=codigo_limpio,
            tipo_celda=tipo_limpio,
            ocupada=False # Toda celda nueva inicia disponible
        )

        db.session.add(nueva_celda)
        db.session.commit()

        return jsonify({
            "message": f"Celda {codigo_limpio} registrada con éxito como uso prioritario.",
            "celda": {
                "id": nueva_celda.id,
                "codigo_celda": nueva_celda.codigo_celda,
                "tipo_celda": nueva_celda.tipo_celda
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en POST /celdas: {str(e)}")
        return jsonify({"error": f"Error interno al registrar la celda: {str(e)}"}), 500