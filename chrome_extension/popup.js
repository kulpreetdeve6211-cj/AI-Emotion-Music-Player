// ===============================
// CONFIGURATION
// ===============================
const API = "http://127.0.0.1:5000";

let playlist = [];
let currentIndex = 0;
let stream = null;
let isDetecting = false;

console.log("✅ popup.js loading...");
console.log("API URL:", API);

// ===============================
// LOAD THEME FROM STORAGE
// ===============================
chrome.storage.local.get(["theme"], (result) => {
    if (result.theme === "light") {
        document.body.classList.add("light");
    }
});

// ===============================
// PAGE INITIALIZATION
// ===============================
document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ popup.js loaded - DOM ready");
    setupEventListeners();
    checkAPIConnection();
    loadDefaultPlaylist();
});

// ===============================
// EVENT LISTENERS
// ===============================
function setupEventListeners() {
    console.log("Setting up event listeners...");
    
    // Mood buttons
    const moodButtons = document.querySelectorAll(".mood-btn");
    console.log("Found mood buttons:", moodButtons.length);
    
    moodButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const mood = btn.dataset.mood;
            console.log("Mood selected:", mood);
            loadPlaylist(mood);
            updateActiveButton(btn);
        });
    });
    
    // Camera toggle checkbox
    const cameraToggle = document.getElementById("cameraToggle");
    if (cameraToggle) {
        console.log("✅ Found camera toggle");
        cameraToggle.addEventListener("change", () => {
            if (cameraToggle.checked) {
                startCamera();
            } else {
                stopCamera();
            }
        });
    } else {
        console.error("❌ Camera toggle not found");
    }
    
    // Dashboard button
    const dashboardBtn = document.getElementById("openDashboard");
    if (dashboardBtn) {
        console.log("✅ Found dashboard button");
        dashboardBtn.addEventListener("click", openDashboard);
    }
    
    // Play button
    const playBtn = document.getElementById("playBtn");
    if (playBtn) {
        playBtn.addEventListener("click", () => {
            if (playlist.length > 0) {
                const song = playlist[currentIndex];
                window.open(song.url, '_blank');
            }
        });
    }
    
    // Next button
    const nextBtn = document.getElementById("nextBtn");
    if (nextBtn) {
        nextBtn.addEventListener("click", () => {
            if (playlist.length > 0) {
                currentIndex = (currentIndex + 1) % playlist.length;
                updateNowPlaying();
            }
        });
    }
}

// ===============================
// MOOD SELECTION
// ===============================
function updateActiveButton(button) {
    document.querySelectorAll(".mood-btn").forEach(btn => {
        btn.classList.remove("active");
    });
    button.classList.add("active");
}

// ===============================
// CAMERA DETECTION
// ===============================
async function startCamera() {
    try {
        const video = document.getElementById("video");
        if (!video) {
            console.error("❌ Video element not found");
            return;
        }
        
        console.log("Starting camera...");
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: 320, 
                height: 240 
            } 
        });
        
        video.srcObject = stream;
        
        const cameraBox = document.getElementById("cameraBox");
        if (cameraBox) {
            cameraBox.classList.remove("hidden");
        }
        
        isDetecting = true;
        detectEmotionLoop();
        
        console.log("✅ Camera started");
        
    } catch (error) {
        console.error("❌ Camera error:", error);
        const cameraToggle = document.getElementById("cameraToggle");
        if (cameraToggle) {
            cameraToggle.checked = false;
        }
        const statusBadge = document.getElementById("statusBadge");
        if (statusBadge) {
            statusBadge.textContent = "Camera denied";
            statusBadge.className = "status offline";
        }
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
        
        const video = document.getElementById("video");
        if (video) {
            video.srcObject = null;
        }
        
        const cameraBox = document.getElementById("cameraBox");
        if (cameraBox) {
            cameraBox.classList.add("hidden");
        }
        
        isDetecting = false;
        console.log("✅ Camera stopped");
    }
}

async function detectEmotionLoop() {
    if (!isDetecting) return;
    
    try {
        const video = document.getElementById("video");
        if (!video || !video.srcObject) return;
        
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        if (canvas.width === 0 || canvas.height === 0) {
            console.log("Video not ready yet...");
            setTimeout(detectEmotionLoop, 500);
            return;
        }
        
        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0);
        
        const imageData = canvas.toDataURL("image/jpeg");
        
        console.log("Sending image to /detect endpoint...");
        const response = await fetch(`${API}/detect`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ image: imageData })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log("Detection result:", result);
        
        if (result.emotion) {
            console.log("Emotion detected:", result.emotion);
            updateStatusBadge(result.emotion, result.confidence);
            loadPlaylist(result.emotion);
        }
        
    } catch (error) {
        console.error("❌ Detection error:", error);
    }
    
    // Continue detecting every 2 seconds
    setTimeout(detectEmotionLoop, 2000);
}

// ===============================
// PLAYLIST MANAGEMENT
// ===============================
async function loadPlaylist(mood) {
    try {
        console.log("Loading playlist for:", mood);
        
        const response = await fetch(`${API}/playlist/${mood}`);
        
        if (!response.ok) {
            console.error("Playlist not found:", mood);
            displayPlaylist(null);
            return;
        }
        
        const data = await response.json();
        console.log("Playlist data:", data);
        
        displayPlaylist(data);
        
    } catch (error) {
        console.error("❌ Playlist error:", error);
        displayPlaylist(null);
    }
}

function displayPlaylist(data) {
    const playlistContainer = document.getElementById("playlistContainer");
    if (!playlistContainer) {
        console.error("❌ playlistContainer not found");
        return;
    }
    
    if (!data || !data.playlist || !data.playlist.songs) {
        playlistContainer.innerHTML = `
            <div class="empty-state">
                <p>📭 No playlist available</p>
            </div>
        `;
        return;
    }
    
    const { emotion, playlist } = data;
    playlist_data = playlist.songs;
    currentIndex = 0;
    updateNowPlaying();
    
    let html = `<div class="songs-list">`;
    
    playlist.songs.forEach((song, index) => {
        html += `
            <div class="song-item" onclick="playSongAtIndex(${index})">
                <div class="song-number">${index + 1}</div>
                <div class="song-info">
                    <div class="song-title">${song.title}</div>
                    <div class="song-artist">${song.artist}</div>
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    playlistContainer.innerHTML = html;
    console.log("✅ Playlist displayed");
}

function updateNowPlaying() {
    if (playlist_data && playlist_data.length > 0) {
        const song = playlist_data[currentIndex];
        document.getElementById("songTitle").textContent = song.title;
        document.getElementById("songArtist").textContent = song.artist;
    }
}

function playSongAtIndex(index) {
    if (playlist_data && playlist_data[index]) {
        currentIndex = index;
        updateNowPlaying();
        window.open(playlist_data[index].url, '_blank');
    }
}

function loadDefaultPlaylist() {
    console.log("Loading default neutral playlist...");
    loadPlaylist("neutral");
}

let playlist_data = [];

// ===============================
// STATUS UPDATES
// ===============================
function updateStatusBadge(emotion, confidence) {
    const statusBadge = document.getElementById("statusBadge");
    if (!statusBadge) return;
    
    const confPercent = Math.round(confidence * 100);
    statusBadge.textContent = `${emotion.toUpperCase()} (${confPercent}%)`;
    statusBadge.className = `status ${emotion}`;
}

async function checkAPIConnection() {
    try {
        console.log("Checking API connection...");
        const response = await fetch(`${API}/health`);
        
        if (response.ok) {
            console.log("✅ API connected");
            const statusBadge = document.getElementById("statusBadge");
            if (statusBadge) {
                statusBadge.textContent = "Connected";
                statusBadge.className = "status connected";
            }
        }
    } catch (error) {
        console.error("❌ API not available:", error);
        const statusBadge = document.getElementById("statusBadge");
        if (statusBadge) {
            statusBadge.textContent = "Offline";
            statusBadge.className = "status offline";
        }
    }
}

// ===============================
// DASHBOARD
// ===============================
function openDashboard() {
    chrome.tabs.create({
        url: chrome.runtime.getURL("dashboard.html")
    });
}

console.log("✅ All functions loaded");
