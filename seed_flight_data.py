from mongo import airlines, cities, flight_routes, flight_paths, organs
from datetime import datetime, timedelta

def seed_flight_data():
    """Seed the database with airlines, cities, and flight routes using GeoJSON format"""
    
    # Clear existing data
    airlines.delete_many({})
    cities.delete_many({})
    flight_routes.delete_many({})
    flight_paths.delete_many({})
    
    # Insert airlines
    airline_data = [
        {"name": "Delta Airlines", "color": "#dc3545", "icon": "✈️", "code": "DL"},
        {"name": "United Airlines", "color": "#17a2b8", "icon": "✈️", "code": "UA"},
        {"name": "American Airlines", "color": "#28a745", "icon": "✈️", "code": "AA"},
        {"name": "Southwest Airlines", "color": "#ffc107", "icon": "✈️", "code": "WN"},
        {"name": "JetBlue Airways", "color": "#6f42c1", "icon": "✈️", "code": "B6"},
        {"name": "British Airways", "color": "#007cba", "icon": "✈️", "code": "BA"},
        {"name": "Lufthansa", "color": "#05164d", "icon": "✈️", "code": "LH"},
        {"name": "Emirates", "color": "#d71920", "icon": "✈️", "code": "EK"},
        {"name": "Singapore Airlines", "color": "#004b87", "icon": "✈️", "code": "SQ"},
        {"name": "Japan Airlines", "color": "#e60012", "icon": "✈️", "code": "JL"}
    ]
    
    airlines.insert_many(airline_data)
    print(f"✅ Inserted {len(airline_data)} airlines")
    
    # Insert cities with GeoJSON format
    city_data = [
        # North America
        {
            "name": "New York", 
            "location": {"type": "Point", "coordinates": [-74.0060, 40.7128]}, 
            "country": "USA", 
            "continent": "North America"
        },
        {
            "name": "Los Angeles", 
            "location": {"type": "Point", "coordinates": [-118.2437, 34.0522]}, 
            "country": "USA", 
            "continent": "North America"
        },
        {
            "name": "Chicago", 
            "location": {"type": "Point", "coordinates": [-87.6298, 41.8781]}, 
            "country": "USA", 
            "continent": "North America"
        },
        {
            "name": "Toronto", 
            "location": {"type": "Point", "coordinates": [-79.3832, 43.6532]}, 
            "country": "Canada", 
            "continent": "North America"
        },
        {
            "name": "Vancouver", 
            "location": {"type": "Point", "coordinates": [-123.1207, 49.2827]}, 
            "country": "Canada", 
            "continent": "North America"
        },
        {
            "name": "Mexico City", 
            "location": {"type": "Point", "coordinates": [-99.1332, 19.4326]}, 
            "country": "Mexico", 
            "continent": "North America"
        },
        
        # Europe
        {
            "name": "London", 
            "location": {"type": "Point", "coordinates": [-0.1278, 51.5074]}, 
            "country": "UK", 
            "continent": "Europe"
        },
        {
            "name": "Paris", 
            "location": {"type": "Point", "coordinates": [2.3522, 48.8566]}, 
            "country": "France", 
            "continent": "Europe"
        },
        {
            "name": "Berlin", 
            "location": {"type": "Point", "coordinates": [13.4050, 52.5200]}, 
            "country": "Germany", 
            "continent": "Europe"
        },
        {
            "name": "Rome", 
            "location": {"type": "Point", "coordinates": [12.4964, 41.9028]}, 
            "country": "Italy", 
            "continent": "Europe"
        },
        {
            "name": "Madrid", 
            "location": {"type": "Point", "coordinates": [-3.7038, 40.4168]}, 
            "country": "Spain", 
            "continent": "Europe"
        },
        {
            "name": "Amsterdam", 
            "location": {"type": "Point", "coordinates": [4.9041, 52.3676]}, 
            "country": "Netherlands", 
            "continent": "Europe"
        },
        {
            "name": "Moscow", 
            "location": {"type": "Point", "coordinates": [37.6176, 55.7558]}, 
            "country": "Russia", 
            "continent": "Europe"
        },
        {
            "name": "Istanbul", 
            "location": {"type": "Point", "coordinates": [28.9784, 41.0082]}, 
            "country": "Turkey", 
            "continent": "Europe"
        },
        
        # Asia
        {
            "name": "Tokyo", 
            "location": {"type": "Point", "coordinates": [139.6503, 35.6762]}, 
            "country": "Japan", 
            "continent": "Asia"
        },
        {
            "name": "Beijing", 
            "location": {"type": "Point", "coordinates": [116.4074, 39.9042]}, 
            "country": "China", 
            "continent": "Asia"
        },
        {
            "name": "Shanghai", 
            "location": {"type": "Point", "coordinates": [121.4737, 31.2304]}, 
            "country": "China", 
            "continent": "Asia"
        },
        {
            "name": "Seoul", 
            "location": {"type": "Point", "coordinates": [126.9780, 37.5665]}, 
            "country": "South Korea", 
            "continent": "Asia"
        },
        {
            "name": "Singapore", 
            "location": {"type": "Point", "coordinates": [103.8198, 1.3521]}, 
            "country": "Singapore", 
            "continent": "Asia"
        },
        {
            "name": "Bangkok", 
            "location": {"type": "Point", "coordinates": [100.5018, 13.7563]}, 
            "country": "Thailand", 
            "continent": "Asia"
        },
        {
            "name": "Mumbai", 
            "location": {"type": "Point", "coordinates": [72.8777, 19.0760]}, 
            "country": "India", 
            "continent": "Asia"
        },
        {
            "name": "Delhi", 
            "location": {"type": "Point", "coordinates": [77.1025, 28.7041]}, 
            "country": "India", 
            "continent": "Asia"
        },
        {
            "name": "Dubai", 
            "location": {"type": "Point", "coordinates": [55.2708, 25.2048]}, 
            "country": "UAE", 
            "continent": "Asia"
        },
        {
            "name": "Hong Kong", 
            "location": {"type": "Point", "coordinates": [114.1694, 22.3193]}, 
            "country": "China", 
            "continent": "Asia"
        },
        
        # Africa
        {
            "name": "Cairo", 
            "location": {"type": "Point", "coordinates": [31.2357, 30.0444]}, 
            "country": "Egypt", 
            "continent": "Africa"
        },
        {
            "name": "Lagos", 
            "location": {"type": "Point", "coordinates": [3.3792, 6.5244]}, 
            "country": "Nigeria", 
            "continent": "Africa"
        },
        {
            "name": "Nairobi", 
            "location": {"type": "Point", "coordinates": [36.8219, -1.2921]}, 
            "country": "Kenya", 
            "continent": "Africa"
        },
        {
            "name": "Johannesburg", 
            "location": {"type": "Point", "coordinates": [28.0473, -26.2041]}, 
            "country": "South Africa", 
            "continent": "Africa"
        },
        {
            "name": "Casablanca", 
            "location": {"type": "Point", "coordinates": [-7.5898, 33.5731]}, 
            "country": "Morocco", 
            "continent": "Africa"
        },
        
        # South America
        {
            "name": "São Paulo", 
            "location": {"type": "Point", "coordinates": [-46.6333, -23.5505]}, 
            "country": "Brazil", 
            "continent": "South America"
        },
        {
            "name": "Rio de Janeiro", 
            "location": {"type": "Point", "coordinates": [-43.1729, -22.9068]}, 
            "country": "Brazil", 
            "continent": "South America"
        },
        {
            "name": "Buenos Aires", 
            "location": {"type": "Point", "coordinates": [-58.3960, -34.6118]}, 
            "country": "Argentina", 
            "continent": "South America"
        },
        {
            "name": "Lima", 
            "location": {"type": "Point", "coordinates": [-77.0428, -12.0464]}, 
            "country": "Peru", 
            "continent": "South America"
        },
        {
            "name": "Bogotá", 
            "location": {"type": "Point", "coordinates": [-74.0721, 4.7110]}, 
            "country": "Colombia", 
            "continent": "South America"
        },
        
        # Oceania
        {
            "name": "Sydney", 
            "location": {"type": "Point", "coordinates": [151.2093, -33.8688]}, 
            "country": "Australia", 
            "continent": "Oceania"
        },
        {
            "name": "Melbourne", 
            "location": {"type": "Point", "coordinates": [144.9631, -37.8136]}, 
            "country": "Australia", 
            "continent": "Oceania"
        },
        {
            "name": "Auckland", 
            "location": {"type": "Point", "coordinates": [174.7633, -36.8485]}, 
            "country": "New Zealand", 
            "continent": "Oceania"
        }
    ]
    
    cities.insert_many(city_data)
    print(f"✅ Inserted {len(city_data)} cities with GeoJSON format")
    
    # Generate flight routes with GeoJSON format
    import random
    flight_routes_list = []
    
    for airline in airline_data:
        # Create 1 route per airline (reduced from 3)
        start_city = random.choice(city_data)
        end_city = random.choice(city_data)
        
        if start_city != end_city:  # Ensure different cities
            # Extract coordinates from GeoJSON
            start_coords = start_city["location"]["coordinates"]
            end_coords = end_city["location"]["coordinates"]
            
            route = {
                "airline_name": airline["name"],
                "airline_code": airline["code"],
                "airline_color": airline["color"],
                "airline_icon": airline["icon"],
                "start_city": start_city["name"],
                "start_location": {
                    "type": "Point",
                    "coordinates": start_coords
                },
                "end_city": end_city["name"],
                "end_location": {
                    "type": "Point",
                    "coordinates": end_coords
                },
                "speed": 0.2 + random.random() * 0.3,
                "active": True,
                "created_at": datetime.now()
            }
            flight_routes_list.append(route)
    
    flight_routes.insert_many(flight_routes_list)
    print(f"✅ Inserted {len(flight_routes_list)} flight routes with GeoJSON format")
    
    print("🎉 Flight data seeding completed with geospatial support!")

def seed_organs():
    import random
    from datetime import datetime, timedelta
    organs.delete_many({})
    organ_types = ["Heart", "Liver", "Kidney", "Lung", "Pancreas"]
    statuses = ["available", "in_transit", "delivered"]
    city_docs = list(cities.find({}))
    organ_docs = []
    for i in range(10):  # Reduced from 30 to 10 organs
        city = random.choice(city_docs)
        organ_type = random.choice(organ_types)
        status = random.choices(statuses, weights=[0.5, 0.3, 0.2])[0]
        organ = {
            "organ_type": organ_type,
            "status": status,
            "city": city["name"],
            "location": city["location"],
            "flight_id": None,
            "last_updated": datetime.now() - timedelta(hours=random.randint(0, 48))
        }
        organ_docs.append(organ)
    organs.insert_many(organ_docs)
    print(f"✅ Inserted {len(organ_docs)} organs with GeoJSON format")

if __name__ == "__main__":
    seed_flight_data()
    seed_organs() 