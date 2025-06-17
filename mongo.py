import pymongo
from config import MONGO_URI

# MongoDB connection with timeout settings
client = pymongo.MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,  # 5 second timeout
    connectTimeoutMS=10000,         # 10 second connection timeout
    socketTimeoutMS=10000,          # 10 second socket timeout
    maxPoolSize=10,                 # Connection pool size
    retryWrites=True,
    retryReads=True
)

# Test connection
try:
    client.admin.command('ping')
except Exception as e:
    # Fallback to local MongoDB if available
    try:
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
    except Exception as e2:
        pass

db = client.iot

# Collections for all tables
machines = db.machines
parts = db.parts
sensor_data = db.sensor_data
maintenance_records = db.maintenance_records
alerts = db.alerts
users = db.users
file_metadata = db.file_metadata
ai_interactions = db.ai_interactions
predictive_models = db.predictive_models
device_types = db.device_types
devices = db.devices
organs = db.organs
donors = db.donors

# New collections for dashboard data with geospatial support
airlines = db.airlines
flight_routes = db.flight_routes
cities = db.cities
metrics_data = db.metrics_data
flight_paths = db.flight_paths

# Create geospatial indexes for better performance
def create_geospatial_indexes():
    try:
        # Create 2dsphere index on cities collection for location-based queries
        cities.create_index([("location", pymongo.GEOSPHERE)])
        
        # Create 2dsphere index on flight_routes for route-based queries
        flight_routes.create_index([("start_location", pymongo.GEOSPHERE)])
        flight_routes.create_index([("end_location", pymongo.GEOSPHERE)])
        
        # Create compound index for flight paths
        flight_paths.create_index([("route_id", pymongo.ASCENDING), ("coordinates", pymongo.GEOSPHERE)])
        
        # Create 2dsphere index on organs collection for organ location queries
        organs.create_index([("location", pymongo.GEOSPHERE)])
        
        # Create 2dsphere index on donors collection for donor location queries
        donors.create_index([("location", pymongo.GEOSPHERE)])
        
    except Exception as e:
        pass

# Initialize geospatial indexes
create_geospatial_indexes()

hospitals = db['hospitals']
vehicles = db['vehicles']
devices = db['devices']
recipients = db['recipients']
