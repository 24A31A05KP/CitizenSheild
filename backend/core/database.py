import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'secureshe_db')
        self.port = int(os.getenv('DB_PORT', 5432))
    
    def get_connection(self):
        """Get PostgreSQL database connection"""
        try:
            conn = psycopg2.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                dbname=self.database,
                port=self.port,
                cursor_factory=RealDictCursor,
                sslmode='require'  # Required for Render PostgreSQL
            )
            return conn
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return None
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        conn = None
        try:
            conn = self.get_connection()
            if not conn:
                return None
            
            with conn.cursor() as cursor:
                # Convert MySQL placeholders (%s) to PostgreSQL placeholders
                # PostgreSQL also uses %s, so it might work directly
                cursor.execute(query, params or ())
                
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    conn.commit()
                    result = {
                        'affected_rows': cursor.rowcount,
                        'last_id': None  # PostgreSQL handles this differently
                    }
                    # Get last inserted ID if it's an INSERT
                    if query.strip().upper().startswith('INSERT'):
                        cursor.execute("SELECT LASTVAL()")
                        last_id = cursor.fetchone()
                        if last_id:
                            result['last_id'] = last_id['lastval']
                
                return result
        except Exception as e:
            print(f"❌ Query error: {e}")
            return None
        finally:
            if conn:
                conn.close()

# Global database instance
db = Database()

def init_db():
    """Test database connection"""
    try:
        conn = db.get_connection()
        if conn:
            conn.close()
            print("✅ PostgreSQL database connected successfully!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False