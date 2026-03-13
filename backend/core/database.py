import pymysql
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'secureshe_db')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.ssl_ca = os.getenv('SSL_CA_PATH', None)
    
    def get_connection(self):
        """Get database connection with SSL support for TiDB Cloud"""
        try:
            # Create SSL context if connecting to TiDB Cloud
            ssl_context = None
            if self.ssl_ca:
                ssl_context = ssl.create_default_context(cafile=self.ssl_ca)
            
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                cursorclass=pymysql.cursors.DictCursor,
                ssl=ssl_context
            )
            return conn
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return None
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    conn.commit()
                    result = {
                        'affected_rows': cursor.rowcount, 
                        'last_id': cursor.lastrowid
                    }
                return result
        except Exception as e:
            print(f"❌ Query error: {e}")
            return None
        finally:
            conn.close()

# Global database instance
db = Database()

def init_db():
    """Test database connection"""
    conn = db.get_connection()
    if conn:
        conn.close()
        print("✅ Database connected successfully!")
        return True
    else:
        print("❌ Database connection failed!")
        return False
