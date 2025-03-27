// Background script for handling side panel operations

// Cache for tracking operations
const operationState = {
  sidePanelOpenRequests: 0,
  lastOpenAttempt: 0
};

console.log("Background script loaded");

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("Background script received message:", message.action);

  if (message.action === "openSidePanel") {
    handleSidePanelOpen(sendResponse);
    // Return true to indicate we'll respond asynchronously
    return true;
  }

  if (message.action === "checkSidePanel") {
    sendResponse({ checked: true, timestamp: Date.now() });
    return true;
  }
});

/**
 * Handles the side panel opening with retry logic
 * @param {Function} sendResponse - Function to send response back to caller
 */
async function handleSidePanelOpen(sendResponse) {
  console.log("Attempting to open side panel from background script");

  // Prevent rapid repeated attempts (debounce)
  const now = Date.now();
  if (now - operationState.lastOpenAttempt < 1000) {
    operationState.sidePanelOpenRequests++;
    if (operationState.sidePanelOpenRequests > 3) {
      sendResponse({
        success: false,
        error: "Too many requests in short time",
        retryAfter: 1000,
      });
      return;
    }
  } else {
    operationState.sidePanelOpenRequests = 1;
  }

  operationState.lastOpenAttempt = now;

  try {
    // Check if sidePanel API is available
    if (!chrome.sidePanel || !chrome.sidePanel.open) {
      sendResponse({
        success: false,
        error: "Side panel API not available in this browser",
      });
      return;
    }

    // Try to open the side panel
    await chrome.sidePanel.open();
    console.log("Side panel opened successfully from background");
    sendResponse({ success: true, message: "Side panel opened" });
  } catch (error) {
    console.error("Error opening side panel from background:", error);

    // Try again after a short delay
    setTimeout(async () => {
      try {
        await chrome.sidePanel.open();
        console.log("Side panel opened successfully after retry");
        sendResponse({
          success: true,
          message: "Side panel opened after retry",
        });
      } catch (retryError) {
        console.error("Error opening side panel on retry:", retryError);
        sendResponse({ success: false, error: retryError.message });
      }
    }, 500);
  }
}

// Listen for side panel status changes
if (chrome.sidePanel) {
  if (chrome.sidePanel.onShow) {
    chrome.sidePanel.onShow.addListener(() => {
      console.log("Side panel was shown");
      operationState.sidePanelOpenRequests = 0; // Reset counter on success
    });
  }

  if (chrome.sidePanel.onHide) {
    chrome.sidePanel.onHide.addListener(() => {
      console.log("Side panel was hidden");
    });
  }
}

// Handle extension installation or update
chrome.runtime.onInstalled.addListener((details) => {
  console.log("Extension installed/updated:", details.reason);

  // Reset state on update or install
  operationState.sidePanelOpenRequests = 0;
  operationState.lastOpenAttempt = 0;
});
