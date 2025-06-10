# 🌙 Esoteric AI Agent - Web API Guide

## Quick Start

### 1. Start the Web API Server
```bash
# From project root directory
python start_web_api.py
```

The server will start on `http://localhost:8000`

### 2. Access API Documentation
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Key Endpoints

### 🌐 Browser Compatibility
```bash
# Standard web assets (all return 200 OK)
curl "http://localhost:8000/favicon.ico"
curl "http://localhost:8000/apple-touch-icon.png"
curl "http://localhost:8000/robots.txt"
curl "http://localhost:8000/manifest.json"
```

### 💬 Chat with the Agent
```bash
# Simple chat (creates new session)
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the current date?"}'

# Chat with existing session
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the moon illumination percentage?", "session_id": "your-session-id"}'
```

### 🌙 Get Lunar Information
```bash
curl "http://localhost:8000/lunar"
```

### 📊 System Status
```bash
curl "http://localhost:8000/status"
```

### 🎯 Manage Domains
```bash
# List domains
curl "http://localhost:8000/domains"

# Enable a domain
curl -X POST "http://localhost:8000/domains/numerology/toggle?enable=true"

# Disable a domain  
curl -X POST "http://localhost:8000/domains/numerology/toggle?enable=false"
```

### 📝 Session Management
```bash
# List all sessions
curl "http://localhost:8000/sessions"

# Get session history
curl "http://localhost:8000/sessions/{session-id}/history"
```

### 🔧 System Commands
```bash
# Execute system commands
curl -X POST "http://localhost:8000/command" \
  -H "Content-Type: application/json" \
  -d '{"command": "stats"}'
```

## Testing the API

Run the test script to verify everything works:
```bash
python test_web_api.py
```

## Response Format

### Chat Response
```json
{
  "response": "Today is June 10, 2025. May this day bring you clarity and insight on your path.",
  "session_id": "abc12345-6789-def0-1234-567890abcdef",
  "message_type": "logical",
  "rag_used": false,
  "cache_hit": false,
  "timestamp": "2025-06-10T12:00:00.000Z"
}
```

### System Status
```json
{
  "active_domains": ["lunar", "ifs"],
  "available_domains": ["lunar", "ifs", "numerology", "astrology", "crystals", "tarot", "archetypes"],
  "total_documents": 1234,
  "cache_size": 56,
  "memory_enabled": {
    "short_term": true,
    "medium_term": true
  },
  "lunar_info": "🌕 Full Moon (99.6% illuminated) on June 10, 2025..."
}
```

## Features Preserved

✅ **All CLI Features Available**:
- Domain management
- Memory systems (short-term, medium-term)
- Session persistence  
- Q&A cache optimization
- Lunar information integration
- Command system

✅ **Web-Specific Enhancements**:
- RESTful API endpoints
- JSON request/response format
- CORS support for frontend integration
- Session management via API
- Health monitoring
- Comprehensive error handling
- Browser compatibility (favicon, touch icons, robots.txt)
- Progressive Web App manifest
- Professional error responses with metadata

## Next Steps

1. **Frontend Integration**: Use these endpoints to build a React/Vue.js chat interface
2. **Mobile App**: The REST API can be consumed by mobile applications
3. **Authentication**: Ready for Auth0 integration when needed
4. **Scaling**: FastAPI supports async operations and can be deployed with multiple workers

The web API preserves all the sophisticated features of your CLI system while making it accessible via HTTP for web and mobile applications. 