"""
Machine Learning Models for Content Analytics
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
import logging
from datetime import datetime
import joblib
import os
from abc import ABC, abstractmethod

# ML Libraries
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
import xgboost as xgb

# Text processing
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class BaseMLModel(ABC):
    """Base class for ML models"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.scaler = None
        self.is_trained = False
        self.training_history = []
        
    @abstractmethod
    def train(self, X: List[str], y: List[str], **kwargs) -> Dict[str, Any]:
        """Train the model"""
        pass
    
    @abstractmethod
    def predict(self, X: List[str]) -> List[str]:
        """Make predictions"""
        pass
    
    @abstractmethod
    def predict_proba(self, X: List[str]) -> np.ndarray:
        """Get prediction probabilities"""
        pass
    
    def save_model(self, filepath: str) -> bool:
        """Save the trained model"""
        try:
            model_data = {
                'model': self.model,
                'vectorizer': self.vectorizer,
                'label_encoder': self.label_encoder,
                'scaler': self.scaler,
                'is_trained': self.is_trained,
                'training_history': self.training_history,
                'model_name': self.model_name
            }
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            joblib.dump(model_data, filepath)
            
            logger.info(f"Model {self.model_name} saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model {self.model_name}: {str(e)}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Load a trained model"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"Model file not found: {filepath}")
                return False
            
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.vectorizer = model_data['vectorizer']
            self.label_encoder = model_data['label_encoder']
            self.scaler = model_data.get('scaler')
            self.is_trained = model_data['is_trained']
            self.training_history = model_data.get('training_history', [])
            self.model_name = model_data['model_name']
            
            logger.info(f"Model {self.model_name} loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {str(e)}")
            return False

class GenreClassificationModel(BaseMLModel):
    """Genre classification model using traditional ML"""
    
    def __init__(self, algorithm: str = 'random_forest'):
        super().__init__(f"genre_classifier_{algorithm}")
        self.algorithm = algorithm
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Initialize model based on algorithm
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the ML model based on algorithm"""
        if self.algorithm == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
        elif self.algorithm == 'svm':
            self.model = SVC(
                kernel='rbf',
                probability=True,
                random_state=42
            )
        elif self.algorithm == 'logistic':
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        elif self.algorithm == 'naive_bayes':
            self.model = MultinomialNB()
        elif self.algorithm == 'xgboost':
            self.model = xgb.XGBClassifier(
                objective='multi:softprob',
                random_state=42
            )
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
        # Initialize vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),
            stop_words='english',
            lowercase=True,
            min_df=2,
            max_df=0.95
        )
        
        self.label_encoder = LabelEncoder()
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for training/prediction"""
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Remove special characters and digits
            text = re.sub(r'[^a-zA-Z\s]', '', text)
            
            # Tokenize
            tokens = word_tokenize(text)
            
            # Remove stopwords and lemmatize
            tokens = [
                self.lemmatizer.lemmatize(token)
                for token in tokens
                if token not in self.stop_words and len(token) > 2
            ]
            
            return ' '.join(tokens)
            
        except Exception as e:
            logger.error(f"Error preprocessing text: {str(e)}")
            return text
    
    def train(self, X: List[str], y: List[str], **kwargs) -> Dict[str, Any]:
        """Train the genre classification model"""
        try:
            logger.info(f"Training genre classification model with {len(X)} samples")
            
            # Preprocess texts
            X_processed = [self._preprocess_text(text) for text in X]
            
            # Remove empty texts
            valid_indices = [i for i, text in enumerate(X_processed) if text.strip()]
            X_processed = [X_processed[i] for i in valid_indices]
            y_filtered = [y[i] for i in valid_indices]
            
            if len(X_processed) < 10:
                raise ValueError("Insufficient training data after preprocessing")
            
            # Split data
            test_size = kwargs.get('test_size', 0.2)
            random_state = kwargs.get('random_state', 42)
            
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y_filtered,
                test_size=test_size,
                random_state=random_state,
                stratify=y_filtered
            )
            
            # Vectorize text
            X_train_vec = self.vectorizer.fit_transform(X_train)
            X_test_vec = self.vectorizer.transform(X_test)
            
            # Encode labels
            y_train_encoded = self.label_encoder.fit_transform(y_train)
            y_test_encoded = self.label_encoder.transform(y_test)
            
            # Train model
            self.model.fit(X_train_vec, y_train_encoded)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_vec)
            accuracy = accuracy_score(y_test_encoded, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(
                self.model, X_train_vec, y_train_encoded, cv=5
            )
            
            # Generate classification report
            report = classification_report(
                y_test_encoded, y_pred,
                target_names=self.label_encoder.classes_,
                output_dict=True
            )
            
            training_results = {
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'classification_report': report,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'classes': list(self.label_encoder.classes_),
                'timestamp': datetime.now().isoformat()
            }
            
            self.training_history.append(training_results)
            self.is_trained = True
            
            logger.info(f"Model trained successfully. Accuracy: {accuracy:.4f}")
            return training_results
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def predict(self, X: List[str]) -> List[str]:
        """Make genre predictions"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            # Preprocess texts
            X_processed = [self._preprocess_text(text) for text in X]
            
            # Vectorize
            X_vec = self.vectorizer.transform(X_processed)
            
            # Predict
            y_pred_encoded = self.model.predict(X_vec)
            
            # Decode labels
            y_pred = self.label_encoder.inverse_transform(y_pred_encoded)
            
            return list(y_pred)
            
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            raise
    
    def predict_proba(self, X: List[str]) -> np.ndarray:
        """Get prediction probabilities"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            # Preprocess texts
            X_processed = [self._preprocess_text(text) for text in X]
            
            # Vectorize
            X_vec = self.vectorizer.transform(X_processed)
            
            # Get probabilities
            probabilities = self.model.predict_proba(X_vec)
            
            return probabilities
            
        except Exception as e:
            logger.error(f"Error getting prediction probabilities: {str(e)}")
            raise
    
    def get_genre_probabilities(self, text: str) -> Dict[str, float]:
        """Get genre probabilities for a single text"""
        try:
            probabilities = self.predict_proba([text])[0]
            classes = self.label_encoder.classes_
            
            return {
                genre: float(prob)
                for genre, prob in zip(classes, probabilities)
            }
            
        except Exception as e:
            logger.error(f"Error getting genre probabilities: {str(e)}")
            return {}

class SentimentAnalysisModel(BaseMLModel):
    """Sentiment analysis model"""
    
    def __init__(self, algorithm: str = 'logistic'):
        super().__init__(f"sentiment_analyzer_{algorithm}")
        self.algorithm = algorithm
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the sentiment model"""
        if self.algorithm == 'logistic':
            self.model = LogisticRegression(max_iter=1000, random_state=42)
        elif self.algorithm == 'naive_bayes':
            self.model = MultinomialNB()
        elif self.algorithm == 'svm':
            self.model = SVC(kernel='linear', probability=True, random_state=42)
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english',
            lowercase=True
        )
        
        self.label_encoder = LabelEncoder()
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Remove URLs
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            
            # Remove user mentions and hashtags
            text = re.sub(r'@\w+|#\w+', '', text)
            
            # Remove special characters but keep emoticons
            text = re.sub(r'[^a-zA-Z\s:);(]', '', text)
            
            # Tokenize
            tokens = word_tokenize(text)
            
            # Remove stopwords and lemmatize
            tokens = [
                self.lemmatizer.lemmatize(token)
                for token in tokens
                if token not in self.stop_words and len(token) > 1
            ]
            
            return ' '.join(tokens)
            
        except Exception as e:
            logger.error(f"Error preprocessing text for sentiment: {str(e)}")
            return text
    
    def train(self, X: List[str], y: List[str], **kwargs) -> Dict[str, Any]:
        """Train the sentiment analysis model"""
        try:
            logger.info(f"Training sentiment analysis model with {len(X)} samples")
            
            # Preprocess texts
            X_processed = [self._preprocess_text(text) for text in X]
            
            # Remove empty texts
            valid_indices = [i for i, text in enumerate(X_processed) if text.strip()]
            X_processed = [X_processed[i] for i in valid_indices]
            y_filtered = [y[i] for i in valid_indices]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y_filtered, test_size=0.2, random_state=42
            )
            
            # Vectorize
            X_train_vec = self.vectorizer.fit_transform(X_train)
            X_test_vec = self.vectorizer.transform(X_test)
            
            # Encode labels
            y_train_encoded = self.label_encoder.fit_transform(y_train)
            y_test_encoded = self.label_encoder.transform(y_test)
            
            # Train model
            self.model.fit(X_train_vec, y_train_encoded)
            
            # Evaluate
            y_pred = self.model.predict(X_test_vec)
            accuracy = accuracy_score(y_test_encoded, y_pred)
            
            training_results = {
                'accuracy': accuracy,
                'classes': list(self.label_encoder.classes_),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'timestamp': datetime.now().isoformat()
            }
            
            self.training_history.append(training_results)
            self.is_trained = True
            
            logger.info(f"Sentiment model trained. Accuracy: {accuracy:.4f}")
            return training_results
            
        except Exception as e:
            logger.error(f"Error training sentiment model: {str(e)}")
            raise
    
    def predict(self, X: List[str]) -> List[str]:
        """Predict sentiment"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            X_processed = [self._preprocess_text(text) for text in X]
            X_vec = self.vectorizer.transform(X_processed)
            y_pred_encoded = self.model.predict(X_vec)
            return list(self.label_encoder.inverse_transform(y_pred_encoded))
            
        except Exception as e:
            logger.error(f"Error predicting sentiment: {str(e)}")
            raise
    
    def predict_proba(self, X: List[str]) -> np.ndarray:
        """Get sentiment probabilities"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            X_processed = [self._preprocess_text(text) for text in X]
            X_vec = self.vectorizer.transform(X_processed)
            return self.model.predict_proba(X_vec)
            
        except Exception as e:
            logger.error(f"Error getting sentiment probabilities: {str(e)}")
            raise

class ModelManager:
    """Manager for ML models"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.models = {}
        os.makedirs(models_dir, exist_ok=True)
    
    def register_model(self, model: BaseMLModel, model_id: str = None):
        """Register a model"""
        model_id = model_id or model.model_name
        self.models[model_id] = model
        logger.info(f"Registered model: {model_id}")
    
    def get_model(self, model_id: str) -> Optional[BaseMLModel]:
        """Get a registered model"""
        return self.models.get(model_id)
    
    def save_model(self, model_id: str, filename: str = None) -> bool:
        """Save a model to disk"""
        if model_id not in self.models:
            logger.error(f"Model {model_id} not found")
            return False
        
        filename = filename or f"{model_id}.joblib"
        filepath = os.path.join(self.models_dir, filename)
        
        return self.models[model_id].save_model(filepath)
    
    def load_model(self, model_id: str, filepath: str = None) -> bool:
        """Load a model from disk"""
        if filepath is None:
            filepath = os.path.join(self.models_dir, f"{model_id}.joblib")
        
        if model_id not in self.models:
            # Create a placeholder model
            if "genre" in model_id:
                algorithm = model_id.split("_")[-1] if "_" in model_id else "random_forest"
                model = GenreClassificationModel(algorithm)
            elif "sentiment" in model_id:
                algorithm = model_id.split("_")[-1] if "_" in model_id else "logistic"
                model = SentimentAnalysisModel(algorithm)
            else:
                logger.error(f"Unknown model type for {model_id}")
                return False
            
            self.models[model_id] = model
        
        return self.models[model_id].load_model(filepath)
    
    def list_models(self) -> List[str]:
        """List all registered models"""
        return list(self.models.keys())
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get information about a model"""
        if model_id not in self.models:
            return {}
        
        model = self.models[model_id]
        return {
            'model_id': model_id,
            'model_name': model.model_name,
            'is_trained': model.is_trained,
            'training_history': model.training_history,
            'last_training': model.training_history[-1] if model.training_history else None
        }
