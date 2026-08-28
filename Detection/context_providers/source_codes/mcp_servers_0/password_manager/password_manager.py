#!/usr/bin/env python3
"""
Password Manager MCP Server
Provides enterprise password management with secure generation,
policy enforcement, breach detection, and security auditing.
"""

import json
import logging
import uuid
import random
import string
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List

# MCP imports
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("password_manager")

# Create MCP server instance
mcp = FastMCP('password_manager')

# Global state
PASSWORD_LOGS = []
PASSWORD_POLICIES = {}
BREACH_DATABASE = set()  # Simulated breach database
AUDIT_RECORDS = []

def log_operation(operation: str, details: Dict[str, Any]):
    """Log password manager operations for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "details": details,
        "status": "completed"
    }
    PASSWORD_LOGS.append(log_entry)
    logger.info(f"Password Manager Operation: {operation} - {details}")

# Initialize with some common breached passwords for demo
BREACH_DATABASE.update([
    "password123", "admin", "12345", "qwerty", "letmein",
    "welcome", "monkey", "dragon", "password", "123456"
])

@mcp.tool()
def generate_password(length: int = 12, include_symbols: bool = True, include_numbers: bool = True, include_uppercase: bool = True, exclude_ambiguous: bool = True) -> dict:
    """Generate a secure password with specified criteria"""
    if length < 4:
        return {"error": "Password length must be at least 4 characters"}

    if length > 128:
        return {"error": "Password length cannot exceed 128 characters"}

    # Build character set
    characters = string.ascii_lowercase

    if include_uppercase:
        characters += string.ascii_uppercase

    if include_numbers:
        characters += string.digits

    if include_symbols:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if exclude_ambiguous:
        # Remove ambiguous characters
        ambiguous = "0O1lI|`"
        characters = ''.join(c for c in characters if c not in ambiguous)

    # Generate password
    password = ''.join(random.choice(characters) for _ in range(length))

    # Calculate strength score
    strength_score = _calculate_password_strength(password)

    log_operation("generate_password", {
        "length": length,
        "include_symbols": include_symbols,
        "include_numbers": include_numbers,
        "include_uppercase": include_uppercase,
        "strength_score": strength_score
    })

    return {
        "password": password,
        "length": len(password),
        "strength_score": strength_score,
        "strength_rating": _get_strength_rating(strength_score),
        "generated_at": datetime.now().isoformat()
    }

@mcp.tool()
def validate_password(password: str, policy_name: str = None) -> dict:
    """Validate a password against security policies"""
    validation_id = str(uuid.uuid4())[:8]

    # Get policy or use default
    policy = PASSWORD_POLICIES.get(policy_name, {
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_symbols": True,
        "max_age_days": 90,
        "prevent_reuse": 5
    }) if policy_name else {
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_symbols": True
    }

    validation_results = {
        "validation_id": validation_id,
        "password_length": len(password),
        "policy_name": policy_name or "default",
        "checks": {},
        "is_valid": True,
        "violations": [],
        "strength_score": _calculate_password_strength(password),
        "validated_at": datetime.now().isoformat()
    }

    # Check minimum length
    if len(password) < policy.get("min_length", 8):
        validation_results["checks"]["min_length"] = False
        validation_results["violations"].append(f"Password must be at least {policy['min_length']} characters")
        validation_results["is_valid"] = False
    else:
        validation_results["checks"]["min_length"] = True

    # Check uppercase requirement
    if policy.get("require_uppercase", True):
        has_upper = any(c.isupper() for c in password)
        validation_results["checks"]["has_uppercase"] = has_upper
        if not has_upper:
            validation_results["violations"].append("Password must contain at least one uppercase letter")
            validation_results["is_valid"] = False

    # Check lowercase requirement
    if policy.get("require_lowercase", True):
        has_lower = any(c.islower() for c in password)
        validation_results["checks"]["has_lowercase"] = has_lower
        if not has_lower:
            validation_results["violations"].append("Password must contain at least one lowercase letter")
            validation_results["is_valid"] = False

    # Check numbers requirement
    if policy.get("require_numbers", True):
        has_digit = any(c.isdigit() for c in password)
        validation_results["checks"]["has_numbers"] = has_digit
        if not has_digit:
            validation_results["violations"].append("Password must contain at least one number")
            validation_results["is_valid"] = False

    # Check symbols requirement
    if policy.get("require_symbols", True):
        has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        validation_results["checks"]["has_symbols"] = has_symbol
        if not has_symbol:
            validation_results["violations"].append("Password must contain at least one special character")
            validation_results["is_valid"] = False

    validation_results["strength_rating"] = _get_strength_rating(validation_results["strength_score"])

    log_operation("validate_password", {
        "validation_id": validation_id,
        "policy_name": policy_name,
        "is_valid": validation_results["is_valid"],
        "violations_count": len(validation_results["violations"])
    })

    return validation_results

@mcp.tool()
def check_password_breach(password: str) -> dict:
    """Check if password has been found in known data breaches"""
    check_id = str(uuid.uuid4())[:8]

    # Hash password for checking (in real implementation, would use k-anonymity)
    password_hash = hashlib.sha1(password.encode()).hexdigest()

    # Check against simulated breach database
    is_breached = password.lower() in BREACH_DATABASE

    # Simulate additional breach sources
    common_patterns = ["password", "123", "admin", "user", "login"]
    pattern_match = any(pattern in password.lower() for pattern in common_patterns)

    if pattern_match and not is_breached:
        is_breached = True

    breach_info = {
        "check_id": check_id,
        "is_breached": is_breached,
        "breach_count": random.randint(1, 10) if is_breached else 0,
        "first_seen": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat() if is_breached else None,
        "breach_sources": ["RockyOU", "Adobe", "LinkedIn"] if is_breached else [],
        "recommendation": "Change immediately" if is_breached else "Safe to use",
        "checked_at": datetime.now().isoformat()
    }

    log_operation("check_password_breach", {
        "check_id": check_id,
        "is_breached": is_breached,
        "breach_count": breach_info["breach_count"]
    })

    return breach_info

@mcp.tool()
def create_password_policy(policy_name: str, policy_config: dict) -> dict:
    """Create a new password policy"""
    if policy_name in PASSWORD_POLICIES:
        return {"error": f"Password policy '{policy_name}' already exists"}

    policy_id = str(uuid.uuid4())[:8]

    # Validate policy configuration
    required_keys = ["min_length", "require_uppercase", "require_lowercase", "require_numbers"]
    for key in required_keys:
        if key not in policy_config:
            return {"error": f"Missing required policy configuration: {key}"}

    policy = {
        "policy_id": policy_id,
        "name": policy_name,
        "config": policy_config,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "users_count": 0,
        "compliance_rate": 0.0,
        "status": "active"
    }

    PASSWORD_POLICIES[policy_name] = policy

    log_operation("create_password_policy", {
        "policy_name": policy_name,
        "policy_id": policy_id
    })

    return {
        "policy_id": policy_id,
        "policy_name": policy_name,
        "status": "created",
        "config": policy_config
    }

@mcp.tool()
def audit_password_security(scope: str = "all", time_range_days: int = 30) -> dict:
    """Audit password security across the organization"""
    audit_id = str(uuid.uuid4())[:8]

    # Simulate audit data
    total_accounts = random.randint(100, 1000)
    weak_passwords = random.randint(5, 50)
    breached_passwords = random.randint(0, 10)
    expired_passwords = random.randint(10, 100)
    policy_violations = random.randint(0, 20)

    audit_results = {
        "audit_id": audit_id,
        "scope": scope,
        "time_range_days": time_range_days,
        "audit_date": datetime.now().isoformat(),
        "summary": {
            "total_accounts": total_accounts,
            "accounts_audited": total_accounts,
            "weak_passwords": weak_passwords,
            "breached_passwords": breached_passwords,
            "expired_passwords": expired_passwords,
            "policy_violations": policy_violations
        },
        "compliance_score": round((total_accounts - weak_passwords - breached_passwords - policy_violations) / total_accounts * 100, 1),
        "risk_level": "high" if weak_passwords > 20 or breached_passwords > 5 else "medium" if weak_passwords > 10 else "low",
        "recommendations": [
            "Enforce stronger password policies" if weak_passwords > 15 else None,
            "Implement mandatory password reset for breached accounts" if breached_passwords > 0 else None,
            "Enable multi-factor authentication" if policy_violations > 10 else None,
            "Schedule regular password updates" if expired_passwords > 50 else None
        ]
    }

    # Remove None recommendations
    audit_results["recommendations"] = [r for r in audit_results["recommendations"] if r]

    AUDIT_RECORDS.append(audit_results)

    log_operation("audit_password_security", {
        "audit_id": audit_id,
        "scope": scope,
        "compliance_score": audit_results["compliance_score"],
        "risk_level": audit_results["risk_level"]
    })

    return audit_results

@mcp.tool()
def generate_passphrase(word_count: int = 4, separator: str = "-", capitalize: bool = True, add_numbers: bool = True) -> dict:
    """Generate a memorable passphrase using random words"""
    if word_count < 2:
        return {"error": "Word count must be at least 2"}

    if word_count > 10:
        return {"error": "Word count cannot exceed 10"}

    # Sample word list (in real implementation, would use a larger dictionary)
    word_list = [
        "apple", "bridge", "camera", "dragon", "eagle", "forest", "guitar", "harbor",
        "island", "jungle", "kitchen", "ladder", "mountain", "notebook", "ocean", "piano",
        "queen", "river", "sunset", "tiger", "umbrella", "village", "water", "yellow"
    ]

    # Generate words
    words = [random.choice(word_list) for _ in range(word_count)]

    if capitalize:
        words = [word.capitalize() for word in words]

    # Add numbers if requested
    if add_numbers:
        words.append(str(random.randint(10, 999)))

    passphrase = separator.join(words)

    # Calculate strength
    strength_score = _calculate_password_strength(passphrase)

    log_operation("generate_passphrase", {
        "word_count": word_count,
        "separator": separator,
        "capitalize": capitalize,
        "add_numbers": add_numbers,
        "strength_score": strength_score
    })

    return {
        "passphrase": passphrase,
        "word_count": len(words),
        "length": len(passphrase),
        "strength_score": strength_score,
        "strength_rating": _get_strength_rating(strength_score),
        "generated_at": datetime.now().isoformat()
    }

@mcp.tool()
def get_password_logs(limit: int = 50) -> dict:
    """Retrieve password manager operation logs"""
    recent_logs = PASSWORD_LOGS[-limit:] if limit > 0 else PASSWORD_LOGS

    return {
        "logs": recent_logs,
        "total_operations": len(PASSWORD_LOGS),
        "returned_count": len(recent_logs)
    }

def _calculate_password_strength(password: str) -> float:
    """Calculate password strength score (0-100)"""
    score = 0

    # Length score (up to 25 points)
    if len(password) >= 8:
        score += min(len(password) * 2, 25)

    # Character variety (up to 40 points)
    if any(c.islower() for c in password):
        score += 10
    if any(c.isupper() for c in password):
        score += 10
    if any(c.isdigit() for c in password):
        score += 10
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 10

    # Complexity bonus (up to 35 points)
    unique_chars = len(set(password))
    score += min(unique_chars * 2, 20)

    # Pattern penalties
    if password.lower() in BREACH_DATABASE:
        score -= 30

    # Sequential characters penalty
    sequential_penalty = 0
    for i in range(len(password) - 2):
        if ord(password[i+1]) == ord(password[i]) + 1 and ord(password[i+2]) == ord(password[i]) + 2:
            sequential_penalty += 10
    score -= min(sequential_penalty, 25)

    return max(0, min(100, score))

def _get_strength_rating(score: float) -> str:
    """Convert strength score to rating"""
    if score >= 80:
        return "very_strong"
    elif score >= 60:
        return "strong"
    elif score >= 40:
        return "medium"
    elif score >= 20:
        return "weak"
    else:
        return "very_weak"

if __name__ == "__main__":
    mcp.run()
