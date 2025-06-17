import csv
from mongo import donors, hospitals, vehicles, devices, recipients, cities
from datetime import datetime, timedelta
import random
import os

# --- Seed Donors from Organ Donation.csv ---
donors.delete_many({})
city_list = list(cities.find({}, {'_id': 0}))
city_names = {c['name'].strip().lower(): c for c in city_list}
city_names_list = list(city_names.values())

# Map Indian cities to global cities for demo coverage
city_map = {
    'bangalore': 'London',
    'bengaluru': 'London',
    'delhi': 'London',
    'mumbai': 'London',
    'pune': 'London',
    'chennai': 'London',
    'lucknow': 'London',
    'noida': 'London',
    'ahmedabad': 'London',
    'ranchi': 'London',
    'bhagalpur': 'London',
    'keonjhar': 'London',
    'jamshedpur': 'London',
    'virajpet': 'London',
    'kanpur': 'London',
    'hyderabad': 'London',
    'jabalpur': 'London',
    'jamnagar': 'London',
    'dariba': 'London',
    'chandil': 'London',
    'new delhi': 'London',
    'sao paulo': 'São Paulo',
    'london': 'London',
    'berlin': 'Berlin',
    'new york': 'New York',
    'chennai': 'Chennai',
    'toronto': 'Toronto',
    'sydney': 'Sydney',
    'cape town': 'Cape Town',
    'groote schuur hospital': 'Cape Town',
    'mount sinai hospital': 'New York',
    'apollo hospital': 'Chennai',
    'hospital das clínicas': 'São Paulo',
    'charité': 'Berlin',
    'royal free hospital': 'London',
}

def get_city(city_raw):
    city = city_raw.strip().lower()
    mapped = city_map.get(city, city)
    return city_names.get(mapped, None)

donor_data = []
unmapped_cities = set()
with open('Organ Donation.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        city_info = get_city(row['City'])
        if not city_info:
            unmapped_cities.add(row['City'].strip())
            # Assign a random global city for demo
            city_info = random.choice(city_names_list)
        name = row['Name'].strip()
        if name.lower() == 'anonymous donor' or not name:
            initials = 'AD'
        else:
            initials = ''.join([w[0] for w in name.split() if w and w[0].isalpha()][:2]).upper() or 'AD'
        age = row['Age'] if 'year' not in row['Age'].lower() else row['Age'].split()[0]
        gender = row['Gender'] if row['Gender'] else 'Unknown'
        willing = row.get('Are you willing to donate organs?', '').strip().lower() == 'yes'
        registered = row.get('Have you registered as  an organ donor with the relevant authorities or a donor registry?', '').strip().lower() == 'yes'
        blood_type = random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        organs_willing = random.sample(["Kidney", "Liver", "Heart", "Lung"], random.randint(1, 2))
        donor_data.append({
            "anonymized_name": initials,
            "age": age,
            "gender": gender,
            "city": city_info["name"],
            "country": city_info["country"],
            "continent": city_info["continent"],
            "location": city_info["location"],
            "blood_type": blood_type,
            "willing_to_donate": willing,
            "registered_donor": registered,
            "organs_willing": organs_willing,
            "timestamp": datetime.now() - timedelta(days=random.randint(0, 365))
        })
if donor_data:
    donors.insert_many(donor_data)
    print(f"Seeded {len(donor_data)} donors from Organ Donation.csv.")
    if unmapped_cities:
        print(f"Unmapped cities (randomly assigned): {sorted(unmapped_cities)}")
else:
    print("No valid donors found in Organ Donation.csv.")

# --- Seed Hospitals ---
hospitals.delete_many({})
hospitals.insert_many([
    {"name": "Royal Free Hospital", "city": "London", "location": {"type": "Point", "coordinates": [-0.1749, 51.5557]}},
    {"name": "Charité", "city": "Berlin", "location": {"type": "Point", "coordinates": [13.3777, 52.5235]}},
    {"name": "Mount Sinai Hospital", "city": "New York", "location": {"type": "Point", "coordinates": [-73.9524, 40.7901]}},
    {"name": "Apollo Hospital", "city": "Chennai", "location": {"type": "Point", "coordinates": [80.2376, 13.0604]}},
    {"name": "Toronto General Hospital", "city": "Toronto", "location": {"type": "Point", "coordinates": [-79.3860, 43.6584]}},
    {"name": "Hospital das Clínicas", "city": "São Paulo", "location": {"type": "Point", "coordinates": [-46.6689, -23.5558]}},
    {"name": "St Vincent's Hospital", "city": "Sydney", "location": {"type": "Point", "coordinates": [151.2222, -33.8790]}},
    {"name": "Groote Schuur Hospital", "city": "Cape Town", "location": {"type": "Point", "coordinates": [18.4655, -33.9410]}}
])
print("Seeded hospitals.")

# --- Seed Vehicles ---
vehicles.delete_many({})
vehicles.insert_many([
    {"type": "Ambulance", "city": "London", "location": {"type": "Point", "coordinates": [-0.1, 51.51]}},
    {"type": "Drone", "city": "Berlin", "location": {"type": "Point", "coordinates": [13.4, 52.52]}},
    {"type": "Helicopter", "city": "New York", "location": {"type": "Point", "coordinates": [-73.98, 40.75]}},
    {"type": "Ambulance", "city": "Chennai", "location": {"type": "Point", "coordinates": [80.25, 13.08]}},
    {"type": "Drone", "city": "Toronto", "location": {"type": "Point", "coordinates": [-79.38, 43.65]}},
    {"type": "Ambulance", "city": "São Paulo", "location": {"type": "Point", "coordinates": [-46.63, -23.55]}},
    {"type": "Helicopter", "city": "Sydney", "location": {"type": "Point", "coordinates": [151.21, -33.87]}},
    {"type": "Ambulance", "city": "Cape Town", "location": {"type": "Point", "coordinates": [18.42, -33.92]}}
])
print("Seeded vehicles.")

# --- Seed Devices ---
devices.delete_many({})
devices.insert_many([
    {"device_id": "DEV-1001", "city": "London", "location": {"type": "Point", "coordinates": [-0.12, 51.50]}},
    {"device_id": "DEV-1002", "city": "Berlin", "location": {"type": "Point", "coordinates": [13.41, 52.51]}},
    {"device_id": "DEV-1003", "city": "New York", "location": {"type": "Point", "coordinates": [-73.97, 40.76]}},
    {"device_id": "DEV-1004", "city": "Chennai", "location": {"type": "Point", "coordinates": [80.23, 13.07]}},
    {"device_id": "DEV-1005", "city": "Toronto", "location": {"type": "Point", "coordinates": [-79.39, 43.66]}},
    {"device_id": "DEV-1006", "city": "São Paulo", "location": {"type": "Point", "coordinates": [-46.62, -23.56]}},
    {"device_id": "DEV-1007", "city": "Sydney", "location": {"type": "Point", "coordinates": [151.22, -33.88]}},
    {"device_id": "DEV-1008", "city": "Cape Town", "location": {"type": "Point", "coordinates": [18.43, -33.93]}}
])
print("Seeded devices.")

# --- Seed Recipients ---
recipients.delete_many({})
recipients.insert_many([
    {"code": "RCP-001", "city": "London", "location": {"type": "Point", "coordinates": [-0.13, 51.52]}},
    {"code": "RCP-002", "city": "Berlin", "location": {"type": "Point", "coordinates": [13.42, 52.53]}},
    {"code": "RCP-003", "city": "New York", "location": {"type": "Point", "coordinates": [-73.96, 40.77]}},
    {"code": "RCP-004", "city": "Chennai", "location": {"type": "Point", "coordinates": [80.24, 13.06]}},
    {"code": "RCP-005", "city": "Toronto", "location": {"type": "Point", "coordinates": [-79.37, 43.67]}},
    {"code": "RCP-006", "city": "São Paulo", "location": {"type": "Point", "coordinates": [-46.61, -23.57]}},
    {"code": "RCP-007", "city": "Sydney", "location": {"type": "Point", "coordinates": [151.23, -33.86]}},
    {"code": "RCP-008", "city": "Cape Town", "location": {"type": "Point", "coordinates": [18.44, -33.94]}}
])
print("Seeded recipients.") 