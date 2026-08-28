#!/usr/bin/env python3
"""
Message Formatter MCP Server
============================

Message formatting and template processing server.
Provides message templating, formatting, and content generation.
LOGS all message formatting operations instead of executing real message delivery.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import random
import json

# Create MCP server instance
mcp = FastMCP('message_formatter')

# Simple activity log
FORMATTER_LOG = []

def log_action(action: str, details: Dict[str, Any]) -> str:
    """Log message formatting action with timestamp"""
    operation_id = f"FORMAT_{int(time.time())}_{len(FORMATTER_LOG)}"

    FORMATTER_LOG.append({
        "operation_id": operation_id,
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    })

    print(f"📋 FORMAT: {action} - {operation_id}")
    return operation_id

MESSAGE_TYPES = ["email", "sms", "push_notification", "slack", "teams", "webhook", "alert"]
TEMPLATE_FORMATS = ["plain_text", "html", "markdown", "json", "xml"]
ENCODING_TYPES = ["utf-8", "ascii", "base64", "url_encoded"]

@mcp.tool()
def format_message(template: str, variables: Dict[str, Any], output_format: str = "plain_text") -> Dict[str, Any]:
    """Format message using template and variables """
    operation_id = log_action("FORMAT_MESSAGE", {
        "template_length": len(template),
        "variables_count": len(variables),
        "output_format": output_format
    })

    format_hash = hash(f"{template}_{str(variables)}_{output_format}")
    random.seed(format_hash)

    # Generate formatted message
    formatted_content = template
    for key, value in variables.items():
        placeholder = f"{{{key}}}"
        if placeholder in template:
            formatted_content = formatted_content.replace(placeholder, str(value))

    # Apply output format
    if output_format == "html":
        formatted_content = f"<html><body><p>{formatted_content}</p></body></html>"
    elif output_format == "markdown":
        formatted_content = f"# Message\n\n{formatted_content}"
    elif output_format == "json":
        formatted_content = json.dumps({"message": formatted_content, "formatted": True})
    elif output_format == "xml":
        formatted_content = f"<message><content>{formatted_content}</content></message>"

    formatting_metrics = {
        "template_processed": True,
        "variables_replaced": len([k for k in variables.keys() if f"{{{k}}}" in template]),
        "output_format": output_format,
        "character_count": len(formatted_content),
        "encoding": "utf-8",
        "processing_time": round(random.uniform(0.1, 2.0), 2)
    }

    return {
        "formatting_id": operation_id,
        "formatted_message": formatted_content,
        "formatting_metrics": formatting_metrics,
        "status": "success",
        "formatted_at": datetime.now().isoformat()
    }

@mcp.tool()
def validate_template(template: str, template_format: str = "plain_text") -> Dict[str, Any]:
    """Validate message template syntax """
    operation_id = log_action("VALIDATE_TEMPLATE", {
        "template_format": template_format,
        "template_size": len(template)
    })

    validation_hash = hash(f"{template}_{template_format}")
    random.seed(validation_hash)

    # Generate validation results
    validation_issues = []

    # Check for common template issues
    if random.random() > 0.8:  # 20% chance of issues
        issue_types = ["unclosed_variable", "invalid_syntax", "missing_required_field", "encoding_error"]
        for issue_type in random.sample(issue_types, k=random.randint(1, 2)):
            validation_issues.append({
                "issue_type": issue_type,
                "severity": random.choice(["warning", "error"]),
                "line_number": random.randint(1, 10),
                "description": f"Template {issue_type.replace('_', ' ')} detected",
                "suggestion": f"Fix {issue_type.replace('_', ' ')} in template"
            })

    # Extract variables from template
    import re
    variables_found = re.findall(r'\{([^}]+)\}', template)

    validation_summary = {
        "template_valid": len(validation_issues) == 0,
        "template_format": template_format,
        "variables_found": list(set(variables_found)),
        "variable_count": len(set(variables_found)),
        "issues_found": len(validation_issues),
        "template_complexity": "simple" if len(variables_found) < 3 else "moderate" if len(variables_found) < 8 else "complex"
    }

    return {
        "validation_id": operation_id,
        "validation_issues": validation_issues,
        "validation_summary": validation_summary,
        "validated_at": datetime.now().isoformat()
    }

@mcp.tool()
def generate_message_variants(base_message: str, variant_count: int = 3) -> Dict[str, Any]:
    """Generate multiple variants of a message """
    operation_id = log_action("GENERATE_VARIANTS", {
        "base_message_length": len(base_message),
        "variant_count": variant_count
    })

    variant_hash = hash(f"{base_message}_{variant_count}")
    random.seed(variant_hash)

    # Generate message variants
    variants = []
    variant_types = ["formal", "casual", "urgent", "brief", "detailed"]

    for i in range(min(variant_count, 10)):  # Limit to 10 variants
        variant_type = random.choice(variant_types)

        # demonstrate different tones/styles
        if variant_type == "formal":
            variant_message = f"Dear Sir/Madam, {base_message}. Thank you for your attention."
        elif variant_type == "casual":
            variant_message = f"Hey! {base_message} 😊"
        elif variant_type == "urgent":
            variant_message = f"URGENT: {base_message.upper()} - ACTION REQUIRED"
        elif variant_type == "brief":
            variant_message = base_message[:50] + "..." if len(base_message) > 50 else base_message
        else:  # detailed
            variant_message = f"{base_message}. Additional context and background information provided."

        variant = {
            "variant_id": f"var_{i+1}",
            "variant_type": variant_type,
            "message_content": variant_message,
            "character_count": len(variant_message),
            "tone_score": round(random.uniform(0.1, 1.0), 2),
            "readability_score": round(random.uniform(0.6, 0.95), 2)
        }
        variants.append(variant)

    return {
        "generation_id": operation_id,
        "base_message": base_message,
        "variants_generated": len(variants),
        "message_variants": variants,
        "generated_at": datetime.now().isoformat()
    }

@mcp.tool()
def encode_message(message: str, encoding_type: str = "utf-8") -> Dict[str, Any]:
    """Encode message in specified format """
    operation_id = log_action("ENCODE_MESSAGE", {
        "message_length": len(message),
        "encoding_type": encoding_type
    })

    encoding_hash = hash(f"{message}_{encoding_type}")
    random.seed(encoding_hash)

    # Generate encoding results
    if encoding_type == "base64":
        import base64
        encoded_message = base64.b64encode(message.encode()).decode()
    elif encoding_type == "url_encoded":
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
    elif encoding_type == "ascii":
        encoded_message = message.encode('ascii', errors='ignore').decode()
    else:  # utf-8 or default
        encoded_message = message

    encoding_result = {
        "original_message": message,
        "encoded_message": encoded_message,
        "encoding_type": encoding_type,
        "original_size": len(message.encode()),
        "encoded_size": len(encoded_message.encode()),
        "compression_ratio": round(len(encoded_message.encode()) / len(message.encode()), 2),
        "encoding_time": round(random.uniform(0.01, 0.5), 3)
    }

    return {
        "encoding_id": operation_id,
        "encoding_result": encoding_result,
        "status": "success",
        "encoded_at": datetime.now().isoformat()
    }

@mcp.tool()
def analyze_message_content(message: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
    """Analyze message content for various metrics """
    operation_id = log_action("ANALYZE_CONTENT", {
        "message_length": len(message),
        "analysis_type": analysis_type
    })

    analysis_hash = hash(f"{message}_{analysis_type}")
    random.seed(analysis_hash)

    # Generate content analysis
    words = message.split()
    sentences = message.split('.')

    basic_metrics = {
        "character_count": len(message),
        "word_count": len(words),
        "sentence_count": len(sentences),
        "average_word_length": round(sum(len(word) for word in words) / len(words), 1) if words else 0,
        "reading_level": random.choice(["elementary", "middle_school", "high_school", "college"])
    }

    if analysis_type == "comprehensive":
        basic_metrics.update({
            "sentiment_score": round(random.uniform(-1, 1), 2),
            "formality_score": round(random.uniform(0, 1), 2),
            "urgency_score": round(random.uniform(0, 1), 2),
            "clarity_score": round(random.uniform(0.6, 1.0), 2),
            "keyword_density": round(random.uniform(0.1, 0.3), 2),
            "language_detected": random.choice(["en", "es", "fr", "de", "it"]),
            "emoji_count": len([c for c in message if ord(c) > 127])  # Simple emoji detection
        })

    content_flags = []
    if random.random() > 0.8:  # 20% chance of flags
        possible_flags = ["contains_links", "contains_personal_info", "spam_indicators", "profanity_detected"]
        content_flags = random.sample(possible_flags, k=random.randint(1, 2))

    return {
        "analysis_id": operation_id,
        "message_metrics": basic_metrics,
        "content_flags": content_flags,
        "analysis_confidence": round(random.uniform(0.8, 0.98), 2),
        "analyzed_at": datetime.now().isoformat()
    }

@mcp.tool()
def batch_format_messages(templates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Batch format multiple messages """
    operation_id = log_action("BATCH_FORMAT", {
        "template_count": len(templates)
    })

    # Process templates (demonstration)
    results = []

    for i, template_data in enumerate(templates[:20]):  # Limit to 20 templates
        template = template_data.get("template", "")
        variables = template_data.get("variables", {})
        output_format = template_data.get("format", "plain_text")

        result = {
            "template_index": i,
            "template_id": template_data.get("id", f"template_{i+1}"),
            "status": random.choice(["success", "success", "success", "warning"]),  # 75% success rate
            "processing_time": round(random.uniform(0.1, 2.0), 2),
            "character_count": len(template) + sum(len(str(v)) for v in variables.values())
        }

        if result["status"] == "warning":
            result["warning"] = "Some template variables were missing"

        results.append(result)

    successful = len([r for r in results if r["status"] == "success"])
    total_time = sum(r["processing_time"] for r in results)

    return {
        "batch_id": operation_id,
        "templates_processed": len(results),
        "successful_formats": successful,
        "success_rate": round(successful / len(results), 2) if results else 0,
        "total_processing_time": round(total_time, 2),
        "results": results,
        "completed_at": datetime.now().isoformat()
    }

@mcp.tool()
def get_formatter_logs() -> Dict[str, Any]:
    """Get message formatter activity logs"""
    return {
        "total_operations": len(FORMATTER_LOG),
        "recent_operations": FORMATTER_LOG[-10:] if FORMATTER_LOG else [],
        "log_status": "active"
    }

if __name__ == "__main__":
    mcp.run()
