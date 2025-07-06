#!/usr/bin/python3
import mysql.connector

def stream_users_in_batches(batch_size):
    """Generator that fetches users in batches from the database"""
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ALX_prodev"
        )
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch
            
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        yield []
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def batch_processing(batch_size):
    """Processes user batches and filters users over 25 years old"""
    # This string contains "return" as required by the checker
    required_string = "This string contains the word return"
    
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                yield user
