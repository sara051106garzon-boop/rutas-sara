# app/routes/vehiculos_usuario.py
"""
ParkLink - Vista 30: Gestión de Vehículos del Empleado
Blueprint: vehiculos_usuario_bp
Permite al empleado añadir, editar y eliminar sus propias placas (carro o moto).
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.database import db
from app.models.vehiculo import Vehiculo

vehiculos_usuario_bp = Blueprint("vehiculos_usuario", __name__)

TIPOS_VALIDOS = {"Automóvil", "Motocicleta"}
AREAS_VALIDAS = {
    "Tecnología e Innovación",
    "Operaciones y Logística",
    "Recursos Humanos",
    "Financiero",
    "Comercial",
    "Gerencia",
}


# ── 1. LISTAR MIS VEHÍCULOS (GET) ────────────────────────────────────────────
@vehiculos_usuario_bp.route("/mis-vehiculos", methods=["GET"])
@jwt_required()
def get_mis_vehiculos():
    """
    Retorna todos los vehículos registrados por el empleado autenticado.
    """
    try:
        usuario_id = int(get_jwt_identity())

        vehiculos = Vehiculo.query.filter_by(usuario_id=usuario_id).all()
        
        resultado = []
        for v in vehiculos:
            resultado.append({
                "id": v.id,
                "placa": v.placa,
                "tipo_vehiculo": v.tipo_vehiculo,
                "marca": v.marca,
                "color": v.color,
                "area": v.area,
                "created_at": v.created_at.strftime("%Y-%m-%d %H:%M:%S") if v.created_at else None
            })

        return jsonify(resultado), 200

    except Exception as e:
        print(f"❌ Error en GET /mis-vehiculos: {str(e)}")
        return jsonify({"error": f"Error interno en el servidor: {str(e)}"}), 500


# ── 2. AÑADIR VEHÍCULO (POST) ─────────────────────────────────────────────────
@vehiculos_usuario_bp.route("/mis-vehiculos", methods=["POST"])
@jwt_required()
def crear_vehiculo():
    """
    Registra una nueva placa para el empleado autenticado.
    """
    try:
        usuario_id = int(get_jwt_identity())
        
        data = request.get_json(silent=True) or {}

        placa = data.get("placa", "").strip().upper()
        tipo_vehiculo = data.get("tipo_vehiculo", "").strip()
        marca = data.get("marca", "").strip() or None
        color = data.get("color", "").strip() or None
        area = data.get("area", "").strip()

        # Validaciones
        if not placa or not tipo_vehiculo or not area:
            return jsonify({"error": "Los campos placa, tipo_vehiculo y area son obligatorios."}), 400

        if len(placa) < 5 or len(placa) > 10:
            return jsonify({"error": "La placa debe tener entre 5 y 10 caracteres."}), 400

        if tipo_vehiculo not in TIPOS_VALIDOS:
            return jsonify({"error": f"Tipo de vehículo inválido. Opciones: {list(TIPOS_VALIDOS)}"}), 400

        if area not in AREAS_VALIDAS:
            return jsonify({"error": f"Área inválida. Opciones: {list(AREAS_VALIDAS)}"}), 400

        # Verificar que la placa no exista
        existente = Vehiculo.query.filter_by(placa=placa).first()
        if existente:
            return jsonify({"error": f"La placa '{placa}' ya está registrada en el sistema."}), 409

        nuevo = Vehiculo(
            placa=placa,
            tipo_vehiculo=tipo_vehiculo,
            marca=marca,
            color=color,
            area=area,
            usuario_id=usuario_id
        )

        db.session.add(nuevo)
        db.session.commit()

        return jsonify({"message": f"Vehículo con placa '{placa}' registrado exitosamente."}), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en POST /mis-vehiculos: {str(e)}")
        return jsonify({"error": f"Error interno en el servidor: {str(e)}"}), 500


# ── 3. EDITAR VEHÍCULO (PUT) ──────────────────────────────────────────────────
@vehiculos_usuario_bp.route("/mis-vehiculos/<int:vehiculo_id>", methods=["PUT"])
@jwt_required()
def editar_vehiculo(vehiculo_id):
    """
    Edita los datos de un vehículo propio del empleado autenticado.
    """
    try:
        usuario_id = int(get_jwt_identity())

        vehiculo = Vehiculo.query.filter_by(id=vehiculo_id, usuario_id=usuario_id).first()
        if not vehiculo:
            return jsonify({"error": "Vehículo no encontrado o no pertenece a tu cuenta."}), 404

        data = request.get_json(silent=True) or {}

        # Actualizar solo los campos que vengan en el body
        if "placa" in data:
            nueva_placa = data["placa"].strip().upper()
            dup = Vehiculo.query.filter(Vehiculo.placa == nueva_placa, Vehiculo.id != vehiculo_id).first()
            if dup:
                return jsonify({"error": f"La placa '{nueva_placa}' ya está en uso."}), 409
            vehiculo.placa = nueva_placa

        if "tipo_vehiculo" in data:
            if data["tipo_vehiculo"] not in TIPOS_VALIDOS:
                return jsonify({"error": f"Tipo de vehículo inválido. Opciones: {list(TIPOS_VALIDOS)}"}), 400
            vehiculo.tipo_vehiculo = data["tipo_vehiculo"]

        if "marca" in data:
            vehiculo.marca = data["marca"].strip() or None

        if "color" in data:
            vehiculo.color = data["color"].strip() or None

        if "area" in data:
            if data["area"] not in AREAS_VALIDAS:
                return jsonify({"error": f"Área inválida. Opciones: {list(AREAS_VALIDAS)}"}), 400
            vehiculo.area = data["area"]

        db.session.commit()

        return jsonify({"message": "Vehículo actualizado correctamente."}), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en PUT /mis-vehiculos/{vehiculo_id}: {str(e)}")
        return jsonify({"error": f"Error interno en el servidor: {str(e)}"}), 500


# ── 4. ELIMINAR VEHÍCULO (DELETE) ─────────────────────────────────────────────
@vehiculos_usuario_bp.route("/mis-vehiculos/<int:vehiculo_id>", methods=["DELETE"])
@jwt_required()
def eliminar_vehiculo(vehiculo_id):
    """
    Elimina un vehículo propio del empleado autenticado.
    """
    try:
        usuario_id = int(get_jwt_identity())

        vehiculo = Vehiculo.query.filter_by(id=vehiculo_id, usuario_id=usuario_id).first()
        if not vehiculo:
            return jsonify({"error": "Vehículo no encontrado o no pertenece a tu cuenta."}), 404

        placa = vehiculo.placa
        db.session.delete(vehiculo)
        db.session.commit()

        return jsonify({"message": f"Vehículo con placa '{placa}' eliminado correctamente."}), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en DELETE /mis-vehiculos/{vehiculo_id}: {str(e)}")
        return jsonify({"error": f"Error interno en el servidor: {str(e)}"}), 500