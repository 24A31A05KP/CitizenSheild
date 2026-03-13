from core.database import db
from utils.validators import validate_phone

class EmergencyContact:
    @staticmethod
    def create(user_id, name, phone, email=None, relationship=None):
        """Create a new emergency contact"""
        if not validate_phone(phone):
            return None
        
        # Check if this is the first contact - make it primary
        contacts = db.execute_query(
            "SELECT COUNT(*) as count FROM emergency_contacts WHERE user_id = %s",
            (user_id,)
        )
        is_primary = contacts[0]['count'] == 0
        
        query = """
            INSERT INTO emergency_contacts (user_id, name, phone, email, relationship, is_primary)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return db.execute_query(query, (user_id, name, phone, email, relationship, is_primary))
    
    @staticmethod
    def find_by_user(user_id):
        """Find all contacts for a user"""
        query = """
            SELECT id, name, phone, email, relationship, is_primary, created_at
            FROM emergency_contacts
            WHERE user_id = %s
            ORDER BY is_primary DESC, created_at ASC
        """
        return db.execute_query(query, (user_id,))
    
    @staticmethod
    def delete(contact_id, user_id):
        """Delete a contact"""
        # Check if contact exists and belongs to user
        contact = db.execute_query(
            "SELECT id, is_primary FROM emergency_contacts WHERE id = %s AND user_id = %s",
            (contact_id, user_id)
        )
        
        if not contact:
            return None
        
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
        
        return result
    
    @staticmethod
    def set_primary(contact_id, user_id):
        """Set a contact as primary"""
        # Remove primary from all contacts
        db.execute_query(
            "UPDATE emergency_contacts SET is_primary = FALSE WHERE user_id = %s",
            (user_id,)
        )
        
        # Set new primary
        return db.execute_query(
            "UPDATE emergency_contacts SET is_primary = TRUE WHERE id = %s AND user_id = %s",
            (contact_id, user_id)
        )