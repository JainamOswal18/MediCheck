document.addEventListener('DOMContentLoaded', function() {
  const summarizeBtn = document.getElementById('summarizeBtn');
  const statusDiv = document.getElementById('status');

  summarizeBtn.addEventListener('click', async () => {
    try {
      statusDiv.textContent = 'Generating summary...';
      
      // Get the active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // Ensure content script is injected
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
      });
      
      // Send message to content script to scrape the page
      const response = await chrome.tabs.sendMessage(tab.id, { action: 'scrape' });
      
      if (response && response.content) {
        console.log('Content scraped successfully:', response.content);
        
        // Send the content to the backend
        const summaryResponse = await fetch('http://localhost:8000/summarize', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content: response.content })
        });

        if (!summaryResponse.ok) {
          throw new Error(`HTTP error! status: ${summaryResponse.status}`);
        }

        const summaryData = await summaryResponse.json();
        console.log('Summary received:', summaryData);
        
        // Store the summary in chrome.storage
        await chrome.storage.local.set({ summary: summaryData.summary });
        
        // Open the sidebar
        await chrome.sidePanel.open({ windowId: tab.windowId });
        
        statusDiv.textContent = 'Summary generated! Check the sidebar.';
      } else {
        throw new Error('No content received from content script');
      }
    } catch (error) {
      console.error('Detailed error:', error);
      statusDiv.textContent = `Error: ${error.message}. Please check the console for details.`;
    }
  });
}); 