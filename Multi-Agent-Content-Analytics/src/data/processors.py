"""
Data Processing and Management for Content Analytics
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
import asyncio
import logging
from datetime import datetime, timedelta
import json
import os
import sqlite3
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import aiofiles
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

@dataclass
class ContentItem:
    """Data class for content items"""
    content_id: str
    title: str
    content_type: str  # 'script', 'social_media', 'review', etc.
    text_content: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    source: str
    genre_hint: Optional[str] = None
    sentiment_hint: Optional[str] = None

@dataclass
class AnalysisResult:
    """Data class for analysis results"""
    analysis_id: str
    content_id: str
    agent_name: str
    result_data: Dict[str, Any]
    confidence_score: float
    processing_time: float
    created_at: datetime
    model_version: Optional[str] = None

class DataProcessor:
    """Base data processor class"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cache = {}
        
    async def process_text(self, text: str, content_type: str = "general") -> Dict[str, Any]:
        """Process text content"""
        try:
            processed_data = {
                "original_length": len(text),
                "word_count": len(text.split()),
                "character_count": len(text),
                "line_count": len(text.split('\n')),
                "content_type": content_type,
                "processed_at": datetime.now().isoformat()
            }
            
            # Basic text statistics
            words = text.split()
            if words:
                avg_word_length = sum(len(word) for word in words) / len(words)
                processed_data["avg_word_length"] = avg_word_length
            
            # Sentence count (rough estimate)
            sentences = text.split('.')
            processed_data["sentence_count"] = len([s for s in sentences if s.strip()])
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            raise

class ScriptProcessor(DataProcessor):
    """Processor for movie scripts"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.character_patterns = [
            r'^[A-Z][A-Z\s]+:',  # CHARACTER NAME:
            r'^\s*[A-Z][A-Z\s]+\n',  # CHARACTER NAME on separate line
        ]
        
    async def process_script(self, script_text: str) -> Dict[str, Any]:
        """Process movie script content"""
        try:
            base_processing = await self.process_text(script_text, "movie_script")
            
            # Extract characters
            characters = self._extract_characters(script_text)
            
            # Estimate scenes
            scene_markers = ['INT.', 'EXT.', 'FADE IN:', 'FADE OUT:', 'CUT TO:']
            scene_count = sum(script_text.upper().count(marker) for marker in scene_markers)
            
            # Estimate dialogue vs. action
            dialogue_lines, action_lines = self._classify_script_lines(script_text)
            
            # Estimate runtime (rough calculation: 1 page ≈ 1 minute)
            estimated_pages = len(script_text) / 250  # Approx 250 chars per page
            estimated_runtime = int(estimated_pages)
            
            script_data = {
                **base_processing,
                "characters": characters,
                "character_count": len(characters),
                "estimated_scenes": scene_count,
                "dialogue_lines": dialogue_lines,
                "action_lines": action_lines,
                "dialogue_ratio": dialogue_lines / (dialogue_lines + action_lines) if (dialogue_lines + action_lines) > 0 else 0,
                "estimated_runtime_minutes": estimated_runtime,
                "estimated_pages": int(estimated_pages)
            }
            
            return script_data
            
        except Exception as e:
            logger.error(f"Error processing script: {str(e)}")
            raise
    
    def _extract_characters(self, script_text: str) -> List[str]:
        """Extract character names from script"""
        import re
        
        characters = set()
        lines = script_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Pattern 1: CHARACTER NAME:
            if ':' in line and line.isupper():
                char_name = line.split(':')[0].strip()
                if len(char_name) < 50 and char_name.isalpha():  # Basic validation
                    characters.add(char_name)
            
            # Pattern 2: All caps names at start of line
            elif line.isupper() and len(line) < 50 and line.isalpha():
                characters.add(line)
        
        return list(characters)
    
    def _classify_script_lines(self, script_text: str) -> Tuple[int, int]:
        """Classify script lines as dialogue or action"""
        lines = script_text.split('\n')
        dialogue_lines = 0
        action_lines = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Dialogue lines typically follow character names
            if ':' in line or (line.isupper() and len(line) < 50):
                dialogue_lines += 1
            else:
                action_lines += 1
        
        return dialogue_lines, action_lines

class SocialMediaProcessor(DataProcessor):
    """Processor for social media content"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.hashtag_pattern = r'#\w+'
        self.mention_pattern = r'@\w+'
        self.url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    
    async def process_social_media_posts(self, posts: List[str]) -> Dict[str, Any]:
        """Process social media posts"""
        try:
            import re
            
            if not posts:
                return {"error": "No posts provided"}
            
            total_posts = len(posts)
            total_text = ' '.join(posts)
            
            # Basic processing
            base_processing = await self.process_text(total_text, "social_media")
            
            # Extract hashtags
            hashtags = []
            for post in posts:
                hashtags.extend(re.findall(self.hashtag_pattern, post))
            
            # Extract mentions
            mentions = []
            for post in posts:
                mentions.extend(re.findall(self.mention_pattern, post))
            
            # Extract URLs
            urls = []
            for post in posts:
                urls.extend(re.findall(self.url_pattern, post))
            
            # Calculate engagement indicators
            engagement_words = ['love', 'like', 'awesome', 'great', 'amazing', 'terrible', 'hate', 'bad']
            engagement_count = sum(
                sum(word.lower().count(eng_word) for eng_word in engagement_words)
                for word in posts
            )
            
            social_media_data = {
                **base_processing,
                "total_posts": total_posts,
                "unique_hashtags": list(set(hashtags)),
                "hashtag_count": len(hashtags),
                "unique_mentions": list(set(mentions)),
                "mention_count": len(mentions),
                "url_count": len(urls),
                "engagement_indicators": engagement_count,
                "avg_post_length": sum(len(post) for post in posts) / total_posts if total_posts > 0 else 0,
                "posts_with_hashtags": sum(1 for post in posts if '#' in post),
                "posts_with_mentions": sum(1 for post in posts if '@' in post),
                "posts_with_urls": sum(1 for post in posts if 'http' in post)
            }
            
            return social_media_data
            
        except Exception as e:
            logger.error(f"Error processing social media posts: {str(e)}")
            raise

class DatabaseManager:
    """Database manager for content analytics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_type = config.get("type", "sqlite")
        self.connection = None
        
    async def initialize(self):
        """Initialize database connection"""
        try:
            if self.db_type == "sqlite":
                await self._init_sqlite()
            elif self.db_type == "postgresql":
                await self._init_postgresql()
            elif self.db_type == "mongodb":
                await self._init_mongodb()
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
                
            logger.info(f"Database initialized: {self.db_type}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    async def _init_sqlite(self):
        """Initialize SQLite database"""
        db_path = self.config.get("path", "content_analytics.db")
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        
        self.connection = sqlite3.connect(db_path)
        
        # Create tables
        await self._create_sqlite_tables()
    
    async def _init_postgresql(self):
        """Initialize PostgreSQL database"""
        conn_params = {
            "host": self.config.get("host", "localhost"),
            "port": self.config.get("port", 5432),
            "database": self.config.get("database", "content_analytics"),
            "user": self.config.get("user", "postgres"),
            "password": self.config.get("password", "")
        }
        
        self.connection = await asyncpg.connect(**conn_params)
        await self._create_postgresql_tables()
    
    async def _init_mongodb(self):
        """Initialize MongoDB database"""
        uri = self.config.get("uri", "mongodb://localhost:27017")
        db_name = self.config.get("database", "content_analytics")
        
        self.client = AsyncIOMotorClient(uri)
        self.connection = self.client[db_name]
    
    async def _create_sqlite_tables(self):
        """Create SQLite tables"""
        cursor = self.connection.cursor()
        
        # Content items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_items (
                content_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content_type TEXT NOT NULL,
                text_content TEXT,
                metadata TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                source TEXT,
                genre_hint TEXT,
                sentiment_hint TEXT
            )
        """)
        
        # Analysis results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                analysis_id TEXT PRIMARY KEY,
                content_id TEXT,
                agent_name TEXT,
                result_data TEXT,
                confidence_score REAL,
                processing_time REAL,
                created_at TIMESTAMP,
                model_version TEXT,
                FOREIGN KEY (content_id) REFERENCES content_items (content_id)
            )
        """)
        
        self.connection.commit()
    
    async def _create_postgresql_tables(self):
        """Create PostgreSQL tables"""
        # Content items table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS content_items (
                content_id VARCHAR(255) PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                content_type VARCHAR(100) NOT NULL,
                text_content TEXT,
                metadata JSONB,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                source VARCHAR(255),
                genre_hint VARCHAR(100),
                sentiment_hint VARCHAR(100)
            )
        """)
        
        # Analysis results table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                analysis_id VARCHAR(255) PRIMARY KEY,
                content_id VARCHAR(255),
                agent_name VARCHAR(100),
                result_data JSONB,
                confidence_score REAL,
                processing_time REAL,
                created_at TIMESTAMP,
                model_version VARCHAR(100),
                FOREIGN KEY (content_id) REFERENCES content_items (content_id)
            )
        """)
    
    async def store_content_item(self, content_item: ContentItem) -> bool:
        """Store content item in database"""
        try:
            if self.db_type == "sqlite":
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO content_items 
                    (content_id, title, content_type, text_content, metadata, 
                     created_at, updated_at, source, genre_hint, sentiment_hint)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    content_item.content_id,
                    content_item.title,
                    content_item.content_type,
                    content_item.text_content,
                    json.dumps(content_item.metadata),
                    content_item.created_at,
                    content_item.updated_at,
                    content_item.source,
                    content_item.genre_hint,
                    content_item.sentiment_hint
                ))
                self.connection.commit()
                
            elif self.db_type == "postgresql":
                await self.connection.execute("""
                    INSERT INTO content_items 
                    (content_id, title, content_type, text_content, metadata, 
                     created_at, updated_at, source, genre_hint, sentiment_hint)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (content_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    content_type = EXCLUDED.content_type,
                    text_content = EXCLUDED.text_content,
                    metadata = EXCLUDED.metadata,
                    updated_at = EXCLUDED.updated_at,
                    source = EXCLUDED.source,
                    genre_hint = EXCLUDED.genre_hint,
                    sentiment_hint = EXCLUDED.sentiment_hint
                """, 
                    content_item.content_id,
                    content_item.title,
                    content_item.content_type,
                    content_item.text_content,
                    content_item.metadata,
                    content_item.created_at,
                    content_item.updated_at,
                    content_item.source,
                    content_item.genre_hint,
                    content_item.sentiment_hint
                )
                
            elif self.db_type == "mongodb":
                collection = self.connection.content_items
                await collection.replace_one(
                    {"content_id": content_item.content_id},
                    asdict(content_item),
                    upsert=True
                )
            
            logger.info(f"Stored content item: {content_item.content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing content item: {str(e)}")
            return False
    
    async def store_analysis_result(self, analysis_result: AnalysisResult) -> bool:
        """Store analysis result in database"""
        try:
            if self.db_type == "sqlite":
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO analysis_results 
                    (analysis_id, content_id, agent_name, result_data, 
                     confidence_score, processing_time, created_at, model_version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis_result.analysis_id,
                    analysis_result.content_id,
                    analysis_result.agent_name,
                    json.dumps(analysis_result.result_data),
                    analysis_result.confidence_score,
                    analysis_result.processing_time,
                    analysis_result.created_at,
                    analysis_result.model_version
                ))
                self.connection.commit()
                
            elif self.db_type == "postgresql":
                await self.connection.execute("""
                    INSERT INTO analysis_results 
                    (analysis_id, content_id, agent_name, result_data, 
                     confidence_score, processing_time, created_at, model_version)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (analysis_id) DO UPDATE SET
                    result_data = EXCLUDED.result_data,
                    confidence_score = EXCLUDED.confidence_score,
                    processing_time = EXCLUDED.processing_time,
                    model_version = EXCLUDED.model_version
                """,
                    analysis_result.analysis_id,
                    analysis_result.content_id,
                    analysis_result.agent_name,
                    analysis_result.result_data,
                    analysis_result.confidence_score,
                    analysis_result.processing_time,
                    analysis_result.created_at,
                    analysis_result.model_version
                )
                
            elif self.db_type == "mongodb":
                collection = self.connection.analysis_results
                await collection.replace_one(
                    {"analysis_id": analysis_result.analysis_id},
                    asdict(analysis_result),
                    upsert=True
                )
            
            logger.info(f"Stored analysis result: {analysis_result.analysis_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing analysis result: {str(e)}")
            return False
    
    async def get_content_item(self, content_id: str) -> Optional[ContentItem]:
        """Get content item by ID"""
        try:
            if self.db_type == "sqlite":
                cursor = self.connection.cursor()
                cursor.execute(
                    "SELECT * FROM content_items WHERE content_id = ?",
                    (content_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return ContentItem(
                        content_id=row[0],
                        title=row[1],
                        content_type=row[2],
                        text_content=row[3],
                        metadata=json.loads(row[4]) if row[4] else {},
                        created_at=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                        updated_at=datetime.fromisoformat(row[6]) if row[6] else datetime.now(),
                        source=row[7],
                        genre_hint=row[8],
                        sentiment_hint=row[9]
                    )
                    
            elif self.db_type == "postgresql":
                row = await self.connection.fetchrow(
                    "SELECT * FROM content_items WHERE content_id = $1",
                    content_id
                )
                
                if row:
                    return ContentItem(
                        content_id=row['content_id'],
                        title=row['title'],
                        content_type=row['content_type'],
                        text_content=row['text_content'],
                        metadata=row['metadata'] or {},
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        source=row['source'],
                        genre_hint=row['genre_hint'],
                        sentiment_hint=row['sentiment_hint']
                    )
                    
            elif self.db_type == "mongodb":
                collection = self.connection.content_items
                doc = await collection.find_one({"content_id": content_id})
                
                if doc:
                    doc.pop('_id', None)  # Remove MongoDB _id
                    return ContentItem(**doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting content item {content_id}: {str(e)}")
            return None
    
    async def cleanup(self):
        """Cleanup database connections"""
        try:
            if self.db_type == "sqlite" and self.connection:
                self.connection.close()
            elif self.db_type == "postgresql" and self.connection:
                await self.connection.close()
            elif self.db_type == "mongodb" and hasattr(self, 'client'):
                self.client.close()
                
            logger.info("Database connections cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up database: {str(e)}")

class DataManager:
    """Central data manager for content analytics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.processors = {
            "script": ScriptProcessor(config.get("script_processor", {})),
            "social_media": SocialMediaProcessor(config.get("social_media_processor", {})),
            "general": DataProcessor(config.get("general_processor", {}))
        }
        
        self.database = DatabaseManager(config.get("database", {"type": "sqlite", "path": "data/content_analytics.db"}))
        self._initialized = False
    
    async def initialize(self):
        """Initialize data manager"""
        if not self._initialized:
            await self.database.initialize()
            self._initialized = True
            logger.info("Data manager initialized")
    
    async def process_and_store_content(
        self,
        content_id: str,
        title: str,
        content_type: str,
        text_content: str,
        metadata: Dict[str, Any] = None,
        source: str = "api"
    ) -> Optional[ContentItem]:
        """Process and store content"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Create content item
            content_item = ContentItem(
                content_id=content_id,
                title=title,
                content_type=content_type,
                text_content=text_content,
                metadata=metadata or {},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                source=source
            )
            
            # Process content based on type
            if content_type == "movie_script":
                processed_data = await self.processors["script"].process_script(text_content)
            elif content_type == "social_media":
                # For social media, text_content should be a JSON string of posts
                posts = json.loads(text_content) if isinstance(text_content, str) else text_content
                processed_data = await self.processors["social_media"].process_social_media_posts(posts)
            else:
                processed_data = await self.processors["general"].process_text(text_content, content_type)
            
            # Add processed data to metadata
            content_item.metadata.update({"processed_data": processed_data})
            
            # Store in database
            success = await self.database.store_content_item(content_item)
            
            if success:
                logger.info(f"Processed and stored content: {content_id}")
                return content_item
            else:
                logger.error(f"Failed to store content: {content_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing content {content_id}: {str(e)}")
            return None
    
    async def get_content(self, content_id: str) -> Optional[ContentItem]:
        """Get content by ID"""
        if not self._initialized:
            await self.initialize()
        
        return await self.database.get_content_item(content_id)
    
    async def store_analysis_result(
        self,
        analysis_id: str,
        content_id: str,
        agent_name: str,
        result_data: Dict[str, Any],
        confidence_score: float,
        processing_time: float,
        model_version: str = None
    ) -> bool:
        """Store analysis result"""
        try:
            if not self._initialized:
                await self.initialize()
            
            analysis_result = AnalysisResult(
                analysis_id=analysis_id,
                content_id=content_id,
                agent_name=agent_name,
                result_data=result_data,
                confidence_score=confidence_score,
                processing_time=processing_time,
                created_at=datetime.now(),
                model_version=model_version
            )
            
            return await self.database.store_analysis_result(analysis_result)
            
        except Exception as e:
            logger.error(f"Error storing analysis result: {str(e)}")
            return False
    
    async def cleanup(self):
        """Cleanup data manager"""
        if self._initialized:
            await self.database.cleanup()
            self._initialized = False
            logger.info("Data manager cleaned up")
