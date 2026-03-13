from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db

sos_bp = Blueprint('sos', __name__)

@sos_bp.route('/trigger', methods=['POST'])
@jwt_required()
def trigger_sos():
    """Trigger SOS alert"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get user details
        users = db.execute_query(
            "SELECT name, phone FROM users WHERE id = %s",
            (user_id,)
        )
        
        if not users:
            return jsonify({'error': 'User not found'}), 404
        
        # Get emergency contacts
        contacts = db.execute_query(
            "SELECT name, phone FROM emergency_contacts WHERE user_id = %s",
            (user_id,)
        )
        
        # Insert SOS alert
        result = db.execute_query("""
            INSERT INTO sos_alerts (user_id, latitude, longitude, address, message, status, created_at)
            VALUES (%s, %s, %s, %s, %s, 'active', NOW())
        """, (
            user_id, 
            data.get('latitude'), 
            data.get('longitude'), 
            data.get('address', ''),
            data.get('message', 'SOS Emergency! I need help.')
        ))
        
        return jsonify({
            'message': 'SOS triggered successfully',
            'sos_id': result.get('last_id') if result else None,
            'contacts_notified': len(contacts) if contacts else 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sos_bp.route('/history', methods=['GET'])
@jwt_required()
def get_sos_history():
    """Get user's SOS history"""
    try:
        user_id = get_jwt_identity()
        
        alerts = db.execute_query("""
            SELECT id, latitude, longitude, address, message, status, created_at 
            FROM sos_alerts 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """, (user_id,))
        
        return jsonify(alerts or []), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500