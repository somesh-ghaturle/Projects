"""
Document metadata storage using SQLite.
"""

import logging
import sqlite3
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentStore:
    """Manages document metadata using SQLite."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the document store."""
        self.config = config or self._default_config()
        self.db_path = Path(self.config["database_path"])
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for document storage."""
        return {
            "database_path": "./data/documents.db"
        }
    
    def _initialize_database(self):
        """Initialize SQLite database and create tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create documents table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS documents (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        content_hash TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        chunk_count INTEGER DEFAULT 0,
                        character_count INTEGER DEFAULT 0
                    )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON documents(title)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON documents(created_at)')
                
                conn.commit()
                logger.info("Document store database initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    async def add_document(self, title: str, file_path: str, content: str,
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a new document to the store."""
        try:
            document_id = str(uuid.uuid4())
            content_hash = str(hash(content))
            character_count = len(content)
            metadata_json = json.dumps(metadata or {})
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO documents 
                    (id, title, file_path, content_hash, metadata, character_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (document_id, title, file_path, content_hash, metadata_json, character_count))
                
                conn.commit()
            
            logger.info(f"Added document: {title} (ID: {document_id})")
            return document_id
            
        except Exception as e:
            logger.error(f"Failed to add document: {str(e)}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row["id"],
                        "title": row["title"],
                        "file_path": row["file_path"],
                        "content_hash": row["content_hash"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                        "chunk_count": row["chunk_count"],
                        "character_count": row["character_count"]
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {str(e)}")
            return None
    
    async def list_documents(self, limit: int = 20, offset: int = 0,
                           search_term: Optional[str] = None) -> List[Dict[str, Any]]:
        """List documents with optional search."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if search_term:
                    query = '''
                        SELECT * FROM documents 
                        WHERE title LIKE ? OR file_path LIKE ?
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                    '''
                    search_pattern = f"%{search_term}%"
                    cursor.execute(query, (search_pattern, search_pattern, limit, offset))
                else:
                    query = '''
                        SELECT * FROM documents 
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                    '''
                    cursor.execute(query, (limit, offset))
                
                rows = cursor.fetchall()
                
                documents = []
                for row in rows:
                    documents.append({
                        "id": row["id"],
                        "title": row["title"],
                        "file_path": row["file_path"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "created_at": row["created_at"],
                        "chunk_count": row["chunk_count"],
                        "character_count": row["character_count"]
                    })
                
                return documents
                
        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}")
            return []
    
    async def update_document(self, document_id: str, **updates) -> bool:
        """Update document metadata."""
        try:
            # Prepare update fields
            update_fields = []
            values = []
            
            for field, value in updates.items():
                if field in ["title", "file_path", "content_hash", "chunk_count", "character_count"]:
                    update_fields.append(f"{field} = ?")
                    values.append(value)
                elif field == "metadata":
                    update_fields.append("metadata = ?")
                    values.append(json.dumps(value))
            
            if not update_fields:
                return False
            
            # Always update the updated_at timestamp
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(document_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = f"UPDATE documents SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, values)
                
                success = cursor.rowcount > 0
                conn.commit()
                
                if success:
                    logger.info(f"Updated document: {document_id}")
                
                return success
                
        except Exception as e:
            logger.error(f"Failed to update document {document_id}: {str(e)}")
            return False
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
                
                success = cursor.rowcount > 0
                conn.commit()
                
                if success:
                    logger.info(f"Deleted document: {document_id}")
                
                return success
                
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            return False
    
    async def document_exists(self, file_path: str, content_hash: str) -> Optional[str]:
        """Check if a document with the same content already exists."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT id FROM documents WHERE file_path = ? AND content_hash = ?',
                    (file_path, content_hash)
                )
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Failed to check document existence: {str(e)}")
            return None
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total documents
                cursor.execute('SELECT COUNT(*) FROM documents')
                total_docs = cursor.fetchone()[0]
                
                # Total characters
                cursor.execute('SELECT SUM(character_count) FROM documents')
                total_chars = cursor.fetchone()[0] or 0
                
                # Total chunks
                cursor.execute('SELECT SUM(chunk_count) FROM documents')
                total_chunks = cursor.fetchone()[0] or 0
                
                # Recent documents (last 7 days)
                cursor.execute('''
                    SELECT COUNT(*) FROM documents 
                    WHERE created_at >= datetime('now', '-7 days')
                ''')
                recent_docs = cursor.fetchone()[0]
                
                return {
                    "total_documents": total_docs,
                    "total_characters": total_chars,
                    "total_chunks": total_chunks,
                    "recent_documents": recent_docs,
                    "database_path": str(self.db_path)
                }
                
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {"error": str(e)}
