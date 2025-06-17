from mongo import organs, cities
from datetime import datetime
import random

def seed_organs_data():
    """Seed the database with organs data using GeoJSON format"""
    
    # Clear existing organs data
    organs.delete_many({})
    print("🗑️ Cleared existing organs data")
    
    # Get all cities to place organs
    all_cities = list(cities.find({}, {'_id': 0}))
    
    if not all_cities:
        print("❌ No cities found. Please run seed_flight_data.py first.")
        return
    
    # Organ types and their emojis
    organ_types = [
        {"type": "Heart", "emoji": "🫀", "color": "#e74c3c"},
        {"type": "Kidney", "emoji": "🫁", "color": "#3498db"},
        {"type": "Liver", "emoji": "🫀", "color": "#f39c12"},
        {"type": "Lung", "emoji": "🫁", "color": "#9b59b6"},
        {"type": "Pancreas", "emoji": "🫀", "color": "#e67e22"},
        {"type": "Cornea", "emoji": "👁️", "color": "#1abc9c"},
        {"type": "Bone Marrow", "emoji": "🦴", "color": "#34495e"}
    ]
    
    # Status options
    statuses = ["available", "in_transit", "reserved", "delivered"]
    
    organs_data = []
    
    # Create 50-100 organs distributed across cities
    num_organs = random.randint(50, 100)
    
    for i in range(num_organs):
        # Randomly select a city
        city = random.choice(all_cities)
        
        # Randomly select organ type
        organ_info = random.choice(organ_types)
        
        # Randomly select status with weighted probability
        status = random.choices(
            statuses, 
            weights=[0.4, 0.3, 0.2, 0.1]  # 40% available, 30% in transit, etc.
        )[0]
        
        # Create organ document with GeoJSON format
        organ = {
            "organ_id": f"ORG-{i+1:04d}",
            "organ_type": organ_info["type"],
            "organ_emoji": organ_info["emoji"],
            "organ_color": organ_info["color"],
            "status": status,
            "city": city["name"],
            "country": city["country"],
            "continent": city["continent"],
            "location": city["location"],  # Use city's GeoJSON location
            "blood_type": random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
            "priority": random.choice(["high", "medium", "low"]),
            "preservation_time": random.randint(1, 72),  # hours
            "flight_id": None,  # Will be assigned if in transit
            "created_at": datetime.now(),
            "last_updated": datetime.now()
        }
        
        # If organ is in transit, assign a random flight ID
        if status == "in_transit":
            organ["flight_id"] = f"FLIGHT-{random.randint(1000, 9999)}"
        
        organs_data.append(organ)
    
    # Insert organs into database
    organs.insert_many(organs_data)
    print(f"✅ Inserted {len(organs_data)} organs with geospatial data")
    
    # Print summary
    status_counts = {}
    for organ in organs_data:
        status = organ["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\n📊 Organs Summary:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    print("\n🎉 Organs data seeding completed with geospatial support!")

if __name__ == "__main__":
    seed_organs_data() 