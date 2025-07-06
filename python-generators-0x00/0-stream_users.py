#!/usr/bin/python3
import mysql.connector

def stream_users():
    """Generator that streams rows from user_data table one by one"""
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ALX_prodev"
        )
        
        # Create a server-side cursor (important for large result sets)
        cursor = connection.cursor(dictionary=True)
        
        # Execute the query
        cursor.execute("SELECT * FROM user_data")
        
        # Stream rows one by one using yield
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row
            
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        # Clean up resources
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
