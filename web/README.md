# 🌙 Esoteric AI Agent - Web Chat Interface

A simple, intuitive web interface for the Esoteric AI Agent chat system.

## Features

✅ **Chat Interface**
- Real-time messaging with the AI agent
- Message history with timestamps
- Typing indicators and message metadata
- Error handling and status feedback

✅ **Domain Management** 
- Toggle knowledge domains on/off
- View active/inactive domains
- Real-time domain status updates

✅ **Memory Settings**
- Control short-term and medium-term memory
- View memory status indicators
- Execute memory commands

✅ **Session Management**
- Create new chat sessions
- Switch between recent sessions
- View session metadata and message counts

✅ **Lunar Information**
- Current lunar phase display
- Detailed lunar data and timing
- Lunar guidance and timing insights

## Getting Started

### 1. Start the Backend API

```bash
# Make sure your Esoteric AI Agent API is running
python start_web_api.py
```

The API should be running on `http://localhost:8000`

### 2. Open the Web Interface

Simply open `index.html` in your web browser:

```bash
# Option 1: Open directly
open web/index.html

# Option 2: Use a simple HTTP server (recommended)
cd web
python -m http.server 8080
# Then visit http://localhost:8080
```

### 3. Start Chatting

- Type your message in the input field
- Press Enter or click Send
- The AI will respond with guidance, insights, or answers
- Use the tabs to access Settings and Lunar information

## Interface Overview

### Chat Tab
- **Main chat area**: View conversation history
- **Input field**: Type your messages
- **Message metadata**: See if RAG was used, cache hits, and message types
- **Sidebar**: Session info, system status, active domains, recent sessions

### Settings Tab
- **Memory Settings**: Toggle short-term and medium-term memory
- **Knowledge Domains**: Enable/disable specific knowledge areas
- **System Commands**: Execute system commands and refresh data

### Lunar Tab
- **Current Phase**: See today's lunar phase and illumination
- **Detailed Data**: Days from new moon, illumination percentage
- **Lunar Guidance**: Contextual guidance based on current moon phase

## API Integration

The web interface connects to these API endpoints:

- `GET /status` - System status and configuration
- `GET /lunar` - Current lunar information
- `GET /sessions` - List of chat sessions
- `POST /chat` - Send messages to the AI
- `POST /domains/{domain}/toggle` - Toggle knowledge domains
- `POST /command` - Execute system commands

## Customization

### Styling
The interface uses Tailwind CSS loaded via CDN. You can customize colors and styling by modifying the classes in `app.js`.

### API Base URL
Update the `API_BASE` constant in `app.js` if your backend runs on a different port:

```javascript
const API_BASE = 'http://localhost:8000'; // Change this if needed
```

### Features
The React application is built using:
- React 18 (via CDN)
- Tailwind CSS (via CDN)
- Babel Standalone (for JSX compilation)

## Development

### Local Development Server
For better development experience with hot reloading:

```bash
# Install a simple HTTP server
npm install -g http-server

# Serve the web directory
cd web
http-server -p 8080 -c-1

# Visit http://localhost:8080
```

### Production Deployment
For production, you may want to:
1. Bundle the React code with a proper build system
2. Use a web server like Nginx or Apache
3. Enable HTTPS
4. Configure CORS properly on the backend

## Troubleshooting

### Connection Issues
- Ensure the backend API is running on `http://localhost:8000`
- Check browser console for CORS errors
- Verify the API endpoints are accessible

### CORS Issues
If you encounter CORS errors, the backend already includes CORS middleware for common development ports:
- `http://localhost:3000`
- `http://localhost:8080`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:8080`
- `http://127.0.0.1:5173`

### Browser Compatibility
The interface requires a modern browser with:
- ES6+ support
- Fetch API
- CSS Grid and Flexbox

## Architecture

```
web/
├── index.html          # Main HTML file with React setup
├── app.js             # React application with all components
└── README.md          # This file
```

The application is built as a single-page React app that communicates with the FastAPI backend via REST endpoints. It uses functional components with hooks for state management and follows React best practices for a smooth user experience. 