import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'citizenshield_db')
        self.port = int(os.getenv('DB_PORT', 3306))
    
    def get_connection(self):
        """Get MySQL database connection"""
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
                charset='utf8mb4'
            )
            return conn
        except pymysql.err.OperationalError as e:
            print(f"❌ MySQL connection error: {e}")
            print("   Please check:")
            print("   1. MySQL server is running")
            print("   2. Host and port are correct (default: localhost:3306)")
            print("   3. Username and password are correct")
            print("   4. Database exists")
            return None
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
        except pymysql.err.IntegrityError as e:
            print(f"❌ Integrity error: {e}")
            conn.rollback()
            return None
        except Exception as e:
            print(f"❌ Query error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def execute_many(self, query, params_list):
        """Execute a query with multiple parameter sets"""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                cursor.executemany(query, params_list)
                conn.commit()
                return {
                    'affected_rows': cursor.rowcount,
                    'last_id': cursor.lastrowid
                }
        except Exception as e:
            print(f"❌ Batch query error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def test_connection(self):
        """Test database connection"""
        conn = self.get_connection()
        if conn:
            conn.close()
            return True
        return False
    
    def create_database(self):
        """Create database if it doesn't exist"""
        try:
            # Connect without database
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                cursorclass=pymysql.cursors.DictCursor
            )
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Database creation error: {e}")
            return False

# Global database instance
db = Database()

def init_db():
    """Initialize database connection"""
    # First try to create database if it doesn't exist
    db.create_database()
    
    # Then test connection
    conn = db.get_connection()
    if conn:
        print("✅ MySQL Database connected successfully!")
        print(f"   Host: {db.host}:{db.port}")
        print(f"   Database: {db.database}")
        conn.close()
        return True
    else:
        print("❌ MySQL Database connection failed!")
        print("   Please check your MySQL configuration in .env file")
        return False

def get_db():
    """Get database instance"""
    return db