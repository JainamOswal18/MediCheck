chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'scrape') {
    // Get only the text content of the page
    const content = {
      title: document.title,
      text: document.body.innerText,
      url: window.location.href,
      metadata: {
        description:
          document.querySelector('meta[name="description"]')?.content || "",
        keywords:
          document.querySelector('meta[name="keywords"]')?.content || "",
        author: document.querySelector('meta[name="author"]')?.content || "",
        ogTitle:
          document.querySelector('meta[property="og:title"]')?.content || "",
        ogDescription:
          document.querySelector('meta[property="og:description"]')?.content ||
          "",
        ogImage:
          document.querySelector('meta[property="og:image"]')?.content || "",
      },
    };

    // Send the content back to the popup
    sendResponse({ content });
  }
  return true; // Required for async response
}); 