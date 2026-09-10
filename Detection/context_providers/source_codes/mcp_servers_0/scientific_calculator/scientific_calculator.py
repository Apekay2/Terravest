#!/usr/bin/env python3
"""
Scientific Calculator MCP Server
===============================

Advanced mathematical computation server for scientific calculations.
Provides trigonometry, logarithms, statistics, unit conversions, and more.
No external dependencies - uses Python's built-in math and statistics libraries.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Union, Optional
import math
import statistics
import random

# Create MCP server instance
mcp = FastMCP('scientific_calculator')

# Constants and conversion factors
PHYSICAL_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "golden_ratio": (1 + math.sqrt(5)) / 2,
    "speed_of_light": 299792458,  # m/s
    "planck_constant": 6.62607015e-34,  # J⋅Hz⁻¹
    "avogadro_number": 6.02214076e23,  # mol⁻¹
    "boltzmann_constant": 1.380649e-23,  # J⋅K⁻¹
    "electron_charge": 1.602176634e-19,  # C
    "gravitational_constant": 6.67430e-11,  # m³⋅kg⁻¹⋅s⁻²
}

UNIT_CONVERSIONS = {
    "length": {
        "meter": 1.0,
        "kilometer": 1000.0,
        "centimeter": 0.01,
        "millimeter": 0.001,
        "inch": 0.0254,
        "foot": 0.3048,
        "yard": 0.9144,
        "mile": 1609.344
    },
    "mass": {
        "kilogram": 1.0,
        "gram": 0.001,
        "pound": 0.453592,
        "ounce": 0.0283495,
        "ton": 1000.0
    },
    "temperature": {
        "celsius": lambda c: c,
        "fahrenheit": lambda f: (f - 32) * 5/9,
        "kelvin": lambda k: k - 273.15
    }
}

@mcp.tool()
def basic_arithmetic(expression: str) -> Dict[str, Any]:
    """
    Perform basic arithmetic operations with support for complex expressions.

    Args:
        expression: Mathematical expression (e.g., "2 + 3 * 4", "sqrt(16) + pi")

    Returns:
        Result of the calculation with step-by-step breakdown
    """
    if not expression.strip():
        raise ValueError("Expression cannot be empty")

    # Safe evaluation with math functions
    safe_dict = {
        "__builtins__": {},
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow,
        "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
        "log": math.log, "log10": math.log10, "exp": math.exp,
        "pi": math.pi, "e": math.e,
        "floor": math.floor, "ceil": math.ceil,
        "factorial": math.factorial
    }

    try:
        result = eval(expression, safe_dict)

        # Determine result type
        if isinstance(result, int):
            result_type = "integer"
        elif isinstance(result, float):
            result_type = "float"
        elif isinstance(result, complex):
            result_type = "complex"
        else:
            result_type = "unknown"

        return {
            "expression": expression,
            "result": result,
            "result_type": result_type,
            "formatted_result": f"{result:,.6g}" if isinstance(result, (int, float)) else str(result),
            "is_integer": isinstance(result, int) or (isinstance(result, float) and result.is_integer()),
            "scientific_notation": f"{result:.3e}" if isinstance(result, (int, float)) and abs(result) > 1000 else None
        }

    except Exception as e:
        raise ValueError(f"Invalid expression: {str(e)}")

@mcp.tool()
def trigonometric_functions(angle: float, unit: str = "radians", functions: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Calculate trigonometric functions for given angle.

    Args:
        angle: Input angle value
        unit: Angle unit ("radians", "degrees")
        functions: List of functions to calculate (default: all)

    Returns:
        Dictionary with trigonometric function results
    """
    if unit not in ["radians", "degrees"]:
        raise ValueError("Unit must be 'radians' or 'degrees'")

    # Convert to radians if needed
    if unit == "degrees":
        angle_rad = math.radians(angle)
    else:
        angle_rad = angle

    # Default functions if not specified
    if functions is None:
        functions = ["sin", "cos", "tan", "csc", "sec", "cot"]

    results = {"angle": angle, "unit": unit, "angle_radians": angle_rad}

    try:
        for func in functions:
            if func == "sin":
                results["sin"] = math.sin(angle_rad)
            elif func == "cos":
                results["cos"] = math.cos(angle_rad)
            elif func == "tan":
                results["tan"] = math.tan(angle_rad)
            elif func == "csc":
                sin_val = math.sin(angle_rad)
                results["csc"] = 1/sin_val if sin_val != 0 else float('inf')
            elif func == "sec":
                cos_val = math.cos(angle_rad)
                results["sec"] = 1/cos_val if cos_val != 0 else float('inf')
            elif func == "cot":
                tan_val = math.tan(angle_rad)
                results["cot"] = 1/tan_val if tan_val != 0 else float('inf')

    except Exception as e:
        results["error"] = str(e)

    # Add special angle information
    special_angles = {
        0: "0°", 30: "30°", 45: "45°", 60: "60°", 90: "90°",
        180: "180°", 270: "270°", 360: "360°"
    }

    if unit == "degrees" and angle in special_angles:
        results["special_angle"] = special_angles[angle]

    return results

@mcp.tool()
def statistical_analysis(data: List[float], analysis_type: str = "full") -> Dict[str, Any]:
    """
    Perform statistical analysis on numerical data.

    Args:
        data: List of numerical values
        analysis_type: Type of analysis ("basic", "full", "distribution")

    Returns:
        Statistical metrics and analysis results
    """
    if not data:
        raise ValueError("Data list cannot be empty")

    if not all(isinstance(x, (int, float)) for x in data):
        raise ValueError("All data points must be numbers")

    results = {
        "data_size": len(data),
        "analysis_type": analysis_type
    }

    # Basic statistics
    results["basic_stats"] = {
        "mean": statistics.mean(data),
        "median": statistics.median(data),
        "min": min(data),
        "max": max(data),
        "range": max(data) - min(data),
        "sum": sum(data)
    }

    if len(data) > 1:
        results["basic_stats"].update({
            "variance": statistics.variance(data),
            "std_dev": statistics.stdev(data),
            "std_error": statistics.stdev(data) / math.sqrt(len(data))
        })

        # Mode (if meaningful)
        try:
            results["basic_stats"]["mode"] = statistics.mode(data)
        except statistics.StatisticsError:
            results["basic_stats"]["mode"] = "No unique mode"

    if analysis_type in ["full", "distribution"]:
        # Quartiles and percentiles
        sorted_data = sorted(data)
        n = len(data)

        results["distribution_stats"] = {
            "q1": sorted_data[n//4] if n >= 4 else None,
            "q3": sorted_data[3*n//4] if n >= 4 else None,
            "iqr": sorted_data[3*n//4] - sorted_data[n//4] if n >= 4 else None,
            "skewness": _calculate_skewness(data),
            "kurtosis": _calculate_kurtosis(data)
        }

        # Outlier detection (IQR method)
        if n >= 4:
            q1, q3 = results["distribution_stats"]["q1"], results["distribution_stats"]["q3"]
            iqr = results["distribution_stats"]["iqr"]
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = [x for x in data if x < lower_bound or x > upper_bound]
            results["distribution_stats"]["outliers"] = outliers
            results["distribution_stats"]["outlier_count"] = len(outliers)

    return results

@mcp.tool()
def unit_conversion(value: float, from_unit: str, to_unit: str, category: str) -> Dict[str, Any]:
    """
    Convert between different units of measurement.

    Args:
        value: Value to convert
        from_unit: Source unit
        to_unit: Target unit
        category: Unit category ("length", "mass", "temperature")

    Returns:
        Conversion result with formula and explanation
    """
    if category not in UNIT_CONVERSIONS:
        raise ValueError(f"Category must be one of: {', '.join(UNIT_CONVERSIONS.keys())}")

    conversions = UNIT_CONVERSIONS[category]

    if category == "temperature":
        # Special handling for temperature
        if from_unit not in conversions or to_unit not in conversions:
            raise ValueError(f"Units must be: {', '.join(conversions.keys())}")

        # Convert to Celsius first
        if from_unit == "celsius":
            celsius_value = value
        elif from_unit == "fahrenheit":
            celsius_value = (value - 32) * 5/9
        elif from_unit == "kelvin":
            celsius_value = value - 273.15

        # Convert from Celsius to target
        if to_unit == "celsius":
            result = celsius_value
        elif to_unit == "fahrenheit":
            result = celsius_value * 9/5 + 32
        elif to_unit == "kelvin":
            result = celsius_value + 273.15

    else:
        # Standard unit conversion via base unit
        if from_unit not in conversions or to_unit not in conversions:
            raise ValueError(f"Units must be: {', '.join(conversions.keys())}")

        # Convert to base unit, then to target unit
        base_value = value * conversions[from_unit]
        result = base_value / conversions[to_unit]

    return {
        "original_value": value,
        "from_unit": from_unit,
        "to_unit": to_unit,
        "category": category,
        "result": result,
        "formatted_result": f"{result:.6g}",
        "conversion_formula": f"1 {from_unit} = {conversions.get(from_unit, 'N/A')} base units" if category != "temperature" else "Temperature conversion uses specific formulas"
    }

@mcp.tool()
def logarithmic_functions(value: float, base: Optional[float] = None) -> Dict[str, Any]:
    """
    Calculate logarithmic functions with different bases.

    Args:
        value: Input value (must be positive)
        base: Logarithm base (default: natural log)

    Returns:
        Logarithm results with multiple bases
    """
    if value <= 0:
        raise ValueError("Value must be positive for logarithm calculation")

    results = {"input_value": value}

    # Natural logarithm (base e)
    results["ln"] = math.log(value)

    # Common logarithm (base 10)
    results["log10"] = math.log10(value)

    # Binary logarithm (base 2)
    results["log2"] = math.log2(value)

    # Custom base if provided
    if base is not None:
        if base <= 0 or base == 1:
            raise ValueError("Base must be positive and not equal to 1")
        results[f"log_{base}"] = math.log(value, base)

    # Inverse operations (exponentials)
    results["exponentials"] = {
        "e^x": math.exp(value),
        "10^x": 10 ** value,
        "2^x": 2 ** value
    }

    return results

@mcp.tool()
def get_physical_constants(names: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Retrieve physical constants and their values.

    Args:
        names: List of constant names (default: all)

    Returns:
        Dictionary of physical constants with descriptions
    """
    if names is None:
        names = list(PHYSICAL_CONSTANTS.keys())

    results = {}

    for name in names:
        if name in PHYSICAL_CONSTANTS:
            results[name] = {
                "value": PHYSICAL_CONSTANTS[name],
                "formatted": f"{PHYSICAL_CONSTANTS[name]:.6e}" if abs(PHYSICAL_CONSTANTS[name]) > 1000 or abs(PHYSICAL_CONSTANTS[name]) < 0.001 else f"{PHYSICAL_CONSTANTS[name]:.6f}"
            }
        else:
            results[name] = {"error": f"Unknown constant: {name}"}

    results["available_constants"] = list(PHYSICAL_CONSTANTS.keys())

    return results

def _calculate_skewness(data: List[float]) -> float:
    """Calculate skewness of data distribution"""
    if len(data) < 3:
        return 0.0

    mean = statistics.mean(data)
    std_dev = statistics.stdev(data)
    n = len(data)

    skewness = sum(((x - mean) / std_dev) ** 3 for x in data) / n
    return skewness

def _calculate_kurtosis(data: List[float]) -> float:
    """Calculate kurtosis of data distribution"""
    if len(data) < 4:
        return 0.0

    mean = statistics.mean(data)
    std_dev = statistics.stdev(data)
    n = len(data)

    kurtosis = sum(((x - mean) / std_dev) ** 4 for x in data) / n - 3
    return kurtosis

if __name__ == "__main__":
    mcp.run()
