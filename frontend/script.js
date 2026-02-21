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

// --- 2. Auth Logic (FIXED) ---
async function handleAuth(e) {
    if (e) e.preventDefault();

    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const username = usernameInput.value.trim();

    if (!email || !password || (!isLoginMode && !username)) {
        showAuthError("Please fill all fields!");
        return;
    }

    // Backend models ke mutabiq payload
    const payload = isLoginMode
        ? { email: email, password: password }
        : { username: username, email: email, password: password };

    const endpoint = isLoginMode ? "/auth/login" : "/auth/register";

    try {
        authMsg.innerText = "Processing...";
        authMsg.style.color = "#4f46e5";

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
                alert("Account created successfully! Now please login.");
                // Switch to login tab automatically
                isLoginMode = true;
                tabLogin.click();
                authMsg.innerText = "Registration successful. Please login.";
                authMsg.style.color = "#10b981";
            }
        } else {
            // FIX: Handle structured error from FastAPI
            let errorMessage = "Auth failed";
            if (data.detail) {
                errorMessage = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
            }
            showAuthError(errorMessage);
        }
    } catch (err) {
        showAuthError("Cannot connect to server. Is backend running?");
    }
}

// --- 3. Chat Logic (FIXED) ---
async function handleChat() {
    const message = userInput.value.trim();
    const token = localStorage.getItem("token");

    if (!message) return;
    if (!token) {
        appendMsg("ai-msg", "⚠️ Session expired. Please login again.");
        setTimeout(() => { location.reload(); }, 2000);
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
            if (!moodChartContainer.classList.contains('hidden')) {
                fetchMoodHistory();
            }
        } else {
            appendMsg("ai-msg", "⚠️ Error: " + (data.detail || "Something went wrong"));
        }
    } catch (err) {
        appendMsg("ai-msg", "❌ Connection lost with server.");
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
        micBtn.innerText = "🛑 Listening...";
    };

    recognition.onresult = (event) => {
        userInput.value = event.results[0][0].transcript;
        micBtn.classList.remove('recording');
        micBtn.innerText = "🎤";
        handleChat();
    };

    recognition.onerror = () => {
        micBtn.classList.remove('recording');
        micBtn.innerText = "🎤";
    };

    recognition.onend = () => {
        micBtn.classList.remove('recording');
        micBtn.innerText = "🎤";
    };
}

// --- 5. 📈 Mood Graph ---
async function fetchMoodHistory() {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE_URL}/chat/history-stats`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await response.json();

        if (response.ok && data.status === "success") {
            renderChart(data.labels, data.values);
        }
    } catch (err) {
        console.error("Failed to fetch mood history:", err);
    }
}

function renderChart(labels, values) {
    const ctx = document.getElementById('moodChart').getContext('2d');
    if (moodChart) { moodChart.destroy(); }

    moodChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.length > 0 ? labels : ['No Data'],
            datasets: [{
                label: 'Mood Analysis (Last 7 Days)',
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

// --- Event Listeners ---
authBtn.addEventListener('click', handleAuth);
sendBtn.addEventListener('click', handleChat);
userInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') handleChat(); });

tabLogin.onclick = () => {
    isLoginMode = true;
    tabLogin.classList.add('active');
    tabRegister.classList.remove('active');
    usernameContainer.classList.add('hidden');
    authBtn.innerText = "Login";
    authMsg.innerText = "";
};

tabRegister.onclick = () => {
    isLoginMode = false;
    tabRegister.classList.add('active');
    tabLogin.classList.remove('active');
    usernameContainer.classList.remove('hidden');
    authBtn.innerText = "Register";
    authMsg.innerText = "";
};

logoutBtn.onclick = () => {
    localStorage.clear();
    location.reload();
};

if (statsBtn) {
    statsBtn.onclick = () => {
        moodChartContainer.classList.toggle('hidden');
        if (!moodChartContainer.classList.contains('hidden')) {
            fetchMoodHistory();
        }
    };
}

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