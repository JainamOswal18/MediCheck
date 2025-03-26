document.addEventListener('DOMContentLoaded', function() {
  const summaryContent = document.getElementById('summary-content');
  
  // Get the summary from storage
  chrome.storage.local.get(['summary'], function(result) {
    if (result.summary) {
      summaryContent.innerHTML = result.summary;
    } else {
      summaryContent.innerHTML = '<div class="error">No summary available. Please generate a summary first.</div>';
    }
  });
}); 