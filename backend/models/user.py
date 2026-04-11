import bcrypt
from core.database import db
from datetime import datetime

class User:
    """User model for database operations"""
    
    @staticmethod
    def create(name, email, phone, password):
        """Create a new user"""
        # Hash password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        query = """
            INSERT INTO users (name, email, phone, password_hash, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """
        return db.execute_query(query, (name, email.lower(), phone, password_hash))
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        result = db.execute_query(
            "SELECT * FROM users WHERE email = %s",
            (email.lower(),)
        )
        return result[0] if result else None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        result = db.execute_query(
            "SELECT id, name, email, phone, role, is_verified, created_at, last_login FROM users WHERE id = %s",
            (user_id,)
        )
        return result[0] if result else None
    
    @staticmethod
    def find_by_phone(phone):
        """Find user by phone number"""
        result = db.execute_query(
            "SELECT * FROM users WHERE phone = %s",
            (phone,)
        )
        return result[0] if result else None
    
    @staticmethod
    def verify_password(stored_hash, provided_password):
        """Verify password against stored hash"""
        return bcrypt.checkpw(
            provided_password.encode('utf-8'), 
            stored_hash.encode('utf-8')
        )
    
    @staticmethod
    def update_last_login(user_id):
        """Update user's last login timestamp"""
        return db.execute_query(
            "UPDATE users SET last_login = NOW() WHERE id = %s",
            (user_id,)
        )
    
    @staticmethod
    def update_profile(user_id, name=None, email=None, phone=None):
        """Update user profile"""
        updates = []
        params = []
        
        if name:
            updates.append("name = %s")
            params.append(name)
        if email:
            updates.append("email = %s")
            params.append(email.lower())
        if phone:
            updates.append("phone = %s")
            params.append(phone)
        
        if not updates:
            return None
        
        updates.append("updated_at = NOW()")
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        return db.execute_query(query, tuple(params))
    
    @staticmethod
    def change_password(user_id, new_password):
        """Change user password"""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
        
        return db.execute_query(
            "UPDATE users SET password_hash = %s, updated_at = NOW() WHERE id = %s",
            (password_hash, user_id)
        )
    
    @staticmethod
    def verify_user(user_id):
        """Mark user as verified"""
        return db.execute_query(
            "UPDATE users SET is_verified = TRUE, updated_at = NOW() WHERE id = %s",
            (user_id,)
        )
    
    @staticmethod
    def get_all_users(limit=100, offset=0):
        """Get all users with pagination"""
        return db.execute_query("""
            SELECT id, name, email, phone, role, is_verified, created_at, last_login 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """, (limit, offset))
    
    @staticmethod
    def count_users():
        """Get total number of users"""
        result = db.execute_query("SELECT COUNT(*) as count FROM users")
        return result[0]['count'] if result else 0
    
    @staticmethod
    def count_admins():
        """Get total number of admin users"""
        result = db.execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
        return result[0]['count'] if result else 0
    
    @staticmethod
    def delete_user(user_id):
        """Delete user by ID"""
        return db.execute_query("DELETE FROM users WHERE id = %s", (user_id,))
    
    @staticmethod
    def set_role(user_id, role):
        """Set user role (user/admin)"""
        if role not in ['user', 'admin']:
            return None
        return db.execute_query(
            "UPDATE users SET role = %s, updated_at = NOW() WHERE id = %s",
            (role, user_id)
        )
    
    @staticmethod
    def search_users(search_term):
        """Search users by name, email, or phone"""
        search_pattern = f"%{search_term}%"
        return db.execute_query("""
            SELECT id, name, email, phone, role, created_at 
            FROM users 
            WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s
            ORDER BY name ASC
            LIMIT 50
        """, (search_pattern, search_pattern, search_pattern))
    
    @staticmethod
    def get_recent_users(days=30):
        """Get users registered in last N days"""
        return db.execute_query("""
            SELECT id, name, email, created_at 
            FROM users 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            ORDER BY created_at DESC
        """, (days,))
    
    @staticmethod
    def get_user_stats():
        """Get user statistics"""
        stats = {}
        
        # Total users
        stats['total'] = User.count_users()
        
        # Users by role
        role_result = db.execute_query("""
            SELECT role, COUNT(*) as count 
            FROM users 
            GROUP BY role
        """)
        stats['by_role'] = {r['role']: r['count'] for r in role_result} if role_result else {}
        
        # Users by month (last 12 months)
        monthly_result = db.execute_query("""
            SELECT DATE_FORMAT(created_at, '%Y-%m') as month, COUNT(*) as count 
            FROM users 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(created_at, '%Y-%m')
            ORDER BY month ASC
        """)
        stats['monthly'] = monthly_result if monthly_result else []
        
        # Active users (last 30 days)
        active_result = db.execute_query("""
            SELECT COUNT(*) as count 
            FROM users 
            WHERE last_login >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """)
        stats['active_30days'] = active_result[0]['count'] if active_result else 0
        
        return stats