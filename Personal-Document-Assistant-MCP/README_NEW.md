# Personal Document Assistant MCP Server

A powerful Model Context Protocol (MCP) server that provides intelligent document management and RAG (Retrieval-Augmented Generation) capabilities for VS Code.

## 🚀 Quick Start

### 1. Setup
```bash
# Run the setup script
./setup.sh
```

### 2. Start Ollama (if not running)
```bash
# Start Ollama server
ollama serve

# In another terminal, ensure you have llama3
ollama pull llama3
```

### 3. Test the Server
```bash
# Test all components
cd src && python test_server.py
```

### 4. VS Code Integration

1. **Install MCP Extension** in VS Code marketplace

2. **Add to your VS Code settings.json**:
```json
{
  "mcp.servers": {
    "document-assistant": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "/path/to/Personal-Document-Assistant-MCP"
    }
  }
}
```

## 🛠️ Features

- **Document Processing**: PDF, DOCX, TXT, HTML support
- **Semantic Search**: ChromaDB vector embeddings
- **RAG Q&A**: Question answering with document context
- **Local LLM**: Uses Ollama (privacy-first)
- **MCP Integration**: Native VS Code integration

## 📁 Project Structure

```
Personal-Document-Assistant-MCP/
├── config/
│   └── settings.yaml          # Server configuration
├── src/
│   ├── processing/            # Document processing
│   ├── rag/                   # RAG pipeline
│   ├── storage/               # Vector & document storage
│   ├── server.py              # MCP server
│   └── test_server.py         # Component tests
├── requirements.txt           # Python dependencies
├── setup.sh                   # Setup script
└── run.sh                     # Start script
```

## 🔧 Available Tools in VS Code

Once integrated, these tools will be available:

- **upload_document** - Upload and process documents
- **query_documents** - Ask questions about documents
- **search_documents** - Find relevant content
- **list_documents** - Browse document library
- **get_document_info** - View document metadata
- **delete_document** - Remove documents
- **get_system_stats** - Monitor system performance

## 🐛 Troubleshooting

### Ollama Not Running
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

### Component Test
```bash
cd src
python test_server.py
```

### Dependencies
```bash
# Reinstall dependencies
./setup.sh
```

## 💻 Development

The server uses:
- **MCP Protocol** for VS Code integration
- **ChromaDB** for vector storage
- **SQLite** for metadata
- **Ollama** for local LLM
- **Python 3.13+** runtime

## 📄 License

MIT License - feel free to modify and distribute.
