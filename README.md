# 🌙 Esoteric Vectors - Advanced Multi-Agent RAG System

A sophisticated esoteric AI agent with dual-personality architecture, specialized Q&A caching, domain-aware RAG retrieval, and comprehensive spiritual knowledge base.

## 🎯 Product Vision

**Esoteric Vectors** is an intelligent spiritual companion that combines the wisdom of ancient traditions with modern AI technology. The system features dual agents - a compassionate therapist for emotional support and a structured teacher for knowledge delivery - both enhanced with specialized esoteric knowledge across multiple spiritual domains.

## ✨ Key Features

### 🤖 **Dual-Agent Architecture**
- **Therapist Agent**: Emotional support with warm, intuitive guidance
- **Logical Agent**: Structured teaching with clear explanations
- **Intelligent Routing**: Automatic classification between emotional and logical queries

### ⚡ **Advanced Caching System**
- **Q&A Cache**: Lightning-fast responses for direct question matches (199 Q&A pairs)
- **Negative Intent Detection**: Prevents cache bypass for semantically opposite queries
- **Domain Filtering**: Targeted retrieval based on active knowledge domains

### 🎯 **Domain-Aware Knowledge**
- **Lunar Wisdom**: Moon phases, cosmic timing, lunar influences (40 Q&As)
- **Internal Family Systems**: IFS therapy, parts work, psychological healing (30 Q&As)
- **Crystal Healing**: Crystal properties, energy work, formations (40 Q&As)
- **Astrology**: Planetary influences, astrological concepts (40 Q&As)
- **Additional Domains**: Tarot, numerology, shadow work, archetypes

### 🛡️ **Safety & Intelligence**
- **Semantic Domain Detection**: Suggests relevant domain activation
- **Context-Aware Responses**: Maintains conversation continuity
- **Performance Analytics**: Comprehensive statistics and monitoring

## 📁 Project Structure

```
esoteric-vectors/
├── src/                              # Source code
│   ├── main.py                       # Multi-agent system with LangGraph
│   ├── core/                         # Core RAG functionality
│   │   ├── contextual_rag.py         # Main RAG system with domain filtering
│   │   ├── domain_manager.py         # Domain activation/deactivation
│   │   └── stats_collector.py        # Performance monitoring
│   ├── cache/                        # Caching systems
│   │   ├── qa_cache.py               # Q&A cache with question-based retrieval
│   │   └── negative_intent_detector.py # Safety filtering
│   └── utils/                        # Utility modules
│       ├── semantic_domain_detector.py # Domain suggestion system
│       ├── relevance_evaluator.py    # RAG relevance scoring
│       └── lunar_calculator.py       # Lunar phase calculations
├── data/                             # Data storage
│   ├── chroma_db/                    # Vector databases
│   │   ├── qa_cache/                 # Q&A-specific vectorstore
│   │   └── [domain_collections]/     # Domain-specific collections
│   ├── qa/                           # Q&A documents
│   │   ├── lunar_qa.md               # Lunar wisdom Q&As
│   │   ├── ifs_qa.md                 # IFS therapy Q&As
│   │   ├── crystals_qa.md            # Crystal healing Q&As
│   │   └── astrology_qa.md           # Astrology Q&As
│   └── document_registry.json        # Document tracking registry
├── docs/                             # Knowledge base documents
│   ├── Lunar_overview.md             # Comprehensive lunar wisdom
│   ├── ifs.md                        # Internal Family Systems guide
│   ├── crystals.md                   # Crystal healing knowledge
│   ├── astrology.md                  # Astrological concepts
│   ├── tarot.md                      # Tarot symbolism and meanings
│   ├── archetypes.md                 # Jungian archetypes
│   ├── shadow.md                     # Shadow work practices
│   └── Numerology.md                 # Numerological principles
├── tests/                            # Test suites
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── performance/                  # Performance benchmarks
├── config/                           # Configuration
│   ├── requirements_rag.txt          # Python dependencies
│   └── pyproject.toml               # Project configuration
├── document_manager.py               # Document management utility
└── run.py                           # Application entry point
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- OpenAI API key
- Google Gemini API key

### 1. Clone & Setup Environment
```bash
git clone <repository-url>
cd esoteric-vectors

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r config/requirements_rag.txt
```

### 3. Configure Environment
```bash
# Copy and edit environment file
cp .env.example .env

# Add your API keys to .env:
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_gemini_key_here
```

### 4. Initialize Knowledge Base (Optional)
```bash
# Load documents into vector database
python document_manager.py
```

## 🎮 Usage

### Start the Application
```bash
# Method 1: Direct execution
python run.py

# Method 2: From src directory
cd src && python main.py
```

### Interactive Commands
```bash
# System commands
exit                          # Exit the application
stats                         # Show comprehensive system statistics
domains                       # Show active/available domains

# Domain management
domains enable <domain>       # Activate knowledge domain
domains disable <domain>      # Deactivate knowledge domain

# Cache management
cache clear                   # Clear RAG caches
qa cache clear               # Clear Q&A cache specifically
cache stats clear            # Reset query statistics
```

### Example Interactions
```bash
# Emotional support (routes to Therapist Agent)
"I'm feeling anxious and disconnected lately"
"I'm struggling with a difficult relationship"

# Knowledge queries (routes to Logical Agent)  
"Explain the phases of the moon"
"How does IFS therapy work?"
"What are the properties of amethyst?"

# Domain activation suggestions
"Tell me about tarot cards"  # Suggests activating tarot domain
```

## 📚 Document Management

### Adding Standard Documents
```bash
# Using document manager
python document_manager.py

# Interactive mode - follow prompts to:
# 1. Add single documents
# 2. Batch add multiple documents
# 3. Update existing documents
# 4. Remove documents
```

### Adding Q&A Documents
Q&A documents follow a specific format for optimal caching:

```markdown
## 1. Question here?

Answer content here...

---

## 2. Another question?

Another answer...
```

**Steps to add Q&A documents:**
1. Create/edit Q&A file in `data/qa/` directory
2. Use the document manager or run update script:
```bash
# Update Q&A cache after modifications
python -c "
import sys; sys.path.append('src')
from cache.qa_cache import QACache
qa = QACache()
qa.clear_cache()
qa.add_qa_document('data/qa/your_file.md', 'domain_name')
"
```

### Document Types
- **Standard Documents** (`docs/`): Narrative content, chunked at 1000 chars
- **Q&A Documents** (`data/qa/`): Question-answer pairs, chunked at 2000 chars
- **Domain Classification**: lunar, ifs, crystals, astrology, tarot, numerology, archetypes

## 🔧 System Architecture

### Multi-Agent Flow
```
User Input → Classifier → Router → [Therapist|Logical] Agent → Response
                ↓
        RAG Decision → Q&A Cache → RAG Fallback
```

### Caching Strategy
1. **Q&A Cache Hit** (⚡): Direct answer from cached Q&A pairs
2. **Negative Intent Bypass** (🛡️): Skip cache for opposite-meaning queries  
3. **RAG Retrieval** (🔍): Full vector search with domain filtering
4. **Domain Blocked** (🚫): Domain-specific blocking messages

### Performance Indicators
- ⚡ Q&A cache hit (fastest)
- 🛡️ Negative intent bypass (security)
- 🔍 RAG retrieval (comprehensive)
- 🚫 Domain blocked (controlled access)

## 📊 Key Components Deep Dive

### Core Systems
- **`main.py`**: LangGraph-based multi-agent orchestration
- **`contextual_rag.py`**: Domain-aware RAG with ChromaDB integration
- **`qa_cache.py`**: Specialized Q&A caching with question-only embeddings
- **`domain_manager.py`**: Dynamic domain activation/deactivation

### Intelligence Layers
- **`semantic_domain_detector.py`**: Suggests relevant domain activation
- **`negative_intent_detector.py`**: Prevents cache poisoning attacks
- **`relevance_evaluator.py`**: Scores RAG retrieval quality
- **`stats_collector.py`**: Comprehensive performance monitoring

### Utilities
- **`document_manager.py`**: Parallel document processing and management
- **`lunar_calculator.py`**: Astronomical calculations for lunar wisdom

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests  
python -m pytest tests/integration/

# Performance benchmarks
python -m pytest tests/performance/
```

## 📈 Performance Metrics

### Current Statistics
- **Q&A Cache**: 199 question-answer pairs across 4 domains
- **Vector Database**: 1,170+ document chunks
- **Cache Hit Rate**: 85%+ similarity threshold
- **Response Time**: 
  - Q&A Cache: ~0.1-0.3s
  - RAG Retrieval: ~2-6s
  - Domain Detection: ~0.5s

### Optimization Features
- **Parallel Processing**: Multi-threaded document loading
- **Batch Operations**: Efficient vectorstore updates
- **Memory Management**: Chunked processing for large documents
- **Persistent Caching**: Survives application restarts

## 🌟 Advanced Features

### Contextual Understanding
- **Conversation Memory**: Maintains context within sessions
- **Domain Awareness**: Filters knowledge by active domains
- **Intent Classification**: Distinguishes emotional vs. logical needs

### Safety & Reliability
- **Negative Intent Protection**: Prevents semantic manipulation
- **Error Recovery**: Graceful fallbacks for failed operations
- **Data Validation**: Ensures document integrity and consistency

### Extensibility
- **Plugin Architecture**: Easy addition of new domains
- **Configurable Thresholds**: Adjustable similarity and performance settings
- **API Integration**: Multiple LLM providers (OpenAI, Google Gemini)

## 🔮 Future Enhancements

- **Long-term Memory**: User conversation history and preferences
- **Voice Interface**: Audio input/output capabilities
- **Mobile App**: Cross-platform mobile application
- **Community Features**: Shared wisdom and collaborative learning

---

*Built with LangChain, ChromaDB, LangGraph, OpenAI, and Google Gemini - Bridging ancient wisdom with modern AI.* 