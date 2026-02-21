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
                isLoginMode = true;
                tabLogin.click();
            }
        } else {
            showAuthError(data.detail || "Auth failed");
        }
    } catch (err) {
        showAuthError("Server connection failed!");
    }
}

// --- 3. Chat Logic with Smart Image Detection ---
async function handleChat() {
    if (isProcessing) return;

    const message = userInput.value.trim();
    const token = localStorage.getItem("token");

    if (!message) return;
    if (!token) {
        appendMsg("ai-msg", "⚠️ Session expired. Please login.");
        return;
    }

    isProcessing = true;
    appendMsg("user-msg", message);
    userInput.value = "";
    if (typingIndicator) typingIndicator.classList.remove('hidden');
    scrollChat();

    // --- 🔍 SMART LOGIC START ---
    const lowerMsg = message.toLowerCase();

    // In lafzon par image BN'NI chahiye (Generation)
    const genKeywords = ["generate", "create", "make", "bnao", "bnnao", "tasveer do", "draw", "paint", "photo of"];
    const userWantsToCreate = genKeywords.some(word => lowerMsg.includes(word));

    // In lafzon par sirf DESCRIPTION (Lafzon mein personality)
    const personalKeywords = ["personality", "mera character", "image kesi hai", "image kaisa hai", "batao", "describe", "kesa hun"];
    const isDescriptiveRequest = personalKeywords.some(word => lowerMsg.includes(word));

    // Agar user "banao" kahe toh true, agar sirf "kesi hai" kahe toh false
    const isImageRequest = userWantsToCreate && !isDescriptiveRequest;

    // Voice support check
    const voiceKeywords = ["speak", "bolo", "batao", "sunao", "awaz", "talk"];
    const userWantsToHear = voiceKeywords.some(word => lowerMsg.includes(word));
    // --- 🔍 SMART LOGIC END ---

    try {
        const response = await fetch(`${API_BASE_URL}/chat/send`, {
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

        const data = await response.json();
        if (response.ok) {
            // Humesha text response dikhayen
            appendMsg("ai-msg", data.response);

            // Image sirf tabhi jab isImageRequest true ho aur URL mile
            if (data.image_url && isImageRequest) {
                appendImage(data.image_url);
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
        appendMsg("ai-msg", "❌ Connection lost.");
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

// --- 5. 📉 Mood Graph Logic ---
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
        console.error("Mood history error:", err);
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

// --- 🛠️ Helper Functions ---

function appendMsg(cls, text) {
    const div = document.createElement('div');
    div.className = `msg ${cls} fade-in`;
    div.innerText = text;
    chatBox.appendChild(div);
    scrollChat();
}

async function appendImage(url) {
    const imgDiv = document.createElement('div');
    imgDiv.className = "msg ai-msg fade-in image-msg";
    const imgId = `ai-img-${Date.now()}`;

    imgDiv.innerHTML = `
        <div style="margin-top: 10px; width: 100%; min-height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f3f4f6; border-radius: 12px; border: 1px dashed #4f46e5;" id="${imgId}-container">
            <div id="${imgId}-loader" style="border: 3px solid #f3f3f3; border-top: 3px solid #4f46e5; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite;"></div>
            <p id="${imgId}-status" style="font-size: 0.8rem; color: #4f46e5; margin-top: 12px; font-weight: bold; text-align: center;">🎨 AI is painting your request...</p>
        </div>
        <style> @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } } </style>
    `;

    chatBox.appendChild(imgDiv);
    scrollChat();

    const container = document.getElementById(`${imgId}-container`);
    const status = document.getElementById(`${imgId}-status`);
    const loader = document.getElementById(`${imgId}-loader`);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 25000);

    try {
        const response = await fetch(url, { signal: controller.signal });
        if (response.ok) {
            const blob = await response.blob();
            const objectUrl = URL.createObjectURL(blob);

            loader.remove();
            status.remove();
            container.style.minHeight = "auto";
            container.style.background = "transparent";
            container.style.border = "none";

            const img = document.createElement('img');
            img.src = objectUrl;
            img.style.cssText = "width: 100%; max-width: 350px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); display: block;";

            container.appendChild(img);

            const dBtn = document.createElement('button');
            dBtn.innerHTML = "📥 Save Art";
            dBtn.style.cssText = "margin-top: 12px; padding: 8px 20px; background: #4f46e5; color: white; border: none; border-radius: 25px; font-size: 0.75rem; cursor: pointer; font-weight: bold;";
            dBtn.onclick = () => {
                const link = document.createElement('a');
                link.href = objectUrl;
                link.download = `AI_Gen_${Date.now()}.png`;
                link.click();
            };
            container.appendChild(dBtn);
        } else { throw new Error(); }
    } catch (e) {
        loader.remove();
        status.innerHTML = `<span style="color: #ef4444;">❌ Server busy.</span><br><a href="${url}" target="_blank" style="color: #4f46e5; font-size: 0.75rem; text-decoration: underline;">Open direct link</a>`;
    } finally {
        clearTimeout(timeoutId);
        scrollChat();
    }
}

function scrollChat() { chatBox.scrollTop = chatBox.scrollHeight; }

function showAuthError(msg) {
    authMsg.innerText = msg;
    authMsg.style.color = "#ef4444";
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

if (statsBtn) {
    statsBtn.onclick = () => {
        moodChartContainer.classList.toggle('hidden');
        if (!moodChartContainer.classList.contains('hidden')) fetchMoodHistory();
    };
}

window.onload = () => {
    const t = localStorage.getItem("token");
    const u = localStorage.getItem("username");
    if (t && u) switchToChat(u);
};