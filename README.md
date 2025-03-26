# Web Page Summarizer Chrome Extension

A Chrome extension that uses Gemini AI to generate summaries of web pages.

## Features

- Scrapes webpage content when the extension icon is clicked
- Sends content to a FastAPI backend for processing
- Uses Gemini AI to generate concise summaries
- Displays summaries in a Chrome sidebar

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- A Google API key for Gemini AI (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/JainamOswal18/MediCheck.git
cd chrome-extension
```

### 2. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory:
   ```bash
   # backend/.env
   GOOGLE_API_KEY=your_api_key_here
   ```
   Replace `your_api_key_here` with your actual Google API key.

5. Start the FastAPI server:
   ```bash
   python main.py
   ```
   The server will start at `http://localhost:8000`

### 3. Chrome Extension Setup

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" in the top right corner
3. Click "Load unpacked" and select the `frontend` directory from the project
4. The extension icon should appear in your Chrome toolbar

### 4. Testing the Extension

1. Make sure the backend server is running (you should see "Starting FastAPI server..." in the terminal)
2. Navigate to any webpage you want to summarize
3. Click the extension icon in your Chrome toolbar
4. Click "Generate Summary" in the popup
5. The summary will appear in the sidebar

## Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure the FastAPI server is running
   - Check if the server is accessible at `http://localhost:8000`
   - Verify your Google API key is correctly set in the `.env` file

2. **Extension Not Working**
   - Check Chrome DevTools console for errors (right-click extension popup → Inspect)
   - Ensure all permissions are granted in `chrome://extensions/`
   - Try reloading the extension

3. **Content Script Error**
   - Make sure you're on a webpage (not a chrome:// page)
   - Check if the content script is properly injected (visible in Chrome DevTools)

### Debugging

1. **Backend Logs**
   - Check the terminal running the FastAPI server for detailed logs
   - Look for any error messages or exceptions

2. **Extension Logs**
   - Open Chrome DevTools (F12)
   - Go to the Console tab
   - Look for any error messages when using the extension

## Development Notes

- The extension uses Manifest V3
- The backend uses FastAPI and Gemini AI
- The frontend is built with vanilla JavaScript
- Content is limited to 30,000 characters for processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 