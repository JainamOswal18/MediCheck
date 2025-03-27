// Background script for handling side panel operations

console.log("Background script loaded");

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("Background script received message:", message);

  if (message.action === "openSidePanel") {
    console.log("Attempting to open side panel from background script");

    // Try to open the side panel
    try {
      chrome.sidePanel
        .open()
        .then(() => {
          console.log("Side panel opened successfully from background");
          sendResponse({ success: true, message: "Side panel opened" });
        })
        .catch((error) => {
          console.error("Error opening side panel from background:", error);
          sendResponse({ success: false, error: error.message });
        });
    } catch (error) {
      console.error("Exception opening side panel:", error);
      sendResponse({ success: false, error: error.message });
    }

    // Return true to indicate we'll respond asynchronously
    return true;
  }

  if (message.action === "checkSidePanel") {
    console.log("Checking side panel status");
    sendResponse({ checked: true, timestamp: Date.now() });
    return true;
  }
});

// Listen for side panel status changes
if (chrome.sidePanel && chrome.sidePanel.onShow) {
  chrome.sidePanel.onShow.addListener(() => {
    console.log("Side panel was shown");
  });
}

if (chrome.sidePanel && chrome.sidePanel.onHide) {
  chrome.sidePanel.onHide.addListener(() => {
    console.log("Side panel was hidden");
  });
}

// Optional: Handle extension installation or update
chrome.runtime.onInstalled.addListener((details) => {
  console.log("Extension installed/updated:", details.reason);
});
