import csv
import random
from datetime import datetime, timedelta
from mongo import donors, cities

def seed_donors_data():
    """Seeds the database with cleaned organ donor data from a CSV file.
    Anonymizes names and uses proper city coordinates.
    """
    print("🗑️ Clearing existing donors data...")
    donors.delete_many({})
    print("✅ Existing donors data cleared.")

    # Get all cities from database
    all_cities = list(cities.find({}, {'_id': 0}))
    if not all_cities:
        print("❌ No cities found in database. Please run seed_cities_data.py first.")
        return

    # Create realistic donor data
    donor_data = []
    first_names = ["John", "Emma", "Michael", "Sophia", "William", "Olivia", "James", "Ava", "Robert", "Isabella"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    
    # Generate 100 donors distributed across cities
    for _ in range(100):
        # Randomly select a city
        city = random.choice(all_cities)
        
        # Generate random name
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"
        initials = f"{first_name[0]}{last_name[0]}"
        
        # Generate random age between 18 and 70
        age = random.randint(18, 70)
        
        # Generate random timestamp within last year
        days_ago = random.randint(0, 365)
        timestamp = datetime.now() - timedelta(days=days_ago)
        
        # Generate random donor preferences
        willing_to_donate = random.random() < 0.8  # 80% willing to donate
        registered_donor = random.random() < 0.6   # 60% registered
        
        donor_entry = {
            "anonymized_name": initials,
            "age": age,
            "gender": random.choice(["Male", "Female"]),
            "city": city["name"],
            "country": city["country"],
            "continent": city["continent"],
            "location": city["location"],
            "blood_type": random.choice(blood_types),
            "willing_to_donate": willing_to_donate,
            "registered_donor": registered_donor,
            "timestamp": timestamp
        }
        donor_data.append(donor_entry)

    if donor_data:
        donors.insert_many(donor_data)
        print(f"✅ Successfully inserted {len(donor_data)} donor records into MongoDB.")
    else:
        print("ℹ️ No donor data to insert.")

if __name__ == "__main__":
    # Ensure flight data (cities) is seeded first if not already done
    from seed_flight_data import seed_flight_data 
    seed_flight_data() # This will ensure cities collection is populated

    seed_donors_data() 