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
  const contentContainer = document.querySelector(".content-container");

  console.log("Sidebar script loaded - DOM Content Loaded");

  // Initialize layout
  adjustLayout();

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

  // Adjust layout based on current viewport
  function adjustLayout() {
    if (!contentContainer) return;

    const headerSection = document.querySelector(".header-section");
    const tabButtons = document.querySelector(".tab-buttons");

    if (!headerSection || !tabButtons) return;

    const headerHeight = headerSection.offsetHeight;
    const tabsHeight = tabButtons.offsetHeight;
    const paddingHeight =
      parseInt(
        getComputedStyle(document.querySelector(".dashboard-container")).padding
      ) * 2;

    // Update CSS variables
    document.documentElement.style.setProperty(
      "--header-height",
      `${headerHeight}px`
    );
    document.documentElement.style.setProperty(
      "--tabs-height",
      `${tabsHeight}px`
    );

    // Set container height
    contentContainer.style.height = `calc(100vh - ${
      headerHeight + tabsHeight + paddingHeight + 30
    }px)`;

    // Ensure content areas have proper height
    document
      .querySelectorAll(".summary-section, .medical-section, .chat-section")
      .forEach((section) => {
        section.style.height = "100%";
      });

    console.log(
      `Adjusted layout - Header: ${headerHeight}px, Tabs: ${tabsHeight}px, Container height: ${contentContainer.style.height}`
    );
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

  function formatContentForDisplay(content) {
    if (!content) return "<p>No content available</p>";

    let html = "";

    // Format title with proper styling
    if (content.title) {
      html += `<h3 style="margin-bottom: 15px; color: var(--accent-pink);">${content.title}</h3>`;
    } else {
      html += `<h3 style="margin-bottom: 15px; color: var(--accent-pink);">Webpage Content</h3>`;
    }

    // Format URL
    if (content.url) {
      html += `<p style="margin-bottom: 20px;"><strong>Source:</strong> <a href="${content.url}" target="_blank" style="color: var(--accent-blue); text-decoration: underline;">${content.url}</a></p>`;
    }

    // Add a simple message about content validation instead of showing the full text
    html += `<div style="margin-top: 30px; padding: 20px; background-color: var(--bg-secondary); border-radius: 8px; text-align: center;">
      <p style="margin-bottom: 15px; font-size: 16px;">This content has been analyzed by our validation system.</p>
      <p style="color: var(--accent-blue);">View the <strong>Validation</strong> tab to see analysis results.</p>
    </div>`;

    return html;
  }

  function loadDataAndSetupSidebar() {
    // Show loading indicators in all tabs
    summaryContent.innerHTML =
      '<p style="text-align: center; margin-top: 20px;"><em>Loading content...</em></p>';
    medicalSummary.innerHTML =
      '<p style="text-align: center;"><em>Loading validation data...</em></p>';
    validationResults.innerHTML =
      '<p style="text-align: center;"><em>Loading validation results...</em></p>';

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
          summaryContent.innerHTML = formatContentForDisplay(
            result.scrapedContent
          );
        } else {
          console.log("No source content available");
          summaryContent.innerHTML =
            '<div class="error">No content available. Please scrape a webpage first.</div>';
        }

        // Adjust layout after content is loaded
        setTimeout(adjustLayout, 100);
      }
    );
  }

  // Function to display validation results
  function displayValidationResults(data) {
    console.log("Processing validation results:", data);
    // Display the summary
    if (data.summary) {
      medicalSummary.innerHTML = `<p style="line-height: 1.7; font-size: 16px;">${data.summary}</p>`;
      console.log("Set medical summary");
    } else {
      medicalSummary.textContent = "No summary available.";
      console.log("No summary in validation data");
    }

    // Display validation results
    if (data.validation_results && data.validation_results.length > 0) {
      console.log(`Found ${data.validation_results.length} validation results`);
      let resultsHTML = "";

      data.validation_results.forEach((result, index) => {
        resultsHTML += `
          <div class="validation-result" style="margin-bottom: 20px; padding: 15px;">
            <h4 style="margin-bottom: 10px; color: var(--accent-blue);">Issue #${
              index + 1
            }</h4>
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
        '<p style="padding: 15px; background-color: var(--bg-secondary); border-left: 3px solid var(--accent-green); color: var(--accent-green); font-weight: bold;">No issues found. All information appears to be accurate.</p>';
    }
  }

  // Event listener for theme toggle button
  if (modeToggle) {
    modeToggle.addEventListener("click", function () {
      // First, remove all transitions temporarily
      document.documentElement.style.setProperty("--transition-duration", "0s");

      // Toggle the theme
      body.classList.toggle("light-mode");

      // Update button text and store preference
      if (body.classList.contains("light-mode")) {
        modeToggle.textContent = "Dark Mode";
        chrome.storage.local.set({ theme: "light" });
      } else {
        modeToggle.textContent = "Light Mode";
        chrome.storage.local.set({ theme: "dark" });
      }

      // Force reflow to apply color changes immediately
      void document.body.offsetHeight;

      // Adjust layout after theme change
      setTimeout(adjustLayout, 100);
    });
  }

  // Debounced window resize handler
  let resizeTimeout;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(adjustLayout, 200);
  });
});
