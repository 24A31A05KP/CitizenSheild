#!/usr/bin/env python3
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

def create_database():
    """Create MySQL database if it doesn't exist"""
    connection = None
    try:
        # Connect without database
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        
        cursor = connection.cursor()
        
        # Create database
        db_name = os.getenv('MYSQL_DB', 'secureshe_db')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        print(f"✅ Database '{db_name}' created successfully!")
        
        # Switch to database and create tables
        cursor.execute(f"USE {db_name}")
        
        # Read and execute schema.sql
        with open('database/schema.sql', 'r') as schema_file:
            schema_sql = schema_file.read()
            
            # Split by delimiter and execute each statement
            statements = schema_sql.split(';')
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
        
        print("✅ Tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    create_database()