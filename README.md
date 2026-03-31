# 🌱 Smart Farm AI Monitoring & Automation System

A complete AI-powered Smart Farm platform for real-time monitoring, automation, analytics, and intelligent advisory. The system integrates IoT sensors, automated irrigation, AI recommendations, and a web dashboard into a single modular architecture.

---

# 📌 Overview

The Smart Farm system collects real-time environmental and soil data from ESP32 sensor nodes, stores the information in a database, visualizes it on a web dashboard, and automatically controls actuators such as irrigation pumps. The platform also integrates an AI advisory module capable of answering farming-related questions using both online and offline models.

The system is designed to:

* Monitor environmental conditions
* Automate irrigation
* Provide AI-based farming recommendations
* Store and analyze historical data
* Work online and offline
* Be modular and easy to deploy

---

# 🏗️ System Architecture

The system consists of four main layers:

1. Sensor Layer (ESP32 nodes)
2. Backend (Flask API)
3. Database Layer (SQLite)
4. Frontend Dashboard
5. AI Advisory Layer

---

# ⚙️ Features

## 🌡️ Real-time Sensor Monitoring

The system supports multiple sensors including:

* Temperature
* Humidity
* Pressure
* Light intensity
* Rain detection
* Soil moisture
* Soil temperature
* Gas detection
* Water flow
* Tank level
* pH level
* TDS
* EC conductivity

Sensor data is:

* received via HTTP POST
* stored in SQLite database
* cached for real-time dashboard updates
* used for analytics and alerts

---

## 🚰 Automated Irrigation

The system includes:

* Manual pump control
* Scheduled irrigation
* Cyclic irrigation mode
* Manual override protection
* Background scheduler thread

The scheduler automatically:

* checks time
* verifies enabled schedules
* triggers pump
* stops pump after duration

---

## 🤖 AI Farming Advisor

The AI system uses a hybrid architecture:

Primary:

* GPT-based responses (online)

Fallback:

* TinyLlama local model (offline)

The AI can:

* Answer farming questions
* Provide irrigation advice
* Suggest crop management practices
* Use uploaded PDF knowledge

---

## 📚 RAG Document Knowledge

Users can upload agricultural PDFs. The system:

* loads PDFs
* splits text into chunks
* generates embeddings
* stores in vector database
* retrieves context for AI responses

---

## 📊 Analytics & Visualization

Historical data is:

* aggregated by hour/day/week/month
* averaged per interval
* returned as JSON
* visualized using charts

Supports:

* multi-sensor graphs
* time range selection
* value clamping (pH, moisture, etc.)

---

## ⚡ Actuator Control

Supported actuators:

* Pump
* Fan
* Light

Features:

* manual toggle
* scheduler automation
* database persistence
* override handling

---

## 🗄️ Database Storage

SQLite database stores:

* sensor readings
* actuator states
* irrigation schedules

No external DB server required.

---

# 📂 Project Structure

```
smart_farm/
│
├── app.py
├── sensors.py
├── actuators.py
├── analytics.py
├── ai.py
├── alerts.py
├── weather.py
├── pump_scheduler.py
├── state.py
├── smart_farm.db
│
├── rag/
│   ├── process_pdfs.py
│   ├── ask_ai.py
│   ├── ask_tinyllama_superprompt.py
│   └── vector_db/
│
├── data/
│
├── templates/
│
└── static/
```

---

# 💻 Requirements

## System Requirements

* Python 3.10+
* SQLite
* Git
* Internet (optional for GPT)
* Linux / Ubuntu recommended

---

# 📦 Installation

## 1. Clone Repository

```
git clone <your_repo_url>
cd smart_farm
```

## 2. Create Virtual Environment

```
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```
pip install flask flask-cors python-dotenv requests \
langchain langchain-community langchain-openai \
faiss-cpu pypdf tiktoken \
sentence-transformers \
numpy pandas \
llama-cpp-python
```

---

# 🔑 Environment Variables

Create `.env` file:

```
OPENAI_API_KEY=your_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
```

---

# 🧠 Download TinyLlama (Offline AI)

```
mkdir -p rag/models
cd rag/models
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-GGUF/resolve/main/tinyllama-1.1b-chat.Q4_K_M.gguf -O tinyllama.gguf
cd ../..
```

---

# 📄 Add Knowledge PDFs

Place PDF files inside:

```
data/
```

Then build vector database:

```
cd rag
python process_pdfs.py
cd ..
This step can also be done later from the application settings if you prefer to upload PDFs or rebuild the knowledge base after installation.
```

---

# 🗃️ Database Setup

Create database file:

```
touch smart_farm.db
```

Tables are automatically created by the system.

---

# ▶️ Running the System

```
source venv/bin/activate
python app.py
```

Open browser:

```
http://localhost:5000
```

---

# 📡 ESP32 Sensor Format

Sensors send POST request:

```
POST /sensor-data
```

JSON:

```
{
  "sensor": "ESP32_Temp",
  "value": 25.6
}
```

---

# 📊 API Endpoints

### Sensor

* `/sensor-data`
* `/latest-data`

### Actuators

* `/toggle-pump`
* `/toggle-fan`
* `/toggle-light`

### Scheduler

* `/get-pump-schedule`
* `/set-pump-schedule`
* `/delete-pump-schedule`

### Analytics

* `/analytics-data?range=day`

### AI

* `/ask-ai`
* `/retrain-ai`

---

# 🔄 Automation Logic

Scheduler thread:

* runs continuously
* checks schedule
* activates pump
* respects manual override
* updates DB

---

# 🤖 AI Logic

1. User asks question
2. System searches vector DB
3. GPT generates response
4. If offline → TinyLlama fallback

---

# 📈 Analytics Logic

* Fetch historical data
* Group by interval
* Calculate average
* Clamp values
* Return JSON

---

# 🧪 Tested Features

✔ Sensor ingestion
✔ Real-time dashboard updates
✔ Pump automation
✔ Manual override
✔ AI advisory (online)
✔ AI fallback (offline)
✔ PDF knowledge retrieval
✔ Analytics charts
✔ SQLite persistence

---

# 🚀 How Another Developer Uses It

1. Clone repo
2. Install requirements
3. Add `.env`
4. Download TinyLlama
5. Add PDFs (optional)
6. Run `python app.py`
7. Open dashboard

System works immediately.

---

# 🛠️ Technologies Used

* Flask
* SQLite
* LangChain
* FAISS
* TinyLlama
* Chart.js
* ESP32
* Python

---

# 📌 Notes

* Works offline after setup
* No cloud database required
* Lightweight deployment
* Modular design

---

# 👨‍💻 Author

Smart Farm AI SystemContext-Aware Farming
Designed for intelligent irrigation and agricultural automation.

---

