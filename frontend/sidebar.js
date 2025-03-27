// document.addEventListener('DOMContentLoaded', function() {
//   const summaryContent = document.getElementById('summary-content');

//   // Get the summary from storage
//   chrome.storage.local.get(['summary'], function(result) {
//     if (result.summary) {
//       summaryContent.innerHTML = result.summary;
//     } else {
//       summaryContent.innerHTML = '<div class="error">No summary available. Please generate a summary first.</div>';
//     }
//   });
// });

document.addEventListener("DOMContentLoaded", function () {
  // Elements
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabContents = document.querySelectorAll(".tab-content");
  const summaryContent = document.getElementById("summary-content");
  const medicalSummary = document.getElementById("medical-summary");
  const validationResults = document.getElementById("validation-results");
  const modeToggle = document.querySelector(".mode-toggle");
  const body = document.body;

  console.log("Sidebar script loaded - DOM Content Loaded");

  // Debug element presence
  console.log("Elements found:", {
    tabButtons: tabButtons.length,
    tabContents: tabContents.length,
    summaryContent: !!summaryContent,
    medicalSummary: !!medicalSummary,
    validationResults: !!validationResults,
    modeToggle: !!modeToggle,
  });

  // Set up tab switching
  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      console.log("Tab clicked:", button.getAttribute("data-tab"));
      switchToTab(button.getAttribute("data-tab"));
    });
  });

  function switchToTab(tabId) {
    // Remove active class from all tabs
    tabButtons.forEach((btn) => btn.classList.remove("active"));
    tabContents.forEach((content) => content.classList.remove("active"));

    // Add active class to the selected tab
    const selectedButton = document.querySelector(
      `.tab-button[data-tab="${tabId}"]`
    );
    if (selectedButton) {
      selectedButton.classList.add("active");
    }

    const selectedContent = document.getElementById(tabId);
    if (selectedContent) {
      selectedContent.classList.add("active");
    }

    // Save active tab preference
    chrome.storage.local.set({ activeTab: tabId });
  }

  // Initialize data loading
  loadDataAndSetupSidebar();

  // Add listener for storage changes to update the sidebar in real-time
  chrome.storage.onChanged.addListener(function (changes, namespace) {
    console.log("Storage changes detected:", Object.keys(changes));
    if (
      namespace === "local" &&
      (changes.validationData || changes.scrapedContent)
    ) {
      console.log(
        "Validation data or scraped content changed, refreshing sidebar"
      );
      loadDataAndSetupSidebar();
    }
  });

  function loadDataAndSetupSidebar() {
    // Load saved data and populate the sidebar
    chrome.storage.local.get(
      ["validationData", "scrapedContent", "activeTab", "theme"],
      function (result) {
        console.log("Chrome storage data retrieved:", {
          hasValidationData: !!result.validationData,
          hasScrapedContent: !!result.scrapedContent,
          activeTab: result.activeTab,
          theme: result.theme,
        });

        if (result.validationData) {
          console.log("Validation data:", result.validationData);
        }

        // Set theme
        if (result.theme === "light") {
          body.classList.add("light-mode");
          modeToggle.textContent = "Dark Mode";
        } else {
          body.classList.remove("light-mode");
          modeToggle.textContent = "Light Mode";
        }

        // Set active tab
        let tabToShow = result.activeTab;
        if (!tabToShow) {
          // Default to medical-tab if we have validation data, otherwise summary-tab
          tabToShow = result.validationData ? "medical-tab" : "summary-tab";
        }

        console.log("Setting active tab to:", tabToShow);
        switchToTab(tabToShow);

        // Display validation data if available
        if (result.validationData) {
          console.log("Displaying validation results");
          displayValidationResults(result.validationData);
        } else {
          console.log("No validation data available");
          medicalSummary.textContent =
            "No validation data available. Please validate content first.";
          validationResults.innerHTML =
            '<div class="error">No validation results available.</div>';
        }

        // Display source content
        if (result.scrapedContent) {
          console.log("Displaying source content");
          const sourceContent = result.scrapedContent;
          summaryContent.innerHTML = `
          <h3>${sourceContent.title || "No Title"}</h3>
          <p><strong>Source:</strong> <a href="${
            sourceContent.url || "#"
          }" target="_blank">${sourceContent.url || "Unknown Source"}</a></p>
          <div class="content-preview">
            ${(sourceContent.text || "No content available").substring(
              0,
              300
            )}...
          </div>
        `;
        } else {
          console.log("No source content available");
          summaryContent.innerHTML =
            '<div class="error">No content available. Please scrape a webpage first.</div>';
        }
      }
    );
  }

  // Function to display validation results
  function displayValidationResults(data) {
    console.log("Processing validation results:", data);
    // Display the summary
    if (data.summary) {
      medicalSummary.textContent = data.summary;
      console.log("Set medical summary");
    } else {
      medicalSummary.textContent = "No summary available.";
      console.log("No summary in validation data");
    }

    // Display validation results
    if (data.validation_results && data.validation_results.length > 0) {
      console.log(`Found ${data.validation_results.length} validation results`);
      let resultsHTML = "";

      data.validation_results.forEach((result) => {
        resultsHTML += `
          <div class="validation-result">
            <div class="incorrect-text">${result.incorrect_text}</div>
            <div class="correct-text">${result.correct_text}</div>
          </div>
        `;
      });

      validationResults.innerHTML = resultsHTML;
      console.log("Validation results HTML set");
    } else {
      console.log("No validation results array or empty array");
      validationResults.innerHTML =
        "<p>No issues found. All information appears to be accurate.</p>";
    }
  }

  // Event listener for theme toggle button
  if (modeToggle) {
    modeToggle.addEventListener("click", function () {
      body.classList.toggle("light-mode");
      if (body.classList.contains("light-mode")) {
        modeToggle.textContent = "Dark Mode";
        chrome.storage.local.set({ theme: "light" });
      } else {
        modeToggle.textContent = "Light Mode";
        chrome.storage.local.set({ theme: "dark" });
      }
    });
  }
});
