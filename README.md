# GeoOrgan AI

**GeoOrgan AI combines geospatial intelligence, organ transport, and AI-driven insights to empower organ transportation through advanced data modeling on Google Cloud and MongoDB, enabling smarter, life-saving decisions. © 2025 GeoOrgan AI**

---

## 🌟 Why GeoOrgan AI? (Solving Real-World, High-Impact Problems)

Most developers—even experienced ones—struggle with how to model, store, and query geospatial data effectively. GeoOrgan AI was created to bridge this gap by providing:
- **A real-world, high-impact use case:** We chose organ transport logistics as our example because it is life-critical, complex, and globally relevant. This scenario demonstrates the true power and necessity of geospatial modeling.
- **Practical, actionable guidance:** By using real organ donation and transport data, we show developers exactly how to model, index, and query geospatial data in MongoDB, and how to use AI to get recommendations and best practices.
- **Boosting developer productivity worldwide:** By integrating Google Maps, MongoDB Atlas, and Google Cloud AI, we make advanced geospatial modeling accessible, understandable, and actionable for any developer, anywhere.

GeoOrgan AI is not just a demo—it's a blueprint for how to build, visualize, and optimize geospatial data models for any domain, using the best of Google Cloud and MongoDB.

---

## 🚀 Overview
GeoOrgan AI is the world's first open-source geospatial modeling and recommendation platform, purpose-built to solve complex, real-world challenges in organ transport logistics. It demonstrates how to model, visualize, and optimize geospatial data using MongoDB and Google Cloud, with Retrieval-Augmented Generation (RAG) and AI-powered recommendations.

- **Live Use Case:** Real organ donation and transport data
- **Geospatial Modeling:** Visualize, query, and optimize routes, assets, and events
- **AI Advisor:** Get actionable, context-aware recommendations for data modeling and logistics
- **Cloud-Native:** Built on Google Cloud, leverages Gemini, Deepgram, and MongoDB Atlas

---

## 🛠️ Technological Implementation
- **Google Cloud Platform:** Secure, scalable backend, Gemini LLM, and image generation
- **MongoDB Atlas:** Geospatial data storage, 2dsphere/vector indexes, and Atlas Vector Search
- **Retrieval-Augmented Generation (RAG):** Combines LLMs with real-time, domain-specific data
- **Frontend:** Flask, Bootstrap, Leaflet.js, and modern JS for real-time dashboards and maps
- **Voice & Chat AI:** Full-duplex voice assistant (Klaudia), context-aware, concise, and actionable
- **Data Pipelines:** Real-world datasets (organ donors, flights, cities, weather, etc.)
- **Best Practices Engine:** RAG-powered geospatial modeling advisor with real MongoDB schema/query examples

---

## 🎨 Design & User Experience
- **Modern, Accessible UI:** Clean, responsive dashboard with dark/light contrast (red/black theme)
- **Visualizations:** Real-time map, animated markers, asset trees, and alert panels
- **Advisor Panels:** RAG-driven, card-based recommendations for both device and geospatial modeling
- **Voice Assistant:** Natural, conversational, and always available
- **Branding:** Custom favicon, logo, and consistent GeoOrgan AI identity

---

## 🌍 Potential Impact
- **First-of-its-Kind:** The only open-source geospatial modeling advisor for developers and data teams
- **Real-World Relevance:** Tackles a life-critical use case (organ transport) but is extensible to any domain (logistics, health, smart cities, etc.)
- **Global Developer Productivity:** By providing a working, extensible example, GeoOrgan AI helps developers everywhere learn how to use MongoDB and Google Cloud for geospatial data, accelerating innovation and impact.
- **Open Source:** Designed for sharing, learning, and rapid adoption by the global developer community.

---

## 💡 Quality & Creativity
- **Unique Integration:** Combines RAG, LLMs, geospatial search, and real data in a single, developer-friendly platform
- **Actionable Guidance:** Not just visualization—provides step-by-step, context-aware modeling advice
- **Real Data, Real Impact:** Uses real organ transport data to teach and empower
- **Cloud-Native:** Seamless use of Google Cloud and MongoDB for scale and reliability

---

## 🧩 Features
- Geospatial data modeling advisor (RAG-powered)
- Real-time organ transport dashboard and map
- Voice and chat AI assistant (Klaudia)
- Asset, alert, and device management
- Animated, interactive map (Leaflet.js)
- MongoDB vector and geospatial search
- Best practices and schema recommendations
- Secure login/logout and session management
- Modular, extensible codebase

---

## 🏗️ Architecture (Text Diagram)
```
[User/Browser]
   │
   ▼
[Flask App (Python)]
   │   ├──> [MongoDB Atlas: geospatial, vector, and tabular data]
   │   ├──> [Google Gemini API: LLM, embeddings, RAG]
   │   ├──> [Deepgram API: Speech-to-text]
   │   └──> [Frontend: Bootstrap, Leaflet.js, JS]
   │
   ▼
[Advisor Panels, Map, Voice Chat, RAG Search]
```

---

## ⚡ Quickstart
1. **Clone the repo:**
   ```bash
   git clone <your-repo-url>
   cd GeoOrgan-AI
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment:**
   - Set up your Google Cloud and MongoDB Atlas credentials in `config.py`
4. **Seed the database:**
   ```bash
   python seed_guides.py
   python seed_donors_data.py
   python seed_flight_data.py
   # ... (other seed scripts as needed)
   ```
5. **Run the app:**
   ```bash
   python app.py
   ```
6. **Open in browser:**
   - Go to `http://127.0.0.1:5000` (or your server address)

---

## 🧑‍💻 How to Use & Extend
- **Ask the Advisor:** Use the Geospatial Data Advisor panel for RAG-powered best practices
- **Visualize Data:** Explore the real-time map and dashboard
- **Voice Assistant:** Click the mic to ask questions or get help
- **Extend:** Add new RAG collections, seed new data, or connect to other Google Cloud services
- **Adapt:** Use the codebase for any geospatial/AI use case (logistics, health, smart cities, etc.)

---

## 📂 Project Structure
- `app.py` — Main Flask app
- `routes.py` — All API and page routes
- `ai_service.py` — Gemini and embedding logic
- `mongo.py` — MongoDB connection and helpers
- `static/` — JS, CSS, images, favicon
- `templates/` — HTML templates
- `public-datasets/` — Real-world CSVs (organs, cities, flights, weather)
- `seed_*.py` — Data seeding scripts

---

## 📈 Example: Geospatial Modeling for Organ Transport
- **Real Data:** Uses actual organ donation and transport records
- **Modeling:** Shows how to store, index, and query geospatial data in MongoDB
- **Advisor:** RAG panel gives schema, index, and query recommendations
- **Visualization:** Map and dashboard show real-time status and analytics
- **Cloud Power:** Demonstrates ease of scaling and integrating with Google Cloud
- **Developer Guidance:** Every step is documented and visualized, so any developer can follow and learn how to build their own geospatial solution.

---

## 🏅 MongoDB Challenge & Hackathon Excellence

GeoOrgan AI is purpose-built to address the MongoDB Challenge for this hackathon, and stands out as a model solution for:

### ✅ Technological Implementation
- **Deep Google Cloud + MongoDB Integration:** Uses Gemini for LLM, embeddings, and RAG, with MongoDB Atlas for geospatial and vector search.
- **Public Datasets:** Ingests and models real-world organ transport, city, and flight data, demonstrating best practices for data modeling and analytics.
- **Advanced Search:** Implements Atlas Vector Search and 2dsphere indexes for semantic and geospatial queries.
- **Cloud-Native Pipelines:** All data flows, AI, and analytics are cloud-first, scalable, and production-ready.

### ✅ Design
- **User-Centric Dashboard:** Modern, accessible, and visually striking (red/black theme) with real-time maps, advisor panels, and voice assistant.
- **Seamless Experience:** From login to RAG-powered advice, every interaction is intuitive and actionable.
- **Branding:** Consistent, professional, and memorable identity (GeoOrgan AI).

### ✅ Potential Impact
- **Developer Empowerment:** Lowers the barrier for any developer to use advanced geospatial and AI tools with MongoDB.
- **Real-World Relevance:** Tackles a life-critical use case (organ transport) but is extensible to any domain (logistics, health, smart cities, etc.).
- **Open Source:** Designed for sharing, learning, and rapid adoption by the global developer community.

### ✅ Quality of the Idea
- **First-of-its-Kind:** The only open-source, RAG-powered geospatial modeling advisor for MongoDB.
- **Actionable Guidance:** Goes beyond visualization—delivers step-by-step, context-aware modeling and query advice.
- **Creativity:** Uses real data, AI, and cloud to solve a complex, high-impact problem in a way never seen before.

### ✅ MongoDB Challenge Alignment
- **Public Dataset:** Uses real organ donation and transport data, plus global cities and flights.
- **AI for Analysis & Generation:** Gemini LLM, RAG, and vector search power all recommendations and insights.
- **MongoDB Search & Vector Search:** All best practices, queries, and recommendations are stored, indexed, and retrieved using MongoDB Atlas' advanced features.
- **Google Integrations:** Full use of Google Cloud for AI, data, and deployment.

---

GeoOrgan AI is not just a demo—it's a blueprint for the future of geospatial, AI-driven applications on MongoDB and Google Cloud.

---

## 📜 License
© 2025 GeoOrgan AI. All rights reserved.

---

*GeoOrgan AI combines geospatial intelligence, organ transport, and AI-driven insights to empower organ transportation through advanced data modeling on Google Cloud and MongoDB, enabling smarter, life-saving decisions.* 
