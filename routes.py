from flask import render_template, request, redirect, url_for, jsonify, flash, send_from_directory, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from mongo import machines, parts, sensor_data, maintenance_records, alerts, users, airlines, cities, flight_routes, metrics_data, organs, donors, hospitals, vehicles, devices, recipients, db
from bson import ObjectId, errors as bson_errors
import os
from datetime import datetime
import logging
import requests
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel
from typing import List, Dict, Any
import time
from config import MONGO_URI
from ai_service import get_embedding

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.embedding_url = f"https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent?key={self.api_key}"
        self.text_generation_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        self.headers = {
            "Content-Type": "application/json"
        }

    def get_embedding(self, text: str) -> List[float]:
        try:
            payload = {
                "model": "models/embedding-001",
                "content": {
                    "parts": [{"text": text}]
                }
            }
            response = requests.post(
                self.embedding_url,
                headers=self.headers,
                json=payload
            )
            if response.status_code != 200:
                response.raise_for_status()
            result = response.json()
            return result["embedding"]["values"]
        except Exception as e:
            raise

    def generate_summary(self, results: List[Dict[str, Any]], query: str) -> str:
        try:
            context = "\n\n".join([
                f"Title: {r['title']}\nContent: {r['content']}"
                for r in results
            ])
            prompt = f"""Use the following machine repair guides to answer the question.\nIf the guides don't contain relevant information, say so.\n\nGuides:\n{context}\n\nQuestion: {query}\n\nProvide a clear, concise answer based only on the information in the guides."""
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            response = requests.post(
                self.text_generation_url,
                headers=self.headers,
                json=payload
            )
            if response.status_code != 200:
                response.raise_for_status()
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise

gemini_service = GeminiService()

class MongoDBService:
    def __init__(self):
        self.client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            maxPoolSize=10,
            retryWrites=True,
            retryReads=True
        )
        self.db = self.client["rag_db"]
        self.collection = self.db["machine_guides"]
        self._ensure_vector_index()

    def _ensure_vector_index(self):
        try:
            existing_indexes = list(self.collection.list_search_indexes())
            if not any(idx.get("name") == "vector_index" for idx in existing_indexes):
                dummy_id = None
                if self.collection.estimated_document_count() == 0:
                    dummy_id = self.collection.insert_one({"_dummy": True, "embedding": [0.0]*768}).inserted_id
                search_index_model = SearchIndexModel(
                    definition={
                        "fields": [
                            {
                                "type": "vector",
                                "numDimensions": 768,
                                "path": "embedding",
                                "similarity": "cosine"
                            }
                        ]
                    },
                    name="vector_index",
                    type="vectorSearch"
                )
                self.collection.create_search_index(model=search_index_model)
                while True:
                    indices = list(self.collection.list_search_indexes("vector_index"))
                    if len(indices) and indices[0].get("queryable") is True:
                        break
                    time.sleep(5)
                if dummy_id:
                    self.collection.delete_one({"_id": dummy_id})
        except Exception as e:
            raise

    def insert_guide(self, guide_data):
        try:
            result = self.collection.insert_one(guide_data)
            return result.inserted_id
        except Exception as e:
            raise

    def insert_many_guides(self, guides_data):
        try:
            result = self.collection.insert_many(guides_data)
            return result.inserted_ids
        except Exception as e:
            raise

    def search_guides(self, query_embedding, limit=3):
        try:
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "queryVector": query_embedding,
                        "path": "embedding",
                        "exact": True,
                        "limit": limit
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "title": 1,
                        "content": 1,
                        "score": { "$meta": "vectorSearchScore" }
                    }
                }
            ]
            results = list(self.collection.aggregate(pipeline))
            return results
        except Exception as e:
            raise

    def get_stats(self):
        try:
            stats = {
                "total_documents": self.collection.count_documents({}),
                "indexes": list(self.collection.list_search_indexes())
            }
            return stats
        except Exception as e:
            raise

mongodb_service = MongoDBService()

def register_routes(app):
    @app.route('/')
    def dashboard():
        all_machines = list(machines.find())
        machine_count = len(all_machines)
        all_parts = list(parts.find())
        part_count = len(all_parts)
        # Count status for dashboard
        status_data = {'operational': 0, 'warning': 0, 'maintenance': 0, 'error': 0}
        for m in all_machines:
            status = m.get('status', 'operational')
            if status in status_data:
                status_data[status] += 1
        for p in all_parts:
            status = p.get('status', 'operational')
            if status in status_data:
                status_data[status] += 1
        # Fetch recent alerts for dashboard right panel
        recent_alerts = list(alerts.find().sort('timestamp', -1).limit(10))
        for alert in recent_alerts:
            # Ensure timestamp is always a string for Jinja
            if 'timestamp' in alert and hasattr(alert['timestamp'], 'strftime'):
                alert['timestamp'] = alert['timestamp'].strftime('%Y-%m-%d %H:%M')
            elif 'timestamp' in alert and isinstance(alert['timestamp'], str):
                # Try to format string if possible, else leave as is
                try:
                    import datetime
                    dt = datetime.datetime.fromisoformat(alert['timestamp'])
                    alert['timestamp'] = dt.strftime('%Y-%m-%d %H:%M')
                except Exception:
                    pass
        return render_template('dashboard.html', machines=all_machines, machine_count=machine_count, part_count=part_count, status_data=status_data, recent_alerts=recent_alerts)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = users.find_one({'username': username})
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = str(user['_id'])
                return redirect(url_for('dashboard'))
            flash('Invalid credentials')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.route('/ingest')
    def ingest():
        return render_template('ingest.html')

    @app.route('/visualize')
    def visualize():
        return render_template('visualize.html')

    @app.route('/maintenance')
    def maintenance():
        return render_template('maintenance.html')

    @app.route('/reset', methods=['GET', 'POST'])
    def reset_database():
        if request.method == 'POST':
            from run_seed import seed_database
            seed_database()
            flash('Database has been reset and seeded!')
            return redirect(url_for('dashboard'))
        return render_template('reset.html')

    @app.route('/api/asset-tree')
    def asset_tree():
        try:
            machine_list = list(machines.find())
            part_list = list(parts.find())
            tree = []
            def get_color(status):
                colors = {
                    'operational': '#28a745',
                    'critical': '#e53935',
                    'warning': '#ffc107',
                    'maintenance': '#e53935',
                    'error': '#e53935',
                    'in_transit': '#6c757d'
                }
                return colors.get(status, '#6c757d')
            for m in machine_list:
                m_id = str(m['_id'])
                health_color = get_color(m.get('status', 'operational'))
                health_circle = f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{health_color};margin-right:7px;vertical-align:middle;border:1.5px solid #222;"></span>'
                m_node = {
                    'id': f'machine-{m_id}',
                    'text': health_circle + m.get('name', 'Machine'),
                    'type': 'machine',
                    'machine_id': m_id,
                    'status': m.get('status', 'operational'),
                    'children': []
                }
                for p in part_list:
                    if str(p.get('machine_id')) == m_id:
                        p_id = str(p['_id'])
                        health_color = get_color(p.get('status', 'operational'))
                        health_circle = f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{health_color};margin-right:7px;vertical-align:middle;border:1.5px solid #222;"></span>'
                        p_node = {
                            'id': f'part-{p_id}',
                            'text': health_circle + p.get('name', 'Part'),
                            'type': 'part',
                            'part_id': p_id,
                            'machine_id': m_id,
                            'status': p.get('status', 'operational'),
                            'children': []
                        }
                        m_node['children'].append(p_node)
                tree.append(m_node)
            return jsonify(tree)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/asset/<asset_type>/<asset_id>')
    def asset_details(asset_type, asset_id):
        try:
            chart_data = {}
            if asset_type == 'machine':
                asset = machines.find_one({'_id': ObjectId(asset_id)})
                if not asset:
                    return jsonify({'error': 'Asset not found'}), 404
                asset['_id'] = str(asset['_id'])
                asset['id'] = asset['_id']
                asset['name'] = asset.get('name', 'Unknown Machine')
                asset['parts'] = [
                    {k: (str(v) if k == '_id' or isinstance(v, ObjectId) else v) for k, v in p.items()}
                    for p in parts.find({'machine_id': asset['_id']})
                ]
                # Fetch sensor data for this machine (use ObjectId if possible)
                try:
                    sensor_oid = ObjectId(asset['_id'])
                except bson_errors.InvalidId:
                    sensor_oid = asset['_id']
                sensor_cursor = sensor_data.find({'machine_id': sensor_oid})
                # Fetch alerts for this machine
                asset_alerts = list(alerts.find({'machine_id': asset['_id']}).sort('timestamp', -1).limit(5))
            elif asset_type == 'part':
                asset = parts.find_one({'_id': ObjectId(asset_id)})
                if not asset:
                    return jsonify({'error': 'Asset not found'}), 404
                asset['_id'] = str(asset['_id'])
                asset['id'] = asset['_id']
                asset['name'] = asset.get('name', 'Unknown Part')
                for k, v in asset.items():
                    if isinstance(v, ObjectId):
                        asset[k] = str(v)
                machine_name = ''
                if 'machine_id' in asset and asset['machine_id']:
                    try:
                        machine = machines.find_one({'_id': ObjectId(asset['machine_id'])})
                        if not machine:
                            machine = machines.find_one({'_id': asset['machine_id']})
                        machine_name = machine['name'] if machine else ''
                    except Exception as e:
                        machine_name = ''
                asset['machine_name'] = machine_name
                # Fetch sensor data for this part (use ObjectId if possible)
                try:
                    sensor_oid = ObjectId(asset['_id'])
                except bson_errors.InvalidId:
                    sensor_oid = asset['_id']
                sensor_cursor = sensor_data.find({'part_id': sensor_oid})
                # Fetch alerts for this part
                asset_alerts = list(alerts.find({'part_id': asset['_id']}).sort('timestamp', -1).limit(5))
            else:
                return jsonify({'error': 'Invalid asset type'}), 400

            # Build chart_data from sensor_cursor
            for s in sensor_cursor:
                sensor_type = s.get('sensor_type', 'Unknown')
                if sensor_type not in chart_data:
                    chart_data[sensor_type] = {'timestamps': [], 'values': [], 'labels': [], 'anomalies': []}
                ts = s.get('timestamp')
                val = s.get('value')
                is_anomaly = s.get('is_anomaly', False)
                chart_data[sensor_type]['timestamps'].append(ts)
                chart_data[sensor_type]['values'].append(val)
                chart_data[sensor_type]['labels'].append(ts)
                chart_data[sensor_type]['anomalies'].append(is_anomaly)

            # Format alerts for frontend
            formatted_alerts = []
            for alert in asset_alerts:
                formatted_alerts.append({
                    'type': alert.get('alert_type', ''),
                    'message': alert.get('message', ''),
                    'severity': alert.get('severity', ''),
                    'timestamp': alert.get('timestamp', '')
                })
            asset['alerts'] = formatted_alerts
            
            # Generate AI recommendations based on asset data
            ai_recommendation = generate_ai_recommendation(asset, chart_data, formatted_alerts)
            asset['ai_recommendation'] = ai_recommendation
            asset['chart_data'] = chart_data
            return jsonify(asset)
        except Exception as e:
            import traceback
            print('Asset details error:', e)
            traceback.print_exc()
            return jsonify({'error': f'Failed to load asset details: {str(e)}'}), 500

    @app.route('/api/alerts/recent')
    def recent_alerts():
        try:
            recent = list(alerts.find().sort('timestamp', -1).limit(10))
            for alert in recent:
                alert['_id'] = str(alert['_id'])
                if 'machine_id' in alert and isinstance(alert['machine_id'], ObjectId):
                    alert['machine_id'] = str(alert['machine_id'])
                if 'part_id' in alert and isinstance(alert['part_id'], ObjectId):
                    alert['part_id'] = str(alert['part_id'])
            return jsonify(recent)
        except Exception as e:
            import traceback
            print('Recent alerts error:', e)
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/maintenance')
    def maintenance_list():
        try:
            records = list(maintenance_records.find().sort('start_date', -1))
            for rec in records:
                rec['_id'] = str(rec['_id'])
                if 'machine_id' in rec and isinstance(rec['machine_id'], ObjectId):
                    rec['machine_id'] = str(rec['machine_id'])
                if 'part_id' in rec and isinstance(rec['part_id'], ObjectId):
                    rec['part_id'] = str(rec['part_id'])
            return jsonify(records)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/sensor-data')
    def sensor_data_api():
        try:
            data = list(sensor_data.find().sort('timestamp', -1).limit(1000))
            for d in data:
                d['_id'] = str(d['_id'])
                if 'machine_id' in d and isinstance(d['machine_id'], ObjectId):
                    d['machine_id'] = str(d['machine_id'])
                if 'part_id' in d and isinstance(d['part_id'], ObjectId):
                    d['part_id'] = str(d['part_id'])
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/ask-ai', methods=['POST'])
    def ask_ai():
        try:
            data = request.get_json()
            question = data.get('question', '')
            asset_id = data.get('machine_id') or data.get('part_id')
            # Load prompt
            with open('prompt.txt', 'r') as f:
                prompt = f.read().strip()
            # Fetch recent alerts for this asset
            asset_alerts = list(alerts.find({}))
            if asset_id:
                asset_alerts = list(alerts.find({'$or': [{'machine_id': asset_id}, {'part_id': asset_id}]}).sort('timestamp', -1).limit(5))
            alert_summaries = []
            for alert in asset_alerts:
                alert_summaries.append(f"[{alert.get('timestamp', '')}] {alert.get('alert_type', '')}: {alert.get('message', '')}")
            alerts_text = '\n'.join(alert_summaries)
            # Compose full prompt
            full_prompt = f"{prompt}\n\nRecent Alerts for this asset:\n{alerts_text}\n\nUser question: {question}"
            # Call Gemini API
            response = gemini_service.generate_summary(asset_alerts, question)
            return jsonify({'response': response})
        except Exception as e:
            import traceback
            print('AI API error:', e)
            traceback.print_exc()
            return jsonify({'response': f'Failed to get a response: {str(e)}'}), 500

    @app.route('/api/metrics')
    def get_metrics():
        try:
            # Count total organs (machines + parts)
            total_machines = machines.count_documents({})
            total_parts = parts.count_documents({})
            total_organs = total_machines + total_parts
            
            # Count total flights (machines with in_transit status)
            total_flights = machines.count_documents({'status': 'in_transit'})
            
            # Count total devices monitored (all machines and parts)
            total_devices = total_organs
            
            # Count active failures (critical, error, maintenance status)
            active_failures = machines.count_documents({
                'status': {'$in': ['critical', 'error', 'maintenance']}
            }) + parts.count_documents({
                'status': {'$in': ['critical', 'error', 'maintenance']}
            })
            
            # Calculate average response time based on recent alerts
            recent_alerts = list(alerts.find().sort('timestamp', -1).limit(100))
            avg_response = 2.3  # Default value, could be calculated from actual data
            
            # Calculate success rate (operational devices / total devices)
            operational_devices = machines.count_documents({'status': 'operational'}) + parts.count_documents({'status': 'operational'})
            success_rate = (operational_devices / total_devices * 100) if total_devices > 0 else 0
            
            # NEW: Count organs from organs collection
            total_available_organs = organs.count_documents({'status': 'available'})
            total_in_transit_organs = organs.count_documents({'status': 'in_transit'})
            total_reserved_organs = organs.count_documents({'status': 'reserved'})
            total_delivered_organs = organs.count_documents({'status': 'delivered'})
            total_medical_organs = total_available_organs + total_in_transit_organs + total_reserved_organs + total_delivered_organs
            
            # Create metrics data
            metrics = {
                'total_organs': total_organs,
                'total_flights': total_flights,
                'total_devices': total_devices,
                'active_failures': active_failures,
                'avg_response': f'{avg_response:.1f}m',
                'success_rate': f'{success_rate:.1f}%',
                'timestamp': datetime.now(),
                'operational_devices': operational_devices,
                'total_machines': total_machines,
                'total_parts': total_parts,
                # NEW: Medical organ metrics
                'total_available_organs': total_available_organs,
                'total_in_transit_organs': total_in_transit_organs,
                'total_reserved_organs': total_reserved_organs,
                'total_delivered_organs': total_delivered_organs,
                'total_medical_organs': total_medical_organs
            }
            
            # Store metrics in database for historical tracking
            metrics_data.insert_one(metrics)
            
            # Clean up old metrics (keep last 1000 records)
            old_count = metrics_data.count_documents({})
            if old_count > 1000:
                # Delete oldest records, keeping only the latest 1000
                oldest_records = list(metrics_data.find().sort('timestamp', 1).limit(old_count - 1000))
                if oldest_records:
                    oldest_ids = [record['_id'] for record in oldest_records]
                    metrics_data.delete_many({'_id': {'$in': oldest_ids}})
            
            return jsonify({
                'total_organs': total_organs,
                'total_flights': total_flights,
                'total_devices': total_devices,
                'active_failures': active_failures,
                'avg_response': f'{avg_response:.1f}m',
                'success_rate': f'{success_rate:.1f}%',
                # NEW: Medical organ metrics
                'total_available_organs': total_available_organs,
                'total_in_transit_organs': total_in_transit_organs,
                'total_reserved_organs': total_reserved_organs,
                'total_delivered_organs': total_delivered_organs,
                'total_medical_organs': total_medical_organs
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/airlines')
    def get_airlines():
        try:
            airline_list = list(airlines.find({}, {'_id': 0}))
            return jsonify(airline_list)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/cities')
    def get_cities():
        try:
            # Convert GeoJSON format to frontend format
            city_list = []
            for city in cities.find({}, {'_id': 0}):
                # Convert GeoJSON coordinates [lng, lat] to frontend format [lat, lng]
                coords = city['location']['coordinates']
                city_list.append({
                    'name': city['name'],
                    'lat': coords[1],  # latitude
                    'lng': coords[0],  # longitude
                    'country': city['country'],
                    'continent': city['continent']
                })
            return jsonify(city_list)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/flight-routes')
    def get_flight_routes():
        try:
            routes_list = []
            for route in flight_routes.find({'active': True}, {'_id': 0}):
                # Convert GeoJSON coordinates to frontend format
                start_coords = route['start_location']['coordinates']
                end_coords = route['end_location']['coordinates']
                
                routes_list.append({
                    'airline_name': route['airline_name'],
                    'airline_code': route['airline_code'],
                    'airline_color': route['airline_color'],
                    'airline_icon': route['airline_icon'],
                    'start_city': route['start_city'],
                    'start_lat': start_coords[1],  # latitude
                    'start_lng': start_coords[0],  # longitude
                    'end_city': route['end_city'],
                    'end_lat': end_coords[1],      # latitude
                    'end_lng': end_coords[0],      # longitude
                    'speed': route['speed'],
                    'active': route['active']
                })
            return jsonify(routes_list)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/cities/near/<float:lng>/<float:lat>/<float:distance>')
    def get_cities_near(lng, lat, distance):
        """Get cities within a certain distance using geospatial query"""
        try:
            # Find cities within distance (in meters) of the given point
            nearby_cities = cities.find({
                "location": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [lng, lat]
                        },
                        "$maxDistance": distance * 1000  # Convert km to meters
                    }
                }
            }, {'_id': 0})
            
            city_list = []
            for city in nearby_cities:
                coords = city['location']['coordinates']
                city_list.append({
                    'name': city['name'],
                    'lat': coords[1],
                    'lng': coords[0],
                    'country': city['country'],
                    'continent': city['continent']
                })
            
            return jsonify(city_list)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/flight-routes/from/<city_name>')
    def get_routes_from_city(city_name):
        """Get all flight routes departing from a specific city"""
        try:
            routes_list = []
            for route in flight_routes.find({
                'active': True,
                'start_city': {'$regex': city_name, '$options': 'i'}
            }, {'_id': 0}):
                start_coords = route['start_location']['coordinates']
                end_coords = route['end_location']['coordinates']
                
                routes_list.append({
                    'airline_name': route['airline_name'],
                    'airline_code': route['airline_code'],
                    'airline_color': route['airline_color'],
                    'airline_icon': route['airline_icon'],
                    'start_city': route['start_city'],
                    'start_lat': start_coords[1],
                    'start_lng': start_coords[0],
                    'end_city': route['end_city'],
                    'end_lat': end_coords[1],
                    'end_lng': end_coords[0],
                    'speed': route['speed'],
                    'active': route['active']
                })
            return jsonify(routes_list)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/metrics/history')
    def get_metrics_history():
        try:
            # Get last 100 metrics records for historical data
            history = list(metrics_data.find().sort('timestamp', -1).limit(100))
            
            # Convert ObjectId to string for JSON serialization
            for record in history:
                record['_id'] = str(record['_id'])
                if 'timestamp' in record and hasattr(record['timestamp'], 'isoformat'):
                    record['timestamp'] = record['timestamp'].isoformat()
            
            return jsonify(history)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/test-metrics')
    def test_metrics():
        return send_from_directory('.', 'test_metrics.html')

    @app.route('/api/organs')
    def get_organs():
        """Get all organs with geospatial data"""
        try:
            organs_list = []
            for organ in organs.find({}, {'_id': 0}):
                # Convert GeoJSON coordinates to frontend format
                coords = organ['location']['coordinates']
                organs_list.append({
                    'organ_type': organ['organ_type'],
                    'status': organ['status'],
                    'city': organ['city'],
                    'country': organ.get('country', 'Unknown'),
                    'continent': organ.get('continent', 'Unknown'),
                    'lat': coords[1],  # latitude
                    'lng': coords[0],  # longitude
                    'flight_id': organ.get('flight_id'),
                    'last_updated': organ['last_updated'].isoformat() if hasattr(organ['last_updated'], 'isoformat') else str(organ['last_updated'])
                })
            return jsonify(organs_list)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/organs/near/<float:lng>/<float:lat>/<float:distance>')
    def get_organs_near(lng, lat, distance):
        """Get organs within a certain distance using geospatial query"""
        try:
            # Find organs within distance (in meters) of the given point
            nearby_organs = organs.find({
                "location": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [lng, lat]
                        },
                        "$maxDistance": distance * 1000  # Convert km to meters
                    }
                }
            }, {'_id': 0})
            
            organs_list = []
            for organ in nearby_organs:
                coords = organ['location']['coordinates']
                organs_list.append({
                    'organ_type': organ['organ_type'],
                    'status': organ['status'],
                    'city': organ['city'],
                    'country': organ.get('country', 'Unknown'),
                    'continent': organ.get('continent', 'Unknown'),
                    'lat': coords[1],
                    'lng': coords[0],
                    'flight_id': organ.get('flight_id'),
                    'last_updated': organ['last_updated'].isoformat() if hasattr(organ['last_updated'], 'isoformat') else str(organ['last_updated'])
                })
            
            return jsonify(organs_list)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/organs/in-city/<city_name>')
    def get_organs_in_city(city_name):
        """Get all organs in a specific city"""
        try:
            organs_list = []
            for organ in organs.find({
                'city': {'$regex': city_name, '$options': 'i'}
            }, {'_id': 0}):
                coords = organ['location']['coordinates']
                organs_list.append({
                    'organ_type': organ['organ_type'],
                    'status': organ['status'],
                    'city': organ['city'],
                    'country': organ.get('country', 'Unknown'),
                    'continent': organ.get('continent', 'Unknown'),
                    'lat': coords[1],
                    'lng': coords[0],
                    'flight_id': organ.get('flight_id'),
                    'last_updated': organ['last_updated'].isoformat() if hasattr(organ['last_updated'], 'isoformat') else str(organ['last_updated'])
                })
            return jsonify(organs_list)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/organs/status/<status>')
    def get_organs_by_status(status):
        """Get all organs with a specific status"""
        try:
            organs_list = []
            for organ in organs.find({
                'status': status
            }, {'_id': 0}):
                coords = organ['location']['coordinates']
                organs_list.append({
                    'organ_type': organ['organ_type'],
                    'status': organ['status'],
                    'city': organ['city'],
                    'country': organ.get('country', 'Unknown'),
                    'continent': organ.get('continent', 'Unknown'),
                    'lat': coords[1],
                    'lng': coords[0],
                    'flight_id': organ.get('flight_id'),
                    'last_updated': organ['last_updated'].isoformat() if hasattr(organ['last_updated'], 'isoformat') else str(organ['last_updated'])
                })
            return jsonify(organs_list)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/donors')
    def get_donors():
        """Get all organ donors with geospatial data"""
        try:
            donors_list = []
            for donor in donors.find({}, {'_id': 0}):
                # Convert GeoJSON coordinates to frontend format (lat, lng)
                coords = donor['location']['coordinates']
                donors_list.append({
                    'anonymized_name': donor.get('anonymized_name', 'Anonymous'),
                    'city': donor.get('city', 'Unknown'),
                    'country': donor.get('country', 'Unknown'),
                    'lat': coords[1],  # latitude
                    'lng': coords[0],  # longitude
                    'willing_to_donate': donor.get('willing_to_donate', False),
                    'registered_donor': donor.get('registered_donor', False),
                    'blood_type': donor.get('blood_type', 'Unknown')
                })
            return jsonify(donors_list)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/voice-chat', methods=['POST'])
    def voice_chat():
        try:
            # Get the audio file from the request
            audio_file = request.files.get('audio')
            if not audio_file:
                return jsonify({'error': 'No audio file provided'}), 400

            # Save the audio file temporarily
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_audio.wav')
            audio_file.save(temp_path)

            # Transcribe the audio
            from voice_chat import transcribe_audio
            from ai_service import ask_gemini_with_context
            transcription = transcribe_audio(temp_path)
            if not transcription:
                return jsonify({'error': 'Could not transcribe audio'}), 400

            # Get response from Gemini using the context-aware function
            response = ask_gemini_with_context(transcription)

            # Clean up
            os.remove(temp_path)

            return jsonify({
                'transcription': transcription,
                'response': response
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/donors/near')
    def donors_near():
        """Find donors near a point (lat, lng, distance_km as query params)"""
        try:
            lat = float(request.args.get('lat'))
            lng = float(request.args.get('lng'))
            distance_km = float(request.args.get('distance_km', 50))
            results = donors.find({
                "location": {
                    "$nearSphere": {
                        "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                        "$maxDistance": distance_km * 1000
                    }
                }
            }, {'_id': 0})
            out = []
            for donor in results:
                coords = donor['location']['coordinates']
                out.append({
                    'anonymized_name': donor.get('anonymized_name', 'Anonymous'),
                    'city': donor.get('city', 'Unknown'),
                    'country': donor.get('country', 'Unknown'),
                    'lat': coords[1],
                    'lng': coords[0],
                    'willing_to_donate': donor.get('willing_to_donate', False),
                    'registered_donor': donor.get('registered_donor', False),
                    'blood_type': donor.get('blood_type', 'Unknown')
                })
            return jsonify(out)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/donors/within', methods=['POST'])
    def donors_within():
        """Find donors within a GeoJSON polygon (POST body: {"polygon": {...}})"""
        try:
            data = request.get_json()
            polygon = data.get('polygon')
            if not polygon:
                return jsonify({'error': 'Missing polygon'}), 400
            results = donors.find({
                "location": {
                    "$geoWithin": {"$geometry": polygon}
                }
            }, {'_id': 0})
            out = []
            for donor in results:
                coords = donor['location']['coordinates']
                out.append({
                    'anonymized_name': donor.get('anonymized_name', 'Anonymous'),
                    'city': donor.get('city', 'Unknown'),
                    'country': donor.get('country', 'Unknown'),
                    'lat': coords[1],
                    'lng': coords[0],
                    'willing_to_donate': donor.get('willing_to_donate', False),
                    'registered_donor': donor.get('registered_donor', False),
                    'blood_type': donor.get('blood_type', 'Unknown')
                })
            return jsonify(out)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/donors/intersects', methods=['POST'])
    def donors_intersects():
        """Find donors whose location intersects a GeoJSON shape (POST body: {"geometry": {...}})"""
        try:
            data = request.get_json()
            geometry = data.get('geometry')
            if not geometry:
                return jsonify({'error': 'Missing geometry'}), 400
            results = donors.find({
                "location": {
                    "$geoIntersects": {"$geometry": geometry}
                }
            }, {'_id': 0})
            out = []
            for donor in results:
                coords = donor['location']['coordinates']
                out.append({
                    'anonymized_name': donor.get('anonymized_name', 'Anonymous'),
                    'city': donor.get('city', 'Unknown'),
                    'country': donor.get('country', 'Unknown'),
                    'lat': coords[1],
                    'lng': coords[0],
                    'willing_to_donate': donor.get('willing_to_donate', False),
                    'registered_donor': donor.get('registered_donor', False),
                    'blood_type': donor.get('blood_type', 'Unknown')
                })
            return jsonify(out)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/hospitals')
    def get_hospitals():
        out = []
        for h in hospitals.find({}, {'_id': 0}):
            coords = h['location']['coordinates']
            out.append({
                'name': h['name'],
                'city': h['city'],
                'lat': coords[1],
                'lng': coords[0]
            })
        return jsonify(out)

    @app.route('/api/vehicles')
    def get_vehicles():
        out = []
        for v in vehicles.find({}, {'_id': 0}):
            coords = v['location']['coordinates']
            out.append({
                'type': v['type'],
                'city': v['city'],
                'lat': coords[1],
                'lng': coords[0]
            })
        return jsonify(out)

    @app.route('/api/devices')
    def get_devices():
        out = []
        for d in devices.find({}, {'_id': 0}):
            coords = d['location']['coordinates']
            out.append({
                'device_id': d['device_id'],
                'city': d['city'],
                'lat': coords[1],
                'lng': coords[0]
            })
        return jsonify(out)

    @app.route('/api/recipients')
    def get_recipients():
        out = []
        for r in recipients.find({}, {'_id': 0}):
            coords = r['location']['coordinates']
            out.append({
                'code': r['code'],
                'city': r['city'],
                'lat': coords[1],
                'lng': coords[0]
            })
        return jsonify(out)

    @app.route('/rag-demo')
    def rag_demo():
        """Render the RAG demo page"""
        return render_template('rag_demo.html')

    @app.route('/api/rag/search', methods=['POST'])
    def rag_search():
        """API endpoint for RAG search"""
        try:
            search_text = request.json.get('search_text', '')
            
            if not search_text:
                return jsonify({'error': 'Please enter text to search for'}), 400
            
            # Get embedding from Gemini
            embedding = gemini_service.get_embedding(search_text)
            
            if not embedding:
                return jsonify({'error': 'Failed to generate embedding'}), 500
            
            # Search MongoDB with the embedding
            results = mongodb_service.search_guides(embedding)
            
            # Filter by minimum score
            min_score = 0.75
            filtered_results = [r for r in results if r.get('score', 0) >= min_score]
            
            # Get summary if there are filtered results
            summary = None
            if filtered_results:
                summary = gemini_service.generate_summary(filtered_results, search_text)
            
            return jsonify({
                'results': filtered_results,
                'count': len(filtered_results),
                'query': search_text,
                'summary': summary
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/geo-advisor/search', methods=['POST'])
    def geo_advisor_search():
        """API endpoint for geospatial best practices RAG search"""
        try:
            search_text = request.json.get('search_text', '')
            if not search_text:
                return jsonify({'error': 'Please enter text to search for'}), 400
            # Get embedding from Gemini
            embedding = get_embedding(search_text)
            if not embedding:
                return jsonify({'error': 'Failed to generate embedding'}), 500
            # Vector search in geo_best_practices
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "queryVector": embedding,
                        "path": "embedding",
                        "exact": True,
                        "limit": 5
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "title": 1,
                        "content": 1,
                        "score": { "$meta": "vectorSearchScore" }
                    }
                }
            ]
            results = list(db['geo_best_practices'].aggregate(pipeline))
            min_score = 0.75
            filtered_results = [r for r in results if r.get('score', 0) >= min_score]
            summary = None
            if filtered_results:
                from ai_service import ask_gemini_with_context
                context = '\n\n'.join([f"Title: {r['title']}\nContent: {r['content']}" for r in filtered_results])
                prompt = f"Use the following geospatial best practices to answer the question. If the practices don't contain relevant information, say so.\n\nBest Practices:\n{context}\n\nQuestion: {search_text}\n\nProvide a clear, concise answer based only on the information in the best practices."
                summary = ask_gemini_with_context(prompt)
            return jsonify({
                'results': filtered_results,
                'count': len(filtered_results),
                'query': search_text,
                'summary': summary
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def generate_ai_recommendation(asset, chart_data, alerts):
    """Generate AI recommendations using Gemini AI based on asset status, alerts, and sensor data"""
    try:
        # Load the prompt template
        with open('prompt.txt', 'r') as f:
            prompt_template = f.read().strip()
        
        # Prepare comprehensive asset data for Gemini
        asset_info = {
            'name': asset.get('name', 'Unknown'),
            'type': asset.get('part_type', asset.get('type', 'Unknown')),
            'status': asset.get('status', 'operational'),
            'manufacturer': asset.get('manufacturer', 'Unknown'),
            'installation_date': asset.get('installation_date', 'Unknown'),
            'expected_lifetime_hours': asset.get('expected_lifetime_hours', 'Unknown'),
            'description': asset.get('description', 'No description available'),
            'machine_name': asset.get('machine_name', 'N/A')
        }
        
        # Calculate health score
        health_score = calculate_health_score(asset, chart_data, alerts)
        
        # Prepare sensor data summary
        sensor_summary = []
        if chart_data:
            for metric, data in chart_data.items():
                if 'values' in data and data['values']:
                    values = data['values']
                    anomalies = data.get('anomalies', [])
                    anomaly_count = sum(1 for a in anomalies if a)
                    avg_value = sum(values) / len(values) if values else 0
                    max_value = max(values) if values else 0
                    min_value = min(values) if values else 0
                    
                    sensor_summary.append({
                        'metric': metric,
                        'average': round(avg_value, 2),
                        'max': round(max_value, 2),
                        'min': round(min_value, 2),
                        'anomalies': anomaly_count,
                        'data_points': len(values)
                    })
        
        # Prepare alerts summary
        alerts_summary = []
        for alert in alerts:
            alerts_summary.append({
                'type': alert.get('type', 'Unknown'),
                'message': alert.get('message', ''),
                'severity': alert.get('severity', 'medium'),
                'timestamp': alert.get('timestamp', '')
            })
        
        # Compose the full prompt for Gemini
        asset_data_text = f"""
Asset Information:
- Name: {asset_info['name']}
- Type: {asset_info['type']}
- Status: {asset_info['status']}
- Manufacturer: {asset_info['manufacturer']}
- Installation Date: {asset_info['installation_date']}
- Expected Lifetime: {asset_info['expected_lifetime_hours']} hours
- Description: {asset_info['description']}
- Parent Machine: {asset_info['machine_name']}

Device Health Score: {health_score}%

Sensor Data Summary:
{chr(10).join([f"- {s['metric']}: Avg={s['average']}, Max={s['max']}, Min={s['min']}, Anomalies={s['anomalies']}, Data Points={s['data_points']}" for s in sensor_summary])}

Recent Alerts ({len(alerts_summary)}):
{chr(10).join([f"- [{a['timestamp']}] {a['type']} ({a['severity']}): {a['message']}" for a in alerts_summary])}

Please provide comprehensive AI recommendations for this asset based on the above data. Focus on:
1. Immediate actions needed based on status and alerts
2. Preventive maintenance recommendations
3. Performance optimization suggestions
4. Risk assessment and mitigation strategies
5. Long-term health monitoring advice
"""
        
        full_prompt = f"{prompt_template}\n\n{asset_data_text}"
        
        # Call Gemini API
        response = gemini_service.generate_summary(alerts, full_prompt)
        return response
            
    except Exception as e:
        print(f"AI recommendation error: {e}")
        return "AI recommendations temporarily unavailable. Please try again later."

def calculate_health_score(asset, chart_data, alerts):
    """Calculate device health score (0-100)"""
    score = 100
    
    # Status penalty
    status_penalty = {
        'critical': 40,
        'error': 30,
        'warning': 20,
        'maintenance': 15,
        'in_transit': 10
    }
    score -= status_penalty.get(asset.get('status', 'operational'), 0)
    
    # Alert penalty
    if alerts:
        score -= len(alerts) * 5
    
    # Anomaly penalty
    if chart_data:
        for metric, data in chart_data.items():
            if 'anomalies' in data:
                anomaly_count = sum(1 for a in data['anomalies'] if a)
                score -= anomaly_count * 2
    
    return max(0, min(100, score))
