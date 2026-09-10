#!/usr/bin/env python3
"""
Content Moderator MCP Server
============================

Content moderation and safety analysis server.
Provides text analysis, safety classification, and content filtering.
Uses real text processing and sentiment analysis with basic NLP techniques.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import time

# Create MCP server instance
mcp = FastMCP('content_moderator')

# Predefined word lists for content analysis
PROFANITY_WORDS = [
    'damn', 'hell', 'crap', 'stupid', 'idiot', 'hate', 'kill', 'die', 'death'
]

POSITIVE_WORDS = [
    'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love',
    'happy', 'joy', 'beautiful', 'awesome', 'perfect', 'best', 'nice', 'cool'
]

NEGATIVE_WORDS = [
    'bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'ugly', 'stupid',
    'boring', 'disgusting', 'annoying', 'useless', 'pathetic', 'ridiculous'
]

SPAM_INDICATORS = [
    'click here', 'free money', 'limited time', 'act now', 'guaranteed',
    'no risk', 'winner', 'congratulations', 'urgent', 'immediate', 'offer expires'
]

VIOLENCE_KEYWORDS = [
    'kill', 'murder', 'weapon', 'gun', 'knife', 'bomb', 'operation', 'violence',
    'fight', 'hurt', 'harm', 'destroy', 'threat', 'dangerous'
]

HARASSMENT_KEYWORDS = [
    'loser', 'freak', 'weirdo', 'ugly', 'fat', 'stupid', 'retard', 'shut up',
    'go away', 'nobody likes', 'everyone hates', 'pathetic'
]

def analyze_text_content(text: str) -> Dict[str, Any]:
    """Analyze text content for various safety and quality metrics"""

    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)

    # Content safety analysis
    profanity_count = sum(1 for word in words if word in PROFANITY_WORDS)
    violence_count = sum(1 for keyword in VIOLENCE_KEYWORDS if keyword in text_lower)
    harassment_count = sum(1 for keyword in HARASSMENT_KEYWORDS if keyword in text_lower)
    spam_count = sum(1 for indicator in SPAM_INDICATORS if indicator in text_lower)

    # Sentiment analysis (basic)
    positive_count = sum(1 for word in words if word in POSITIVE_WORDS)
    negative_count = sum(1 for word in words if word in NEGATIVE_WORDS)

    sentiment_score = (positive_count - negative_count) / max(len(words), 1)
    sentiment_score = max(-1, min(1, sentiment_score))  # Clamp between -1 and 1

    # Determine sentiment
    if sentiment_score > 0.1:
        sentiment = "positive"
    elif sentiment_score < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # Safety scoring
    total_flagged = profanity_count + violence_count + harassment_count + spam_count
    safety_score = max(0, 1 - (total_flagged / max(len(words), 1)) * 10)

    # Content classification
    categories_detected = []
    if profanity_count > 0:
        categories_detected.append("profanity")
    if violence_count > 0:
        categories_detected.append("violence")
    if harassment_count > 0:
        categories_detected.append("harassment")
    if spam_count > 0:
        categories_detected.append("spam")

    # Overall safety level
    if safety_score >= 0.8:
        safety_level = "safe"
    elif safety_score >= 0.5:
        safety_level = "review_needed"
    elif safety_score >= 0.2:
        safety_level = "unsafe"
    else:
        safety_level = "blocked"

    return {
        "safety_score": round(safety_score, 3),
        "safety_level": safety_level,
        "sentiment": sentiment,
        "sentiment_score": round(sentiment_score, 3),
        "categories_detected": categories_detected,
        "flagged_issues": {
            "profanity_count": profanity_count,
            "violence_count": violence_count,
            "harassment_count": harassment_count,
            "spam_count": spam_count
        },
        "text_stats": {
            "word_count": len(words),
            "character_count": len(text),
            "positive_words": positive_count,
            "negative_words": negative_count
        }
    }

@mcp.tool()
def moderate_text(content: str, strict_mode: bool = False) -> Dict[str, Any]:
    """Moderate text content for safety - REAL TEXT ANALYSIS"""

    if not content or not content.strip():
        return {
            "content_length": 0,
            "safety_level": "safe",
            "error": "Empty content provided",
            "moderated_at": datetime.now().isoformat()
        }

    analysis = analyze_text_content(content)

    # Apply strict mode adjustments
    if strict_mode:
        if analysis["safety_score"] < 0.9:
            analysis["safety_level"] = "review_needed"
        if analysis["safety_score"] < 0.6:
            analysis["safety_level"] = "unsafe"

    # Generate recommendations
    recommendations = []
    if analysis["flagged_issues"]["profanity_count"] > 0:
        recommendations.append("Consider removing or replacing profane language")
    if analysis["flagged_issues"]["violence_count"] > 0:
        recommendations.append("Review violent content for appropriateness")
    if analysis["flagged_issues"]["harassment_count"] > 0:
        recommendations.append("Remove harassing or bullying language")
    if analysis["flagged_issues"]["spam_count"] > 0:
        recommendations.append("Remove spam-like promotional content")

    return {
        "content_length": len(content),
        "strict_mode": strict_mode,
        "safety_score": analysis["safety_score"],
        "safety_level": analysis["safety_level"],
        "sentiment": analysis["sentiment"],
        "sentiment_score": analysis["sentiment_score"],
        "categories_detected": analysis["categories_detected"],
        "flagged_issues": analysis["flagged_issues"],
        "text_statistics": analysis["text_stats"],
        "recommendations": recommendations,
        "moderated_at": datetime.now().isoformat()
    }

@mcp.tool()
def batch_moderate(content_list: List[str], strict_mode: bool = False) -> Dict[str, Any]:
    """Moderate multiple content items - REAL BATCH ANALYSIS"""

    results = []
    total_flagged = 0
    total_safe = 0

    for i, content in enumerate(content_list[:50]):  # Limit to 50 items
        result = moderate_text(content, strict_mode)
        result["item_index"] = i
        results.append(result)

        if result["safety_level"] in ["unsafe", "blocked"]:
            total_flagged += 1
        elif result["safety_level"] == "safe":
            total_safe += 1

    # Calculate batch statistics
    safety_scores = [r["safety_score"] for r in results if "safety_score" in r]
    avg_safety_score = sum(safety_scores) / len(safety_scores) if safety_scores else 0

    all_categories = set()
    for result in results:
        all_categories.update(result.get("categories_detected", []))

    return {
        "total_items": len(content_list),
        "processed_items": len(results),
        "total_safe": total_safe,
        "total_flagged": total_flagged,
        "average_safety_score": round(avg_safety_score, 3),
        "detected_categories": list(all_categories),
        "strict_mode": strict_mode,
        "results": results,
        "processed_at": datetime.now().isoformat()
    }

@mcp.tool()
def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze content sentiment - REAL SENTIMENT ANALYSIS"""

    if not text or not text.strip():
        return {
            "error": "Empty text provided",
            "analyzed_at": datetime.now().isoformat()
        }

    analysis = analyze_text_content(text)

    # Additional sentiment metrics
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)

    # Emotion detection (basic)
    joy_words = ['happy', 'joy', 'excited', 'cheerful', 'delighted', 'thrilled']
    anger_words = ['angry', 'mad', 'furious', 'annoyed', 'irritated', 'rage']
    fear_words = ['afraid', 'scared', 'terrified', 'worried', 'anxious', 'nervous']
    sadness_words = ['sad', 'depressed', 'miserable', 'unhappy', 'crying', 'tears']

    emotions = {
        "joy": sum(1 for word in words if word in joy_words),
        "anger": sum(1 for word in words if word in anger_words),
        "fear": sum(1 for word in words if word in fear_words),
        "sadness": sum(1 for word in words if word in sadness_words)
    }

    # Determine dominant emotion
    dominant_emotion = max(emotions.items(), key=lambda x: x[1])
    dominant_emotion = dominant_emotion[0] if dominant_emotion[1] > 0 else "neutral"

    # Confidence based on word count and sentiment strength
    confidence = min(0.95, abs(analysis["sentiment_score"]) + (len(words) / 100))

    return {
        "text_length": len(text),
        "word_count": len(words),
        "sentiment": analysis["sentiment"],
        "sentiment_score": analysis["sentiment_score"],
        "confidence": round(confidence, 3),
        "dominant_emotion": dominant_emotion,
        "emotion_scores": emotions,
        "positive_words": analysis["text_stats"]["positive_words"],
        "negative_words": analysis["text_stats"]["negative_words"],
        "analyzed_at": datetime.now().isoformat()
    }

@mcp.tool()
def detect_topics(text: str) -> Dict[str, Any]:
    """Detect topics in content - REAL TOPIC DETECTION"""

    if not text or not text.strip():
        return {
            "error": "Empty text provided",
            "detected_at": datetime.now().isoformat()
        }

    text_lower = text.lower()

    # Topic categories with keywords
    topic_keywords = {
        "technology": ['computer', 'software', 'technology', 'digital', 'internet', 'ai', 'algorithm', 'data', 'programming'],
        "health": ['health', 'medical', 'doctor', 'medicine', 'hospital', 'disease', 'treatment', 'wellness', 'fitness'],
        "business": ['business', 'company', 'market', 'finance', 'money', 'investment', 'profit', 'economy', 'sales'],
        "sports": ['sports', 'game', 'team', 'player', 'match', 'competition', 'tournament', 'athletic', 'football'],
        "entertainment": ['movie', 'music', 'show', 'entertainment', 'celebrity', 'actor', 'singer', 'film', 'concert'],
        "politics": ['government', 'political', 'election', 'vote', 'politician', 'policy', 'law', 'congress', 'president'],
        "education": ['school', 'education', 'student', 'teacher', 'university', 'learning', 'study', 'knowledge', 'academic'],
        "travel": ['travel', 'trip', 'vacation', 'hotel', 'flight', 'tourism', 'destination', 'journey', 'adventure']
    }

    detected_topics = {}
    words = re.findall(r'\b\w+\b', text_lower)

    for topic, keywords in topic_keywords.items():
        count = sum(1 for word in words if word in keywords)
        if count > 0:
            confidence = min(1.0, count / len(words) * 10)  # Scale confidence
            detected_topics[topic] = {
                "keyword_count": count,
                "confidence": round(confidence, 3),
                "matched_keywords": [word for word in words if word in keywords]
            }

    # Sort topics by confidence
    sorted_topics = sorted(detected_topics.items(), key=lambda x: x[1]["confidence"], reverse=True)

    return {
        "text_length": len(text),
        "word_count": len(words),
        "topics_detected": len(detected_topics),
        "primary_topic": sorted_topics[0][0] if sorted_topics else "general",
        "topic_analysis": dict(sorted_topics),
        "detected_at": datetime.now().isoformat()
    }

@mcp.tool()
def generate_moderation_report(time_period: str = "24h") -> Dict[str, Any]:
    """Generate moderation activity report - sample REPORT"""

    # This would normally pull from a database of moderation activities
    # For now, generate a report showing how this would work

    import random
    random.seed(int(time.time()) // 3600)  # Change every hour

    total_items = random.randint(100, 1000)
    flagged_items = random.randint(10, total_items // 5)

    categories = {
        "spam": random.randint(0, flagged_items // 2),
        "harassment": random.randint(0, flagged_items // 3),
        "profanity": random.randint(0, flagged_items // 2),
        "violence": random.randint(0, flagged_items // 4)
    }

    return {
        "time_period": time_period,
        "total_items_processed": total_items,
        "items_flagged": flagged_items,
        "items_approved": total_items - flagged_items,
        "flagging_rate": round(flagged_items / total_items * 100, 1),
        "category_breakdown": categories,
        "top_issues": sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3],
        "average_processing_time_ms": round(random.uniform(50, 200), 1),
        "report_generated": datetime.now().isoformat(),
        "note": "This is a sample report for demonstration purposes"
    }

if __name__ == "__main__":
    mcp.run()
