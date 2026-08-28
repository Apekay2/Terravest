#!/usr/bin/env python3
"""
Patent Analyzer MCP Server
=========================

Intellectual property research and patent analysis server.
Provides patent search, analysis, and competitive intelligence.
No external APIs required - uses sample patent database.
"""

from fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import hashlib
import random
from datetime import datetime, timedelta

# Create MCP server instance
mcp = FastMCP('patent_analyzer')

# Patent classification systems
PATENT_CLASSES = [
    "A01 - Agriculture", "A23 - Foods", "A61 - Medical", "A63 - Sports/Games",
    "B01 - Physical/Chemical Processes", "B21 - Mechanical Metal-Working", "B25 - Hand Tools",
    "B29 - Working of Plastics", "B32 - Layered Products", "B60 - Vehicles",
    "C01 - Inorganic Chemistry", "C07 - Organic Chemistry", "C08 - Macromolecules",
    "C12 - Biochemistry", "E01 - Construction", "E04 - Building",
    "F01 - Machines/Engines", "F15 - Fluid-Pressure Actuators", "F16 - Engineering Elements",
    "F21 - Lighting", "F23 - Combustion Apparatus", "F24 - Heating",
    "G01 - Measuring", "G02 - Optics", "G03 - Photography", "G06 - Computing",
    "G08 - Signalling", "G09 - Education", "G10 - Musical Instruments",
    "H01 - Basic Electric Elements", "H02 - Electric Power", "H03 - Electronic Circuits",
    "H04 - Electric Communication", "H05 - Electric Techniques"
]

PATENT_OFFICES = [
    "USPTO", "EPO", "JPO", "KIPO", "CNIPA", "CIPO", "IP Australia", "UKIPO",
    "DPMA", "INPI France", "INPI Brazil", "Rospatent", "IP India"
]

ASSIGNEE_TYPES = [
    "Large Corporation", "Startup", "University", "Government Agency",
    "Research Institute", "Individual Inventor", "Non-Profit Organization"
]

def generate_patent_id(title: str, year: int, office: str) -> str:
    """Generate consistent patent ID"""
    hash_input = f"{title.lower().replace(' ', '_')}_{year}_{office}"
    return hashlib.md5(hash_input.encode()).hexdigest()[:10].upper()

def demonstrate_patent_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """demonstrate patent search with realistic results"""
    query_hash = hash(query.lower())
    random.seed(query_hash)

    patents = []
    for i in range(min(limit, 25)):
        filing_year = random.randint(2010, 2024)
        patent_office = random.choice(PATENT_OFFICES)

        # Generate patent title variations
        title_templates = [
            f"Method and System for {query.title()} Enhancement",
            f"Apparatus for {query.title()} Processing",
            f"Improved {query.title()} Technology",
            f"Advanced {query.title()} Device and Method",
            f"System for Optimized {query.title()} Implementation",
            f"Novel Approach to {query.title()} Integration",
            f"Smart {query.title()} Management System",
            f"Automated {query.title()} Control Method"
        ]

        title = random.choice(title_templates)
        patent_id = generate_patent_id(title, filing_year, patent_office)

        # Generate inventor names
        num_inventors = random.randint(1, 5)
        inventors = [f"Inventor_{random.randint(1000, 9999)}" for _ in range(num_inventors)]

        # Generate assignee
        assignee_type = random.choice(ASSIGNEE_TYPES)
        if assignee_type == "Large Corporation":
            assignee = random.choice(["TechCorp Inc", "InnovateTech LLC", "FutureSystems Corp", "GlobalTech Industries"])
        elif assignee_type == "University":
            assignee = random.choice(["MIT", "Stanford University", "CMU", "UC Berkeley"])
        else:
            assignee = f"{assignee_type} Entity"

        patents.append({
            "patent_id": patent_id,
            "title": title,
            "inventors": inventors,
            "assignee": assignee,
            "assignee_type": assignee_type,
            "filing_date": f"{filing_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "publication_date": f"{filing_year + random.randint(1, 2)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "patent_office": patent_office,
            "patent_class": random.choice(PATENT_CLASSES),
            "claims_count": random.randint(5, 50),
            "abstract": f"This patent describes an innovative approach to {query} that addresses key technical challenges in the field. The invention provides improved efficiency and functionality compared to existing solutions.",
            "citation_count": random.randint(0, 100),
            "family_size": random.randint(1, 15),
            "status": random.choice(["Active", "Expired", "Pending", "Abandoned"]),
            "priority_countries": random.sample(["US", "EP", "JP", "CN", "KR", "CA", "AU"], k=random.randint(1, 4))
        })

    return sorted(patents, key=lambda x: x['citation_count'], reverse=True)

@mcp.tool()
def search_patents(query: str, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Search patents by keywords with optional filters.

    Args:
        query: Search terms for patent discovery
        limit: Maximum number of results (default: 10, max: 50)
        filters: Optional filters (year_range, patent_office, status, etc.)

    Returns:
        Patent search results with metadata
    """
    if not query.strip():
        raise ValueError("Query cannot be empty")

    limit = min(max(1, limit), 50)
    patents = demonstrate_patent_search(query, limit)

    # Apply filters if provided
    if filters:
        # Year range filter
        if 'year_range' in filters:
            try:
                start_year, end_year = map(int, filters['year_range'].split('-'))
                patents = [p for p in patents if start_year <= int(p['filing_date'][:4]) <= end_year]
            except ValueError:
                pass

        # Patent office filter
        if 'patent_office' in filters:
            patents = [p for p in patents if p['patent_office'] == filters['patent_office']]

        # Status filter
        if 'status' in filters:
            patents = [p for p in patents if p['status'] == filters['status']]

        # Assignee type filter
        if 'assignee_type' in filters:
            patents = [p for p in patents if p['assignee_type'] == filters['assignee_type']]

    return {
        "query": query,
        "total_results": len(patents),
        "patents": patents[:limit],
        "search_metadata": {
            "patent_offices": list(set(p['patent_office'] for p in patents)),
            "patent_classes": list(set(p['patent_class'] for p in patents)),
            "year_distribution": _calculate_year_distribution(patents),
            "status_distribution": _calculate_status_distribution(patents),
            "top_assignees": _get_top_assignees(patents)
        },
        "applied_filters": filters or {}
    }

@mcp.tool()
def analyze_patent_landscape(technology_area: str, analysis_period: str = "recent") -> Dict[str, Any]:
    """
    Analyze patent landscape for a specific technology area.

    Args:
        technology_area: Technology domain to analyze
        analysis_period: Time period ("recent", "historical", "all")

    Returns:
        Comprehensive patent landscape analysis
    """
    # Generate deterministic analysis
    area_hash = hash(f"{technology_area}_{analysis_period}")
    random.seed(area_hash)

    # demonstrate patent activity trends
    patent_trend = {}
    base_year = 2015 if analysis_period == "recent" else 2005
    end_year = 2024

    for year in range(base_year, end_year + 1):
        # demonstrate growth trend with some randomness
        base_count = random.randint(50, 500)
        growth_factor = (year - base_year) * 0.1 + 1
        patent_trend[str(year)] = int(base_count * growth_factor * random.uniform(0.8, 1.2))

    # Top companies in this area
    top_companies = []
    company_names = [
        "TechGiant Corp", "InnovateAI Inc", "FutureTech Systems", "GlobalPatents LLC",
        "SmartSolutions Inc", "NextGen Technologies", "Advanced Systems Corp"
    ]

    for company in random.sample(company_names, k=random.randint(5, 7)):
        top_companies.append({
            "company": company,
            "patent_count": random.randint(10, 200),
            "market_share": round(random.uniform(5, 25), 1),
            "innovation_score": round(random.uniform(0.3, 1.0), 3),
            "recent_growth": round(random.uniform(-10, 50), 1)
        })

    top_companies.sort(key=lambda x: x['patent_count'], reverse=True)

    # Emerging trends
    emerging_trends = []
    trend_prefixes = ["AI-Enhanced", "Quantum", "Blockchain-Based", "IoT-Enabled",
                     "Cloud-Native", "Edge-Computing", "5G-Enabled", "Sustainable"]

    for prefix in random.sample(trend_prefixes, k=random.randint(3, 6)):
        emerging_trends.append({
            "trend": f"{prefix} {technology_area}",
            "growth_rate": round(random.uniform(20, 150), 1),
            "patent_velocity": random.randint(5, 50),
            "maturity_level": random.choice(["emerging", "growing", "maturing"])
        })

    return {
        "technology_area": technology_area,
        "analysis_period": analysis_period,
        "patent_trends": patent_trend,
        "top_companies": top_companies,
        "emerging_trends": emerging_trends,
        "landscape_metrics": {
            "total_patents": sum(patent_trend.values()),
            "annual_growth_rate": round(random.uniform(5, 25), 1),
            "market_concentration": round(random.uniform(0.3, 0.8), 2),
            "innovation_diversity": round(random.uniform(0.4, 0.9), 2)
        },
        "geographic_distribution": {
            "US": round(random.uniform(25, 45), 1),
            "China": round(random.uniform(20, 35), 1),
            "Europe": round(random.uniform(15, 25), 1),
            "Japan": round(random.uniform(8, 15), 1),
            "Others": round(random.uniform(10, 20), 1)
        }
    }

@mcp.tool()
def check_patent_freedom_to_operate(technology_description: str, geographic_scope: List[str] = None) -> Dict[str, Any]:
    """
    Analyze freedom to operate for a given technology.

    Args:
        technology_description: Description of the technology
        geographic_scope: List of countries/regions to analyze

    Returns:
        Freedom to operate analysis with risk assessment
    """
    if not technology_description.strip():
        raise ValueError("Technology description cannot be empty")

    if geographic_scope is None:
        geographic_scope = ["US", "EU", "JP", "CN"]

    # Generate deterministic analysis
    tech_hash = hash(technology_description.lower())
    random.seed(tech_hash)

    # Analyze potential blocking patents
    blocking_patents = []
    for i in range(random.randint(0, 8)):
        blocking_patents.append({
            "patent_id": f"BLOCK_{tech_hash % 10000}_{i}",
            "title": f"Related Technology Patent {i+1}",
            "overlap_score": round(random.uniform(0.3, 0.9), 2),
            "expiry_date": f"20{random.randint(25, 35)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "geographic_coverage": random.sample(geographic_scope, k=random.randint(1, len(geographic_scope))),
            "risk_level": random.choice(["low", "medium", "high"])
        })

    # Calculate overall risk
    high_risk_patents = len([p for p in blocking_patents if p['risk_level'] == 'high'])
    medium_risk_patents = len([p for p in blocking_patents if p['risk_level'] == 'medium'])

    if high_risk_patents > 2:
        overall_risk = "high"
    elif high_risk_patents > 0 or medium_risk_patents > 3:
        overall_risk = "medium"
    else:
        overall_risk = "low"

    # Generate recommendations
    recommendations = []
    if overall_risk == "high":
        recommendations.extend([
            "Consider design-around strategies",
            "Investigate licensing opportunities",
            "Perform detailed claim analysis"
        ])
    elif overall_risk == "medium":
        recommendations.extend([
            "Monitor patent landscape for changes",
            "Consider filing continuation applications"
        ])
    else:
        recommendations.append("Proceed with caution but low blocking risk detected")

    return {
        "technology_description": technology_description,
        "geographic_scope": geographic_scope,
        "blocking_patents": blocking_patents,
        "risk_assessment": {
            "overall_risk": overall_risk,
            "total_blocking_patents": len(blocking_patents),
            "high_risk_count": high_risk_patents,
            "medium_risk_count": medium_risk_patents,
            "coverage_score": round(random.uniform(0.1, 0.8), 2)
        },
        "recommendations": recommendations,
        "geographic_analysis": {
            region: {
                "blocking_patents": len([p for p in blocking_patents if region in p['geographic_coverage']]),
                "risk_level": random.choice(["low", "medium", "high"])
            }
            for region in geographic_scope
        }
    }

@mcp.tool()
def analyze_patent_citations(patent_id: str) -> Dict[str, Any]:
    """
    Analyze citation patterns for a specific patent.

    Args:
        patent_id: Patent identifier to analyze

    Returns:
        Citation analysis with forward and backward citations
    """
    # Generate deterministic citation data
    patent_hash = hash(patent_id)
    random.seed(patent_hash)

    # Backward citations (prior art)
    backward_citations = []
    for i in range(random.randint(5, 25)):
        backward_citations.append({
            "cited_patent_id": f"PRIOR_{patent_hash % 1000}_{i}",
            "title": f"Prior Art Patent {i+1}",
            "filing_year": random.randint(2000, 2020),
            "relevance_score": round(random.uniform(0.3, 1.0), 2),
            "citation_type": random.choice(["examiner", "applicant", "third_party"])
        })

    # Forward citations (citing patents)
    forward_citations = []
    for i in range(random.randint(0, 50)):
        forward_citations.append({
            "citing_patent_id": f"CITE_{patent_hash % 1000}_{i}",
            "title": f"Citing Patent {i+1}",
            "filing_year": random.randint(2015, 2024),
            "relevance_score": round(random.uniform(0.2, 0.9), 2),
            "technology_area": random.choice(PATENT_CLASSES)
        })

    # Calculate citation metrics
    citation_velocity = len([c for c in forward_citations if c['filing_year'] >= 2020])
    impact_score = len(forward_citations) * 0.1 + citation_velocity * 0.2

    return {
        "patent_id": patent_id,
        "backward_citations": backward_citations,
        "forward_citations": forward_citations,
        "citation_metrics": {
            "total_backward": len(backward_citations),
            "total_forward": len(forward_citations),
            "citation_velocity": citation_velocity,
            "impact_score": round(impact_score, 2),
            "self_citations": random.randint(0, min(5, len(forward_citations))),
            "international_citations": random.randint(0, len(forward_citations) // 2)
        },
        "citation_trends": {
            str(year): len([c for c in forward_citations if c['filing_year'] == year])
            for year in range(2015, 2025)
        },
        "technology_influence": {
            "cross_domain_citations": random.randint(0, len(forward_citations) // 3),
            "industry_adoption": round(random.uniform(0.1, 0.8), 2),
            "research_impact": round(random.uniform(0.2, 0.9), 2)
        }
    }

def _calculate_year_distribution(patents: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate distribution of patents by year"""
    year_dist = {}
    for patent in patents:
        year = patent['filing_date'][:4]
        year_dist[year] = year_dist.get(year, 0) + 1
    return year_dist

def _calculate_status_distribution(patents: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate distribution of patents by status"""
    status_dist = {}
    for patent in patents:
        status = patent['status']
        status_dist[status] = status_dist.get(status, 0) + 1
    return status_dist

def _get_top_assignees(patents: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    """Get top patent assignees by count"""
    assignee_count = {}
    for patent in patents:
        assignee = patent['assignee']
        assignee_count[assignee] = assignee_count.get(assignee, 0) + 1

    top_assignees = sorted(assignee_count.items(), key=lambda x: x[1], reverse=True)[:limit]
    return [{"assignee": name, "patent_count": count} for name, count in top_assignees]

if __name__ == "__main__":
    mcp.run()
