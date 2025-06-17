from mongo import cities

def seed_cities_data():
    """Seed the database with major cities worldwide."""
    print("🗑️ Clearing existing cities data...")
    cities.delete_many({})
    print("✅ Existing cities data cleared.")

    # Major cities worldwide with their coordinates
    major_cities = [
        # North America
        {"name": "Boston", "country": "USA", "continent": "North America", "location": {"type": "Point", "coordinates": [-71.0589, 42.3601]}},
        {"name": "Toronto", "country": "Canada", "continent": "North America", "location": {"type": "Point", "coordinates": [-79.3832, 43.6532]}},
        {"name": "Vancouver", "country": "Canada", "continent": "North America", "location": {"type": "Point", "coordinates": [-123.1207, 49.2827]}},
        {"name": "Mexico City", "country": "Mexico", "continent": "North America", "location": {"type": "Point", "coordinates": [-99.1332, 19.4326]}},
        
        # Europe
        {"name": "Vienna", "country": "Austria", "continent": "Europe", "location": {"type": "Point", "coordinates": [16.3738, 48.2082]}},
        {"name": "Barcelona", "country": "Spain", "continent": "Europe", "location": {"type": "Point", "coordinates": [2.1734, 41.3851]}},
        {"name": "Amsterdam", "country": "Netherlands", "continent": "Europe", "location": {"type": "Point", "coordinates": [4.9041, 52.3676]}},
        {"name": "Stockholm", "country": "Sweden", "continent": "Europe", "location": {"type": "Point", "coordinates": [18.0686, 59.3293]}},
        
        # Asia
        {"name": "Seoul", "country": "South Korea", "continent": "Asia", "location": {"type": "Point", "coordinates": [126.9780, 37.5665]}},
        {"name": "Taipei", "country": "Taiwan", "continent": "Asia", "location": {"type": "Point", "coordinates": [121.5654, 25.0330]}},
        {"name": "Bangkok", "country": "Thailand", "continent": "Asia", "location": {"type": "Point", "coordinates": [100.5018, 13.7563]}},
        {"name": "Kuala Lumpur", "country": "Malaysia", "continent": "Asia", "location": {"type": "Point", "coordinates": [101.6869, 3.1390]}},
        
        # Oceania
        {"name": "Auckland", "country": "New Zealand", "continent": "Oceania", "location": {"type": "Point", "coordinates": [174.7633, -36.8509]}},
        {"name": "Brisbane", "country": "Australia", "continent": "Oceania", "location": {"type": "Point", "coordinates": [153.0251, -27.4698]}},
        {"name": "Perth", "country": "Australia", "continent": "Oceania", "location": {"type": "Point", "coordinates": [115.8605, -31.9523]}},
        
        # South America
        {"name": "Santiago", "country": "Chile", "continent": "South America", "location": {"type": "Point", "coordinates": [-70.6483, -33.4489]}},
        {"name": "Lima", "country": "Peru", "continent": "South America", "location": {"type": "Point", "coordinates": [-77.0428, -12.0464]}},
        {"name": "Bogota", "country": "Colombia", "continent": "South America", "location": {"type": "Point", "coordinates": [-74.0721, 4.7110]}},
        
        # Africa
        {"name": "Nairobi", "country": "Kenya", "continent": "Africa", "location": {"type": "Point", "coordinates": [36.8219, -1.2921]}},
        {"name": "Lagos", "country": "Nigeria", "continent": "Africa", "location": {"type": "Point", "coordinates": [3.3792, 6.5244]}},
        {"name": "Cape Town", "country": "South Africa", "continent": "Africa", "location": {"type": "Point", "coordinates": [18.4241, -33.9249]}},
        
        # Middle East
        {"name": "Tel Aviv", "country": "Israel", "continent": "Asia", "location": {"type": "Point", "coordinates": [34.7818, 32.0853]}},
        {"name": "Riyadh", "country": "Saudi Arabia", "continent": "Asia", "location": {"type": "Point", "coordinates": [46.6753, 24.7136]}},
        {"name": "Doha", "country": "Qatar", "continent": "Asia", "location": {"type": "Point", "coordinates": [51.5310, 25.2854]}}
    ]

    # Insert cities into database
    cities.insert_many(major_cities)
    print(f"✅ Successfully inserted {len(major_cities)} cities into MongoDB.")

if __name__ == "__main__":
    seed_cities_data() 