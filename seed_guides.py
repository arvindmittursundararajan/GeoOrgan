import os
from ai_service import get_embedding
from mongo import db
from pymongo.operations import SearchIndexModel
import time

# Organ transport device guides
machine_guides = [
    {
        "title": "Organ Preservation Device Maintenance",
        "content": """Step 1: Pre-Transport Check
- Verify power supply and backup battery
- Check temperature monitoring system
- Inspect perfusion circuit for leaks
- Calibrate pressure sensors

Step 2: Perfusion System Setup
- Prime the system with preservation solution
- Verify flow rates and pressure readings
- Check oxygen saturation levels
- Test alarm systems

Step 3: Transport Preparation
- Secure organ container in transport unit
- Connect monitoring leads
- Verify GPS tracking system
- Test communication systems

Step 4: Post-Transport Care
- Clean and sterilize all components
- Replace disposable parts
- Document maintenance in system
- Schedule next calibration"""
    },
    {
        "title": "Organ Transport Container Troubleshooting",
        "content": """Common Issues and Solutions:

1. Temperature Control
- Check cooling system operation
- Verify temperature sensors
- Inspect insulation integrity
- Test backup cooling

2. Power Management
- Monitor battery levels
- Check charging system
- Test power transfer
- Verify backup power

3. Monitoring Systems
- Calibrate sensors
- Check data transmission
- Verify alarm thresholds
- Test connectivity

4. Container Integrity
- Inspect seals and gaskets
- Check pressure integrity
- Verify shock absorption
- Test locking mechanisms

5. Communication Systems
- Test GPS tracking
- Verify cellular connectivity
- Check emergency alerts
- Test data logging"""
    },
    {
        "title": "Organ Monitoring Equipment Guide",
        "content": """Regular Maintenance Checklist:

1. Vital Signs Monitoring
- Calibrate pressure sensors
- Check oxygen saturation probes
- Verify temperature sensors
- Test ECG leads

2. Data Recording
- Verify data storage
- Check transmission systems
- Test backup systems
- Validate timestamps

3. Alarm Systems
- Test all alarm conditions
- Verify notification systems
- Check escalation protocols
- Test backup alerts

4. Power Systems
- Monitor battery health
- Check charging circuits
- Test power redundancy
- Verify UPS operation

5. Communication
- Test cellular connectivity
- Verify satellite backup
- Check emergency channels
- Test data encryption"""
    },
    {
        "title": "Transport Vehicle Equipment Guide",
        "content": """Essential Equipment Maintenance:

1. Climate Control
- Check temperature regulation
- Verify humidity control
- Test air filtration
- Monitor CO2 levels

2. Power Systems
- Inspect main power supply
- Test backup generators
- Check battery banks
- Verify power distribution

3. Monitoring Equipment
- Calibrate all sensors
- Test data transmission
- Verify alarm systems
- Check recording devices

4. Safety Systems
- Test emergency lighting
- Verify fire suppression
- Check security systems
- Test emergency exits

5. Communication
- Test radio systems
- Verify GPS tracking
- Check cellular backup
- Test emergency beacons"""
    }
]

# Geospatial best practices for MongoDB (RAG entries)
geospatial_best_practices = [
    {
        "title": "Store Points as GeoJSON",
        "content": "Use GeoJSON 'Point' type for storing single locations. Example: { 'type': 'Point', 'coordinates': [longitude, latitude] } (longitude first)."
    },
    {
        "title": "Store Areas as Polygons",
        "content": "Use GeoJSON 'Polygon' type for areas. Example: { 'type': 'Polygon', 'coordinates': [[[lng1, lat1], [lng2, lat2], ...]] }. The first and last point must be the same. Exterior bounds counterclockwise, holes clockwise."
    },
    {
        "title": "Create 2dsphere Index for Spherical Queries",
        "content": "For most geospatial queries, create a 2dsphere index: db.collection.createIndex({location: '2dsphere'}). This supports all GeoJSON types and spherical calculations."
    },
    {
        "title": "Create 2d Index for Flat Plane Queries",
        "content": "For legacy or flat-plane queries, use a 2d index: db.collection.createIndex({location: '2d'}). Use only for legacy or non-GeoJSON data."
    },
    {
        "title": "Use $near for Proximity Search",
        "content": "Find documents within a distance of a point: db.collection.find({location: {$near: {$geometry: {type: 'Point', coordinates: [...]}, $maxDistance: 1000, $minDistance: 10}}})"
    },
    {
        "title": "Use $geoWithin for Containment",
        "content": "Find documents fully within a shape (circle, box, polygon): db.collection.find({location: {$geoWithin: {$centerSphere: [[lng, lat], radiusInRadians]}}})"
    },
    {
        "title": "Use $geoIntersects for Overlap",
        "content": "Find documents that intersect a geometry: db.collection.find({location: {$geoIntersects: {$geometry: {type: 'Polygon', coordinates: [...]}}}})"
    },
    {
        "title": "Store Timestamps with Locations",
        "content": "Include timestamps with geospatial data for time-based and spatiotemporal queries."
    },
    {
        "title": "Visualize and Validate Data",
        "content": "Use tools like Google Maps or MongoDB Charts to visualize and validate your geospatial data and queries."
    },
    {
        "title": "Model for Query Patterns",
        "content": "Design your schema based on the most common geospatial queries (e.g., proximity, containment, intersection) to optimize performance."
    },
    {
        "title": "Embed vs Reference for IoT Data",
        "content": "Embed sensor readings if they are small and queried together; use references for large or time-series data to keep documents manageable."
    },
    {
        "title": "Monitor Index Usage",
        "content": "Regularly monitor geospatial index usage and query performance using MongoDB Atlas or explain plans to ensure optimal performance."
    }
]

def ensure_vector_index(collection, num_dimensions=768, index_name="vector_index"):
    """Ensure a vector index exists on the collection for the embedding field."""
    try:
        existing_indexes = list(collection.list_search_indexes())
        if not any(idx.get("name") == index_name for idx in existing_indexes):
            print(f"Creating vector index '{index_name}' on {collection.name}...")
            search_index_model = SearchIndexModel(
                definition={
                    "fields": [
                        {
                            "type": "vector",
                            "numDimensions": num_dimensions,
                            "path": "embedding",
                            "similarity": "cosine"
                        }
                    ]
                },
                name=index_name,
                type="vectorSearch"
            )
            collection.create_search_index(model=search_index_model)
            # Wait for index to be queryable
            print("Waiting for vector index to become queryable...")
            while True:
                indices = list(collection.list_search_indexes(index_name))
                if len(indices) and indices[0].get("queryable") is True:
                    break
                time.sleep(5)
            print(f"Vector index '{index_name}' is ready.")
        else:
            print(f"Vector index '{index_name}' already exists on {collection.name}.")
    except Exception as e:
        print(f"Error ensuring vector index: {e}")
        raise

def seed_guides():
    """Seed the database with sample guides and geospatial best practices"""
    try:
        # Ensure vector index for geo_best_practices
        ensure_vector_index(db['geo_best_practices'])
        # Generate embeddings for each guide
        for guide in machine_guides:
            guide['embedding'] = get_embedding(guide['content'])
        # Insert guides into MongoDB
        result = db['machine_guides'].insert_many(machine_guides)
        print(f"Successfully inserted {len(result.inserted_ids)} guides")
        # Generate embeddings for each geospatial best practice
        for entry in geospatial_best_practices:
            entry['embedding'] = get_embedding(entry['content'])
        # Insert best practices into MongoDB
        geo_result = db['geo_best_practices'].insert_many(geospatial_best_practices)
        print(f"Successfully inserted {len(geo_result.inserted_ids)} geospatial best practices")
    except Exception as e:
        print(f"Error seeding guides: {str(e)}")
        raise

if __name__ == "__main__":
    seed_guides() 