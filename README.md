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
- Python 3.13+
- [UV package manager](https://docs.astral.sh/uv/) (recommended) or pip
- OpenAI API key
- Google Gemini API key

### 1. Clone & Setup Environment
```bash
git clone <repository-url>
cd esoteric-vectors

# Using UV (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Alternative: Using pip
# python -m venv .venv
# source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
# Using UV (recommended)
uv sync

# Alternative: Using pip
# pip install -r config/requirements_rag.txt
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

## 🛠️ Advanced Document Management Commands

### Document Manager CLI (`document_manager.py`)

The document manager provides comprehensive document processing with parallel contextualization and batch operations.

#### **Basic Commands**

```bash
# Add a single document
python document_manager.py add <filepath> --domain <domain>

# Add with contextualization (default: enabled)
python document_manager.py add docs/crystals.md --domain crystals

# Add without contextualization (faster, less optimal retrieval)
python document_manager.py add docs/crystals.md --domain crystals --no-contextualize

# Add Q&A document with specialized chunking
python document_manager.py add data/qa/lunar_qa.md --domain lunar --doc-type qa
```

#### **Batch Operations**

```bash
# Create batch file (JSON format)
cat > batch_docs.json << EOF
[
  {"filepath": "docs/astrology.md", "domain": "astrology"},
  {"filepath": "docs/tarot.md", "domain": "tarot"},
  {"filepath": "data/qa/crystals_qa.md", "domain": "crystals"}
]
EOF

# Process batch with parallel workers
python document_manager.py batch batch_docs.json

# Batch with custom settings
python document_manager.py batch batch_docs.json --workers 8 --batch-size 50 --no-contextualize
```

#### **Document Management**

```bash
# Update existing document
python document_manager.py update docs/ifs.md --domain ifs

# Remove document
python document_manager.py remove docs/old_file.md

# List all documents
python document_manager.py list

# List by domain
python document_manager.py list --domain lunar

# Get document information
python document_manager.py info docs/crystals.md
```

#### **Validation & Maintenance**

```bash
# Validate document integrity
python document_manager.py validate

# Validate specific domain
python document_manager.py validate --domain astrology

# Fix vectorstore inconsistencies
python document_manager.py fix

# Fix specific domain issues
python document_manager.py fix --domain crystals
```

#### **Advanced Configuration**

```bash
# Custom parallel processing
python document_manager.py add docs/large_file.md --domain lunar --workers 12

# Custom batch size for vectorstore operations
python document_manager.py add docs/file.md --domain ifs --batch-size 200

# Custom timeout for AI contextualization
python document_manager.py add docs/file.md --domain tarot --timeout 60.0
```

### Q&A Cache Management (`qa_cache.py`)

The Q&A cache provides specialized management for question-answer pairs with semantic similarity search.

#### **Programmatic Usage**

```python
import sys
sys.path.insert(0, 'src')
from cache.qa_cache import QACache

# Initialize Q&A cache
qa = QACache()

# Add single Q&A pair
qa.add_qa_pair(
    question="What is the meaning of the full moon?",
    answer="The full moon represents completion, manifestation, and peak energy...",
    domain="lunar",
    source="manual"
)

# Batch add Q&A pairs
qa_pairs = [
    {
        "question": "How do I cleanse crystals?",
        "answer": "Crystals can be cleansed using moonlight, sage, or running water...",
        "domain": "crystals",
        "source": "batch_import"
    },
    {
        "question": "What is shadow work?",
        "answer": "Shadow work involves integrating rejected aspects of the self...",
        "domain": "archetypes",
        "source": "batch_import"
    }
]
qa._add_documents_batch(qa_pairs, batch_size=50)

# Search Q&A cache
result = qa.search_qa("moon phases", active_domains=["lunar"], k=3)
if result:
    print(f"Question: {result['question']}")
    print(f"Answer: {result['answer']}")
    print(f"Similarity: {result['similarity']:.3f}")

# Get cache statistics
stats = qa.get_stats()
print(f"Total Q&A pairs: {stats['total_qa_pairs']}")
print(f"Hit rate: {stats['hit_rate']:.1f}%")
print(f"Average response time: {stats['avg_response_time']:.3f}s")

# Get collection information with health metrics
info = qa.get_collection_info()
print(f"Health status: {info['health']['hit_rate_status']}")
print(f"Domain distribution: {info['domain_distribution']}")

# Update collection metadata
qa.update_collection_metadata({
    "version": "1.3.0",
    "description": "Updated Q&A cache with enhanced features"
})

# Clear cache
qa.clear_cache()
```

#### **Command Line Utilities**

```bash
# Quick Q&A cache operations
python -c "
import sys; sys.path.insert(0, 'src')
from cache.qa_cache import QACache
qa = QACache()

# Show cache stats
stats = qa.get_stats()
print(f'Q&A Cache: {stats[\"total_qa_pairs\"]} pairs, {stats[\"hit_rate\"]:.1f}% hit rate')

# Show domain distribution
domains = qa.get_domain_stats()
for domain, count in domains.items():
    print(f'{domain}: {count} pairs')
"

# Clear Q&A cache
python -c "
import sys; sys.path.insert(0, 'src')
from cache.qa_cache import QACache
qa = QACache()
qa.clear_cache()
print('Q&A cache cleared')
"

# Test Q&A search
python -c "
import sys; sys.path.insert(0, 'src')
from cache.qa_cache import QACache
qa = QACache()
result = qa.search_qa('moon phases')
if result:
    print(f'Found: {result[\"question\"]} (similarity: {result[\"similarity\"]:.3f})')
else:
    print('No matching Q&A found')
"
```

#### **Integration with Main System**

```bash
# The Q&A cache is automatically used by the main system
python run.py

# Commands within the main system:
"What are moon phases?"           # May hit Q&A cache
"cache clear"                     # Clears all caches including Q&A
"qa cache clear"                  # Clears only Q&A cache
"stats"                          # Shows Q&A cache statistics
```

### Performance Optimization Tips

#### **Document Manager**
- **Contextualization**: Enabled by default for better retrieval, use `--no-contextualize` for speed
- **Parallel Workers**: Auto-configured based on CPU cores, adjust with `--workers` for I/O optimization
- **Batch Size**: Default 100 chunks per batch, increase for faster processing of large documents
- **Document Types**: Use `--doc-type qa` for Q&A documents to enable specialized chunking

#### **Q&A Cache**
- **Similarity Threshold**: Default 0.75, adjust in constructor for stricter/looser matching
- **Batch Operations**: Use `_add_documents_batch()` for bulk imports (50 pairs per batch recommended)
- **Domain Filtering**: Provide `active_domains` parameter for targeted searches
- **Health Monitoring**: Monitor hit rate and response time for cache effectiveness

#### **Best Practices**
1. **Document Organization**: Keep Q&A documents in `data/qa/` and narrative documents in `docs/`
2. **Domain Consistency**: Use consistent domain names across all documents
3. **Regular Validation**: Run `python document_manager.py validate` periodically
4. **Cache Monitoring**: Check Q&A cache hit rates and clear if performance degrades
5. **Batch Processing**: Use batch operations for multiple documents to leverage parallel processing

### 📋 Quick Reference

#### **Most Common Commands**

```bash
# Document Management
python document_manager.py add docs/new_file.md --domain crystals
python document_manager.py list
python document_manager.py info docs/crystals.md

# Q&A Cache Status
python -c "import sys; sys.path.insert(0, 'src'); from cache.qa_cache import QACache; qa = QACache(); print(f'Q&A Cache: {qa.get_stats()[\"total_qa_pairs\"]} pairs')"

# System Status
python run.py
# Then type: stats, domains, cache clear
```

#### **Troubleshooting Commands**

```bash
# Fix document issues
python document_manager.py validate
python document_manager.py fix

# Clear caches if performance degrades
python -c "import sys; sys.path.insert(0, 'src'); from cache.qa_cache import QACache; QACache().clear_cache()"

# Check system health
python -c "import sys; sys.path.insert(0, 'src'); from core.contextual_rag import OptimizedContextualRAGSystem; rag = OptimizedContextualRAGSystem(); print(rag.get_stats())"
```

#### **Available Domains**
- `lunar` - Moon phases, cosmic timing, lunar influences
- `ifs` - Internal Family Systems therapy, parts work
- `crystals` - Crystal properties, energy work, formations  
- `astrology` - Planetary influences, astrological concepts
- `tarot` - Tarot symbolism, card meanings, spreads
- `numerology` - Number meanings, calculations, interpretations
- `archetypes` - Jungian archetypes, shadow work, psychological patterns

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