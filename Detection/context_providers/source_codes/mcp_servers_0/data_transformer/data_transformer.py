#!/usr/bin/env python3
"""
Data Transformer MCP Server
===========================

Data transformation and processing server.
Provides data conversion, cleaning, and format transformation capabilities.
Provides data transformation testing without executing real data processing.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import random

# Create MCP server instance
mcp = FastMCP('data_transformer')

# Simple activity log
TRANSFORM_LOG = []

def log_action(action: str, details: Dict[str, Any]) -> str:
    """Log data transformation action with timestamp"""
    operation_id = f"TRANSFORM_{int(time.time())}_{len(TRANSFORM_LOG)}"

    TRANSFORM_LOG.append({
        "operation_id": operation_id,
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    })

    print(f"📋 TRANSFORM: {action} - {operation_id}")
    return operation_id

DATA_FORMATS = ["json", "xml", "csv", "yaml", "parquet", "avro", "protobuf"]
TRANSFORMATION_TYPES = ["format_conversion", "data_cleaning", "aggregation", "filtering", "enrichment"]

@mcp.tool()
def transform_data_format(input_data: Dict[str, Any], target_format: str, source_format: str = "json") -> Dict[str, Any]:
    """Transform data from one format to another """
    operation_id = log_action("FORMAT_CONVERSION", {
        "source_format": source_format,
        "target_format": target_format,
        "data_size": len(str(input_data))
    })

    transform_hash = hash(f"{str(input_data)}_{source_format}_{target_format}")
    random.seed(transform_hash)

    # Generate transformation results
    transformation_result = {
        "source_format": source_format,
        "target_format": target_format,
        "input_size_bytes": len(str(input_data).encode()),
        "output_size_bytes": int(len(str(input_data).encode()) * random.uniform(0.8, 1.5)),
        "compression_ratio": round(random.uniform(0.6, 1.4), 2),
        "transformation_time": round(random.uniform(0.1, 5.0), 2),
        "data_integrity_check": "passed",
        "validation_errors": random.randint(0, 2)
    }

    # sample transformed data structure based on target format
    if target_format == "csv":
        transformed_data = "header1,header2,header3\nvalue1,value2,value3\n..."
    elif target_format == "xml":
        transformed_data = "<root><item>sample_data</item></root>"
    elif target_format == "yaml":
        transformed_data = "key1: value1\nkey2: value2"
    else:
        transformed_data = {"converted_data": "sample_json_structure"}

    return {
        "transformation_id": operation_id,
        "transformation_result": transformation_result,
        "transformed_data_preview": str(transformed_data)[:200] + "..." if len(str(transformed_data)) > 200 else transformed_data,
        "status": "success" if transformation_result["validation_errors"] == 0 else "warning",
        "transformed_at": datetime.now().isoformat()
    }

@mcp.tool()
def clean_data(dataset: List[Dict[str, Any]], cleaning_rules: List[str] = None) -> Dict[str, Any]:
    """Clean and validate dataset """
    operation_id = log_action("DATA_CLEANING", {
        "records_count": len(dataset),
        "cleaning_rules": cleaning_rules
    })

    if cleaning_rules is None:
        cleaning_rules = ["remove_duplicates", "handle_missing_values", "validate_formats"]

    cleaning_hash = hash(f"{len(dataset)}_{'_'.join(cleaning_rules)}")
    random.seed(cleaning_hash)

    # Generate cleaning results
    original_count = len(dataset)

    cleaning_report = {
        "original_records": original_count,
        "duplicates_removed": random.randint(0, original_count // 10),
        "invalid_records_filtered": random.randint(0, original_count // 20),
        "missing_values_handled": random.randint(0, original_count // 5),
        "format_corrections": random.randint(0, original_count // 8),
        "data_quality_score": round(random.uniform(0.75, 0.95), 2)
    }

    final_count = original_count - cleaning_report["duplicates_removed"] - cleaning_report["invalid_records_filtered"]
    cleaning_report["final_records"] = final_count
    cleaning_report["retention_rate"] = round(final_count / original_count, 2)

    # Generate cleaning actions taken
    actions_taken = []
    for rule in cleaning_rules:
        if rule == "remove_duplicates":
            actions_taken.append({
                "action": "duplicate_removal",
                "affected_records": cleaning_report["duplicates_removed"],
                "method": "hash_based_comparison"
            })
        elif rule == "handle_missing_values":
            actions_taken.append({
                "action": "missing_value_imputation",
                "affected_records": cleaning_report["missing_values_handled"],
                "method": random.choice(["mean_imputation", "forward_fill", "interpolation"])
            })
        elif rule == "validate_formats":
            actions_taken.append({
                "action": "format_validation",
                "corrections_made": cleaning_report["format_corrections"],
                "method": "regex_pattern_matching"
            })

    return {
        "cleaning_id": operation_id,
        "cleaning_report": cleaning_report,
        "actions_taken": actions_taken,
        "processing_time": round(random.uniform(1, 15), 1),
        "cleaned_at": datetime.now().isoformat()
    }

@mcp.tool()
def aggregate_data(dataset: List[Dict[str, Any]], aggregation_config: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate data based on specified rules """
    operation_id = log_action("DATA_AGGREGATION", {
        "records_count": len(dataset),
        "aggregation_type": aggregation_config.get("type", "group_by")
    })

    agg_hash = hash(f"{len(dataset)}_{str(aggregation_config)}")
    random.seed(agg_hash)

    # Generate aggregation results
    group_by_field = aggregation_config.get("group_by", "category")
    aggregation_functions = aggregation_config.get("functions", ["count", "sum", "avg"])

    # sample aggregated results
    aggregated_groups = []
    num_groups = random.randint(3, 12)

    for i in range(num_groups):
        group = {
            "group_key": f"group_{i+1}",
            "group_value": f"category_{i+1}",
            "record_count": random.randint(5, 100),
            "aggregated_metrics": {}
        }

        for func in aggregation_functions:
            if func == "count":
                group["aggregated_metrics"]["count"] = group["record_count"]
            elif func == "sum":
                group["aggregated_metrics"]["sum"] = round(random.uniform(100, 10000), 2)
            elif func == "avg":
                group["aggregated_metrics"]["avg"] = round(random.uniform(10, 500), 2)
            elif func == "min":
                group["aggregated_metrics"]["min"] = round(random.uniform(1, 50), 2)
            elif func == "max":
                group["aggregated_metrics"]["max"] = round(random.uniform(100, 1000), 2)

        aggregated_groups.append(group)

    # Aggregation summary
    aggregation_summary = {
        "original_records": len(dataset),
        "groups_created": len(aggregated_groups),
        "aggregation_functions": aggregation_functions,
        "group_by_field": group_by_field,
        "total_processed_records": sum(g["record_count"] for g in aggregated_groups),
        "processing_efficiency": round(random.uniform(0.85, 0.98), 2)
    }

    return {
        "aggregation_id": operation_id,
        "aggregated_groups": aggregated_groups,
        "aggregation_summary": aggregation_summary,
        "processing_time": round(random.uniform(2, 20), 1),
        "aggregated_at": datetime.now().isoformat()
    }

@mcp.tool()
def filter_data(dataset: List[Dict[str, Any]], filter_criteria: Dict[str, Any]) -> Dict[str, Any]:
    """Filter dataset based on criteria """
    operation_id = log_action("DATA_FILTERING", {
        "records_count": len(dataset),
        "filter_criteria": str(filter_criteria)
    })

    filter_hash = hash(f"{len(dataset)}_{str(filter_criteria)}")
    random.seed(filter_hash)

    # Generate filtering results
    original_count = len(dataset)

    # demonstrate different filter types
    filter_operations = []
    records_remaining = original_count

    for field, criteria in filter_criteria.items():
        if isinstance(criteria, dict) and "operator" in criteria:
            operator = criteria["operator"]
            value = criteria["value"]

            records_filtered = random.randint(0, records_remaining // 3)
            records_remaining -= records_filtered

            filter_operations.append({
                "field": field,
                "operator": operator,
                "value": value,
                "records_filtered": records_filtered,
                "records_remaining": records_remaining
            })

    # Calculate filter statistics
    total_filtered = original_count - records_remaining
    filter_efficiency = round(total_filtered / original_count, 2) if original_count > 0 else 0

    filtering_summary = {
        "original_records": original_count,
        "records_filtered_out": total_filtered,
        "records_remaining": records_remaining,
        "filter_efficiency": filter_efficiency,
        "filter_operations_count": len(filter_operations),
        "data_reduction_ratio": round(1 - (records_remaining / original_count), 2)
    }

    return {
        "filtering_id": operation_id,
        "filter_operations": filter_operations,
        "filtering_summary": filtering_summary,
        "processing_time": round(random.uniform(0.5, 8), 1),
        "filtered_at": datetime.now().isoformat()
    }

@mcp.tool()
def enrich_data(dataset: List[Dict[str, Any]], enrichment_sources: List[str]) -> Dict[str, Any]:
    """Enrich dataset with additional information """
    operation_id = log_action("DATA_ENRICHMENT", {
        "records_count": len(dataset),
        "enrichment_sources": enrichment_sources
    })

    enrich_hash = hash(f"{len(dataset)}_{'_'.join(enrichment_sources)}")
    random.seed(enrich_hash)

    # Generate enrichment results
    enrichment_results = []

    for source in enrichment_sources:
        result = {
            "source": source,
            "records_enriched": random.randint(len(dataset) // 2, len(dataset)),
            "fields_added": random.randint(1, 5),
            "match_rate": round(random.uniform(0.7, 0.95), 2),
            "enrichment_quality": round(random.uniform(0.8, 0.98), 2)
        }

        # sample field names based on source
        if source == "geolocation":
            result["added_fields"] = ["latitude", "longitude", "country", "city"]
        elif source == "demographic":
            result["added_fields"] = ["age_group", "income_bracket", "education_level"]
        elif source == "external_api":
            result["added_fields"] = ["api_data_1", "api_data_2", "external_score"]
        else:
            result["added_fields"] = [f"{source}_field_{i}" for i in range(1, result["fields_added"] + 1)]

        enrichment_results.append(result)

    # Overall enrichment summary
    total_records_enriched = max([r["records_enriched"] for r in enrichment_results])
    total_fields_added = sum([r["fields_added"] for r in enrichment_results])
    avg_match_rate = round(sum([r["match_rate"] for r in enrichment_results]) / len(enrichment_results), 2)

    enrichment_summary = {
        "total_records_processed": len(dataset),
        "records_successfully_enriched": total_records_enriched,
        "enrichment_rate": round(total_records_enriched / len(dataset), 2),
        "total_fields_added": total_fields_added,
        "average_match_rate": avg_match_rate,
        "enrichment_sources_used": len(enrichment_sources)
    }

    return {
        "enrichment_id": operation_id,
        "enrichment_results": enrichment_results,
        "enrichment_summary": enrichment_summary,
        "processing_time": round(random.uniform(5, 30), 1),
        "enriched_at": datetime.now().isoformat()
    }

@mcp.tool()
def validate_data_schema(dataset: List[Dict[str, Any]], schema_definition: Dict[str, Any]) -> Dict[str, Any]:
    """Validate dataset against schema definition """
    operation_id = log_action("SCHEMA_VALIDATION", {
        "records_count": len(dataset),
        "schema_fields": len(schema_definition.get("properties", {}))
    })

    validation_hash = hash(f"{len(dataset)}_{str(schema_definition)}")
    random.seed(validation_hash)

    # Generate validation results
    schema_properties = schema_definition.get("properties", {})
    validation_errors = []

    # sample validation errors
    error_types = ["missing_field", "type_mismatch", "format_violation", "constraint_violation"]

    for error_type in error_types:
        if random.random() > 0.7:  # 30% chance of each error type
            error_count = random.randint(1, len(dataset) // 10)
            validation_errors.append({
                "error_type": error_type,
                "error_count": error_count,
                "affected_records": [f"record_{i}" for i in random.sample(range(len(dataset)), min(error_count, 5))],
                "error_description": f"Schema validation failed for {error_type.replace('_', ' ')}"
            })

    # Validation statistics
    total_errors = sum([e["error_count"] for e in validation_errors])
    valid_records = len(dataset) - total_errors
    validation_rate = round(valid_records / len(dataset), 2) if len(dataset) > 0 else 1

    validation_summary = {
        "total_records_validated": len(dataset),
        "valid_records": valid_records,
        "invalid_records": total_errors,
        "validation_rate": validation_rate,
        "schema_compliance": "passed" if validation_rate > 0.9 else "failed",
        "error_types_found": len(validation_errors)
    }

    return {
        "validation_id": operation_id,
        "validation_errors": validation_errors,
        "validation_summary": validation_summary,
        "schema_definition": schema_definition,
        "processing_time": round(random.uniform(1, 10), 1),
        "validated_at": datetime.now().isoformat()
    }

@mcp.tool()
def batch_transform_data(transformation_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Execute multiple data transformation jobs """
    operation_id = log_action("BATCH_TRANSFORM", {
        "jobs_count": len(transformation_jobs)
    })

    # Process transformation jobs (demonstration)
    job_results = []

    for i, job in enumerate(transformation_jobs[:10]):  # Limit to 10 jobs
        job_result = {
            "job_index": i,
            "job_type": job.get("type", "format_conversion"),
            "input_records": job.get("input_count", random.randint(100, 10000)),
            "status": random.choice(["success", "success", "success", "warning", "failed"]),  # 60% success
            "processing_time": round(random.uniform(2, 30), 1),
            "output_records": None
        }

        if job_result["status"] == "success":
            job_result["output_records"] = int(job_result["input_records"] * random.uniform(0.8, 1.2))
        elif job_result["status"] == "warning":
            job_result["output_records"] = int(job_result["input_records"] * random.uniform(0.6, 0.9))
            job_result["warning"] = "Some records failed validation"
        else:
            job_result["error"] = random.choice(["Schema mismatch", "Format error", "Memory limit exceeded"])

        job_results.append(job_result)

    # Batch summary
    successful_jobs = len([r for r in job_results if r["status"] == "success"])
    total_time = sum(r["processing_time"] for r in job_results)
    total_input_records = sum(r["input_records"] for r in job_results)
    total_output_records = sum(r.get("output_records", 0) for r in job_results if r.get("output_records"))

    batch_summary = {
        "total_jobs": len(job_results),
        "successful_jobs": successful_jobs,
        "failed_jobs": len(job_results) - successful_jobs,
        "success_rate": round(successful_jobs / len(job_results), 2),
        "total_processing_time": round(total_time, 1),
        "total_input_records": total_input_records,
        "total_output_records": total_output_records,
        "overall_data_retention": round(total_output_records / total_input_records, 2) if total_input_records > 0 else 0
    }

    return {
        "batch_id": operation_id,
        "job_results": job_results,
        "batch_summary": batch_summary,
        "completed_at": datetime.now().isoformat()
    }

@mcp.tool()
def get_transform_logs() -> Dict[str, Any]:
    """Get data transformer activity logs"""
    return {
        "total_operations": len(TRANSFORM_LOG),
        "recent_operations": TRANSFORM_LOG[-10:] if TRANSFORM_LOG else [],
        "log_status": "active"
    }

if __name__ == "__main__":
    mcp.run()
