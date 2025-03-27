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
  const summaryContent = document.getElementById("summary-content");
  const modeToggle = document.querySelector(".mode-toggle"); // Select the toggle button
  const body = document.body;

  // Get the summary from storage
  chrome.storage.local.get(["summary"], function (result) {
    if (result.summary) {
      summaryContent.innerHTML = result.summary;
    } else {
      summaryContent.innerHTML =
        '<div class="error">No summary available. Please generate a summary first.</div>';
    }
  });

  // Function to toggle theme
  function toggleTheme() {
    body.classList.toggle("light-mode");
    if (body.classList.contains("light-mode")) {
      modeToggle.textContent = "Dark Mode";
      chrome.storage.local.set({ theme: "light" }); // Save preference
    } else {
      modeToggle.textContent = "Light Mode";
      chrome.storage.local.set({ theme: "dark" }); // Save preference
    }
  }

  // Check for saved theme preference on page load
  chrome.storage.local.get(["theme"], function (result) {
    if (result.theme === "light") {
      body.classList.add("light-mode");
      modeToggle.textContent = "Dark Mode";
    } else {
      body.classList.remove("light-mode");
      modeToggle.textContent = "Light Mode";
    }
  });

  // Event listener for theme toggle button
  if (modeToggle) {
    modeToggle.addEventListener("click", toggleTheme);
  }
});
