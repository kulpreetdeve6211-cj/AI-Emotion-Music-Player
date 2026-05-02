// ===============================
// CREATE ALARM BASED ON TIMER
// ===============================
function createAlarm(minutes) {
  chrome.alarms.clear("rescanAlarm");

  chrome.alarms.create("rescanAlarm", {
    delayInMinutes: Number(minutes)
  });

  console.log("✅ Alarm set for", minutes, "minutes");
}

// ===============================
// STOP ALARM (🔥 NEW)
// ===============================
function stopAlarm() {
  chrome.alarms.clear("rescanAlarm");
  console.log("⛔ Alarm stopped (API OFF)");
}

// ===============================
// LISTEN FOR TIMER CHANGE (storage)
// ===============================
chrome.storage.onChanged.addListener((changes) => {
  if (changes.rescanTime) {
    createAlarm(changes.rescanTime.newValue);
  }
});

// ===============================
// LISTEN FOR DIRECT MESSAGE
// ===============================
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === "updateTimer") {
    createAlarm(msg.time);
  }
});

// ===============================
// INITIAL LOAD
// ===============================
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(["rescanTime"], (result) => {
    createAlarm(result.rescanTime || 5);
  });
});

// ===============================
// WHEN ALARM TRIGGERS
// ===============================
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name !== "rescanAlarm") return;

  try {
    const res = await fetch("http://127.0.0.1:5000/health");

    if (res.ok) {
      console.log("✅ API ON → showing notification");
      showNotification();
    } else {
      console.log("⚠️ API responded but not OK → stopping timer");
      stopAlarm(); // 🔥 IMPORTANT
    }

  } catch (err) {
    console.log("❌ API OFF → stopping timer completely");
    stopAlarm(); // 🔥 THIS FIXES YOUR ISSUE
  }
});

// ===============================
// SHOW NOTIFICATION
// ===============================
function showNotification() {
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icons/icon128.png",
    title: "Emotion Player",
    message: "Do you want to rescan your mood?",
    buttons: [
      { title: "Yes" },
      { title: "No" }
    ],
    priority: 2
  });
}

// ===============================
// HANDLE BUTTON CLICK
// ===============================
chrome.notifications.onButtonClicked.addListener((notifId, btnIndex) => {
  
  chrome.storage.local.get(["rescanTime"], (result) => {
    const time = result.rescanTime || 5;

    if (btnIndex === 0) {
      // YES → open extension like popup window (NOT full tab)
      chrome.windows.create({
        url: chrome.runtime.getURL("popup.html"),
        type: "popup",
        width: 420,
        height: 650,
        focused: true
      });

      console.log("User clicked YES → opened popup extension");

    } else {
      console.log("User clicked NO");
    }

    // restart timer
    createAlarm(time);
  });

});