from datetime import datetime
import bcrypt

class User:
    @staticmethod
    def create(name, email, phone, password):
        """Create a new user"""
        from core.database import db
        
        # Hash password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        query = """
            INSERT INTO users (name, email, phone, password_hash, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """
        return db.execute_query(query, (name, email, phone, password_hash))
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        from core.database import db
        result = db.execute_query("SELECT * FROM users WHERE email = %s", (email,))
        return result[0] if result else None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        from core.database import db
        result = db.execute_query("SELECT * FROM users WHERE id = %s", (user_id,))
        return result[0] if result else None
    
    @staticmethod
    def verify_password(stored_hash, provided_password):
        """Verify password"""
        return bcrypt.checkpw(
            provided_password.encode('utf-8'), 
            stored_hash.encode('utf-8')
        )