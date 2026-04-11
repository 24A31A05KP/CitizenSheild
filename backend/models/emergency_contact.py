from core.database import db
from utils.validators import validate_phone

class EmergencyContact:
    """Emergency Contact model for database operations"""
    
    @staticmethod
    def create(user_id, name, phone, email=None, relationship=None):
        """Create a new emergency contact"""
        # Validate phone number
        if not validate_phone(phone):
            return None
        
        # Check if this is the first contact - make it primary
        contacts = db.execute_query(
            "SELECT COUNT(*) as count FROM emergency_contacts WHERE user_id = %s",
            (user_id,)
        )
        is_primary = contacts[0]['count'] == 0 if contacts else True
        
        query = """
            INSERT INTO emergency_contacts (user_id, name, phone, email, relationship, is_primary, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        return db.execute_query(query, (user_id, name, phone, email, relationship, is_primary))
    
    @staticmethod
    def find_by_id(contact_id, user_id=None):
        """Find emergency contact by ID, optionally verify ownership"""
        if user_id:
            query = """
                SELECT id, user_id, name, phone, email, relationship, is_primary, created_at
                FROM emergency_contacts
                WHERE id = %s AND user_id = %s
            """
            result = db.execute_query(query, (contact_id, user_id))
        else:
            query = """
                SELECT id, user_id, name, phone, email, relationship, is_primary, created_at
                FROM emergency_contacts
                WHERE id = %s
            """
            result = db.execute_query(query, (contact_id,))
        
        return result[0] if result else None
    
    @staticmethod
    def find_by_user(user_id, include_primary_first=True):
        """Find all contacts for a user"""
        if include_primary_first:
            query = """
                SELECT id, name, phone, email, relationship, is_primary, created_at
                FROM emergency_contacts
                WHERE user_id = %s
                ORDER BY is_primary DESC, created_at ASC
            """
        else:
            query = """
                SELECT id, name, phone, email, relationship, is_primary, created_at
                FROM emergency_contacts
                WHERE user_id = %s
                ORDER BY created_at ASC
            """
        return db.execute_query(query, (user_id,))
    
    @staticmethod
    def get_primary_contact(user_id):
        """Get the primary emergency contact for a user"""
        result = db.execute_query("""
            SELECT id, name, phone, email, relationship, created_at
            FROM emergency_contacts
            WHERE user_id = %s AND is_primary = TRUE
            LIMIT 1
        """, (user_id,))
        return result[0] if result else None
    
    @staticmethod
    def update(contact_id, user_id, name=None, phone=None, email=None, relationship=None):
        """Update an emergency contact"""
        updates = []
        params = []
        
        if name:
            updates.append("name = %s")
            params.append(name)
        if phone:
            if not validate_phone(phone):
                return None
            updates.append("phone = %s")
            params.append(phone)
        if email is not None:
            updates.append("email = %s")
            params.append(email)
        if relationship is not None:
            updates.append("relationship = %s")
            params.append(relationship)
        
        if not updates:
            return None
        
        updates.append("updated_at = NOW()")
        params.append(contact_id)
        params.append(user_id)
        
        query = f"UPDATE emergency_contacts SET {', '.join(updates)} WHERE id = %s AND user_id = %s"
        return db.execute_query(query, tuple(params))
    
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
            # Check if there are other contacts
            remaining = db.execute_query(
                "SELECT id FROM emergency_contacts WHERE user_id = %s LIMIT 1",
                (user_id,)
            )
            if remaining:
                EmergencyContact.set_primary(remaining[0]['id'], user_id)
        
        return result
    
    @staticmethod
    def set_primary(contact_id, user_id):
        """Set a contact as primary"""
        # First verify contact belongs to user
        contact = db.execute_query(
            "SELECT id FROM emergency_contacts WHERE id = %s AND user_id = %s",
            (contact_id, user_id)
        )
        if not contact:
            return None
        
        # Remove primary from all contacts
        db.execute_query(
            "UPDATE emergency_contacts SET is_primary = FALSE WHERE user_id = %s",
            (user_id,)
        )
        
        # Set new primary
        return db.execute_query(
            "UPDATE emergency_contacts SET is_primary = TRUE, updated_at = NOW() WHERE id = %s AND user_id = %s",
            (contact_id, user_id)
        )
    
    @staticmethod
    def count_by_user(user_id):
        """Count emergency contacts for a user"""
        result = db.execute_query(
            "SELECT COUNT(*) as count FROM emergency_contacts WHERE user_id = %s",
            (user_id,)
        )
        return result[0]['count'] if result else 0
    
    @staticmethod
    def delete_all_by_user(user_id):
        """Delete all emergency contacts for a user"""
        return db.execute_query(
            "DELETE FROM emergency_contacts WHERE user_id = %s",
            (user_id,)
        )
    
    @staticmethod
    def get_contacts_with_phone_numbers(user_id):
        """Get all contacts with phone numbers only (for SOS alerts)"""
        return db.execute_query("""
            SELECT id, name, phone
            FROM emergency_contacts
            WHERE user_id = %s AND phone IS NOT NULL AND phone != ''
            ORDER BY is_primary DESC, name ASC
        """, (user_id,))
    
    @staticmethod
    def search_contacts(user_id, search_term):
        """Search contacts by name, phone, or email"""
        search_pattern = f"%{search_term}%"
        return db.execute_query("""
            SELECT id, name, phone, email, relationship, is_primary
            FROM emergency_contacts
            WHERE user_id = %s AND (name LIKE %s OR phone LIKE %s OR email LIKE %s)
            ORDER BY is_primary DESC, name ASC
            LIMIT 20
        """, (user_id, search_pattern, search_pattern, search_pattern))
    
    @staticmethod
    def get_user_contacts_summary(user_id):
        """Get summary of user's emergency contacts"""
        contacts = EmergencyContact.find_by_user(user_id)
        
        if not contacts:
            return {
                'count': 0,
                'has_primary': False,
                'primary_name': None,
                'primary_phone': None
            }
        
        primary = next((c for c in contacts if c.get('is_primary')), None)
        
        return {
            'count': len(contacts),
            'has_primary': primary is not None,
            'primary_name': primary['name'] if primary else None,
            'primary_phone': primary['phone'] if primary else None
        }