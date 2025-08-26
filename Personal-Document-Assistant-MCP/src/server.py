#!/usr/bin/env python3
"""
Personal Document Assistant MCP Server

A Model Context Protocol server that provides RAG capabilities
for personal document management and intelligent Q&A.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from rag.pipeline import RAGPipeline
from rag.generation import RAGGenerator
from storage.vector_store import VectorStore
from storage.document_store import DocumentStore
from processing.parsers import DocumentParserFactory
from processing.text_processor import TextProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("personal-document-assistant")

# Global components
vector_store = None
document_store = None
rag_pipeline = None
parser_factory = None
text_processor = None


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available MCP tools for document management and RAG."""
    return [
        types.Tool(
            name="add_document",
            description="Upload and index a document for RAG retrieval",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the document file"
                    },
                    "title": {
                        "type": "string",
                        "description": "Document title (optional)"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata (optional)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        types.Tool(
            name="search_documents",
            description="Perform semantic search across indexed documents",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="ask_question",
            description="Ask a question using RAG (Retrieval-Augmented Generation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Question to ask"
                    },
                    "context_limit": {
                        "type": "integer",
                        "description": "Maximum number of context chunks (default: 5)",
                        "default": 5
                    }
                },
                "required": ["question"]
            }
        ),
        types.Tool(
            name="list_documents",
            description="List all indexed documents",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of documents (default: 20)",
                        "default": 20
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Offset for pagination (default: 0)",
                        "default": 0
                    }
                }
            }
        ),
        types.Tool(
            name="delete_document",
            description="Remove a document from the index",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "ID of the document to delete"
                    }
                },
                "required": ["document_id"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle MCP tool calls."""
    
    try:
        if name == "add_document":
            return await add_document_handler(arguments)
        elif name == "search_documents":
            return await search_documents_handler(arguments)
        elif name == "ask_question":
            return await ask_question_handler(arguments)
        elif name == "list_documents":
            return await list_documents_handler(arguments)
        elif name == "delete_document":
            return await delete_document_handler(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error handling tool {name}: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def add_document_handler(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle document addition."""
    file_path = arguments["file_path"]
    title = arguments.get("title", Path(file_path).stem)
    metadata = arguments.get("metadata", {})
    
    # Parse document
    parsed_doc = parser_factory.parse_document(file_path)
    content = parsed_doc['content']
    
    # Chunk text
    chunks = text_processor.chunk_text(content, metadata)
    
    # Generate embeddings and store
    document_id = await document_store.add_document(
        title=title,
        file_path=file_path,
        content=content,
        metadata=metadata
    )
    
    # Store chunks in vector database
    await vector_store.add_chunks(document_id, chunks)
    
    return [types.TextContent(
        type="text",
        text=f"Successfully added document '{title}' with {len(chunks)} chunks. Document ID: {document_id}"
    )]


async def search_documents_handler(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle document search."""
    query = arguments["query"]
    limit = arguments.get("limit", 5)
    
    # Perform semantic search
    results = await rag_pipeline.search_documents(query, limit=limit)
    
    # Format results
    if not results:
        return [types.TextContent(
            type="text",
            text="No relevant documents found."
        )]
    
    response = "Search Results:\n\n"
    for i, result in enumerate(results, 1):
        response += f"{i}. **{result['title']}** (Score: {result['score']:.3f})\n"
        response += f"   {result['content'][:200]}...\n\n"
    
    return [types.TextContent(type="text", text=response)]


async def ask_question_handler(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle RAG question answering."""
    question = arguments["question"]
    context_limit = arguments.get("context_limit", 5)
    
    # Use RAG pipeline for Q&A
    answer = await rag_pipeline.generate_answer(question, context_limit=context_limit)
    
    return [types.TextContent(type="text", text=answer)]


async def list_documents_handler(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle document listing."""
    limit = arguments.get("limit", 20)
    offset = arguments.get("offset", 0)
    
    documents = await document_store.list_documents(limit=limit, offset=offset)
    
    if not documents:
        return [types.TextContent(
            type="text",
            text="No documents found in the index."
        )]
    
    response = f"Documents ({len(documents)}):\n\n"
    for doc in documents:
        response += f"• **{doc['title']}**\n"
        response += f"  ID: {doc['id']}\n"
        response += f"  File: {doc['file_path']}\n"
        response += f"  Added: {doc['created_at']}\n\n"
    
    return [types.TextContent(type="text", text=response)]


async def delete_document_handler(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle document deletion."""
    document_id = arguments["document_id"]
    
    # Delete from both stores
    await document_store.delete_document(document_id)
    await vector_store.delete_document(document_id)
    
    return [types.TextContent(
        type="text",
        text=f"Successfully deleted document with ID: {document_id}"
    )]


async def initialize_components():
    """Initialize all system components."""
    global vector_store, document_store, rag_pipeline
    global parser_factory, text_processor
    
    logger.info("Initializing MCP server components...")
    
    # Initialize storage systems
    vector_store = VectorStore()
    document_store = DocumentStore()
    
    # Initialize processing systems
    rag_pipeline = RAGPipeline()
    parser_factory = DocumentParserFactory()
    text_processor = TextProcessor()
    
    logger.info("All components initialized successfully!")


async def main():
    """Main entry point for the MCP server."""
    # Initialize components
    await initialize_components()
    
    # Run the MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="personal-document-assistant",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
