from flask_cors import CORS, cross_origin
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
from core.database import db, init_db
from models.user import User
from models.emergency_contact import EmergencyContact
from utils.validators import validate_email, validate_phone, validate_password
import json

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # 🔥 COMPLETE CORS CONFIGURATION 🔥
    CORS(app, 
         resources={r"/api/*": {
             "origins": [
                 "http://localhost:5500",
                 "http://127.0.0.1:5500",
                 "https://24a31a05kp.github.io",
                 "https://*.github.io"
             ],
             "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
             "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 86400,
             "send_wildcard": False,
             "always_send": True
         }})
    
    # Setup logging
    setup_logging(app)
    
    # Test database connection
    if not init_db():
        app.logger.error("Failed to connect to database")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register routes
    register_routes(app)
    
    # 🔥 ADD THIS AFTER ALL ROUTES ARE REGISTERED 🔥
    @app.after_request
    def add_cors_headers(response):
        """Add CORS headers to all responses"""
        origin = request.headers.get('Origin')
        if origin and (origin == 'https://24a31a05kp.github.io' or 
                      origin.endswith('github.io') or 
                      origin.endswith('localhost:5500')):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    return app

def setup_logging(app):
    """Setup logging configuration"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/secureshe.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('SecureShe startup')

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
            'name': 'SecureShe API',
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
                'location_share': '/api/location/share',
                'location_stop': '/api/location/stop-sharing'
            }
        })
    
    @app.route('/api/health', methods=['GET'])
    def health():
        conn = db.get_connection()
        db_status = 'connected' if conn else 'disconnected'
        if conn: conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        })
    
    # ============ AUTH ROUTES ============
    
    @app.route('/api/auth/register', methods=['OPTIONS', 'POST'])
    def register():
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
            
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
                        'phone': data['phone']
                    }
                }), 201
            
            return jsonify({'error': 'Failed to create user'}), 500
            
        except Exception as e:
            app.logger.error(f"Registration error: {str(e)}")
            return jsonify({'error': 'Registration failed'}), 500
    
    @app.route('/api/auth/login', methods=['OPTIONS', 'POST'])
    def login():
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
            
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
    
    @app.route('/api/profile', methods=['GET', 'OPTIONS'])
    @jwt_required()
    def profile():
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
            
        """Get user profile"""
        try:
            user_id = get_jwt_identity()
            print(f"Fetching profile for user ID: {user_id}")
            
            # Get user details
            users = db.execute_query(
                "SELECT id, name, email, phone, role, created_at FROM users WHERE id = %s",
                (user_id,)
            )
            
            if not users:
                return jsonify({'error': 'User not found'}), 404
            
            user = users[0]
            print(f"User found: {user}")
            
            # Get emergency contacts - with error handling
            try:
                contacts = db.execute_query(
                    """SELECT id, name, phone, email, relationship, is_primary 
                       FROM emergency_contacts 
                       WHERE user_id = %s 
                       ORDER BY is_primary DESC, created_at ASC""",
                    (user_id,)
                )
                print(f"Contacts found: {contacts}")
            except Exception as e:
                print(f"Error fetching contacts: {e}")
                contacts = []
            
            # Get SOS count
            try:
                sos_count = db.execute_query(
                    "SELECT COUNT(*) as count FROM sos_alerts WHERE user_id = %s",
                    (user_id,)
                )
                sos_count_value = sos_count[0]['count'] if sos_count else 0
            except Exception as e:
                print(f"Error fetching SOS count: {e}")
                sos_count_value = 0
            
            user['emergency_contacts'] = contacts if contacts else []
            user['sos_count'] = sos_count_value
            
            print(f"Returning profile data: {user}")
            
            return jsonify(user), 200
            
        except Exception as e:
            print(f"Profile error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/profile/update', methods=['PUT', 'OPTIONS'])
    @jwt_required()
    def update_user_profile():
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'PUT, OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
            
        """Update user profile (single version)"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            print(f"Updating profile for user {user_id} with data: {data}")
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Build update query dynamically
            updates = []
            params = []
            
            if 'name' in data and data['name']:
                updates.append("name = %s")
                params.append(data['name'])
            
            if 'phone' in data and data['phone']:
                # Check if phone already exists for another user
                existing_phone = db.execute_query(
                    "SELECT id FROM users WHERE phone = %s AND id != %s",
                    (data['phone'], user_id)
                )
                if existing_phone:
                    return jsonify({'error': 'Phone number already in use'}), 400
                
                # Basic phone validation
                if not data['phone'].replace('+', '').replace('-', '').replace(' ', '').isdigit():
                    return jsonify({'error': 'Invalid phone number format'}), 400
                updates.append("phone = %s")
                params.append(data['phone'])
            
            if 'email' in data and data['email']:
                # Check if email already exists for another user
                existing_email = db.execute_query(
                    "SELECT id FROM users WHERE email = %s AND id != %s",
                    (data['email'], user_id)
                )
                if existing_email:
                    return jsonify({'error': 'Email already in use'}), 400
                
                # Basic email validation
                if '@' not in data['email']:
                    return jsonify({'error': 'Invalid email format'}), 400
                updates.append("email = %s")
                params.append(data['email'])
            
            if not updates:
                return jsonify({'error': 'No fields to update'}), 400
            
            # Add user_id to params
            params.append(user_id)
            
            # Execute update
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            result = db.execute_query(query, tuple(params))
            
            print(f"Update result: {result}")
            
            if result and result.get('affected_rows', 0) > 0:
                # Fetch updated user data
                updated_user = db.execute_query(
                    "SELECT id, name, email, phone FROM users WHERE id = %s",
                    (user_id,)
                )
                
                return jsonify({
                    'message': 'Profile updated successfully',
                    'user': updated_user[0] if updated_user else None
                }), 200
            else:
                return jsonify({'error': 'No changes made or user not found'}), 400
                
        except Exception as e:
            print(f"Profile update error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    # ============ EMERGENCY CONTACTS ROUTES ============
    
    @app.route('/api/profile/contacts', methods=['POST', 'OPTIONS'])
    @jwt_required()
    def add_emergency_contact():
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
            
        """Add emergency contact"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            print(f"Adding contact for user {user_id}: {data}")
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            required = ['name', 'phone']
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Missing field: {field}'}), 400
            
            # Check if this is the first contact - make it primary
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
            
            print(f"Insert result: {result}")
            
            if result and result.get('last_id'):
                return jsonify({
                    'message': 'Emergency contact added',
                    'contact_id': result['last_id'],
                    'is_primary': is_primary
                }), 201
            else:
                return jsonify({'error': 'Failed to add contact'}), 500
                
        except Exception as e:
            print(f"Add contact error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/profile/contacts/<int:contact_id>', methods=['DELETE', 'OPTIONS'])
    @jwt_required()
    def delete_emergency_contact(contact_id):
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
            
        """Delete emergency contact"""
        try:
            user_id = get_jwt_identity()
            
            # Check if contact exists and belongs to user
            contact = db.execute_query(
                "SELECT id, is_primary FROM emergency_contacts WHERE id = %s AND user_id = %s",
                (contact_id, user_id)
            )
            
            if not contact:
                return jsonify({'error': 'Contact not found'}), 404
            
            # Delete contact
            result = db.execute_query(
                "DELETE FROM emergency_contacts WHERE id = %s AND user_id = %s",
                (contact_id, user_id)
            )
            
            # If we deleted a primary contact, make another contact primary
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
    
    @app.route('/api/profile/contacts/<int:contact_id>/primary', methods=['PUT', 'OPTIONS'])
    @jwt_required()
    def set_primary_contact(contact_id):
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'PUT, OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
            
        """Set a contact as primary"""
        try:
            user_id = get_jwt_identity()
            
            # Remove primary from all contacts
            db.execute_query(
                "UPDATE emergency_contacts SET is_primary = FALSE WHERE user_id = %s",
                (user_id,)
            )
            
            # Set new primary
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
    
    @app.route('/api/helplines', methods=['GET', 'OPTIONS'])
    def get_helplines():
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
            
        """Get all helplines"""
        try:
            country = request.args.get('country')
            
            if country:
                result = db.execute_query(
                    "SELECT * FROM helplines WHERE country = %s AND is_active = TRUE ORDER BY service_name",
                    (country,)
                )
            else:
                result = db.execute_query(
                    "SELECT * FROM helplines WHERE is_active = TRUE ORDER BY country, service_name"
                )
            
            return jsonify(result or [])
            
        except Exception as e:
            app.logger.error(f"Helplines error: {str(e)}")
            return jsonify([])  # Return empty array on error
    
    # ============ SOS ROUTES ============
    
    @app.route('/api/sos/trigger', methods=['POST', 'OPTIONS'])
    @jwt_required()
    def trigger_sos():
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
            
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
            
            # Log SOS event
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
    
    @app.route('/api/sos/history', methods=['GET', 'OPTIONS'])
    @jwt_required()
    def get_sos_history():
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
            
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
    
    # ============ LOCATION SHARING ROUTES ============
    
    @app.route('/api/location/share', methods=['POST', 'OPTIONS'])
    @jwt_required()
    def share_location():
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
            
        """Share live location"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            # First, deactivate any previous active shares
            db.execute_query("""
                UPDATE location_shares 
                SET is_active = FALSE, ended_at = NOW() 
                WHERE user_id = %s AND is_active = TRUE
            """, (user_id,))
            
            # Store new location in database
            result = db.execute_query("""
                INSERT INTO location_shares (user_id, latitude, longitude, accuracy, mode, recipients, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE)
            """, (
                user_id, 
                data.get('latitude'), 
                data.get('longitude'), 
                data.get('accuracy', 0),
                data.get('mode', 'live'),
                json.dumps(data.get('recipients', 'all'))
            ))
            
            return jsonify({
                'message': 'Location shared successfully',
                'share_id': result.get('last_id') if result else None
            }), 200
        
        except Exception as e:
            app.logger.error(f"Location share error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/location/stop-sharing', methods=['POST', 'OPTIONS'])
    @jwt_required()
    def stop_sharing():
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
            
        """Stop sharing location"""
        try:
            user_id = get_jwt_identity()
            
            db.execute_query("""
                UPDATE location_shares 
                SET is_active = FALSE, ended_at = NOW() 
                WHERE user_id = %s AND is_active = TRUE
            """, (user_id,))
            
            return jsonify({'message': 'Location sharing stopped'}), 200
        
        except Exception as e:
            app.logger.error(f"Stop sharing error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/location/contacts/<int:contact_id>', methods=['GET', 'OPTIONS'])
    @jwt_required()
    def get_contact_location(contact_id):
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            origin = request.headers.get('Origin')
            if origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response, 200
            
        """Get live location of a contact (for trusted contacts)"""
        try:
            user_id = get_jwt_identity()
            
            # Check if contact belongs to user
            contact = db.execute_query(
                "SELECT * FROM emergency_contacts WHERE id = %s AND user_id = %s",
                (contact_id, user_id)
            )
            
            if not contact:
                return jsonify({'error': 'Contact not found'}), 404
            
            # Get contact's live location (if they're sharing)
            location = db.execute_query("""
                SELECT ls.*, u.name 
                FROM location_shares ls
                JOIN users u ON ls.user_id = u.id
                WHERE ls.user_id = %s AND ls.is_active = TRUE
                ORDER BY ls.created_at DESC
                LIMIT 1
            """, (contact_id,))
            
            return jsonify(location[0] if location else None), 200
        
        except Exception as e:
            app.logger.error(f"Get contact location error: {str(e)}")
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    print("\n" + "="*60)
    print("🚀 SecureShe API Server v2.0")
    print("="*60)
    print(f"📍 Server: http://localhost:{port}")
    print(f"📍 Health: http://localhost:{port}/api/health")
    print(f"📍 Logs: ./logs/secureshe.log")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=port, debug=True)