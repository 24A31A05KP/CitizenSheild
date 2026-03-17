#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import db

def run_migration():
    """Run database migration"""
    print("🚀 Running database migration...")
    
    # Path to schema file in root directory
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'schema_postgres.sql')
    
    try:
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Split and execute each statement
        statements = schema_sql.split(';')
        
        conn = db.get_connection()
        if not conn:
            print("❌ Failed to connect to database")
            return False
        
        with conn.cursor() as cursor:
            for i, statement in enumerate(statements):
                statement = statement.strip()
                if statement:
                    try:
                        cursor.execute(statement)
                        print(f"✅ Executed statement {i+1}")
                    except Exception as e:
                        if "already exists" in str(e):
                            print(f"⚠️  Table already exists: {statement[:50]}...")
                        else:
                            print(f"❌ Error: {e}")
            
            conn.commit()
        
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    run_migration()