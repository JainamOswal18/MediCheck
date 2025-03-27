document.addEventListener('DOMContentLoaded', function() {
  const summarizeBtn = document.getElementById("summarizeBtn");
  const statusDiv = document.getElementById("status");
  let isProcessing = false;

  // Constants for UI messages and styling
  const STATUS_STYLES = {
    SUCCESS: "color: #4aff91; font-weight: bold; margin-bottom: 10px;",
    INFO: "font-size: 12px; color: #999;",
    ERROR: "font-size: 12px; color: #ff4a4a;",
  };

  console.log("Popup script loaded");

  // Check if side panel is already open
  chrome.runtime.sendMessage({ action: "checkSidePanel" });

  /**
   * Updates the status message
   * @param {string} mainMessage - The main status message
   * @param {string} subMessage - The secondary status message
   * @param {boolean} isError - Whether this is an error message
   */
  function updateStatus(mainMessage, subMessage = "", isError = false) {
    const subStyle = isError ? STATUS_STYLES.ERROR : STATUS_STYLES.INFO;
    statusDiv.innerHTML = `
      <div style="${STATUS_STYLES.SUCCESS}">${mainMessage}</div>
      ${subMessage ? `<div style="${subStyle}">${subMessage}</div>` : ""}
    `;
  }

  /**
   * Attempts to open the side panel using available methods
   * @param {Object} tab - The current browser tab
   */
  async function openSidePanel(tab) {
    console.log("Automatically opening side panel");
    updateStatus("✓ Content validated successfully!", "Opening side panel...");

    try {
      // Method 1: Using chrome.sidePanel.open API
      await chrome.sidePanel.open({ windowId: tab.windowId });
      console.log("Side panel opened via sidePanel.open API");
      updateStatus("✓ Content validated successfully!", "Side panel opened");
    } catch (error) {
      console.log("Could not open side panel via API, trying method 2");

      // Method 2: Using chrome.runtime.sendMessage
      chrome.runtime.sendMessage({ action: "openSidePanel" }, (response) => {
        console.log("Side panel message sent:", response);
        if (response && response.success) {
          updateStatus(
            "✓ Content validated successfully!",
            "Side panel requested"
          );
        } else {
          const errorMsg =
            'Could not open side panel automatically. Right-click the extension icon and select "Open side panel"';
          updateStatus("✓ Content validated successfully!", errorMsg, true);
        }
      });
    }
  }

  summarizeBtn.addEventListener("click", async () => {
    // Prevent multiple clicks
    if (isProcessing) {
      console.log("Already processing a request, ignoring click");
      return;
    }

    try {
      isProcessing = true;
      statusDiv.textContent = "Scraping text content...";

      // Get the active tab
      const [tab] = await chrome.tabs.query({
        active: true,
        currentWindow: true,
      });

      // Check if the URL is a chrome:// URL
      if (tab.url.startsWith("chrome://")) {
        throw new Error(
          "This extension cannot be used on Chrome internal pages (chrome:// URLs). Please try it on a regular webpage."
        );
      }

      // Ensure content script is injected
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ["content.js"],
      });

      // Send message to content script to scrape the page
      const response = await chrome.tabs.sendMessage(tab.id, {
        action: "scrape",
      });

      if (!response || !response.content) {
        throw new Error("No content received from content script");
      }

      statusDiv.textContent = "Validating content...";

      // Send the content to the backend
      const validationResponse = await fetch(
        "http://localhost:8000/summarize",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ content: response.content }),
        }
      );

      if (!validationResponse.ok) {
        throw new Error(`HTTP error! status: ${validationResponse.status}`);
      }

      const validationData = await validationResponse.json();

      // Store the validation result in chrome.storage
      await chrome.storage.local.set({
        validationData,
        scrapedContent: response.content,
        activeTab: "medical-tab", // Ensure medical tab is active
        lastUpdate: Date.now(), // Add timestamp for freshness check
      });

      // Open the side panel
      await openSidePanel(tab);
    } catch (error) {
      console.error("Error:", error);
      statusDiv.textContent = `Error: ${error.message}. Please check the console for details.`;
    } finally {
      isProcessing = false;
    }
  });
}); 