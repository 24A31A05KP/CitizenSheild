import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', '')
        self.database = os.getenv('MYSQL_DB', 'secureshe_db')
        self.port = int(os.getenv('MYSQL_PORT', 3306))
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                cursorclass=pymysql.cursors.DictCursor
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
    if db.get_connection():
        print("✅ Database connected successfully!")
        return True
    else:
        print("❌ Database connection failed!")
        return False