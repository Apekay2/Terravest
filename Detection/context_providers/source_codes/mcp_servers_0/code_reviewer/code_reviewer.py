#!/usr/bin/env python3
"""
Code Reviewer MCP Server
=======================

Static code analysis and security scanning server.
Provides code quality assessment, configuration detection, and best practices analysis.
No external dependencies - uses pattern matching and heuristics.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import re
import hashlib
import ast
import keyword

# Create MCP server instance
mcp = FastMCP('code_reviewer')

# Security configuration patterns
SECURITY_PATTERNS = {
    "sql_injection": [
        r'execute\s*\(\s*["\'][^"\']*\+.*["\']',
        r'cursor\.execute\s*\(\s*f["\']',
        r'query\s*=.*\+.*input',
        r'SELECT.*\+.*request\.',
        r'INSERT.*\+.*input'
    ],
    "xss_vulnerability": [
        r'innerHTML\s*=.*input',
        r'document\.write\s*\(.*input',
        r'eval\s*\(.*input',
        r'setTimeout\s*\(.*input',
        r'<script>.*\+.*input'
    ],
    "hardcoded_secrets": [
        r'password\s*=\s*["\'][^"\']{8,}["\']',
        r'api_key\s*=\s*["\'][^"\']{16,}["\']',
        r'secret\s*=\s*["\'][^"\']{8,}["\']',
        r'token\s*=\s*["\'][^"\']{20,}["\']',
        r'key\s*=\s*["\'][A-Za-z0-9+/]{32,}["\']'
    ],
    "command_injection": [
        r'os\.system\s*\(.*input',
        r'subprocess\.call\s*\(.*input',
        r'exec\s*\(.*input',
        r'eval\s*\(.*request\.',
        r'shell=True.*input'
    ],
    "path_traversal": [
        r'open\s*\(.*\.\./.*\)',
        r'file_path.*\.\./.*input',
        r'filename.*input.*\.\.',
        r'os\.path\.join.*input.*\.\.'
    ]
}

# Code quality patterns
QUALITY_PATTERNS = {
    "long_functions": r'def\s+\w+\([^)]*\):(?:\n(?:[ \t]+[^\n]*|\n))*',
    "deep_nesting": r'(?: {4}){4,}',  # 4+ levels of indentation
    "magic_numbers": r'(?<!["\w])(?:[1-9]\d{2,}|[2-9]\d)(?!["\w])',  # Numbers > 9
    "commented_code": r'#\s*[a-zA-Z_]\w*\s*[=\(\)]',
    "todo_fixme": r'#\s*(TODO|FIXME|access|XXX)',
    "long_lines": None,  # Handled separately
    "missing_docstrings": r'def\s+\w+\([^)]*\):\s*\n(?:[ \t]*\n)*[ \t]*[^"\']',
    "unused_imports": None,  # Handled with AST analysis
    "global_variables": r'global\s+\w+',
    "bare_except": r'except\s*:'
}

# Best practices patterns
BEST_PRACTICES = {
    "function_naming": r'def\s+[A-Z]\w*\(',  # PascalCase functions (should be snake_case)
    "variable_naming": r'[A-Z]{2,}\s*=',  # ALL_CAPS variables (should be constants)
    "import_organization": None,  # Handled separately
    "string_formatting": r'%\s*[sd]',  # Old-style string formatting
    "list_comprehension": None,  # Opportunities for list comprehensions
    "context_managers": r'file\s*=\s*open\(',  # Missing context manager
    "exception_handling": r'except\s+Exception:',  # Too broad exception
    "type_hints": None  # Missing type hints
}

@mcp.tool()
def analyze_code_security(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Analyze code for security vulnerabilities.

    Args:
        code: Source code to analyze
        language: Programming language ("python", "javascript", "generic")

    Returns:
        Security analysis results with configuration findings
    """
    if not code.strip():
        raise ValueError("Code cannot be empty")

    vulnerabilities = []
    total_issues = 0

    for vuln_type, patterns in SECURITY_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    "type": vuln_type,
                    "line": line_num,
                    "code_snippet": match.group(0)[:100],
                    "severity": _determine_severity(vuln_type),
                    "description": _get_vulnerability_description(vuln_type),
                    "recommendation": _get_security_recommendation(vuln_type)
                })
                total_issues += 1

    # Calculate security score
    security_score = max(0, 100 - (total_issues * 10))
    risk_level = _calculate_risk_level(security_score)

    return {
        "language": language,
        "total_vulnerabilities": total_issues,
        "vulnerabilities": vulnerabilities,
        "security_metrics": {
            "security_score": security_score,
            "risk_level": risk_level,
            "critical_issues": len([v for v in vulnerabilities if v["severity"] == "critical"]),
            "high_issues": len([v for v in vulnerabilities if v["severity"] == "high"]),
            "medium_issues": len([v for v in vulnerabilities if v["severity"] == "medium"]),
            "low_issues": len([v for v in vulnerabilities if v["severity"] == "low"])
        },
        "vulnerability_types": list(set(v["type"] for v in vulnerabilities)),
        "recommendations": _generate_security_recommendations(vulnerabilities)
    }

@mcp.tool()
def analyze_code_quality(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Analyze code quality and maintainability.

    Args:
        code: Source code to analyze
        language: Programming language

    Returns:
        Code quality analysis with metrics and suggestions
    """
    if not code.strip():
        raise ValueError("Code cannot be empty")

    quality_issues = []
    lines = code.split('\n')

    # Check each quality pattern
    for issue_type, pattern in QUALITY_PATTERNS.items():
        if pattern is None:
            continue

        if issue_type == "long_lines":
            for i, line in enumerate(lines, 1):
                if len(line) > 88:  # PEP 8 recommends 79, but 88 is common
                    quality_issues.append({
                        "type": issue_type,
                        "line": i,
                        "severity": "low",
                        "description": f"Line too long ({len(line)} characters)",
                        "recommendation": "Break long lines for better readability"
                    })
        else:
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                quality_issues.append({
                    "type": issue_type,
                    "line": line_num,
                    "severity": _determine_quality_severity(issue_type),
                    "description": _get_quality_description(issue_type),
                    "recommendation": _get_quality_recommendation(issue_type)
                })

    # Calculate complexity metrics
    complexity_metrics = _calculate_complexity_metrics(code)

    # Calculate overall quality score
    quality_score = _calculate_quality_score(quality_issues, complexity_metrics)

    return {
        "language": language,
        "total_issues": len(quality_issues),
        "quality_issues": quality_issues,
        "complexity_metrics": complexity_metrics,
        "quality_score": quality_score,
        "maintainability_index": _calculate_maintainability_index(complexity_metrics, len(quality_issues)),
        "issue_summary": {
            "critical": len([i for i in quality_issues if i["severity"] == "critical"]),
            "high": len([i for i in quality_issues if i["severity"] == "high"]),
            "medium": len([i for i in quality_issues if i["severity"] == "medium"]),
            "low": len([i for i in quality_issues if i["severity"] == "low"])
        },
        "recommendations": _generate_quality_recommendations(quality_issues, complexity_metrics)
    }

@mcp.tool()
def check_best_practices(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Check code against best practices and style guidelines.

    Args:
        code: Source code to analyze
        language: Programming language

    Returns:
        Best practices analysis with style recommendations
    """
    if not code.strip():
        raise ValueError("Code cannot be empty")

    style_issues = []

    # Check naming conventions
    for issue_type, pattern in BEST_PRACTICES.items():
        if pattern is None:
            continue

        matches = re.finditer(pattern, code, re.MULTILINE)
        for match in matches:
            line_num = code[:match.start()].count('\n') + 1
            style_issues.append({
                "type": issue_type,
                "line": line_num,
                "severity": "medium",
                "description": _get_style_description(issue_type),
                "recommendation": _get_style_recommendation(issue_type),
                "code_snippet": match.group(0)[:50]
            })

    # Additional checks for Python
    if language == "python":
        style_issues.extend(_check_python_specific_practices(code))

    # Calculate style score
    style_score = max(0, 100 - (len(style_issues) * 5))

    return {
        "language": language,
        "total_style_issues": len(style_issues),
        "style_issues": style_issues,
        "style_score": style_score,
        "compliance_level": _get_compliance_level(style_score),
        "categories": {
            "naming_conventions": len([i for i in style_issues if "naming" in i["type"]]),
            "code_organization": len([i for i in style_issues if "import" in i["type"] or "organization" in i["type"]]),
            "modern_practices": len([i for i in style_issues if i["type"] in ["string_formatting", "context_managers", "type_hints"]]),
            "error_handling": len([i for i in style_issues if "exception" in i["type"]])
        },
        "improvement_suggestions": _generate_style_improvements(style_issues)
    }

@mcp.tool()
def comprehensive_code_review(code: str, language: str = "python", include_metrics: bool = True) -> Dict[str, Any]:
    """
    Perform comprehensive code review including security, quality, and style.

    Args:
        code: Source code to analyze
        language: Programming language
        include_metrics: Whether to include detailed metrics

    Returns:
        Complete code review report
    """
    if not code.strip():
        raise ValueError("Code cannot be empty")

    # Perform all analyses
    security_analysis = analyze_code_security(code, language)
    quality_analysis = analyze_code_quality(code, language)
    style_analysis = check_best_practices(code, language)

    # Calculate overall score
    overall_score = (
        security_analysis["security_metrics"]["security_score"] * 0.4 +
        quality_analysis["quality_score"] * 0.35 +
        style_analysis["style_score"] * 0.25
    )

    # Generate summary
    total_issues = (
        security_analysis["total_vulnerabilities"] +
        quality_analysis["total_issues"] +
        style_analysis["total_style_issues"]
    )

    # Determine review result
    if overall_score >= 90:
        review_result = "excellent"
    elif overall_score >= 75:
        review_result = "good"
    elif overall_score >= 60:
        review_result = "needs_improvement"
    else:
        review_result = "poor"

    review_summary = {
        "overall_score": round(overall_score, 1),
        "review_result": review_result,
        "total_issues": total_issues,
        "language": language,
        "lines_of_code": len(code.split('\n')),
        "analysis_timestamp": "2024-01-01T00:00:00Z"  # sample timestamp
    }

    result = {
        "review_summary": review_summary,
        "security_analysis": security_analysis,
        "quality_analysis": quality_analysis,
        "style_analysis": style_analysis
    }

    if include_metrics:
        result["detailed_metrics"] = _generate_detailed_metrics(code, language)

    result["prioritized_fixes"] = _prioritize_fixes(
        security_analysis["vulnerabilities"],
        quality_analysis["quality_issues"],
        style_analysis["style_issues"]
    )

    return result

# Helper functions
def _determine_severity(vuln_type: str) -> str:
    severity_map = {
        "sql_injection": "critical",
        "command_injection": "critical",
        "xss_vulnerability": "high",
        "hardcoded_secrets": "high",
        "path_traversal": "medium"
    }
    return severity_map.get(vuln_type, "medium")

def _get_vulnerability_description(vuln_type: str) -> str:
    descriptions = {
        "sql_injection": "Potential SQL injection configuration detected",
        "xss_vulnerability": "Cross-site scripting (XSS) configuration found",
        "hardcoded_secrets": "Hardcoded credentials or secrets detected",
        "command_injection": "Command injection configuration identified",
        "path_traversal": "Path traversal configuration detected"
    }
    return descriptions.get(vuln_type, "Security issue detected")

def _get_security_recommendation(vuln_type: str) -> str:
    recommendations = {
        "sql_injection": "Use parameterized queries or prepared statements",
        "xss_vulnerability": "Sanitize user input and use safe DOM manipulation",
        "hardcoded_secrets": "Store secrets in environment variables or secure vaults",
        "command_injection": "Avoid executing user input; use safe alternatives",
        "path_traversal": "Validate and sanitize file paths; use allowlists"
    }
    return recommendations.get(vuln_type, "Review and fix security issue")

def _calculate_risk_level(security_score: int) -> str:
    if security_score >= 80:
        return "low"
    elif security_score >= 60:
        return "medium"
    elif security_score >= 40:
        return "high"
    else:
        return "critical"

def _determine_quality_severity(issue_type: str) -> str:
    severity_map = {
        "long_functions": "medium",
        "deep_nesting": "medium",
        "magic_numbers": "low",
        "commented_code": "low",
        "todo_fixme": "low",
        "long_lines": "low",
        "missing_docstrings": "medium",
        "global_variables": "medium",
        "bare_except": "high"
    }
    return severity_map.get(issue_type, "low")

def _get_quality_description(issue_type: str) -> str:
    descriptions = {
        "long_functions": "Function is too long and complex",
        "deep_nesting": "Code has deep nesting levels",
        "magic_numbers": "Magic numbers found; use named constants",
        "commented_code": "Commented-out code detected",
        "todo_fixme": "TODO/FIXME comment found",
        "missing_docstrings": "Function missing docstring",
        "global_variables": "Global variable usage detected",
        "bare_except": "Bare except clause found"
    }
    return descriptions.get(issue_type, "Code quality issue")

def _get_quality_recommendation(issue_type: str) -> str:
    recommendations = {
        "long_functions": "Break function into smaller, focused functions",
        "deep_nesting": "Reduce nesting using early returns or helper functions",
        "magic_numbers": "Replace with named constants",
        "commented_code": "Remove commented code or add explanation",
        "todo_fixme": "Address or track TODO items properly",
        "missing_docstrings": "Add docstring describing function purpose",
        "global_variables": "Use function parameters or class attributes",
        "bare_except": "Catch specific exceptions instead"
    }
    return recommendations.get(issue_type, "Improve code quality")

def _calculate_complexity_metrics(code: str) -> Dict[str, Any]:
    lines = code.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]

    return {
        "lines_of_code": len(lines),
        "logical_lines": len(non_empty_lines),
        "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
        "blank_lines": len(lines) - len(non_empty_lines),
        "functions": len(re.findall(r'def\s+\w+', code)),
        "classes": len(re.findall(r'class\s+\w+', code)),
        "cyclomatic_complexity": _estimate_cyclomatic_complexity(code)
    }

def _estimate_cyclomatic_complexity(code: str) -> int:
    # Simple estimation based on control flow keywords
    complexity_keywords = r'\b(if|elif|for|while|except|and|or)\b'
    return len(re.findall(complexity_keywords, code)) + 1

def _calculate_quality_score(quality_issues: List[Dict], complexity_metrics: Dict) -> int:
    base_score = 100

    # Deduct points for issues
    for issue in quality_issues:
        if issue["severity"] == "critical":
            base_score -= 15
        elif issue["severity"] == "high":
            base_score -= 10
        elif issue["severity"] == "medium":
            base_score -= 5
        else:
            base_score -= 2

    # Adjust for complexity
    if complexity_metrics["cyclomatic_complexity"] > 10:
        base_score -= 10

    return max(0, base_score)

def _calculate_maintainability_index(complexity_metrics: Dict, issue_count: int) -> float:
    # Simplified maintainability index calculation
    loc = complexity_metrics["logical_lines"]
    complexity = complexity_metrics["cyclomatic_complexity"]

    if loc == 0:
        return 100.0

    base_index = 171 - 5.2 * (complexity / loc) - 0.23 * complexity - 16.2 * (issue_count / loc)
    return max(0.0, min(100.0, base_index))

def _generate_security_recommendations(vulnerabilities: List[Dict]) -> List[str]:
    recommendations = set()
    for vuln in vulnerabilities:
        recommendations.add(vuln["recommendation"])
    return list(recommendations)

def _generate_quality_recommendations(quality_issues: List[Dict], complexity_metrics: Dict) -> List[str]:
    recommendations = []

    if complexity_metrics["cyclomatic_complexity"] > 10:
        recommendations.append("Reduce cyclomatic complexity by breaking down complex functions")

    if quality_issues:
        recommendations.append("Address code quality issues to improve maintainability")

    return recommendations

def _get_style_description(issue_type: str) -> str:
    descriptions = {
        "function_naming": "Function name should use snake_case",
        "variable_naming": "Variable should use lowercase with underscores",
        "string_formatting": "Use modern string formatting (f-strings or .format())",
        "context_managers": "Use context manager for file operations",
        "exception_handling": "Avoid catching generic Exception"
    }
    return descriptions.get(issue_type, "Style guideline violation")

def _get_style_recommendation(issue_type: str) -> str:
    recommendations = {
        "function_naming": "Use snake_case for function names",
        "variable_naming": "Use UPPER_CASE only for constants",
        "string_formatting": "Use f-strings for string formatting",
        "context_managers": "Use 'with open()' for file operations",
        "exception_handling": "Catch specific exception types"
    }
    return recommendations.get(issue_type, "Follow style guidelines")

def _check_python_specific_practices(code: str) -> List[Dict]:
    """Check Python-specific best practices"""
    issues = []

    # Check for missing type hints
    function_defs = re.findall(r'def\s+\w+\([^)]*\)(?:\s*->\s*\w+)?:', code)
    functions_without_hints = [f for f in function_defs if '->' not in f]

    for i, func in enumerate(functions_without_hints[:5]):  # Limit to first 5
        issues.append({
            "type": "type_hints",
            "line": i + 1,  # Simplified line number
            "severity": "low",
            "description": "Function missing type hints",
            "recommendation": "Add type hints for better code documentation",
            "code_snippet": func[:50]
        })

    return issues

def _get_compliance_level(style_score: int) -> str:
    if style_score >= 90:
        return "excellent"
    elif style_score >= 75:
        return "good"
    elif style_score >= 60:
        return "fair"
    else:
        return "poor"

def _generate_style_improvements(style_issues: List[Dict]) -> List[str]:
    improvements = set()
    for issue in style_issues:
        improvements.add(issue["recommendation"])
    return list(improvements)

def _generate_detailed_metrics(code: str, language: str) -> Dict[str, Any]:
    """Generate detailed code metrics"""
    lines = code.split('\n')

    return {
        "file_metrics": {
            "total_lines": len(lines),
            "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            "comment_ratio": len([l for l in lines if l.strip().startswith('#')]) / max(1, len(lines)),
            "average_line_length": sum(len(line) for line in lines) / max(1, len(lines))
        },
        "language_specific": {
            "imports": len(re.findall(r'^\s*(import|from)', code, re.MULTILINE)),
            "functions": len(re.findall(r'def\s+\w+', code)),
            "classes": len(re.findall(r'class\s+\w+', code))
        } if language == "python" else {}
    }

def _prioritize_fixes(vulnerabilities: List[Dict], quality_issues: List[Dict], style_issues: List[Dict]) -> List[Dict]:
    """Prioritize all issues for fixing"""
    all_issues = []

    # Add vulnerabilities with highest priority
    for vuln in vulnerabilities:
        all_issues.append({
            "category": "security",
            "priority": 1 if vuln["severity"] in ["critical", "high"] else 2,
            "description": vuln["description"],
            "line": vuln["line"],
            "recommendation": vuln["recommendation"]
        })

    # Add quality issues
    for issue in quality_issues:
        priority = 2 if issue["severity"] in ["high", "medium"] else 3
        all_issues.append({
            "category": "quality",
            "priority": priority,
            "description": issue["description"],
            "line": issue["line"],
            "recommendation": issue["recommendation"]
        })

    # Add style issues with lowest priority
    for issue in style_issues[:10]:  # Limit style issues
        all_issues.append({
            "category": "style",
            "priority": 3,
            "description": issue["description"],
            "line": issue["line"],
            "recommendation": issue["recommendation"]
        })

    # Sort by priority and return top 20
    return sorted(all_issues, key=lambda x: (x["priority"], x["line"]))[:20]

if __name__ == "__main__":
    mcp.run()
