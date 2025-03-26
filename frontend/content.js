chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'scrape') {
    // Get the main content of the page
    const content = {
      title: document.title,
      text: document.body.innerText,
      url: window.location.href
    };
    
    // Send the content back to the popup
    sendResponse({ content });
  }
  return true; // Required for async response
}); 