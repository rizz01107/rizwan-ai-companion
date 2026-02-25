const API_BASE_URL = "http://127.0.0.1:8000";
let isLoginMode = true;
let moodChart = null;
let isProcessing = false;

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
    if (authMsg) authMsg.innerText = "";
    scrollChat();
}

function speakText(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    }
}

// --- 2. Auth Logic ---
async function handleAuth(e) {
    if (e) e.preventDefault();

    if (!authMsg) return; // Safety check

    const email = emailInput ? emailInput.value.trim() : "";
    const password = passwordInput ? passwordInput.value.trim() : "";
    const username = usernameInput ? usernameInput.value.trim() : "";

    if (!email || !password || (!isLoginMode && !username)) {
        showAuthError("⚠️ Please fill all required fields!");
        return;
    }

    const payload = isLoginMode ? { email: email, password: password } : { username: username, email: email, password: password };
    const endpoint = isLoginMode ? "/auth/login" : "/auth/register";

    try {
        authMsg.style.color = "#4f46e5";
        authMsg.innerText = "⏳ Processing...";

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            authMsg.innerText = "";
            if (isLoginMode) {
                localStorage.setItem("token", data.access_token);
                localStorage.setItem("username", data.username || email.split('@')[0]);
                switchToChat(data.username || email.split('@')[0]);
            } else {
                alert("✅ Account created successfully! Please login.");
                isLoginMode = true;
                if (tabLogin) tabLogin.click();
            }
        } else {
            let errorMsg = "❌ Auth failed. Check credentials.";
            if (data.detail) {
                if (Array.isArray(data.detail)) {
                    errorMsg = "❌ Validation Error: Please check input formats.";
                } else {
                    errorMsg = "❌ " + data.detail;
                }
            }
            showAuthError(errorMsg);
        }
    } catch (err) {
        console.error("Auth Error:", err);
        showAuthError("🚫 Server connection failed! Is backend running?");
    }
}

// --- 3. Chat Logic with Smart Image Detection ---
async function handleChat() {
    if (isProcessing) return;

    const message = userInput.value.trim();
    const token = localStorage.getItem("token");

    if (!message) return;
    if (!token) {
        appendMsg("ai-msg", "⚠️ Session expired. Please login again.");
        return;
    }

    isProcessing = true;
    appendMsg("user-msg", message);
    userInput.value = "";
    if (typingIndicator) typingIndicator.classList.remove('hidden');
    scrollChat();

    // --- 🔍 SMART DETECTION LOGIC ---
    const lowerMsg = message.toLowerCase();
    const genKeywords = ["generate", "create", "make", "bnao", "bnnao", "tasveer do", "draw", "paint", "photo of"];
    const personalKeywords = ["personality", "mera character", "image kesi hai", "image kaisa hai", "batao", "describe"];

    const isImageRequest = genKeywords.some(word => lowerMsg.includes(word)) &&
        !personalKeywords.some(word => lowerMsg.includes(word));

    const voiceKeywords = ["speak", "bolo", "batao", "sunao", "awaz", "talk"];
    const userWantsToHear = voiceKeywords.some(word => lowerMsg.includes(word));

    try {
        // UPDATED: Added /api prefix to match your backend app.py routing
        const response = await fetch(`${API_BASE_URL}/api/chat/send`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                message: message,
                is_image_request: isImageRequest
            })
        });

        if (response.status === 401) {
            localStorage.clear();
            appendMsg("ai-msg", "⚠️ Session expired. Redirecting to login...");
            setTimeout(() => location.reload(), 2000);
            return;
        }

        const data = await response.json();
        if (response.ok) {
            appendMsg("ai-msg", data.response);

            if (data.image_url && isImageRequest) {
                await appendImage(data.image_url);
            }

            if (userWantsToHear) {
                speakText(data.response);
            }

            if (moodChartContainer && !moodChartContainer.classList.contains('hidden')) {
                fetchMoodHistory();
            }
        } else {
            appendMsg("ai-msg", "⚠️ Error: " + (data.detail || "Server issue"));
        }
    } catch (err) {
        console.error("Chat Error:", err);
        appendMsg("ai-msg", "❌ Connection lost. Check backend.");
    } finally {
        isProcessing = false;
        if (typingIndicator) typingIndicator.classList.add('hidden');
        scrollChat();
    }
}

// --- 4. 🎤 Voice Input ---
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;

    if (micBtn) {
        micBtn.onclick = () => {
            try {
                recognition.start();
                micBtn.classList.add('recording');
                micBtn.innerText = "🛑 Listening...";
            } catch (e) {
                recognition.stop();
            }
        };
    }

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (userInput) userInput.value = transcript;
        if (micBtn) {
            micBtn.classList.remove('recording');
            micBtn.innerText = "🎤";
        }
        handleChat();
    };

    recognition.onerror = (event) => {
        console.error("Speech Error:", event.error);
        if (micBtn) {
            micBtn.classList.remove('recording');
            micBtn.innerText = "🎤";
        }
    };

    recognition.onend = () => {
        if (micBtn) {
            micBtn.classList.remove('recording');
            micBtn.innerText = "🎤";
        }
    };
}

// --- 5. 📉 Mood Graph Logic ---
async function fetchMoodHistory() {
    const token = localStorage.getItem("token");
    if (!token) return;
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/history-stats`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await response.json();
        if (response.ok && data.status === "success") {
            renderChart(data.labels, data.values);
        }
    } catch (err) {
        console.error("Mood history error:", err);
    }
}

function renderChart(labels, values) {
    const chartCanvas = document.getElementById('moodChart');
    if (!chartCanvas) return;

    const ctx = chartCanvas.getContext('2d');
    if (moodChart) { moodChart.destroy(); }

    moodChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels && labels.length > 0 ? labels : ['No Data'],
            datasets: [{
                label: 'Mood Analysis (Last 7 Days)',
                data: values && values.length > 0 ? values : [0],
                backgroundColor: 'rgba(79, 70, 229, 0.6)',
                borderColor: '#4f46e5',
                borderWidth: 1,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1, precision: 0 }
                }
            },
            plugins: {
                legend: { display: true, position: 'top' }
            }
        }
    });
}

// --- 🛠️ Helper Functions ---
function appendMsg(cls, text) {
    if (!chatBox) return;
    const div = document.createElement('div');
    div.className = `msg ${cls} fade-in`;
    div.innerText = text;
    chatBox.appendChild(div);
    scrollChat();
}

async function appendImage(url) {
    if (!chatBox) return;
    const imgDiv = document.createElement('div');
    imgDiv.className = "msg ai-msg fade-in image-msg";
    const imgId = `ai-img-${Date.now()}`;

    imgDiv.innerHTML = `
        <div style="margin-top: 10px; width: 100%; min-height: 250px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f3f4f6; border-radius: 12px; border: 1px dashed #4f46e5;" id="${imgId}-container">
            <div id="${imgId}-loader" class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #4f46e5; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite;"></div>
            <p id="${imgId}-status" style="font-size: 0.85rem; color: #4f46e5; margin-top: 15px; font-weight: 600; text-align: center;">🎨 Creating your art...</p>
        </div>
        <style> @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } } </style>
    `;

    chatBox.appendChild(imgDiv);
    scrollChat();

    const container = document.getElementById(`${imgId}-container`);
    const status = document.getElementById(`${imgId}-status`);
    const loader = document.getElementById(`${imgId}-loader`);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 90000);

    try {
        const response = await fetch(url, { signal: controller.signal });
        if (response.ok) {
            const blob = await response.blob();
            const objectUrl = URL.createObjectURL(blob);

            if (loader) loader.remove();
            if (status) status.remove();

            container.style.minHeight = "auto";
            container.style.background = "transparent";
            container.style.border = "none";

            const img = document.createElement('img');
            img.src = objectUrl;
            img.className = "generated-art";
            img.style.cssText = "width: 100%; max-width: 400px; border-radius: 12px; box-shadow: 0 10px 20px rgba(0,0,0,0.15); display: block;";

            container.appendChild(img);

            const dBtn = document.createElement('button');
            dBtn.innerHTML = "📥 Download Masterpiece";
            dBtn.className = "download-btn";
            dBtn.style.cssText = "margin-top: 15px; padding: 10px 25px; background: #4f46e5; color: white; border: none; border-radius: 30px; font-size: 0.8rem; cursor: pointer; font-weight: bold; transition: transform 0.2s;";
            dBtn.onclick = () => {
                const link = document.createElement('a');
                link.href = objectUrl;
                link.download = `Rizwan_AI_Art_${Date.now()}.png`;
                link.click();
            };
            container.appendChild(dBtn);
        } else { throw new Error("Fetch failed"); }
    } catch (e) {
        if (loader) loader.remove();
        if (status) status.innerHTML = `<span style="color: #ef4444;">❌ AI Artist is busy.</span><br><a href="${url}" target="_blank" style="color: #4f46e5; font-size: 0.8rem; text-decoration: underline; margin-top: 5px; display: inline-block;">View direct link</a>`;
    } finally {
        clearTimeout(timeoutId);
        scrollChat();
    }
}

function scrollChat() {
    if (chatBox) chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
}

function showAuthError(msg) {
    if (authMsg) {
        authMsg.innerText = msg;
        authMsg.style.color = "#ef4444";
        authMsg.classList.add('shake');
        setTimeout(() => authMsg.classList.remove('shake'), 500);
    }
}

// --- Event Listeners ---
if (authBtn) authBtn.addEventListener('click', handleAuth);
if (sendBtn) sendBtn.addEventListener('click', handleChat);
if (userInput) userInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') handleChat(); });

if (tabLogin) {
    tabLogin.onclick = () => {
        isLoginMode = true;
        tabLogin.classList.add('active');
        if (tabRegister) tabRegister.classList.remove('active');
        if (usernameContainer) usernameContainer.classList.add('hidden');
        if (authBtn) authBtn.innerText = "Login";
        if (authMsg) authMsg.innerText = "";
    };
}

if (tabRegister) {
    tabRegister.onclick = () => {
        isLoginMode = false;
        tabRegister.classList.add('active');
        if (tabLogin) tabLogin.classList.remove('active');
        if (usernameContainer) usernameContainer.classList.remove('hidden');
        if (authBtn) authBtn.innerText = "Create Account";
        if (authMsg) authMsg.innerText = "";
    };
}

if (logoutBtn) {
    logoutBtn.onclick = () => {
        localStorage.clear();
        location.reload();
    };
}

if (statsBtn) {
    statsBtn.onclick = () => {
        if (moodChartContainer) {
            const isHidden = moodChartContainer.classList.toggle('hidden');
            if (!isHidden) fetchMoodHistory();
        }
    };
}

window.onload = () => {
    const token = localStorage.getItem("token");
    const username = localStorage.getItem("username");
    if (token && username) {
        switchToChat(username);
    }
};