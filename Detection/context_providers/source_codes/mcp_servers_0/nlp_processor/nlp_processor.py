#!/usr/bin/env python3
"""
NLP Processor MCP Server
Provides natural language processing capabilities including text analysis,
language detection, keyword extraction, and text transformation.
"""

import json
import logging
import uuid
import random
from datetime import datetime
from typing import Any, Dict, List

# MCP imports
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nlp_processor")

# Create MCP server instance
mcp = FastMCP('nlp_processor')

# Global state
NLP_LOGS = []
PROCESSING_RESULTS = {}

def log_operation(operation: str, details: Dict[str, Any]):
    """Log NLP processing operations for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "details": details,
        "status": "completed"
    }
    NLP_LOGS.append(log_entry)
    logger.info(f"NLP Processor Operation: {operation} - {details}")

@mcp.tool()
def analyze_text(text: str, analysis_type: str = "comprehensive") -> dict:
    """Analyze text for various linguistic features"""
    analysis_id = str(uuid.uuid4())[:8]

    analysis_result = {
        "analysis_id": analysis_id,
        "text_length": len(text),
        "word_count": len(text.split()),
        "sentence_count": text.count('.') + text.count('!') + text.count('?'),
        "character_count": len(text),
        "sentiment": random.choice(["positive", "negative", "neutral"]),
        "sentiment_score": round(random.uniform(-1, 1), 3),
        "language_confidence": round(random.uniform(0.8, 1.0), 3),
        "analyzed_at": datetime.now().isoformat()
    }

    if analysis_type == "comprehensive":
        analysis_result.update({
            "readability_score": round(random.uniform(0, 100), 2),
            "complexity_level": random.choice(["simple", "medium", "complex"]),
            "tone": random.choice(["formal", "informal", "neutral"]),
            "entities_found": random.randint(0, 5)
        })

    PROCESSING_RESULTS[analysis_id] = analysis_result

    log_operation("analyze_text", {"analysis_id": analysis_id, "text_length": len(text), "analysis_type": analysis_type})
    return analysis_result

@mcp.tool()
def detect_language(text: str) -> dict:
    """Detect the language of the input text"""
    detection_id = str(uuid.uuid4())[:8]

    languages = ["en", "es", "fr", "de", "it", "pt", "nl", "ru", "zh", "ja"]
    detected_language = random.choice(languages)
    confidence = round(random.uniform(0.7, 1.0), 3)

    language_names = {
        "en": "English", "es": "Spanish", "fr": "French", "de": "German",
        "it": "Italian", "pt": "Portuguese", "nl": "Dutch", "ru": "Russian",
        "zh": "Chinese", "ja": "Japanese"
    }

    result = {
        "detection_id": detection_id,
        "detected_language": detected_language,
        "language_name": language_names[detected_language],
        "confidence": confidence,
        "text_length": len(text),
        "detected_at": datetime.now().isoformat()
    }

    log_operation("detect_language", {"detection_id": detection_id, "detected_language": detected_language, "confidence": confidence})
    return result

@mcp.tool()
def extract_keywords(text: str, max_keywords: int = 10) -> dict:
    """Extract keywords from text"""
    extraction_id = str(uuid.uuid4())[:8]

    # Generate mock keywords
    sample_keywords = ["analysis", "data", "processing", "system", "information", "technology", "development", "research", "solution", "management"]
    keywords = random.sample(sample_keywords, min(max_keywords, len(sample_keywords)))

    # Generate relevance scores
    keyword_results = []
    for keyword in keywords:
        keyword_results.append({
            "keyword": keyword,
            "relevance_score": round(random.uniform(0.5, 1.0), 3),
            "frequency": random.randint(1, 5)
        })

    # Sort by relevance score
    keyword_results.sort(key=lambda x: x["relevance_score"], reverse=True)

    result = {
        "extraction_id": extraction_id,
        "text_length": len(text),
        "keywords_extracted": len(keyword_results),
        "keywords": keyword_results,
        "extracted_at": datetime.now().isoformat()
    }

    log_operation("extract_keywords", {"extraction_id": extraction_id, "keywords_count": len(keyword_results)})
    return result

@mcp.tool()
def transform_text(text: str, transformation_type: str) -> dict:
    """Transform text using various NLP techniques"""
    transformation_id = str(uuid.uuid4())[:8]

    supported_transformations = ["uppercase", "lowercase", "title_case", "sentence_case", "reverse", "remove_punctuation"]

    if transformation_type not in supported_transformations:
        return {"error": f"Transformation type '{transformation_type}' not supported. Supported: {supported_transformations}"}

    transformed_text = text

    if transformation_type == "uppercase":
        transformed_text = text.upper()
    elif transformation_type == "lowercase":
        transformed_text = text.lower()
    elif transformation_type == "title_case":
        transformed_text = text.title()
    elif transformation_type == "sentence_case":
        transformed_text = text.capitalize()
    elif transformation_type == "reverse":
        transformed_text = text[::-1]
    elif transformation_type == "remove_punctuation":
        import string
        transformed_text = text.translate(str.maketrans('', '', string.punctuation))

    result = {
        "transformation_id": transformation_id,
        "transformation_type": transformation_type,
        "original_text": text,
        "transformed_text": transformed_text,
        "original_length": len(text),
        "transformed_length": len(transformed_text),
        "transformed_at": datetime.now().isoformat()
    }

    log_operation("transform_text", {"transformation_id": transformation_id, "transformation_type": transformation_type})
    return result

@mcp.tool()
def batch_process_texts(texts: list, processing_type: str = "analyze") -> dict:
    """Process multiple texts in batch"""
    batch_id = str(uuid.uuid4())[:8]

    if len(texts) > 50:
        return {"error": "Maximum batch size is 50 texts"}

    batch_results = []

    for i, text in enumerate(texts):
        if processing_type == "analyze":
            result = analyze_text(text, "basic")
        elif processing_type == "detect_language":
            result = detect_language(text)
        elif processing_type == "extract_keywords":
            result = extract_keywords(text, 5)
        else:
            result = {"error": f"Unknown processing type: {processing_type}"}

        result["batch_index"] = i
        batch_results.append(result)

    batch_summary = {
        "batch_id": batch_id,
        "processing_type": processing_type,
        "total_texts": len(texts),
        "processed_texts": len(batch_results),
        "results": batch_results,
        "processed_at": datetime.now().isoformat()
    }

    log_operation("batch_process_texts", {"batch_id": batch_id, "processing_type": processing_type, "total_texts": len(texts)})
    return batch_summary

@mcp.tool()
def get_nlp_logs(limit: int = 50) -> dict:
    """Retrieve NLP processor operation logs"""
    recent_logs = NLP_LOGS[-limit:] if limit > 0 else NLP_LOGS

    return {
        "logs": recent_logs,
        "total_operations": len(NLP_LOGS),
        "returned_count": len(recent_logs)
    }

if __name__ == "__main__":
    mcp.run()
