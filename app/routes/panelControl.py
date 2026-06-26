# app/routes/panel_control.py
"""
ParkLink - Vista PanelControl: Dashboard principal del empleado
Blueprint: panel_control_bp
Resumen rápido: vehículos del empleado, último acceso, cupos y alertas urgentes.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.vehiculo import Vehiculo
from app.models.acceso import Acceso
from app.models.alertas import Alerta
from app.models.celda import Celda

panel_control_bp = Blueprint("panel_control", __name__)


# ── RESUMEN GENERAL DEL PANEL (GET) ──────────────────────────────────────────
@panel_control_bp.route("/panel", methods=["GET"])
@jwt_required()
def get_panel():
    """
    Retorna el resumen del dashboard para el empleado autenticado:
    - Cantidad de vehículos registrados
    - Último acceso al parqueadero
    - Disponibilidad general de celdas
    - Cantidad de alertas urgentes activas
    """
    try:
        datos_token = get_jwt_identity()
        if not datos_token:
            return jsonify({"error": "No se pudo validar la identidad corporativa."}), 401

        usuario_id = datos_token.get("id")

        # Vehículos del empleado
        vehiculos = Vehiculo.query.filter_by(usuario_id=usuario_id).all()
        ids_vehiculos = [v.id for v in vehiculos]

        # Último acceso registrado
        ultimo_acceso = None
        if ids_vehiculos:
            acceso = (
                Acceso.query
                .filter(Acceso.vehiculo_id.in_(ids_vehiculos))
                .order_by(Acceso.fecha_hora.desc())
                .first()
            )
            if acceso:
                ultimo_acceso = {
                    "placa": acceso.placa,
                    "tipo_movimiento": acceso.tipo_movimiento,
                    "celda_asignada": acceso.celda_asignada,
                    "fecha_hora": acceso.fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
                }

        # Disponibilidad del parqueadero
        total_celdas = Celda.query.count()
        celdas_ocupadas = Celda.query.filter_by(ocupada=True).count()
        celdas_libres = total_celdas - celdas_ocupadas

        # Alertas urgentes activas
        alertas_urgentes = Alerta.query.filter_by(severidad="urgente").count()

        return jsonify({
            "mis_vehiculos": len(vehiculos),
            "ultimo_acceso": ultimo_acceso,
            "parqueadero": {
                "total_celdas": total_celdas,
                "celdas_libres": celdas_libres,
                "celdas_ocupadas": celdas_ocupadas
            },
            "alertas_urgentes": alertas_urgentes
        }), 200

    except Exception as e:
        print(f"❌ Error en GET /panel: {str(e)}")
        return jsonify({"error": f"Error interno en el servidor: {str(e)}"}), 500