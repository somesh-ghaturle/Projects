"""
Marketing Recommendation Agent
Specializes in analyzing social media data and generating marketing insights
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from textblob import TextBlob
import pandas as pd

from .base_agent import BaseAgent
from ..config import settings

logger = logging.getLogger(__name__)


class MarketingRecommendationAgent(BaseAgent):
    """Agent specialized in marketing insights and recommendations"""
    
    def __init__(self):
        super().__init__(
            agent_id="marketing_agent",
            name="Marketing Recommendation Agent",
            description="Analyzes social media data and generates marketing recommendations"
        )
        self.sentiment_analyzer = None
        self.emotion_analyzer = None
        self.tokenizer = None
        
    async def _initialize_dependencies(self) -> None:
        """Initialize sentiment analysis and NLP models"""
        try:
            # Initialize sentiment analysis pipeline
            logger.info(f"Loading sentiment model: {settings.SENTIMENT_MODEL}")
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model=settings.SENTIMENT_MODEL,
                tokenizer=settings.SENTIMENT_MODEL
            )
            
            # Initialize emotion analysis (optional)
            try:
                self.emotion_analyzer = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base"
                )
            except Exception as e:
                logger.warning(f"Could not load emotion analyzer: {e}")
                self.emotion_analyzer = None
            
            logger.info("Marketing Recommendation Agent dependencies initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Marketing Agent: {str(e)}")
            raise
    
    async def _custom_validation(self, input_data: Dict[str, Any]) -> None:
        """Validate marketing analysis input"""
        if "social_media_data" not in input_data:
            raise ValueError("'social_media_data' is required in input data")
        
        social_data = input_data["social_media_data"]
        if not isinstance(social_data, list):
            raise ValueError("'social_media_data' must be a list of text strings")
        
        if len(social_data) == 0:
            raise ValueError("'social_media_data' cannot be empty")
        
        # Check if all items are strings
        for i, item in enumerate(social_data):
            if not isinstance(item, str):
                raise ValueError(f"Item {i} in social_media_data must be a string")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze social media data and generate marketing recommendations
        
        Args:
            input_data: Dictionary containing 'social_media_data' and optional metadata
            
        Returns:
            Dictionary with sentiment analysis, trends, and marketing recommendations
        """
        social_data = input_data["social_media_data"]
        metadata = input_data.get("metadata", {})
        
        try:
            # Preprocess social media data
            cleaned_data = await self._preprocess_social_data(social_data)
            
            # Sentiment analysis
            sentiment_results = await self._analyze_sentiment(cleaned_data)
            
            # Emotion analysis
            emotion_results = await self._analyze_emotions(cleaned_data)
            
            # Keyword and trend analysis
            keyword_analysis = await self._analyze_keywords(cleaned_data)
            
            # Generate marketing insights
            marketing_insights = await self._generate_marketing_insights(
                sentiment_results, emotion_results, keyword_analysis
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                sentiment_results, emotion_results, keyword_analysis, metadata
            )
            
            result = {
                "sentiment_analysis": sentiment_results,
                "emotion_analysis": emotion_results,
                "keyword_analysis": keyword_analysis,
                "marketing_insights": marketing_insights,
                "recommendations": recommendations,
                "data_summary": {
                    "total_posts": len(social_data),
                    "processed_posts": len(cleaned_data),
                    "analysis_timestamp": pd.Timestamp.now().isoformat()
                },
                "metadata": metadata
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing marketing data: {str(e)}")
            raise
    
    async def _preprocess_social_data(self, social_data: List[str]) -> List[str]:
        """Clean and preprocess social media text"""
        cleaned_data = []
        
        for text in social_data:
            # Remove URLs
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            
            # Remove mentions and hashtags for sentiment analysis (keep for keyword analysis)
            text_for_sentiment = re.sub(r'@\w+|#\w+', '', text)
            
            # Remove extra whitespace
            text_for_sentiment = ' '.join(text_for_sentiment.split())
            
            # Skip very short texts
            if len(text_for_sentiment.strip()) > 10:
                cleaned_data.append(text_for_sentiment.strip())
        
        return cleaned_data
    
    async def _analyze_sentiment(self, texts: List[str]) -> Dict[str, Any]:
        """Perform sentiment analysis on social media texts"""
        try:
            # Batch process for efficiency
            batch_size = 50
            all_sentiments = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_results = self.sentiment_analyzer(batch)
                all_sentiments.extend(batch_results)
            
            # Aggregate results
            sentiment_counts = Counter([result['label'] for result in all_sentiments])
            
            # Calculate statistics
            total_posts = len(all_sentiments)
            positive_count = sentiment_counts.get('POSITIVE', 0) + sentiment_counts.get('POS', 0)
            negative_count = sentiment_counts.get('NEGATIVE', 0) + sentiment_counts.get('NEG', 0)
            neutral_count = sentiment_counts.get('NEUTRAL', 0)
            
            # Handle different model outputs
            if neutral_count == 0:
                neutral_count = total_posts - positive_count - negative_count
            
            sentiment_distribution = {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": max(0, neutral_count),
                "total": total_posts
            }
            
            # Calculate percentages
            sentiment_percentages = {
                "positive_percent": (positive_count / total_posts) * 100 if total_posts > 0 else 0,
                "negative_percent": (negative_count / total_posts) * 100 if total_posts > 0 else 0,
                "neutral_percent": (neutral_count / total_posts) * 100 if total_posts > 0 else 0
            }
            
            # Calculate overall sentiment score
            overall_sentiment = self._calculate_overall_sentiment(sentiment_distribution)
            
            return {
                "distribution": sentiment_distribution,
                "percentages": sentiment_percentages,
                "overall_sentiment": overall_sentiment,
                "detailed_results": all_sentiments[:100]  # Limit for response size
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return self._get_fallback_sentiment(texts)
    
    def _calculate_overall_sentiment(self, distribution: Dict[str, int]) -> str:
        """Calculate overall sentiment based on distribution"""
        total = distribution["total"]
        if total == 0:
            return "neutral"
        
        positive_ratio = distribution["positive"] / total
        negative_ratio = distribution["negative"] / total
        
        if positive_ratio > 0.6:
            return "very_positive"
        elif positive_ratio > 0.4:
            return "positive"
        elif negative_ratio > 0.6:
            return "very_negative"
        elif negative_ratio > 0.4:
            return "negative"
        else:
            return "neutral"
    
    def _get_fallback_sentiment(self, texts: List[str]) -> Dict[str, Any]:
        """Fallback sentiment analysis using TextBlob"""
        try:
            sentiments = []
            for text in texts[:100]:  # Limit for performance
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                
                if polarity > 0.1:
                    sentiments.append("POSITIVE")
                elif polarity < -0.1:
                    sentiments.append("NEGATIVE")
                else:
                    sentiments.append("NEUTRAL")
            
            sentiment_counts = Counter(sentiments)
            total = len(sentiments)
            
            return {
                "distribution": {
                    "positive": sentiment_counts.get("POSITIVE", 0),
                    "negative": sentiment_counts.get("NEGATIVE", 0),
                    "neutral": sentiment_counts.get("NEUTRAL", 0),
                    "total": total
                },
                "percentages": {
                    "positive_percent": (sentiment_counts.get("POSITIVE", 0) / total) * 100 if total > 0 else 0,
                    "negative_percent": (sentiment_counts.get("NEGATIVE", 0) / total) * 100 if total > 0 else 0,
                    "neutral_percent": (sentiment_counts.get("NEUTRAL", 0) / total) * 100 if total > 0 else 0
                },
                "overall_sentiment": "neutral",
                "method": "fallback_textblob"
            }
            
        except Exception as e:
            logger.error(f"Fallback sentiment analysis failed: {str(e)}")
            return {"error": "Sentiment analysis failed"}
    
    async def _analyze_emotions(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze emotions in social media texts"""
        if not self.emotion_analyzer:
            return {"emotions": {}, "note": "Emotion analysis not available"}
        
        try:
            # Process subset for performance
            sample_texts = texts[:100] if len(texts) > 100 else texts
            
            emotion_results = self.emotion_analyzer(sample_texts)
            emotion_counts = Counter([result['label'] for result in emotion_results])
            
            total = len(emotion_results)
            emotion_percentages = {
                emotion: (count / total) * 100
                for emotion, count in emotion_counts.items()
            }
            
            return {
                "emotion_distribution": dict(emotion_counts),
                "emotion_percentages": emotion_percentages,
                "dominant_emotion": emotion_counts.most_common(1)[0][0] if emotion_counts else "neutral",
                "sample_size": total
            }
            
        except Exception as e:
            logger.error(f"Error in emotion analysis: {str(e)}")
            return {"emotions": {}, "error": str(e)}
    
    async def _analyze_keywords(self, original_texts: List[str]) -> Dict[str, Any]:
        """Extract keywords and trending topics"""
        try:
            # Extract hashtags
            hashtags = []
            mentions = []
            all_words = []
            
            for text in original_texts:
                # Extract hashtags
                hashtags.extend(re.findall(r'#(\w+)', text.lower()))
                
                # Extract mentions
                mentions.extend(re.findall(r'@(\w+)', text.lower()))
                
                # Extract words (excluding stop words)
                words = re.findall(r'\b\w+\b', text.lower())
                # Simple stop word removal
                stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
                filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
                all_words.extend(filtered_words)
            
            # Get top keywords
            top_hashtags = Counter(hashtags).most_common(10)
            top_mentions = Counter(mentions).most_common(10)
            top_keywords = Counter(all_words).most_common(20)
            
            return {
                "top_hashtags": [{"tag": tag, "count": count} for tag, count in top_hashtags],
                "top_mentions": [{"mention": mention, "count": count} for mention, count in top_mentions],
                "top_keywords": [{"keyword": keyword, "count": count} for keyword, count in top_keywords],
                "trending_topics": self._identify_trending_topics(top_keywords)
            }
            
        except Exception as e:
            logger.error(f"Error in keyword analysis: {str(e)}")
            return {"keywords": [], "error": str(e)}
    
    def _identify_trending_topics(self, top_keywords: List[Tuple[str, int]]) -> List[str]:
        """Identify trending topics from keywords"""
        # Group related keywords into topics
        topics = []
        
        # Movie-related topics
        movie_keywords = {'movie', 'film', 'cinema', 'watch', 'director', 'actor', 'actress', 'plot', 'story'}
        entertainment_keywords = {'entertainment', 'show', 'series', 'episode', 'season', 'streaming'}
        
        keyword_dict = dict(top_keywords)
        
        if any(keyword in keyword_dict for keyword in movie_keywords):
            topics.append("Movie Discussion")
        
        if any(keyword in keyword_dict for keyword in entertainment_keywords):
            topics.append("Entertainment")
        
        # Add top keywords as potential topics
        for keyword, count in top_keywords[:5]:
            if count > 2 and keyword not in [topic.lower() for topic in topics]:
                topics.append(keyword.title())
        
        return topics[:5]
    
    async def _generate_marketing_insights(
        self, 
        sentiment: Dict[str, Any], 
        emotions: Dict[str, Any], 
        keywords: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate marketing insights from analysis results"""
        insights = {
            "audience_sentiment": self._interpret_sentiment(sentiment),
            "engagement_opportunities": self._identify_engagement_opportunities(keywords),
            "content_themes": self._suggest_content_themes(sentiment, keywords),
            "risk_factors": self._identify_risk_factors(sentiment, emotions),
            "viral_potential": self._assess_viral_potential(sentiment, keywords)
        }
        
        return insights
    
    def _interpret_sentiment(self, sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret sentiment analysis results"""
        overall = sentiment.get("overall_sentiment", "neutral")
        distribution = sentiment.get("distribution", {})
        
        interpretation = {
            "overall_mood": overall,
            "audience_reception": "positive" if overall in ["positive", "very_positive"] else "mixed" if overall == "neutral" else "negative",
            "sentiment_strength": "strong" if overall in ["very_positive", "very_negative"] else "moderate",
            "positive_ratio": distribution.get("positive", 0) / max(distribution.get("total", 1), 1)
        }
        
        return interpretation
    
    def _identify_engagement_opportunities(self, keywords: Dict[str, Any]) -> List[str]:
        """Identify opportunities for audience engagement"""
        opportunities = []
        
        top_hashtags = keywords.get("top_hashtags", [])
        trending_topics = keywords.get("trending_topics", [])
        
        if top_hashtags:
            opportunities.append(f"Leverage trending hashtag: #{top_hashtags[0]['tag']}")
        
        if trending_topics:
            opportunities.append(f"Create content around: {trending_topics[0]}")
        
        opportunities.extend([
            "Host Q&A sessions with cast/crew",
            "Share behind-the-scenes content",
            "Create interactive polls about movie elements"
        ])
        
        return opportunities[:5]
    
    def _suggest_content_themes(self, sentiment: Dict[str, Any], keywords: Dict[str, Any]) -> List[str]:
        """Suggest content themes for marketing"""
        themes = []
        
        overall_sentiment = sentiment.get("overall_sentiment", "neutral")
        top_keywords = keywords.get("top_keywords", [])
        
        if overall_sentiment in ["positive", "very_positive"]:
            themes.extend([
                "Highlight positive audience reactions",
                "Share fan testimonials and reviews",
                "Create celebration content"
            ])
        
        # Add themes based on keywords
        if top_keywords:
            for keyword_data in top_keywords[:3]:
                keyword = keyword_data["keyword"]
                themes.append(f"Focus on '{keyword}' aspect of the movie")
        
        return themes[:5]
    
    def _identify_risk_factors(self, sentiment: Dict[str, Any], emotions: Dict[str, Any]) -> List[str]:
        """Identify potential marketing risk factors"""
        risks = []
        
        negative_percent = sentiment.get("percentages", {}).get("negative_percent", 0)
        
        if negative_percent > 40:
            risks.append("High negative sentiment - address concerns proactively")
        
        if negative_percent > 60:
            risks.append("Crisis management may be needed")
        
        # Check for specific negative emotions
        emotion_dist = emotions.get("emotion_distribution", {})
        if emotion_dist.get("anger", 0) > emotion_dist.get("joy", 0):
            risks.append("Anger detected - investigate specific issues")
        
        return risks
    
    def _assess_viral_potential(self, sentiment: Dict[str, Any], keywords: Dict[str, Any]) -> Dict[str, Any]:
        """Assess content's viral potential"""
        positive_percent = sentiment.get("percentages", {}).get("positive_percent", 0)
        hashtag_count = len(keywords.get("top_hashtags", []))
        trending_topics = len(keywords.get("trending_topics", []))
        
        # Simple scoring system
        viral_score = 0
        if positive_percent > 60:
            viral_score += 3
        elif positive_percent > 40:
            viral_score += 2
        
        viral_score += min(hashtag_count, 3)
        viral_score += min(trending_topics, 2)
        
        potential = "high" if viral_score >= 6 else "medium" if viral_score >= 3 else "low"
        
        return {
            "potential": potential,
            "score": viral_score,
            "factors": {
                "positive_sentiment": positive_percent > 40,
                "hashtag_presence": hashtag_count > 0,
                "trending_topics": trending_topics > 0
            }
        }
    
    async def _generate_recommendations(
        self, 
        sentiment: Dict[str, Any], 
        emotions: Dict[str, Any], 
        keywords: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate actionable marketing recommendations"""
        recommendations = {
            "immediate_actions": [],
            "content_strategy": [],
            "target_audience": {},
            "marketing_channels": [],
            "campaign_themes": []
        }
        
        overall_sentiment = sentiment.get("overall_sentiment", "neutral")
        positive_percent = sentiment.get("percentages", {}).get("positive_percent", 0)
        
        # Immediate actions
        if overall_sentiment in ["positive", "very_positive"]:
            recommendations["immediate_actions"].extend([
                "Amplify positive reviews and testimonials",
                "Increase social media posting frequency",
                "Launch user-generated content campaigns"
            ])
        elif overall_sentiment in ["negative", "very_negative"]:
            recommendations["immediate_actions"].extend([
                "Address negative feedback directly",
                "Highlight positive aspects of the content",
                "Consider damage control messaging"
            ])
        
        # Content strategy
        top_keywords = keywords.get("top_keywords", [])[:3]
        for keyword_data in top_keywords:
            keyword = keyword_data["keyword"]
            recommendations["content_strategy"].append(
                f"Create content highlighting '{keyword}' elements"
            )
        
        # Target audience
        recommendations["target_audience"] = {
            "primary": "Engaged social media users" if positive_percent > 50 else "Broader general audience",
            "engagement_level": "high" if positive_percent > 60 else "medium",
            "sentiment_alignment": overall_sentiment
        }
        
        # Marketing channels
        if positive_percent > 50:
            recommendations["marketing_channels"].extend([
                "Social media amplification",
                "Influencer partnerships",
                "User-generated content platforms"
            ])
        else:
            recommendations["marketing_channels"].extend([
                "Traditional advertising",
                "Targeted social campaigns",
                "Review platform focus"
            ])
        
        # Campaign themes
        if overall_sentiment == "positive":
            recommendations["campaign_themes"].extend([
                "Celebration and excitement",
                "Community and shared experience",
                "Quality and entertainment value"
            ])
        
        return recommendations
