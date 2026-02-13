"""Jurisdiction-specific configuration registry."""

from typing import Dict, List, Any


JURISDICTION_CONFIG: Dict[str, Dict[str, Any]] = {
    "colorado": {
        "display_name": "Colorado",
        "regulatory_bodies": [
            "Colorado Public Utilities Commission (CPUC)",
            "Colorado Energy Office (CEO)",
        ],
        "grid_operator": "Western Interconnection (WECC)",
        "market_type": "regulated",
        "disclaimer_urls": {
            "Colorado Public Utilities Commission": "https://puc.colorado.gov",
            "Colorado Energy Office": "https://energyoffice.colorado.gov",
        },
        "scraper_sources": ["CPUC", "Colorado CRS", "eCFR"],
        "prompt_context": (
            "Colorado has a regulated electricity market under the Colorado Public Utilities Commission (CPUC). "
            "Colorado is part of the Western Interconnection and subject to WECC reliability standards. "
            "Colorado has a Renewable Energy Standard (RES) requiring 30% renewable energy for IOUs by 2020, "
            "increasing to 100% clean energy by 2040. Colorado also has a Clean Heat Standard."
        ),
        "ferc_jurisdiction": True,
    },
    "texas": {
        "display_name": "Texas",
        "regulatory_bodies": [
            "Public Utility Commission of Texas (PUCT)",
            "Electric Reliability Council of Texas (ERCOT)",
            "Railroad Commission of Texas (RRC)",
        ],
        "grid_operator": "ERCOT (Electric Reliability Council of Texas)",
        "market_type": "deregulated",
        "disclaimer_urls": {
            "Public Utility Commission of Texas": "https://www.puc.texas.gov",
            "ERCOT": "https://www.ercot.com",
            "Railroad Commission of Texas": "https://www.rrc.texas.gov",
        },
        "scraper_sources": ["PUCT", "Texas Statutes", "ERCOT", "eCFR"],
        "prompt_context": (
            "Texas has a DEREGULATED electricity market. ERCOT operates as the independent system operator "
            "for most of Texas and is largely isolated from the Eastern and Western Interconnections. "
            "Texas has LIMITED FERC jurisdiction because ERCOT does not cross state lines. "
            "The Public Utility Regulatory Act (PURA, Texas Utilities Code Title 2) governs the electric market. "
            "Chapter 39 established retail competition and market restructuring. "
            "PUCT Substantive Rules are in 16 TAC Chapter 25. "
            "There is no mandatory Renewable Portfolio Standard in Texas (Section 39.904 set voluntary goals). "
            "The Railroad Commission of Texas regulates natural gas utilities and pipelines."
        ),
        "ferc_jurisdiction": False,
    },
}


def get_jurisdiction_config(jurisdiction: str) -> Dict[str, Any]:
    """Get configuration for a jurisdiction."""
    return JURISDICTION_CONFIG.get(jurisdiction.lower(), JURISDICTION_CONFIG["colorado"])


def get_supported_jurisdictions() -> List[str]:
    """Get list of supported jurisdiction keys."""
    return list(JURISDICTION_CONFIG.keys())
