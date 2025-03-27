document.addEventListener('DOMContentLoaded', function() {
  const summarizeBtn = document.getElementById('summarizeBtn');
  const statusDiv = document.getElementById('status');
  let isProcessing = false;

  console.log("Popup script loaded");

  // Check if side panel is already open
  chrome.runtime.sendMessage({ action: "checkSidePanel" }, (response) => {
    console.log("Side panel status check:", response);
  });

  summarizeBtn.addEventListener("click", async () => {
    // Prevent multiple clicks
    if (isProcessing) {
      console.log("Already processing a request, ignoring click");
      return;
    }

    try {
      isProcessing = true;
      statusDiv.textContent = "Scraping text content...";
      console.log("Scrape button clicked");

      // Get the active tab
      const [tab] = await chrome.tabs.query({
        active: true,
        currentWindow: true,
      });

      console.log("Active tab:", tab.url);

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
      console.log("Content script injected");

      // Send message to content script to scrape the page
      const response = await chrome.tabs.sendMessage(tab.id, {
        action: "scrape",
      });
      console.log("Received response from content script");

      if (response && response.content) {
        console.log(
          "Text content scraped successfully, content structure:",
          Object.keys(response.content)
        );
        statusDiv.textContent = "Validating content...";

        // Send the content to the backend
        console.log("Sending content to backend for validation");
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
        console.log("Validation data received from backend:", validationData);
        console.log("Validation data structure:", {
          hasData: !!validationData,
          dataType: typeof validationData,
          hasSummary: validationData && "summary" in validationData,
          hasValidationResults:
            validationData && "validation_results" in validationData,
          validationResultsCount:
            validationData && validationData.validation_results
              ? validationData.validation_results.length
              : 0,
        });

        // Store the validation result in chrome.storage
        console.log("Storing validation data in chrome.storage");
        await chrome.storage.local.set({
          validationData: validationData,
          scrapedContent: response.content,
          activeTab: "medical-tab", // Ensure medical tab is active
          lastUpdate: Date.now(), // Add timestamp for freshness check
        });

        // Show a simple success message with button to open side panel
        statusDiv.innerHTML = `
          <div style="color: #4aff91; font-weight: bold; margin-bottom: 10px;">✓ Content validated successfully!</div>
          <div id="sidepanel-instructions">
            <button id="open-sidepanel-btn" style="
              background-color: #5d3fdd; 
              color: white; 
              border: none; 
              padding: 8px 12px; 
              border-radius: 4px; 
              cursor: pointer;
              margin-bottom: 10px;
              width: 100%;
            ">Open Side Panel</button>
            <div style="font-size: 12px; color: #999;">
              If the button doesn't work, right-click the extension icon and select "Open side panel"
            </div>
          </div>
        `;

        // Add event listener to the button
        document
          .getElementById("open-sidepanel-btn")
          .addEventListener("click", async () => {
            try {
              console.log("Open side panel button clicked");

              // Try both methods
              try {
                // Method 1: Using chrome.sidePanel.open
                await chrome.sidePanel.open({ windowId: tab.windowId });
                console.log("Side panel opened via sidePanel.open API");
              } catch (error) {
                console.log(
                  "Could not open side panel via API, trying method 2"
                );

                // Method 2: Using chrome.runtime.sendMessage
                chrome.runtime.sendMessage(
                  { action: "openSidePanel" },
                  (response) => {
                    console.log("Side panel message sent:", response);
                  }
                );
              }

              // Update button text to show success
              document.getElementById("open-sidepanel-btn").textContent =
                "✓ Panel Requested";
              document.getElementById(
                "open-sidepanel-btn"
              ).style.backgroundColor = "#4aff91";
            } catch (error) {
              console.error("Error opening side panel:", error);
              document.getElementById("open-sidepanel-btn").textContent =
                "Could not open panel";
              document.getElementById(
                "open-sidepanel-btn"
              ).style.backgroundColor = "#ff4a4a";
            }
          });
      } else {
        throw new Error("No content received from content script");
      }
    } catch (error) {
      console.error("Detailed error:", error);
      statusDiv.textContent = `Error: ${error.message}. Please check the console for details.`;
    } finally {
      isProcessing = false;
    }
  });
}); 