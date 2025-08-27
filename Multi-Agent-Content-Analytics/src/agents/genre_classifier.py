"""
Genre Classification Agent
Specializes in classifying movie content by genre using ML models
"""

import logging
import pickle
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib

from .base_agent import BaseAgent
from ..config import settings

logger = logging.getLogger(__name__)


class GenreClassificationAgent(BaseAgent):
    """Agent specialized in movie genre classification"""
    
    SUPPORTED_GENRES = [
        "Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", 
        "Documentary", "Drama", "Family", "Fantasy", "History", "Horror",
        "Music", "Mystery", "Romance", "Sci-Fi", "Sport", "Thriller", "War", "Western"
    ]
    
    def __init__(self):
        super().__init__(
            agent_id="genre_classifier",
            name="Genre Classification Agent",
            description="Classifies movie content by genre using embeddings and ML"
        )
        self.embedder = None
        self.classifier = None
        self.label_encoder = None
        self.confidence_threshold = 0.3
        
    async def _initialize_dependencies(self) -> None:
        """Initialize embedding model and classifier"""
        try:
            # Initialize sentence transformer for embeddings
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
            
            # Try to load pre-trained classifier
            await self._load_or_train_classifier()
            
            logger.info("Genre Classification Agent dependencies initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Genre Classification Agent: {str(e)}")
            raise
    
    async def _load_or_train_classifier(self) -> None:
        """Load existing classifier or train a new one"""
        classifier_path = "./models/trained/genre_classifier.joblib"
        encoder_path = "./models/trained/label_encoder.joblib"
        
        try:
            # Try to load existing model
            self.classifier = joblib.load(classifier_path)
            self.label_encoder = joblib.load(encoder_path)
            logger.info("Loaded pre-trained genre classifier")
            
        except FileNotFoundError:
            logger.warning("Pre-trained classifier not found, using simple rule-based approach")
            # For demo purposes, create a simple classifier
            await self._create_demo_classifier()
    
    async def _create_demo_classifier(self) -> None:
        """Create a demo classifier for initial functionality"""
        # This is a simplified approach - in production, you'd train on real data
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(self.SUPPORTED_GENRES)
        
        # Create a simple logistic regression model (placeholder)
        self.classifier = LogisticRegression(random_state=42)
        
        # Generate some dummy training data for demo
        dummy_features = np.random.rand(len(self.SUPPORTED_GENRES) * 10, 384)  # 384 is embedding dimension
        dummy_labels = np.repeat(range(len(self.SUPPORTED_GENRES)), 10)
        
        self.classifier.fit(dummy_features, dummy_labels)
        logger.info("Created demo classifier (replace with real training data)")
    
    async def _custom_validation(self, input_data: Dict[str, Any]) -> None:
        """Validate genre classification input"""
        required_fields = ["text_content"]
        
        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"'{field}' is required in input data")
        
        text_content = input_data["text_content"]
        if not isinstance(text_content, str) or len(text_content.strip()) == 0:
            raise ValueError("'text_content' must be a non-empty string")
        
        if len(text_content) < 50:
            raise ValueError("Text content too short for meaningful genre classification")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify movie genre based on text content
        
        Args:
            input_data: Dictionary containing 'text_content' and optional metadata
            
        Returns:
            Dictionary with genre predictions, confidence scores, and analysis
        """
        text_content = input_data["text_content"]
        metadata = input_data.get("metadata", {})
        
        try:
            # Generate embeddings
            embeddings = await self._generate_embeddings(text_content)
            
            # Classify genre
            primary_genre, confidence = await self._classify_primary_genre(embeddings)
            
            # Get secondary genres
            secondary_genres = await self._get_secondary_genres(embeddings)
            
            # Analyze genre-specific features
            features = await self._analyze_genre_features(text_content)
            
            result = {
                "primary_genre": {
                    "genre": primary_genre,
                    "confidence": float(confidence)
                },
                "secondary_genres": secondary_genres,
                "all_predictions": await self._get_all_predictions(embeddings),
                "features": features,
                "analysis": {
                    "content_length": len(text_content),
                    "classification_method": "ML + Embeddings",
                    "model_version": "1.0",
                    "supported_genres": self.SUPPORTED_GENRES
                },
                "metadata": metadata
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error classifying genre: {str(e)}")
            raise
    
    async def _generate_embeddings(self, text: str) -> np.ndarray:
        """Generate embeddings for text content"""
        try:
            # Truncate text if too long
            max_length = 5000
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            embeddings = self.embedder.encode(text)
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    async def _classify_primary_genre(self, embeddings: np.ndarray) -> Tuple[str, float]:
        """Classify primary genre with confidence score"""
        try:
            # Reshape for prediction
            embeddings_2d = embeddings.reshape(1, -1)
            
            # Get predictions and probabilities
            prediction = self.classifier.predict(embeddings_2d)[0]
            probabilities = self.classifier.predict_proba(embeddings_2d)[0]
            
            # Get genre name and confidence
            genre = self.label_encoder.inverse_transform([prediction])[0]
            confidence = float(max(probabilities))
            
            return genre, confidence
            
        except Exception as e:
            logger.error(f"Error in primary classification: {str(e)}")
            # Fallback to rule-based classification
            return await self._rule_based_classification(embeddings)
    
    async def _rule_based_classification(self, embeddings: np.ndarray) -> Tuple[str, float]:
        """Fallback rule-based classification"""
        # Simple fallback - return most common genre with low confidence
        return "Drama", 0.1
    
    async def _get_secondary_genres(self, embeddings: np.ndarray) -> List[Dict[str, Any]]:
        """Get secondary genre predictions"""
        try:
            embeddings_2d = embeddings.reshape(1, -1)
            probabilities = self.classifier.predict_proba(embeddings_2d)[0]
            
            # Get top genres above threshold
            genre_probs = []
            for i, prob in enumerate(probabilities):
                if prob >= self.confidence_threshold:
                    genre = self.label_encoder.inverse_transform([i])[0]
                    genre_probs.append({
                        "genre": genre,
                        "confidence": float(prob)
                    })
            
            # Sort by confidence and return top 3 (excluding primary)
            genre_probs.sort(key=lambda x: x["confidence"], reverse=True)
            return genre_probs[1:4]  # Skip first (primary) and take next 3
            
        except Exception as e:
            logger.error(f"Error getting secondary genres: {str(e)}")
            return []
    
    async def _get_all_predictions(self, embeddings: np.ndarray) -> Dict[str, float]:
        """Get all genre predictions with confidence scores"""
        try:
            embeddings_2d = embeddings.reshape(1, -1)
            probabilities = self.classifier.predict_proba(embeddings_2d)[0]
            
            predictions = {}
            for i, prob in enumerate(probabilities):
                genre = self.label_encoder.inverse_transform([i])[0]
                predictions[genre] = float(prob)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error getting all predictions: {str(e)}")
            return {}
    
    async def _analyze_genre_features(self, text: str) -> Dict[str, Any]:
        """Analyze text for genre-specific features"""
        try:
            text_lower = text.lower()
            
            # Define genre-specific keywords
            genre_keywords = {
                "Action": ["fight", "explosion", "chase", "battle", "weapon", "combat"],
                "Comedy": ["funny", "laugh", "joke", "humor", "comedy", "silly"],
                "Horror": ["scary", "fear", "terror", "monster", "ghost", "blood"],
                "Romance": ["love", "heart", "kiss", "romantic", "relationship", "couple"],
                "Sci-Fi": ["space", "future", "robot", "alien", "technology", "science"],
                "Drama": ["emotion", "conflict", "character", "struggle", "life", "family"]
            }
            
            # Count keyword occurrences
            keyword_scores = {}
            for genre, keywords in genre_keywords.items():
                score = sum(text_lower.count(keyword) for keyword in keywords)
                keyword_scores[genre] = score
            
            # Additional text features
            features = {
                "keyword_analysis": keyword_scores,
                "text_statistics": {
                    "word_count": len(text.split()),
                    "sentence_count": text.count('.') + text.count('!') + text.count('?'),
                    "exclamation_count": text.count('!'),
                    "question_count": text.count('?')
                },
                "style_indicators": {
                    "dialogue_heavy": text.count('"') > 10,
                    "action_heavy": text.upper().count(text.lower()) > 0.1,
                    "descriptive": len([w for w in text.split() if len(w) > 6]) > len(text.split()) * 0.3
                }
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error analyzing genre features: {str(e)}")
            return {}
    
    async def train_classifier(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train the genre classifier with new data
        
        Args:
            training_data: List of dicts with 'text' and 'genre' keys
            
        Returns:
            Training results and metrics
        """
        try:
            logger.info(f"Training classifier with {len(training_data)} samples")
            
            # Prepare training data
            texts = [item["text"] for item in training_data]
            genres = [item["genre"] for item in training_data]
            
            # Generate embeddings
            embeddings = []
            for text in texts:
                embedding = await self._generate_embeddings(text)
                embeddings.append(embedding)
            
            X = np.array(embeddings)
            
            # Encode labels
            self.label_encoder = LabelEncoder()
            y = self.label_encoder.fit_transform(genres)
            
            # Train classifier
            self.classifier = LogisticRegression(
                random_state=42,
                max_iter=1000,
                class_weight='balanced'
            )
            self.classifier.fit(X, y)
            
            # Save trained model
            import os
            os.makedirs("./models/trained", exist_ok=True)
            joblib.dump(self.classifier, "./models/trained/genre_classifier.joblib")
            joblib.dump(self.label_encoder, "./models/trained/label_encoder.joblib")
            
            # Calculate training metrics
            y_pred = self.classifier.predict(X)
            report = classification_report(y, y_pred, output_dict=True)
            
            result = {
                "training_samples": len(training_data),
                "unique_genres": len(set(genres)),
                "accuracy": report["accuracy"],
                "model_saved": True,
                "supported_genres": list(self.label_encoder.classes_)
            }
            
            logger.info("Classifier training completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error training classifier: {str(e)}")
            raise
