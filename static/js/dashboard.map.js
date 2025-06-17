// Map logic for dashboard
let map;
let flightPaths = [];
let flightMarkers = [];
let planes = [];
let airlineData = [];
let cityData = [];
let organMarkers = []; // Array to store organ markers
let donorMarkers = []; // NEW: Array to store donor markers

// --- Geospatial Demo Control Refactor ---
let geoDemoMarkers = {
  donors: [],
  hospitals: [],
  vehicles: [],
  devices: [],
  recipients: [],
  organs: [],
  flights: []
};
let geoDemoActive = null; // Track which dataset is active

function initializeMap() {
    console.log('Initializing Leaflet map...');
    // Remove any existing map instance (for hot reloads)
    if (window._leaflet_map) {
        window._leaflet_map.remove();
    }
    try {
        map = L.map('map').setView([20, 0], 2); // Global view
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '©OpenStreetMap, ©CartoDB',
            maxZoom: 19
        }).addTo(map);
        window._leaflet_map = map;
        
        // Clear any existing flight paths and organ markers
        flightPaths = [];
        organMarkers = [];
        donorMarkers = []; // NEW: Clear existing donor markers
        
        // Load data from MongoDB
        loadFlightData();
        loadOrgansData(); // NEW: Load organs data
        loadDonorsData(); // NEW: Load donors data
        
        return map;
    } catch (e) {
        console.error('Map initialization failed:', e);
        // Try fallback simple map
        return initializeSimpleMap();
    }
}

function loadFlightData() {
    console.log('Loading flight data from MongoDB...');
    
    fetch('/api/flight-routes')
        .then(response => {
            console.log('Airlines API response status:', response.status);
            return response.json();
        })
        .then(routes => {
            console.log('Loaded', routes.length, 'flight routes from database:', routes);
            
            if (routes.length === 0) {
                console.warn('No flight routes found in database');
                return;
            }
            
            // Clear existing flight paths and markers
            flightPaths.forEach(path => map.removeLayer(path));
            flightMarkers.forEach(marker => map.removeLayer(marker));
            flightPaths = [];
            flightMarkers = [];
            
            // Create flight paths
            createAirlineFlightPaths(routes);
            
            console.log(`✅ Successfully created ${flightPaths.length} flight paths`);
        })
        .catch(error => {
            console.error('Error loading flight data:', error);
        });
}

function createAirlineFlightPaths(routes) {
    console.log('Creating airline flight paths from database...');
    
    if (!routes || routes.length === 0) {
        console.warn('No flight routes found in database');
        return;
    }
    
    console.log(`Creating flights for ${routes.length} routes...`);
    
    routes.forEach((route, index) => {
        console.log(`Creating flight for ${route.airline_name}: ${route.start_city} to ${route.end_city}`);
        
        // Use lat/lng directly from the route data
        const startLat = route.start_lat;
        const startLng = route.start_lng;
        const endLat = route.end_lat;
        const endLng = route.end_lng;
        
        if (!startLat || !startLng || !endLat || !endLng) {
            console.warn('Missing coordinates for route:', route);
            return;
        }
        
        const startCity = {
            name: route.start_city,
            lat: startLat,
            lng: startLng
        };
        
        const endCity = {
            name: route.end_city,
            lat: endLat,
            lng: endLng
        };
        
        console.log(`Flight route: ${startCity.name} (${startLat}, ${startLng}) to ${endCity.name} (${endLat}, ${endLng})`);
        
        // Create airline icon
        const airlineIcon = L.divIcon({
            html: `<div style="font-size: 20px; color: ${route.airline_color || '#007cba'};">${route.airline_icon || '✈️'}</div>`,
            className: 'airline-marker',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
        
        // Create flight path using the same curved path as animation
        const curvedPathCoords = createCurvedPath(startCity, endCity);
        const flightPath = L.polyline(curvedPathCoords, {
            color: route.airline_color || '#007cba',
            weight: 2,
            opacity: 0.8,
            dashArray: '10, 5'
        }).addTo(map);
        
        // Create animated plane marker
        const planeMarker = L.marker([startCity.lat, startCity.lng], { icon: airlineIcon }).addTo(map);
        
        // Create popup for flight
        const popupContent = `
            <div class="flight-popup">
                <h4 style="color: ${route.airline_color || '#007cba'}; margin: 0 0 8px 0;">${route.airline_icon || '✈️'} ${route.airline_name}</h4>
                <p><strong>Route:</strong> ${route.start_city} → ${route.end_city}</p>
                <p><strong>Flight Code:</strong> ${route.airline_code || 'N/A'}</p>
                <p><strong>Distance:</strong> ${calculateDistance(startCity.lat, startCity.lng, endCity.lat, endCity.lng).toFixed(0)} km</p>
            </div>
        `;
        
        planeMarker.bindPopup(popupContent);
        
        // Create flight object for animation
        const flightObject = {
            id: index,
            path: flightPath,
            plane: planeMarker,
            airline: {
                name: route.airline_name,
                color: route.airline_color || '#007cba',
                icon: route.airline_icon || '✈️'
            },
            startCity: startCity,
            endCity: endCity,
            pathCoords: curvedPathCoords,
            currentIndex: 0,
            totalPoints: curvedPathCoords.length,
            speed: 0.5 // Faster speed for better visibility
        };
        
        console.log(`Created flight object for ${route.airline_name}:`);
        console.log(`  - Path points: ${flightObject.pathCoords.length}`);
        console.log(`  - Speed: ${flightObject.speed}`);
        console.log(`  - Route: ${startCity.name} to ${endCity.name}`);
        
        // Animate the plane along the route
        animateFlightPath(flightObject);
        
        // Store references
        flightPaths.push(flightObject);
        flightMarkers.push(planeMarker);
        
        console.log(`✅ Created flight path for ${route.airline_name}: ${route.start_city} to ${route.end_city}`);
    });
}

function createFlightPath(airline, startCity, endCity, flightId, speed) {
    try {
        // Create a curved flight path
        const path = createCurvedPath(startCity, endCity);
        
        if (!path || path.length === 0) {
            console.warn('Failed to create flight path for', airline.name);
            return;
        }
        
        // Create the flight path line
        const flightPath = L.polyline(path, {
            color: airline.color,
            weight: 2,
            opacity: 0.6,
            dashArray: '5, 10'
        }).addTo(map);
        
        // Create the plane marker with airline data
        const planeIcon = L.divIcon({
            html: `<div style="font-size: 20px; transform: rotate(${calculateBearing(startCity, endCity)}deg); color: ${airline.color};">${airline.icon}</div>`,
            className: 'plane-marker',
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });
        
        const plane = L.marker(path[0], { icon: planeIcon }).addTo(map);
        
        // Add airline data to plane element
        const planeElement = plane.getElement();
        if (planeElement) {
            planeElement.setAttribute('data-airline', airline.name.toLowerCase().replace(/\s+/g, ''));
            planeElement.setAttribute('title', `${airline.name} - ${startCity.name} to ${endCity.name}`);
        }
        
        // Store flight data with speed from database
        flightPaths.push({
            id: flightId,
            path: flightPath,
            plane: plane,
            airline: airline,
            startCity: startCity,
            endCity: endCity,
            pathCoords: path,
            currentIndex: 0,
            totalPoints: path.length,
            speed: speed || 0.2 // Use speed from database or default
        });
        
        console.log(`Created flight path for ${airline.name}: ${startCity.name} to ${endCity.name} with speed ${speed}`);
    } catch (error) {
        console.error('Error creating flight path:', error);
    }
}

function createCurvedPath(start, end) {
    try {
        const path = [];
        const steps = 150; // More points for smoother slow animation
        
        for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            
            // Create a curved path using quadratic Bezier with consistent curves
            const midLat = (start.lat + end.lat) / 2 + (Math.random() - 0.5) * 6;
            const midLng = (start.lng + end.lng) / 2 + (Math.random() - 0.5) * 6;
            
            const lat = (1 - t) * (1 - t) * start.lat + 2 * (1 - t) * t * midLat + t * t * end.lat;
            const lng = (1 - t) * (1 - t) * start.lng + 2 * (1 - t) * t * midLng + t * t * end.lng;
            
            // Validate coordinates and ensure they're within reasonable bounds
            if (isNaN(lat) || isNaN(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
                console.warn('Invalid coordinates generated, using direct path');
                // Fallback to direct path if curved path fails
                const directLat = start.lat + (end.lat - start.lat) * t;
                const directLng = start.lng + (end.lng - start.lng) * t;
                path.push([directLat, directLng]);
            } else {
                path.push([lat, lng]);
            }
        }
        
        if (path.length === 0) {
            console.warn('No valid path points generated, creating direct path');
            // Create a simple direct path as fallback
            for (let i = 0; i <= steps; i++) {
                const t = i / steps;
                const lat = start.lat + (end.lat - start.lat) * t;
                const lng = start.lng + (end.lng - start.lng) * t;
                path.push([lat, lng]);
            }
        }
        
        return path;
    } catch (error) {
        console.error('Error creating curved path:', error);
        // Return direct path as fallback
        const path = [];
        const steps = 50;
        for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            const lat = start.lat + (end.lat - start.lat) * t;
            const lng = start.lng + (end.lng - start.lng) * t;
            path.push([lat, lng]);
        }
        return path;
    }
}

function calculateBearing(start, end) {
    const lat1 = start.lat * Math.PI / 180;
    const lat2 = end.lat * Math.PI / 180;
    const lng1 = start.lng * Math.PI / 180;
    const lng2 = end.lng * Math.PI / 180;
    
    const y = Math.sin(lng2 - lng1) * Math.cos(lat2);
    const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(lng2 - lng1);
    
    return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
}

function animateFlights() {
    flightPaths.forEach(flight => {
        animateFlightPath(flight);
    });
}

function animateFlightPath(flight) {
    console.log(`Starting animation for ${flight.airline.name}: ${flight.startCity.name} to ${flight.endCity.name}`);
    console.log(`Path has ${flight.pathCoords.length} points, speed: ${flight.speed}`);
    
    const animate = () => {
        try {
            if (!flight || !flight.pathCoords || flight.pathCoords.length === 0) {
                console.warn('Invalid flight data, skipping animation');
                return;
            }
            
            // Move forward along the path
            flight.currentIndex += flight.speed;
            
            // When reaching the end, reset to start for continuous loop
            if (flight.currentIndex >= flight.totalPoints - 1) {
                flight.currentIndex = 0; // Reset to start for continuous loop
                console.log(`Flight ${flight.airline.name} completed route, restarting...`);
            }
            
            const currentIndex = Math.floor(flight.currentIndex);
            if (currentIndex >= 0 && currentIndex < flight.pathCoords.length) {
                const currentPos = flight.pathCoords[currentIndex];
                flight.plane.setLatLng(currentPos);
                
                // Calculate direction to next point for proper plane rotation
                const nextIndex = Math.min(currentIndex + 1, flight.totalPoints - 1);
                if (nextIndex < flight.pathCoords.length) {
                    const nextPos = flight.pathCoords[nextIndex];
                    const bearing = calculateBearing(
                        { lat: currentPos[0], lng: currentPos[1] },
                        { lat: nextPos[0], lng: nextPos[1] }
                    );
                    
                    // Update plane rotation to follow path direction
                    const planeElement = flight.plane.getElement();
                    if (planeElement) {
                        const planeDiv = planeElement.querySelector('div');
                        if (planeDiv) {
                            planeDiv.style.transform = `rotate(${bearing}deg)`;
                            // Add subtle glow effect
                            planeDiv.style.textShadow = `0 0 15px ${flight.airline.color}`;
                        }
                    }
                }
            }
            
            // Continue animation with faster speed for better visibility
            setTimeout(animate, 100); // 100ms delay for smoother movement
        } catch (error) {
            console.error('Error in flight animation:', error);
            // Continue animation even if there's an error
            setTimeout(animate, 100);
        }
    };
    
    animate();
}

function plotOrgansOnMap(map, organs) {
    if (!map) return;
    organs.forEach(organ => {
        const locationCoords = getLocationCoords(organ.location);
        if (locationCoords) {
            const planeIcon = L.icon({
                iconUrl: 'https://cdn-icons-png.flaticon.com/512/684/684908.png',
                iconSize: [32, 32],
                iconAnchor: [16, 16],
                popupAnchor: [0, -16]
            });
            const marker = L.marker(locationCoords, {icon: planeIcon}).addTo(map);
            marker.bindPopup(`<b>${organ.text ? organ.text.replace(/<[^>]+>/g, '') : organ.name}</b><br>Status: ${organ.status}`);
        }
    });
}

function getLocationCoords(location) {
    const map = {
        'Mumbai Airport': [19.0896, 72.8656],
        'Delhi Airport': [28.5562, 77.1000],
        'Chennai Airport': [12.9941, 80.1709],
        'Bangalore Airport': [13.1986, 77.7066],
        'Hyderabad Airport': [17.2403, 78.4294],
        'Kolkata Airport': [22.6547, 88.4467],
        'Ahmedabad Airport': [23.0732, 72.6347],
        'Pune Airport': [18.5822, 73.9197],
        'Goa Airport': [15.3800, 73.8317],
        'Lucknow Airport': [26.7606, 80.8893],
        'Jaipur Airport': [26.8242, 75.8122],
        'Cochin Airport': [10.1520, 76.4019],
        'Trivandrum Airport': [8.4821, 76.9201],
        'Nagpur Airport': [21.0922, 79.0472],
        'Indore Airport': [22.7216, 75.8011]
    };
    return map[location] || null;
}

// Initialize map when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for the DOM to be fully ready
    setTimeout(() => {
        const mapDiv = document.getElementById('map');
        if (mapDiv) {
            initializeMap();
        } else {
            console.error('Map div not found');
        }
    }, 100);
});

// Fallback map initialization
function initializeSimpleMap() {
    try {
        console.log('Initializing simple map...');
        map = L.map('map').setView([20, 0], 2); // Global view
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '©OpenStreetMap, ©CartoDB',
            maxZoom: 19
        }).addTo(map);
        window._leaflet_map = map;
        console.log('Simple map initialized successfully');
        return map;
    } catch (e) {
        console.error('Simple map initialization failed:', e);
        return null;
    }
}

// Export for global access
window.initializeMap = initializeMap;
window.plotOrgansOnMap = plotOrgansOnMap;

function loadOrgansData() {
    console.log('Loading organs data from MongoDB...');
    
    fetch('/api/organs')
        .then(response => {
            console.log('Organs API response status:', response.status);
            return response.json();
        })
        .then(organs => {
            console.log('Loaded', organs.length, 'organs from database:', organs);
            
            if (organs.length === 0) {
                console.warn('No organs found in database');
                return;
            }
            
            // Clear existing organ markers
            organMarkers.forEach(marker => map.removeLayer(marker));
            organMarkers = [];
            
            // Create markers for each organ
            organs.forEach(organ => {
                createOrganMarker(organ);
            });
            
            console.log(`✅ Successfully created ${organMarkers.length} organ markers`);
        })
        .catch(error => {
            console.error('Error loading organs data:', error);
        });
}

function createOrganMarker(organ) {
    try {
        // Define organ emojis and colors based on organ type
        const organEmojis = {
            'Heart': '❤️',
            'Liver': '🫁',
            'Kidney': '🫘',
            'Lung': '🫁',
            'Pancreas': '🫀'
        };
        
        const organColors = {
            'Heart': '#e74c3c',
            'Liver': '#f39c12',
            'Kidney': '#9b59b6',
            'Lung': '#3498db',
            'Pancreas': '#e67e22'
        };
        
        // Get organ emoji and color
        const organEmoji = organEmojis[organ.organ_type] || '🫀';
        const organColor = organColors[organ.organ_type] || '#95a5a6';
        
        // Use lat/lng directly from the organ data
        const lat = organ.lat;
        const lng = organ.lng;
        
        if (!lat || !lng) {
            console.warn('Missing coordinates for organ:', organ);
            return;
        }
        
        console.log(`Creating organ marker for ${organ.organ_type} at ${lat}, ${lng}`);
        
        // Create custom icon for organ
        const organIcon = L.divIcon({
            html: `<div style="font-size: 24px; color: ${organColor};">${organEmoji}</div>`,
            className: 'organ-marker',
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });
        
        // Create marker
        const marker = L.marker([lat, lng], { icon: organIcon }).addTo(map);
        
        // Create popup content
        const popupContent = `
            <div class="organ-popup">
                <h4 style="color: ${organColor}; margin: 0 0 8px 0;">${organEmoji} ${organ.organ_type}</h4>
                <p><strong>Status:</strong> <span style="color: ${organ.status === 'Available' ? '#28a745' : organ.status === 'In Transit' ? '#ffc107' : '#dc3545'}">${organ.status}</span></p>
                <p><strong>Location:</strong> ${organ.city}, ${organ.country || 'Unknown'}</p>
                <p><strong>Last Updated:</strong> ${new Date(organ.last_updated).toLocaleString()}</p>
                ${organ.flight_id ? `<p><strong>Flight ID:</strong> ${organ.flight_id}</p>` : ''}
            </div>
        `;
        
        marker.bindPopup(popupContent);
        
        // Store marker reference
        organMarkers.push(marker);
        
        console.log(`✅ Created organ marker for ${organ.organ_type} at ${lat}, ${lng}`);
        
    } catch (error) {
        console.error('Error creating organ marker:', error, organ);
    }
}

function getStatusColor(status) {
    const colors = {
        'available': '#28a745',
        'in_transit': '#ffc107',
        'reserved': '#17a2b8',
        'delivered': '#6c757d'
    };
    return colors[status] || '#6c757d';
}

function loadOrgansNearLocation(lng, lat, distance) {
    console.log(`Loading organs within ${distance}km of (${lng}, ${lat})...`);
    
    fetch(`/api/organs/near/${lng}/${lat}/${distance}`)
        .then(response => response.json())
        .then(data => {
            console.log(`Found ${data.length} organs nearby:`, data);
            
            // Clear existing organ markers
            organMarkers.forEach(marker => {
                if (map && marker) {
                    map.removeLayer(marker);
                }
            });
            organMarkers = [];
            
            // Create markers for nearby organs
            data.forEach(organ => {
                createOrganMarker(organ);
            });
            
            // Center map on the search location
            map.setView([lat, lng], 6);
        })
        .catch(error => {
            console.error('Error loading nearby organs:', error);
        });
}

function loadOrgansByStatus(status) {
    console.log(`Loading organs with status: ${status}...`);
    
    fetch(`/api/organs/status/${status}`)
        .then(response => response.json())
        .then(data => {
            console.log(`Found ${data.length} organs with status ${status}:`, data);
            
            // Clear existing organ markers
            organMarkers.forEach(marker => {
                if (map && marker) {
                    map.removeLayer(marker);
                }
            });
            organMarkers = [];
            
            // Create markers for organs with this status
            data.forEach(organ => {
                createOrganMarker(organ);
            });
        })
        .catch(error => {
            console.error('Error loading organs by status:', error);
        });
}

// Calculate distance between two points in kilometers
function calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Animate flight along a route
function animateFlight(planeMarker, startCity, endCity, color) {
    const duration = 30000; // 30 seconds
    const steps = 100;
    const stepDuration = duration / steps;
    
    let currentStep = 0;
    
    const animate = () => {
        if (currentStep >= steps) {
            // Reset to start for continuous animation
            currentStep = 0;
            planeMarker.setLatLng([startCity.lat, startCity.lng]);
        }
        
        const progress = currentStep / steps;
        const lat = startCity.lat + (endCity.lat - startCity.lat) * progress;
        const lng = startCity.lng + (endCity.lng - startCity.lng) * progress;
        
        planeMarker.setLatLng([lat, lng]);
        currentStep++;
        
        setTimeout(animate, stepDuration);
    };
    
    animate();
}

// NEW: Function to load donors data
function loadDonorsData() {
    console.log('DEBUG: loadDonorsData() called.'); // NEW: Early debug log
    console.log('Loading donors data from MongoDB...');
    
    fetch('/api/donors')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(donors => {
            console.log('Loaded', donors.length, 'donors:', donors);
            // Clear existing donor markers
            donorMarkers.forEach(marker => map.removeLayer(marker));
            donorMarkers = [];
            
            donors.forEach(donor => {
                const marker = createDonorMarker(donor);
                if (marker) {
                    donorMarkers.push(marker);
                    console.log(`DEBUG: Added donor marker for ${donor.anonymized_name} at [${donor.lat}, ${donor.lng}]`);
                }
            });
            console.log(`✅ Successfully plotted ${donorMarkers.length} donor markers.`);
        })
        .catch(error => {
            console.error('Error loading donor data:', error);
        });
}

// NEW: Function to create donor marker
function createDonorMarker(donor) {
    // Directly use lat and lng from the donor object, which are provided by the API
    const lat = donor.lat;
    const lng = donor.lng;

    if (isNaN(lat) || isNaN(lng)) {
        console.warn('Invalid coordinates for donor:', donor);
        return null;
    }

    console.log(`DEBUG: Creating marker for donor ${donor.anonymized_name} at [${lat}, ${lng}]`);
    
    // Create a simple circle marker instead of divIcon
    const marker = L.circleMarker([lat, lng], {
        radius: 8,
        fillColor: '#00bcd4',
        color: '#fff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
    }).addTo(map);

    // Add pulsing animation
    marker.setStyle({
        className: 'donor-marker-pulse'
    });

    const popupContent = `
        <div class="donor-popup">
            <h5>${donor.anonymized_name}</h5>
            <p><strong>City:</strong> ${donor.city}, ${donor.country}</p>
            <p><strong>Willing to Donate:</strong> ${donor.willing_to_donate ? 'Yes' : 'No'}</p>
            ${donor.registered_donor ? '<p><strong>Registered:</strong> Yes</p>' : ''}
            ${donor.blood_type ? `<p><strong>Blood Type:</strong> ${donor.blood_type}</p>` : ''}
            <p class="future-focus-note">Future focus: Potential donor</p>
        </div>
    `;

    marker.bindPopup(popupContent);
    console.log(`DEBUG: Marker created and added to map for ${donor.anonymized_name}`);

    return marker;
}

// --- GEO DEMO CONTROL ---
function addGeospatialDemoControl() {
    if (document.getElementById('geo-demo-control')) return;
    const control = document.createElement('div');
    control.id = 'geo-demo-control';
    control.style.position = 'absolute';
    control.style.top = '16px';
    control.style.right = '16px';
    control.style.zIndex = 2000;
    control.style.background = 'rgba(30,30,40,0.95)';
    control.style.borderRadius = '8px';
    control.style.boxShadow = '0 2px 8px #0008';
    control.style.padding = '12px 10px 10px 10px';
    control.style.display = 'flex';
    control.style.flexDirection = 'column';
    control.style.gap = '8px';
    control.innerHTML = `
      <b style="color:#fff;font-size:15px;margin-bottom:4px;">Geospatial Demo</b>
      <button id="geo-all-donors" style="margin:0 0 2px 0;">All Donors</button>
      <button id="geo-near-london" style="margin:0 0 2px 0;">Near London</button>
      <button id="geo-within-europe" style="margin:0 0 2px 0;">Within Europe</button>
      <button id="geo-intersect-line" style="margin:0 0 2px 0;">Intersect Paris–Berlin</button>
    `;
    document.body.appendChild(control);
    document.getElementById('geo-all-donors').onclick = showAllDonors;
    document.getElementById('geo-near-london').onclick = showDonorsNearLondon;
    document.getElementById('geo-within-europe').onclick = showDonorsWithinEurope;
    document.getElementById('geo-intersect-line').onclick = showDonorsIntersectLine;
}

function clearDonorMarkers() {
    donorMarkers.forEach(m => map.removeLayer(m));
    donorMarkers = [];
}

function showAllDonors() {
    clearAllGeoDemoMarkers();
    fetch('/api/donors')
      .then(r => r.json())
      .then(donors => {
        donors.forEach(d => {
          const m = createDonorMarker(d, '#2196f3');
          if (m) geoDemoMarkers.donors.push(m);
        });
      });
}

function showDonorsNearLondon() {
    clearAllGeoDemoMarkers();
    fetch('/api/donors/near?lat=51.5074&lng=-0.1278&distance_km=500')
      .then(r => r.json())
      .then(donors => {
        donors.forEach(d => {
          const m = createDonorMarker(d, '#43a047');
          if (m) geoDemoMarkers.donors.push(m);
        });
        if (donors.length) map.setView([51.5074, -0.1278], 5);
      });
}

function showDonorsWithinEurope() {
    clearAllGeoDemoMarkers();
    const poly = {
      type: 'Polygon',
      coordinates: [[
        [-10, 35], [40, 35], [40, 60], [-10, 60], [-10, 35]
      ]]
    };
    fetch('/api/donors/within', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({polygon: poly})
    })
      .then(r => r.json())
      .then(donors => {
        donors.forEach(d => {
          const m = createDonorMarker(d, '#ff9800');
          if (m) geoDemoMarkers.donors.push(m);
        });
        if (donors.length) map.setView([50, 15], 4);
      });
}

function showDonorsIntersectLine() {
    clearAllGeoDemoMarkers();
    const line = {
      type: 'LineString',
      coordinates: [
        [2.3522, 48.8566],   // Paris
        [13.4050, 52.5200]   // Berlin
      ]
    };
    fetch('/api/donors/intersects', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({geometry: line})
    })
      .then(r => r.json())
      .then(donors => {
        donors.forEach(d => {
          const m = createDonorMarker(d, '#9c27b0');
          if (m) geoDemoMarkers.donors.push(m);
        });
        if (donors.length) map.setView([50, 10], 5);
      });
}

function showHospitals() {
    clearAllGeoDemoMarkers();
    fetch('/api/hospitals')
      .then(r => r.json())
      .then(hospitals => {
        hospitals.forEach(h => {
          const marker = L.marker([h.lat, h.lng], {
            icon: L.divIcon({html: '🏥', className: '', iconSize: [24,24]})
          }).addTo(map);
          marker.bindPopup(`<b>${h.name}</b><br>${h.city}`);
          geoDemoMarkers.hospitals.push(marker);
        });
      });
}

function showVehicles() {
    clearAllGeoDemoMarkers();
    fetch('/api/vehicles')
      .then(r => r.json())
      .then(vehicles => {
        vehicles.forEach(v => {
          const icon = v.type === 'Ambulance' ? '🚑' : v.type === 'Drone' ? '🚁' : '🚓';
          const marker = L.marker([v.lat, v.lng], {
            icon: L.divIcon({html: icon, className: '', iconSize: [24,24]})
          }).addTo(map);
          marker.bindPopup(`<b>${v.type}</b><br>${v.city}`);
          geoDemoMarkers.vehicles.push(marker);
        });
      });
}

function showDevices() {
    clearAllGeoDemoMarkers();
    fetch('/api/devices')
      .then(r => r.json())
      .then(devices => {
        devices.forEach(d => {
          const marker = L.marker([d.lat, d.lng], {
            icon: L.divIcon({html: '💉', className: '', iconSize: [24,24]})
          }).addTo(map);
          marker.bindPopup(`<b>Device ${d.device_id}</b><br>${d.city}`);
          geoDemoMarkers.devices.push(marker);
        });
      });
}

function showRecipients() {
    clearAllGeoDemoMarkers();
    fetch('/api/recipients')
      .then(r => r.json())
      .then(recipients => {
        recipients.forEach(r => {
          const marker = L.marker([r.lat, r.lng], {
            icon: L.divIcon({html: '🧑‍⚕️', className: '', iconSize: [24,24]})
          }).addTo(map);
          marker.bindPopup(`<b>Recipient ${r.code}</b><br>${r.city}`);
          geoDemoMarkers.recipients.push(marker);
        });
      });
}

function showOrgans() {
    clearAllGeoDemoMarkers();
    fetch('/api/organs')
      .then(r => r.json())
      .then(organs => {
        organs.forEach(o => {
          const marker = L.marker([o.lat, o.lng], {
            icon: L.divIcon({html: '🫀', className: '', iconSize: [24,24]})
          }).addTo(map);
          marker.bindPopup(`<b>${o.organ_type}</b><br>${o.city}`);
          geoDemoMarkers.organs.push(marker);
        });
      });
}

function showFlights() {
    clearAllGeoDemoMarkers();
    fetch('/api/flight-routes')
      .then(r => r.json())
      .then(routes => {
        routes.forEach(route => {
          const marker = L.marker([route.start_lat, route.start_lng], {
            icon: L.divIcon({html: '✈️', className: '', iconSize: [24,24]})
          }).addTo(map);
          marker.bindPopup(`<b>${route.airline_name}</b><br>${route.start_city} → ${route.end_city}`);
          geoDemoMarkers.flights.push(marker);
        });
      });
}

function clearAllGeoDemoMarkers() {
  Object.values(geoDemoMarkers).forEach(arr => arr.forEach(m => map.removeLayer(m)));
  Object.keys(geoDemoMarkers).forEach(k => geoDemoMarkers[k] = []);
}

// Call the control after map is initialized
const _origInitMap = initializeMap;
initializeMap = function() {
    const m = _origInitMap();
    setTimeout(addGeospatialDemoControl, 1000);
    return m;
};

// Add new dataset buttons to the geospatial demo control
const _origAddGeoDemo = addGeospatialDemoControl;
addGeospatialDemoControl = function() {
    if (document.getElementById('geo-demo-control')) return;
    _origAddGeoDemo();
    const control = document.getElementById('geo-demo-control');
    if (!control) return;
    control.innerHTML += `
      <button id="geo-organs">Show Organs</button>
      <button id="geo-flights">Show Flights</button>
      <button id="geo-hospitals">Show Hospitals</button>
      <button id="geo-vehicles">Show Vehicles</button>
      <button id="geo-devices">Show Devices</button>
      <button id="geo-recipients">Show Recipients</button>
    `;
    document.getElementById('geo-all-donors').onclick = () => toggleGeoDemo('donors', showAllDonors);
    document.getElementById('geo-near-london').onclick = () => toggleGeoDemo('donors', showDonorsNearLondon);
    document.getElementById('geo-within-europe').onclick = () => toggleGeoDemo('donors', showDonorsWithinEurope);
    document.getElementById('geo-intersect-line').onclick = () => toggleGeoDemo('donors', showDonorsIntersectLine);
    document.getElementById('geo-organs').onclick = () => toggleGeoDemo('organs', showOrgans);
    document.getElementById('geo-flights').onclick = () => toggleGeoDemo('flights', showFlights);
    document.getElementById('geo-hospitals').onclick = () => toggleGeoDemo('hospitals', showHospitals);
    document.getElementById('geo-vehicles').onclick = () => toggleGeoDemo('vehicles', showVehicles);
    document.getElementById('geo-devices').onclick = () => toggleGeoDemo('devices', showDevices);
    document.getElementById('geo-recipients').onclick = () => toggleGeoDemo('recipients', showRecipients);
    // Make draggable
    control.style.right = '16px';
    control.style.left = 'auto';
    control.style.top = '16px';
    makeElementDraggable(control);
};

function makeElementDraggable(el) {
  let isDragging = false, startX, startY, startLeft, startTop;
  el.style.cursor = 'move';
  el.addEventListener('mousedown', function(e) {
    if (e.target.tagName === 'BUTTON') return; // Don't drag on button click
    isDragging = true;
    const rect = el.getBoundingClientRect();
    startX = e.clientX;
    startY = e.clientY;
    startLeft = rect.left;
    startTop = rect.top;
    el.style.left = rect.left + 'px';
    el.style.top = rect.top + 'px';
    el.style.right = 'auto';
    el.style.bottom = 'auto';
    document.body.style.userSelect = 'none';
  });
  document.addEventListener('mousemove', function(e) {
    if (!isDragging) return;
    let dx = e.clientX - startX;
    let dy = e.clientY - startY;
    el.style.left = (startLeft + dx) + 'px';
    el.style.top = (startTop + dy) + 'px';
    el.style.right = 'auto';
    el.style.bottom = 'auto';
  });
  document.addEventListener('mouseup', function() {
    isDragging = false;
    document.body.style.userSelect = '';
  });
}

function toggleGeoDemo(dataset, showFn) {
  if (geoDemoActive === dataset) {
    clearAllGeoDemoMarkers();
    geoDemoActive = null;
    return;
  }
  clearAllGeoDemoMarkers();
  geoDemoActive = dataset;
  showFn();
}
