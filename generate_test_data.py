#!/usr/bin/env python3
import uuid
import random
from datetime import datetime, timedelta

# Configuration
USER_IDS = [1]
MIN_LATITUDE = 55.0
MAX_LATITUDE = 57.0
MIN_LONGITUDE = 36.0
MAX_LONGITUDE = 38.0
RATING_RANGE = (1, 10)
POSSIBLE_COMMENTS = [
    "Feeling happy today!",
    "Stressed out",
    "Amazing day",
    "Not my best day",
    "Excited about the progress",
    "Bit worried",
    "So relaxed",
    "Tired but satisfied",
    "New experiences",
    "Just another day",
    None,  # For NULL comments
]

# Generate data for the past year
end_date = datetime.utcnow()
start_date = end_date - timedelta(days=365)

print("-- Generated SQL insert statements for emotions table")
print("-- Run this script in your PostgreSQL database")
print()

# Generate an insert statement for each day
for day in range(365):
    # Create date for this entry (distribute across the whole year)
    current_date = start_date + timedelta(days=day)
    
    # Generate random values
    unique_id = str(uuid.uuid4())
    latitude = random.uniform(MIN_LATITUDE, MAX_LATITUDE)
    longitude = random.uniform(MIN_LONGITUDE, MAX_LONGITUDE)
    rating = random.randint(*RATING_RANGE)
    comment = random.choice(POSSIBLE_COMMENTS)
    user_id = random.choice(USER_IDS)
    
    # Seasonal variations in emotions - higher ratings in summer, lower in winter
    month = current_date.month
    if 5 <= month <= 8:  # Summer months
        rating = min(10, rating + random.randint(0, 2))  # Slightly higher ratings
    elif month in [1, 2, 12]:  # Winter months
        rating = max(1, rating - random.randint(0, 2))  # Slightly lower ratings
    
    # Format the insert statement
    comment_value = f"'{comment}'" if comment else "NULL"
    formatted_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
    
    insert_statement = (
        f"INSERT INTO emotions (unique_id, latitude, longitude, rating, comment, created_at, user_id) "
        f"VALUES ('{unique_id}', {latitude:.6f}, {longitude:.6f}, {rating}, {comment_value}, '{formatted_date}', {user_id});"
    )
    
    print(insert_statement)

print("\n-- End of generated SQL statements")

# Add instructions for running the generated SQL
print("""
/*
To use this data:
1. Save the output to a file: python generate_test_data.py > emotions_test_data.sql
2. Run the SQL file in your PostgreSQL database:
   - Using psql: psql -U username -d database_name -f emotions_test_data.sql
   - Or copy and paste into your database management tool
*/
""") 