from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import json

load_dotenv()

# Import database modules
from core.database import db, init_db
from models.user import User
from models.emergency_contact import EmergencyContact
from utils.validators import validate_email, validate_phone, validate_password

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Initialize extensions
    CORS(app, origins=['http://localhost:5500', 'http://127.0.0.1:5500'])
    jwt = JWTManager(app)
    
    # Setup logging
    setup_logging(app)
    
    # Test database connection
    if not init_db():
        app.logger.error("Failed to connect to database")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register routes
    register_routes(app)
    
    return app

def setup_logging(app):
    """Setup logging configuration"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/citizenshield.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('CitizenShield startup')

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400

def register_routes(app):
    """Register all routes"""
    
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({
            'name': 'CitizenShield API',
            'version': '2.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/health',
                'register': '/api/auth/register',
                'login': '/api/auth/login',
                'refresh': '/api/auth/refresh',
                'profile': '/api/profile',
                'profile_update': '/api/profile/update',
                'helplines': '/api/helplines',
                'sos_trigger': '/api/sos/trigger',
                'sos_history': '/api/sos/history',
                'admin_stats': '/api/admin/stats',
                'admin_users': '/api/admin/users',
                'admin_sos': '/api/admin/sos-alerts'
            }
        })
    
    @app.route('/api/health', methods=['GET'])
    def health():
        conn = db.get_connection()
        db_status = 'connected' if conn else 'disconnected'
        if conn: 
            conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        })
    
    # ============ AUTH ROUTES ============
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """Register a new user"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required = ['name', 'email', 'phone', 'password']
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Missing field: {field}'}), 400
            
            # Validate email
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            
            # Validate phone
            if not validate_phone(data['phone']):
                return jsonify({'error': 'Invalid phone number format'}), 400
            
            # Validate password strength
            is_valid, message = validate_password(data['password'])
            if not is_valid:
                return jsonify({'error': message}), 400
            
            # Check if user exists
            existing = User.find_by_email(data['email'])
            if existing:
                return jsonify({'error': 'Email already registered'}), 409
            
            # Check if phone exists
            existing_phone = db.execute_query(
                "SELECT id FROM users WHERE phone = %s",
                (data['phone'],)
            )
            if existing_phone:
                return jsonify({'error': 'Phone number already registered'}), 409
            
            # Create user
            result = User.create(
                data['name'],
                data['email'],
                data['phone'],
                data['password']
            )
            
            if result and result.get('last_id'):
                # Create access and refresh tokens
                access_token = create_access_token(identity=str(result['last_id']))
                refresh_token = create_access_token(identity=str(result['last_id']), fresh=True)
                
                app.logger.info(f"New user registered: {data['email']}")
                
                return jsonify({
                    'message': 'User created successfully',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'id': result['last_id'],
                        'name': data['name'],
                        'email': data['email'],
                        'phone': data['phone'],
                        'role': 'user'
                    }
                }), 201
            
            return jsonify({'error': 'Failed to create user'}), 500
            
        except Exception as e:
            app.logger.error(f"Registration error: {str(e)}")
            return jsonify({'error': 'Registration failed'}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Login user"""
        try:
            data = request.get_json()
            
            if not data or not data.get('email') or not data.get('password'):
                return jsonify({'error': 'Email and password required'}), 400
            
            # Find user
            user = User.find_by_email(data['email'])
            
            if not user or not User.verify_password(user['password_hash'], data['password']):
                return jsonify({'error': 'Invalid email or password'}), 401
            
            # Update last login
            db.execute_query(
                "UPDATE users SET last_login = NOW() WHERE id = %s",
                (user['id'],)
            )
            
            # Create tokens
            access_token = create_access_token(identity=str(user['id']))
            refresh_token = create_access_token(identity=str(user['id']), fresh=True)
            
            # Remove password hash from response
            del user['password_hash']
            
            app.logger.info(f"User logged in: {data['email']}")
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user
            }), 200
            
        except Exception as e:
            app.logger.error(f"Login error: {str(e)}")
            return jsonify({'error': 'Login failed'}), 500
    
    @app.route('/api/auth/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh():
        """Refresh access token"""
        try:
            current_user = get_jwt_identity()
            new_token = create_access_token(identity=current_user, fresh=False)
            return jsonify({'access_token': new_token}), 200
        except Exception as e:
            return jsonify({'error': 'Token refresh failed'}), 500
    
    # ============ PROFILE ROUTES ============
    
    @app.route('/api/profile', methods=['GET'])
    @jwt_required()
    def profile():
        """Get user profile"""
        try:
            user_id = get_jwt_identity()
            
            # Get user details
            users = db.execute_query(
                "SELECT id, name, email, phone, role, created_at FROM users WHERE id = %s",
                (user_id,)
            )
            
            if not users:
                return jsonify({'error': 'User not found'}), 404
            
            user = users[0]
            
            # Get emergency contacts
            try:
                contacts = db.execute_query(
                    """SELECT id, name, phone, email, relationship, is_primary 
                       FROM emergency_contacts 
                       WHERE user_id = %s 
                       ORDER BY is_primary DESC, created_at ASC""",
                    (user_id,)
                )
            except Exception as e:
                contacts = []
            
            # Get SOS count
            try:
                sos_count = db.execute_query(
                    "SELECT COUNT(*) as count FROM sos_alerts WHERE user_id = %s",
                    (user_id,)
                )
                sos_count_value = sos_count[0]['count'] if sos_count else 0
            except Exception as e:
                sos_count_value = 0
            
            user['emergency_contacts'] = contacts if contacts else []
            user['sos_count'] = sos_count_value
            
            return jsonify(user), 200
            
        except Exception as e:
            app.logger.error(f"Profile error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/profile/update', methods=['PUT'])
    @jwt_required()
    def update_user_profile():
        """Update user profile"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            updates = []
            params = []
            
            if 'name' in data and data['name']:
                updates.append("name = %s")
                params.append(data['name'])
            
            if 'phone' in data and data['phone']:
                existing_phone = db.execute_query(
                    "SELECT id FROM users WHERE phone = %s AND id != %s",
                    (data['phone'], user_id)
                )
                if existing_phone:
                    return jsonify({'error': 'Phone number already in use'}), 400
                
                if not data['phone'].replace('+', '').replace('-', '').replace(' ', '').isdigit():
                    return jsonify({'error': 'Invalid phone number format'}), 400
                updates.append("phone = %s")
                params.append(data['phone'])
            
            if not updates:
                return jsonify({'error': 'No fields to update'}), 400
            
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            result = db.execute_query(query, tuple(params))
            
            if result and result.get('affected_rows', 0) > 0:
                updated_user = db.execute_query(
                    "SELECT id, name, email, phone FROM users WHERE id = %s",
                    (user_id,)
                )
                return jsonify({
                    'message': 'Profile updated successfully',
                    'user': updated_user[0] if updated_user else None
                }), 200
            else:
                return jsonify({'error': 'No changes made'}), 400
                
        except Exception as e:
            app.logger.error(f"Profile update error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # ============ EMERGENCY CONTACTS ROUTES ============
    
    @app.route('/api/profile/contacts', methods=['POST'])
    @jwt_required()
    def add_emergency_contact():
        """Add emergency contact"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            required = ['name', 'phone']
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Missing field: {field}'}), 400
            
            contacts = db.execute_query(
                "SELECT COUNT(*) as count FROM emergency_contacts WHERE user_id = %s",
                (user_id,)
            )
            is_primary = contacts and contacts[0]['count'] == 0
            
            result = db.execute_query("""
                INSERT INTO emergency_contacts (user_id, name, phone, email, relationship, is_primary)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, data['name'], data['phone'], data.get('email'), 
                  data.get('relationship'), is_primary))
            
            if result and result.get('last_id'):
                return jsonify({
                    'message': 'Emergency contact added',
                    'contact_id': result['last_id'],
                    'is_primary': is_primary
                }), 201
            else:
                return jsonify({'error': 'Failed to add contact'}), 500
                
        except Exception as e:
            app.logger.error(f"Add contact error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/profile/contacts/<int:contact_id>', methods=['DELETE'])
    @jwt_required()
    def delete_emergency_contact(contact_id):
        """Delete emergency contact"""
        try:
            user_id = get_jwt_identity()
            
            contact = db.execute_query(
                "SELECT id, is_primary FROM emergency_contacts WHERE id = %s AND user_id = %s",
                (contact_id, user_id)
            )
            
            if not contact:
                return jsonify({'error': 'Contact not found'}), 404
            
            result = db.execute_query(
                "DELETE FROM emergency_contacts WHERE id = %s AND user_id = %s",
                (contact_id, user_id)
            )
            
            if contact[0]['is_primary']:
                db.execute_query("""
                    UPDATE emergency_contacts 
                    SET is_primary = TRUE 
                    WHERE user_id = %s 
                    LIMIT 1
                """, (user_id,))
            
            return jsonify({'message': 'Contact deleted successfully'}), 200
            
        except Exception as e:
            app.logger.error(f"Delete contact error: {str(e)}")
            return jsonify({'error': 'Failed to delete contact'}), 500
    
    @app.route('/api/profile/contacts/<int:contact_id>/primary', methods=['PUT'])
    @jwt_required()
    def set_primary_contact(contact_id):
        """Set a contact as primary"""
        try:
            user_id = get_jwt_identity()
            
            db.execute_query(
                "UPDATE emergency_contacts SET is_primary = FALSE WHERE user_id = %s",
                (user_id,)
            )
            
            result = db.execute_query(
                "UPDATE emergency_contacts SET is_primary = TRUE WHERE id = %s AND user_id = %s",
                (contact_id, user_id)
            )
            
            if result and result.get('affected_rows', 0) > 0:
                return jsonify({'message': 'Primary contact updated'}), 200
            else:
                return jsonify({'error': 'Contact not found'}), 404
                
        except Exception as e:
            app.logger.error(f"Set primary contact error: {str(e)}")
            return jsonify({'error': 'Failed to update primary contact'}), 500
    
    # ============ HELPLINE ROUTES ============
    
    @app.route('/api/helplines', methods=['GET'])
    def get_helplines():
        """Get all helplines"""
        try:
            result = db.execute_query(
                "SELECT * FROM helplines WHERE is_active = TRUE ORDER BY country, service_name"
            )
            return jsonify(result or [])
        except Exception as e:
            app.logger.error(f"Helplines error: {str(e)}")
            return jsonify([])
    
    # ============ SOS ROUTES ============
    
    @app.route('/api/sos/trigger', methods=['POST'])
    @jwt_required()
    def trigger_sos():
        """Trigger SOS alert"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            users = db.execute_query(
                "SELECT name, phone FROM users WHERE id = %s",
                (user_id,)
            )
            
            if not users:
                return jsonify({'error': 'User not found'}), 404
            
            contacts = db.execute_query(
                "SELECT name, phone FROM emergency_contacts WHERE user_id = %s",
                (user_id,)
            )
            
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
            
            app.logger.info(f"SOS triggered for user {user_id}")
            
            return jsonify({
                'message': 'SOS triggered successfully',
                'sos_id': result.get('last_id') if result else None,
                'contacts_notified': len(contacts) if contacts else 0,
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            app.logger.error(f"SOS trigger error: {str(e)}")
            return jsonify({'error': 'Failed to trigger SOS'}), 500
    
    @app.route('/api/sos/history', methods=['GET'])
    @jwt_required()
    def get_sos_history():
        """Get user's SOS history"""
        try:
            user_id = get_jwt_identity()
            
            alerts = db.execute_query("""
                SELECT id, latitude, longitude, address, message, status, 
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at
                FROM sos_alerts 
                WHERE user_id = %s 
                ORDER BY created_at DESC
                LIMIT 50
            """, (user_id,))
            
            return jsonify(alerts or [])
            
        except Exception as e:
            app.logger.error(f"SOS history error: {str(e)}")
            return jsonify([])
    
    # ============ ADMIN ROUTES ============
    
    @app.route('/api/admin/stats', methods=['GET'])
    @jwt_required()
    def admin_stats():
        """Get admin dashboard statistics"""
        try:
            user_id = get_jwt_identity()
            user = db.execute_query("SELECT role FROM users WHERE id = %s", (user_id,))
            if not user or user[0]['role'] != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            total_users = db.execute_query("SELECT COUNT(*) as count FROM users")[0]['count']
            total_sos = db.execute_query("SELECT COUNT(*) as count FROM sos_alerts")[0]['count']
            total_contacts = db.execute_query("SELECT COUNT(*) as count FROM emergency_contacts")[0]['count']
            total_admins = db.execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")[0]['count']
            
            return jsonify({
                'total_users': total_users,
                'total_sos': total_sos,
                'total_contacts': total_contacts,
                'total_admins': total_admins
            }), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/users', methods=['GET'])
    @jwt_required()
    def admin_users():
        """Get all users"""
        try:
            user_id = get_jwt_identity()
            user = db.execute_query("SELECT role FROM users WHERE id = %s", (user_id,))
            if not user or user[0]['role'] != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            users = db.execute_query("""
                SELECT id, name, email, phone, role, created_at 
                FROM users ORDER BY created_at DESC
            """)
            
            return jsonify(users), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/users/<int:user_id>', methods=['GET'])
    @jwt_required()
    def admin_get_user(user_id):
        """Get user by ID"""
        try:
            admin_id = get_jwt_identity()
            admin = db.execute_query("SELECT role FROM users WHERE id = %s", (admin_id,))
            if not admin or admin[0]['role'] != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            user = db.execute_query("SELECT id, name, email, phone, role FROM users WHERE id = %s", (user_id,))
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify(user[0]), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
    @jwt_required()
    def admin_update_user(user_id):
        """Update user by admin"""
        try:
            admin_id = get_jwt_identity()
            admin = db.execute_query("SELECT role FROM users WHERE id = %s", (admin_id,))
            if not admin or admin[0]['role'] != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            data = request.get_json()
            updates = []
            params = []
            
            if 'name' in data:
                updates.append("name = %s")
                params.append(data['name'])
            if 'email' in data:
                updates.append("email = %s")
                params.append(data['email'])
            if 'phone' in data:
                updates.append("phone = %s")
                params.append(data['phone'])
            if 'role' in data:
                updates.append("role = %s")
                params.append(data['role'])
            
            if updates:
                params.append(user_id)
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
                db.execute_query(query, tuple(params))
            
            return jsonify({'message': 'User updated successfully'}), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
    @jwt_required()
    def admin_delete_user(user_id):
        """Delete user by admin"""
        try:
            admin_id = get_jwt_identity()
            admin = db.execute_query("SELECT role FROM users WHERE id = %s", (admin_id,))
            if not admin or admin[0]['role'] != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            db.execute_query("DELETE FROM users WHERE id = %s", (user_id,))
            return jsonify({'message': 'User deleted successfully'}), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/sos-alerts', methods=['GET'])
    @jwt_required()
    def admin_sos_alerts():
        """Get all SOS alerts"""
        try:
            user_id = get_jwt_identity()
            user = db.execute_query("SELECT role FROM users WHERE id = %s", (user_id,))
            if not user or user[0]['role'] != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            alerts = db.execute_query("""
                SELECT s.*, u.name as user_name 
                FROM sos_alerts s
                LEFT JOIN users u ON s.user_id = u.id
                ORDER BY s.created_at DESC
                LIMIT 100
            """)
            
            return jsonify(alerts), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    print("\n" + "="*60)
    print("🚀 CitizenShield API Server v2.0")
    print("="*60)
    print(f"📍 Server: http://localhost:{port}")
    print(f"📍 Health: http://localhost:{port}/api/health")
    print(f"📍 Logs: ./logs/citizenshield.log")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=port, debug=True)