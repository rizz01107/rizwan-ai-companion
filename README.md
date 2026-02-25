# 🤖 Rizwan AI Companion
**An Intelligent Personal AI Assistant with Emotion, Mood Tracking, and WhatsApp Integration.**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Twilio](https://img.shields.io/badge/Twilio-F22F46?style=for-the-badge&logo=twilio&logoColor=white)](https://www.twilio.com/)

A sophisticated AI-driven companion designed to provide personalized interactions, analyze moods, and detect emotions using advanced NLP techniques. This project integrates a modular FastAPI backend with a clean, responsive frontend and a WhatsApp bot interface.

---

## 🌟 Key Features
* **🧠 Brain Engine:** Context-aware conversation logic with integrated short-term and long-term memory.
* **🎭 Emotion & Mood Analysis:** Real-time analysis of user input to track emotional states over time.
* **📊 Dynamic Insights:** Interactive Mood History graphs using Chart.js for personality insights.
* **🎨 AI Image Generation:** Integrated Image-Gen capabilities to turn text descriptions into art.
* **📲 WhatsApp Integration:** Seamlessly chat with your AI companion via Twilio WhatsApp API.
* **🔐 Secure Auth:** JWT-based user registration and login for personalized data management.

---

## 📂 Project Structure
```text
├── backend/
│   ├── ai_engine/      # Core AI Logic (Brain, Memory & Image Gen)
│   ├── api_routes/     # API Endpoints (Auth, Chat, WhatsApp, Stats)
│   ├── database/       # SQLAlchemy Models and DB Connection
│   └── app.py          # Main FastAPI Server Entry Point
├── frontend/
│   ├── index.html      # Main Dashboard UI
│   ├── style.css       # Modern Dark/Light Mode Styling
│   └── script.js       # API Integration & Chart.js Logic
├── requirements.txt    # Python Dependencies
└── .gitignore          # Git exclusion rules
```

---

## 🛠️ Tech Stack

* **Languages:** `Python` (Backend), `JavaScript` (Frontend), `SQL` (Database)
* **Backend:** `FastAPI` (High-performance asynchronous execution)
* **Frontend:** `HTML5`, `CSS3`, `JavaScript` (Vanilla), `Chart.js` (For Mood Visualizations)
* **Database:** `SQLite` / `PostgreSQL` (Managed via `SQLAlchemy ORM`)
* **Communication:** `Twilio Messaging API` (For WhatsApp Integration)
* **AI/ML:** `Generative AI (LLMs)`, `NLP` (Emotion & Mood Analysis)

---

## 🚀 Installation & Setup

### 1. Clone the repository
```bash
git clone [https://github.com/rizz01107/rizwan-ai-companion.git](https://github.com/rizz01107/rizwan-ai-companion.git)
cd rizwan-ai-companion
```
---
### 2. Environment Setup
```bash
python -m venv venv
# Activate on Windows:
venv\Scripts\activate
``` 
---

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
---


## 👨‍💻 About the Developer

**Muhammad Rizwan** is a dedicated **AI Enthusiast** with a deep interest in building intelligent, full-stack systems. His expertise lies in bridging the gap between complex backend architectures (FastAPI) and sophisticated AI models (LLMs/Generative AI). 

He is passionate about NLP, Emotional Intelligence in machines, and creating scalable AI solutions that feel personal and intuitive.


---

## 🔗 Connect with Developer
* **GitHub:** [rizz01107](https://github.com/rizz01107)
* **LinkedIn:** [rizz01107](https://www.linkedin.com/in/rizz01107)
* **Email:** [rizwan01107@gmail.com](mailto:rizwan01107@gmail.com)

---
 *Developed for research and development in AI-human interaction.*
---