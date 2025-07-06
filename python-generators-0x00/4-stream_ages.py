#!/usr/bin/python3
import mysql.connector
import seed

def stream_user_ages():
    """Generator that yields user ages one by one"""
    connection = None
    cursor = None
    try:
        connection = seed.connect_to_prodev()
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row[0]  # Yield just the age value
            
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def calculate_average_age():
    """Calculates average age using memory-efficient generator"""
    total = 0
    count = 0
    
    # First loop: iterate through ages from generator
    for age in stream_user_ages():
        total += age
        count += 1
    
    # Calculate average if we have data
    if count > 0:
        average = total / count
        print(f"Average age of users: {average:.2f}")
    else:
        print("No users found in database")

if __name__ == "__main__":
    calculate_average_age()
