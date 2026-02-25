# 🤖 Rizwan AI Companion
**An Intelligent Personal AI Assistant with Emotion, Mood Tracking, and WhatsApp Integration.**

![AI Engine](https://img.shields.io/badge/AI-Generative--AI-blueviolet)
![Mood Tracking](https://img.shields.io/badge/Mood-Tracking-orange)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Twilio](https://img.shields.io/badge/Twilio-F22F46?style=for-the-badge&logo=twilio&logoColor=white)](https://www.twilio.com/)

---

A sophisticated AI-driven companion designed to provide personalized interactions, analyze moods, and detect emotions using advanced NLP techniques. This project integrates a modular FastAPI backend with a clean, responsive frontend and a WhatsApp bot interface.
---

## 🌟 Key Features

* **🧠 Brain Engine:** Context-aware conversation logic with integrated short-term and long-term memory.
* **🌍 Universal Language Support:** Capable of understanding and responding in almost any global language, including **English, Urdu, Roman Urdu, Arabic, Spanish, and many more**.
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

## 🧠 How It Works (AI Logic)

The **Rizwan AI Companion** uses a sophisticated pipeline to ensure human-like interactions:

* **Natural Language Processing (NLP):** Every user message is analyzed using `TextBlob` and custom logic to determine sentiment (Positive, Neutral, Negative) and detect specific emotional triggers.
* **Contextual Memory:** To maintain a natural flow, the system implements a **Sliding-Window Memory**. It remembers the last few exchanges to provide context-aware responses without overloading the AI's token limit.
* **High-Speed Reasoning:** The "Brain" is powered by **Groq / Google Gemini API**, allowing for near-instantaneous response generation with high reasoning capabilities.

---

## 🗺️ Future Roadmap

I am continuously working to improve this companion. Upcoming features include:

- [ ] **Voice-to-Text & Text-to-Voice:** Enabling real-time voice conversations via WhatsApp.
- [ ] **Multilingual Support:** Enhancing NLP capabilities to support **Urdu** and Roman Urdu natively.
- [ ] **Cloud Deployment:** Moving from local hosting to a scalable cloud architecture (AWS or Azure).
- [ ] **Advanced Analytics:** More detailed personality reports based on weekly mood trends.

---


## 🚀 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/rizz01107/rizwan-ai-companion.git
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

## 🔑 Environment Variables

To run this project, you will need to create a `.env` file in the root directory and add the following variables:

| Variable | Description |
| :--- | :--- |
| `GROQ_API_KEY` | Your API key for Groq LLM |
| `GOOGLE_API_KEY` | Your Google Gemini API key |
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token |
| `DATABASE_URL` | SQLite connection string (e.g., `sqlite+aiosqlite:///./rizwan_ai.db`) |

---

## ⚡ Performance Optimization

- **Asynchronous Processing:** This project leverages `FastAPI`'s `async/await` syntax for non-blocking database operations and API calls, ensuring high performance even under multiple concurrent requests.
- **SQLAlchemy 2.0:** Utilizes the latest ORM features for efficient database querying and management.

---

## 🚀 Running the Project

### **A. Start the Backend Server**
To launch the FastAPI server, run the following command in your terminal:

```bash
python -m backend.app
```

---

### **B. Start the Frontend**
* Open `frontend/index.html` using the **VS Code Live Server** extension or simply open the file in any modern web browser.
* Ensure that the `API_BASE_URL` in your `script.js` matches your running backend (default: `http://127.0.0.1:8000`).

---

### **C. Setup WhatsApp Integration (via ngrok)**
To test the WhatsApp bot on your local machine, you must expose your local server to the internet:

1. **Launch ngrok:**
   ```bash
   # Use ./ if ngrok is in your current directory
   ./ngrok http 8000
    ```

    ---

2. **Configure Twilio Sandbox:**
   * Copy the **Forwarding URL** provided by ngrok (e.g., `https://xxxx.ngrok-free.app`).
   * Go to the **Twilio Console > Messaging > Settings > WhatsApp Sandbox Settings**.
   * Paste the URL in the **"When a message comes in"** field and append the endpoint:
     `https://your-ngrok-url.ngrok-free.app/whatsapp/message`
   * Ensure the request method is set to **HTTP POST** and click **Save**.

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