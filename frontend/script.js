const API_BASE_URL = "http://127.0.0.1:8000";
let isLoginMode = true;
let moodChart = null;

// DOM Elements
const authSection = document.getElementById('auth-section');
const chatSection = document.getElementById('chat-section');
const authBtn = document.getElementById('auth-btn');
const tabLogin = document.getElementById('tab-login');
const tabRegister = document.getElementById('tab-register');
const usernameInput = document.getElementById('username');
const usernameContainer = document.getElementById('username-container');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const authMsg = document.getElementById('auth-msg');
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const micBtn = document.getElementById('mic-btn');
const statsBtn = document.getElementById('stats-btn');
const moodChartContainer = document.getElementById('mood-chart-container');
const displayName = document.getElementById('display-name');
const logoutBtn = document.getElementById('logout-btn');
const typingIndicator = document.getElementById('typing');

// --- 1. UI Logic ---
function switchToChat(name) {
    if (authSection) authSection.classList.add('hidden');
    if (chatSection) chatSection.classList.remove('hidden');
    if (displayName) displayName.innerText = name;
    scrollChat();
}

// --- 2. Auth Logic ---
async function handleAuth(e) {
    if (e) e.preventDefault();
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const username = usernameInput.value.trim();

    if (!email || !password || (!isLoginMode && !username)) {
        showAuthError("Please fill all fields!");
        return;
    }

    const payload = isLoginMode ? { email, password } : { username, email, password };
    const endpoint = isLoginMode ? "/auth/login" : "/auth/register";

    try {
        authMsg.innerText = "Processing...";
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (response.ok) {
            if (isLoginMode) {
                localStorage.setItem("token", data.access_token);
                localStorage.setItem("username", data.username || "User");
                switchToChat(data.username || "User");
            } else {
                alert("Account created! Please login.");
                tabLogin.click();
            }
        } else {
            showAuthError(data.detail || "Auth failed");
        }
    } catch (err) {
        showAuthError("Server connection failed!");
    }
}

// --- 3. Chat Logic ---
async function handleChat() {
    const message = userInput.value.trim();
    const token = localStorage.getItem("token");

    if (!message) return;
    if (!token) {
        appendMsg("ai-msg", "⚠️ Session expired. Please login.");
        return;
    }

    appendMsg("user-msg", message);
    userInput.value = "";
    if (typingIndicator) typingIndicator.classList.remove('hidden');
    scrollChat();

    try {
        const response = await fetch(`${API_BASE_URL}/chat/send`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        if (response.ok) {
            appendMsg("ai-msg", data.response);
            // Refresh graph data if it's currently visible
            if (!moodChartContainer.classList.contains('hidden')) {
                fetchMoodHistory();
            }
        } else {
            appendMsg("ai-msg", "⚠️ Error: " + (data.detail || "Server issue"));
        }
    } catch (err) {
        appendMsg("ai-msg", "❌ Connection lost.");
    } finally {
        if (typingIndicator) typingIndicator.classList.add('hidden');
        scrollChat();
    }
}

// --- 4. 🎤 Voice Input ---
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';

    micBtn.onclick = () => {
        recognition.start();
        micBtn.classList.add('recording');
    };

    recognition.onresult = (event) => {
        userInput.value = event.results[0][0].transcript;
        micBtn.classList.remove('recording');
        handleChat();
    };

    recognition.onerror = () => micBtn.classList.remove('recording');
    recognition.onend = () => micBtn.classList.remove('recording');
}

// --- 5. 📈 Mood Graph (Asli Data Connection) ---
async function fetchMoodHistory() {
    const token = localStorage.getItem("token");
    try {
        // Rizwan, ye hamare naye backend route ko hit karega
        const response = await fetch(`${API_BASE_URL}/chat/history-stats`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await response.json();

        if (response.ok && data.status === "success") {
            renderChart(data.labels, data.values);
        }
    } catch (err) {
        console.error("Failed to fetch history:", err);
    }
}

function renderChart(labels, values) {
    const ctx = document.getElementById('moodChart').getContext('2d');

    // Agar pehle se chart hai toh destroy kar dein taake naya ban sakay
    if (moodChart) {
        moodChart.destroy();
    }

    moodChart = new Chart(ctx, {
        type: 'bar', // Bar chart mood counts ke liye best hai
        data: {
            labels: labels.length > 0 ? labels : ['No Data'],
            datasets: [{
                label: 'Your Mood Patterns (Last 7 Days)',
                data: values.length > 0 ? values : [0],
                backgroundColor: 'rgba(79, 70, 229, 0.6)',
                borderColor: '#4f46e5',
                borderWidth: 1,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
        }
    });
}

// Toggle Graph visibility
if (statsBtn) {
    statsBtn.onclick = () => {
        moodChartContainer.classList.toggle('hidden');
        if (!moodChartContainer.classList.contains('hidden')) {
            fetchMoodHistory();
        }
    };
}

// --- Event Listeners ---
authBtn.addEventListener('click', handleAuth);
sendBtn.addEventListener('click', () => handleChat());
userInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') handleChat(); });

tabLogin.onclick = () => {
    isLoginMode = true;
    tabLogin.classList.add('active');
    tabRegister.classList.remove('active');
    usernameContainer.classList.add('hidden');
    authBtn.innerText = "Login";
};

tabRegister.onclick = () => {
    isLoginMode = false;
    tabRegister.classList.add('active');
    tabLogin.classList.remove('active');
    usernameContainer.classList.remove('hidden');
    authBtn.innerText = "Register";
};

logoutBtn.onclick = () => {
    localStorage.clear();
    location.reload();
};

function appendMsg(cls, text) {
    const div = document.createElement('div');
    div.className = `msg ${cls} fade-in`;
    div.innerText = text;
    chatBox.appendChild(div);
    scrollChat();
}

function scrollChat() { chatBox.scrollTop = chatBox.scrollHeight; }

function showAuthError(msg) {
    authMsg.innerText = msg;
    authMsg.style.color = "#ef4444";
}

window.onload = () => {
    const t = localStorage.getItem("token");
    const u = localStorage.getItem("username");
    if (t && u) switchToChat(u);
};