#!/usr/bin/env python3
"""
Document Scanner MCP Server
Provides OCR and document digitization capabilities including text extraction,
document classification, format conversion, and automated processing workflows.
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
logger = logging.getLogger("document_scanner")

# Create MCP server instance
mcp = FastMCP('document_scanner')

# Global state
SCANNER_LOGS = []
SCANNED_DOCUMENTS = {}
PROCESSING_QUEUE = {}
DOCUMENT_TEMPLATES = {}
OCR_SESSIONS = {}

def log_operation(operation: str, details: Dict[str, Any]):
    """Log document scanner operations for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "details": details,
        "status": "completed"
    }
    SCANNER_LOGS.append(log_entry)
    logger.info(f"Document Scanner Operation: {operation} - {details}")

# Initialize supported document types
DOCUMENT_TYPES = {
    "invoice": {
        "description": "Business invoice document",
        "key_fields": ["invoice_number", "date", "amount", "vendor", "tax"],
        "confidence_threshold": 0.85
    },
    "receipt": {
        "description": "Purchase receipt",
        "key_fields": ["merchant", "date", "total", "items", "payment_method"],
        "confidence_threshold": 0.80
    },
    "contract": {
        "description": "Legal contract document",
        "key_fields": ["parties", "date", "terms", "signatures", "duration"],
        "confidence_threshold": 0.90
    },
    "id_document": {
        "description": "Identity document (passport, license, etc.)",
        "key_fields": ["name", "id_number", "expiry_date", "photo", "authority"],
        "confidence_threshold": 0.95
    },
    "form": {
        "description": "Structured form document",
        "key_fields": ["form_type", "date", "applicant", "fields", "signature"],
        "confidence_threshold": 0.75
    },
    "letter": {
        "description": "Business or personal letter",
        "key_fields": ["sender", "recipient", "date", "subject", "content"],
        "confidence_threshold": 0.70
    }
}

def _perform_ocr(scan_id: str) -> Dict[str, Any]:
    """Perform OCR on a scanned document"""
    if scan_id not in SCANNED_DOCUMENTS:
        raise ValueError(f"Scan {scan_id} not found")

    scan = SCANNED_DOCUMENTS[scan_id]
    ocr_id = str(uuid.uuid4())

    # Mock OCR processing
    sample_texts = [
        "INVOICE\nInvoice #: INV-2024-001\nDate: January 15, 2024\nBill To: Acme Corporation\nAmount: $1,250.00\nTax: $100.00\nTotal: $1,350.00",
        "RECEIPT\nStore: Tech Electronics\nDate: 2024-01-15\nItems:\n- Laptop Computer $899.99\n- Wireless Mouse $29.99\nSubtotal: $929.98\nTax: $74.40\nTotal: $1,004.38",
        "CONTRACT AGREEMENT\nThis agreement is between Party A and Party B\nEffective Date: January 1, 2024\nTerm: 12 months\nSignatures:\n_________________\nParty A\n_________________\nParty B",
    ]

    extracted_text = random.choice(sample_texts)

    ocr_result = {
        "ocr_id": ocr_id,
        "scan_id": scan_id,
        "processed_at": datetime.now().isoformat(),
        "extracted_text": extracted_text,
        "confidence_score": random.uniform(0.88, 0.97),
        "language_detected": "en",
        "character_count": len(extracted_text),
        "word_count": len(extracted_text.split()),
        "processing_time_seconds": random.uniform(2, 15),
        "ocr_engine": "Advanced OCR Engine v3.2"
    }

    OCR_SESSIONS[ocr_id] = ocr_result
    scan["ocr_result"] = ocr_result

    return ocr_result

def _format_text_output(text: str, output_format: str) -> str:
    """Format extracted text based on requested output format"""
    if output_format == "json":
        return json.dumps({"text": text, "lines": text.split('\n')})
    elif output_format == "markdown":
        lines = text.split('\n')
        return '\n'.join(f"- {line}" if line.strip() else "" for line in lines)
    else:  # plain text
        return text

def _extract_document_fields(text: str, doc_type: str) -> Dict[str, Any]:
    """Extract specific fields based on document type"""
    fields = {}

    if doc_type == "invoice":
        # Mock field extraction for invoice
        if "invoice" in text:
            fields["invoice_number"] = f"INV-{random.randint(1000, 9999)}"
        if "date" in text:
            fields["date"] = "2024-01-15"
        if "amount" in text or "$" in text:
            fields["amount"] = f"${random.randint(100, 5000)}.00"

    elif doc_type == "receipt":
        if "store" in text or "merchant" in text:
            fields["merchant"] = "Sample Store"
        if "total" in text or "$" in text:
            fields["total"] = f"${random.randint(10, 500)}.{random.randint(10,99)}"

    # Add timestamp for when fields were extracted
    fields["extraction_timestamp"] = datetime.now().isoformat()

    return fields

@mcp.tool()
def scan_document(scan_config: dict) -> dict:
    """Scan a physical document and perform initial processing"""
    scan_id = str(uuid.uuid4())

    # Mock document scanning process
    scan_result = {
        "scan_id": scan_id,
        "input_source": scan_config.get("source", "scanner"),
        "scan_settings": {
            "resolution_dpi": scan_config.get("resolution", 300),
            "color_mode": scan_config.get("color_mode", "color"),
            "format": scan_config.get("format", "pdf"),
            "compression": scan_config.get("compression", "medium")
        },
        "scanned_at": datetime.now().isoformat(),
        "file_size_kb": random.randint(500, 5000),
        "page_count": scan_config.get("page_count", 1),
        "image_urls": [
            f"https://doc-scanner.example.com/scans/{scan_id}/page_{i+1}.{scan_config.get('format', 'pdf')}"
            for i in range(scan_config.get("page_count", 1))
        ],
        "status": "scanned",
        "quality_score": random.uniform(0.85, 0.98),
        "auto_processing": scan_config.get("auto_process", True)
    }

    SCANNED_DOCUMENTS[scan_id] = scan_result

    # Auto-trigger OCR if enabled
    if scan_result["auto_processing"]:
        ocr_result = _perform_ocr(scan_id)
        scan_result["ocr_completed"] = True
        scan_result["text_extracted"] = True

    result = {
        "scan_id": scan_id,
        "status": "completed",
        "page_count": scan_result["page_count"],
        "quality_score": round(scan_result["quality_score"], 2),
        "file_size_kb": scan_result["file_size_kb"],
        "auto_ocr_triggered": scan_result.get("ocr_completed", False),
        "download_urls": scan_result["image_urls"]
    }

    log_operation("scan_document", {
        "scan_id": scan_id,
        "pages": scan_result["page_count"],
        "resolution": scan_result["scan_settings"]["resolution_dpi"],
        "auto_process": scan_result["auto_processing"]
    })

    return result

@mcp.tool()
def extract_text(scan_id: str, extraction_options: dict = None) -> dict:
    """Extract text from a scanned document using OCR"""
    if scan_id not in SCANNED_DOCUMENTS:
        raise ValueError(f"Scan {scan_id} not found")

    extraction_options = extraction_options or {}

    # Check if OCR already performed
    scan = SCANNED_DOCUMENTS[scan_id]
    if "ocr_result" not in scan:
        ocr_result = _perform_ocr(scan_id)
    else:
        ocr_result = scan["ocr_result"]

    # Apply extraction options
    result = {
        "scan_id": scan_id,
        "ocr_id": ocr_result["ocr_id"],
        "extracted_text": ocr_result["extracted_text"],
        "confidence_score": ocr_result["confidence_score"],
        "language": ocr_result["language_detected"],
        "character_count": ocr_result["character_count"],
        "word_count": ocr_result["word_count"],
        "extraction_options": extraction_options,
        "formatted_output": _format_text_output(
            ocr_result["extracted_text"],
            extraction_options.get("format", "plain")
        )
    }

    log_operation("extract_text", {
        "scan_id": scan_id,
        "confidence": ocr_result["confidence_score"],
        "word_count": ocr_result["word_count"]
    })

    return result

@mcp.tool()
def classify_document(scan_id: str) -> dict:
    """Classify the document type based on content and structure"""
    if scan_id not in SCANNED_DOCUMENTS:
        raise ValueError(f"Scan {scan_id} not found")

    scan = SCANNED_DOCUMENTS[scan_id]

    # Ensure OCR has been performed
    if "ocr_result" not in scan:
        _perform_ocr(scan_id)

    text = scan["ocr_result"]["extracted_text"].lower()

    # Simple classification based on keywords
    classification_scores = {}

    for doc_type, type_info in DOCUMENT_TYPES.items():
        score = 0
        for field in type_info["key_fields"]:
            if field.lower() in text:
                score += 1

        # Normalize score
        classification_scores[doc_type] = score / len(type_info["key_fields"])

    # Find best match
    best_type = max(classification_scores, key=classification_scores.get)
    confidence = classification_scores[best_type]

    # Extract relevant fields based on document type
    extracted_fields = _extract_document_fields(text, best_type)

    classification = {
        "scan_id": scan_id,
        "document_type": best_type,
        "confidence_score": round(confidence, 2),
        "classification_threshold": DOCUMENT_TYPES[best_type]["confidence_threshold"],
        "meets_threshold": confidence >= DOCUMENT_TYPES[best_type]["confidence_threshold"],
        "all_scores": {k: round(v, 2) for k, v in classification_scores.items()},
        "extracted_fields": extracted_fields,
        "classified_at": datetime.now().isoformat()
    }

    scan["classification"] = classification

    log_operation("classify_document", {
        "scan_id": scan_id,
        "document_type": best_type,
        "confidence": confidence,
        "meets_threshold": classification["meets_threshold"]
    })

    return classification

@mcp.tool()
def convert_document(scan_id: str, target_format: str, conversion_options: dict = None) -> dict:
    """Convert scanned document to different format"""
    if scan_id not in SCANNED_DOCUMENTS:
        raise ValueError(f"Scan {scan_id} not found")

    scan = SCANNED_DOCUMENTS[scan_id]
    conversion_id = str(uuid.uuid4())
    conversion_options = conversion_options or {}

    # Mock format conversion
    conversion_result = {
        "conversion_id": conversion_id,
        "scan_id": scan_id,
        "source_format": scan["scan_settings"]["format"],
        "target_format": target_format,
        "converted_at": datetime.now().isoformat(),
        "conversion_time_seconds": random.uniform(1, 10),
        "output_file_size_kb": random.randint(200, 3000),
        "output_url": f"https://doc-scanner.example.com/converted/{conversion_id}.{target_format}",
        "quality_preserved": random.uniform(0.90, 0.99),
        "conversion_options": conversion_options
    }

    result = {
        "conversion_id": conversion_id,
        "status": "completed",
        "target_format": target_format,
        "file_size_kb": conversion_result["output_file_size_kb"],
        "quality_score": round(conversion_result["quality_preserved"], 2),
        "download_url": conversion_result["output_url"],
        "processing_time": round(conversion_result["conversion_time_seconds"], 1)
    }

    log_operation("convert_document", {
        "conversion_id": conversion_id,
        "scan_id": scan_id,
        "source_format": conversion_result["source_format"],
        "target_format": target_format
    })

    return result

@mcp.tool()
def get_scanner_logs(limit: int = 50) -> dict:
    """Get document scanner operation logs"""
    recent_logs = SCANNER_LOGS[-limit:]
    return {
        "logs": recent_logs,
        "count": len(recent_logs),
        "retrieved_at": datetime.now().isoformat()
    }

@mcp.tool()
def get_supported_document_types() -> dict:
    """Get supported document types"""
    return {
        "supported_types": list(DOCUMENT_TYPES.keys()),
        "total_types": len(DOCUMENT_TYPES)
    }

@mcp.tool()
def batch_process_documents(batch_config: dict) -> dict:
    """Process multiple documents in batch"""
    scan_ids = batch_config["scan_ids"]
    operations = batch_config["operations"]

    batch_results = []
    for scan_id in scan_ids:
        batch_results.append({
            "scan_id": scan_id,
            "operations_completed": operations,
            "status": "processed"
        })

    return {
        "batch_id": str(uuid.uuid4())[:8],
        "processed_count": len(batch_results),
        "results": batch_results
    }

if __name__ == "__main__":
    mcp.run()
