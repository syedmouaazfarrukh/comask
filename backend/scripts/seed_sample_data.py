"""Seed the database with sample Colorado energy compliance documents."""

import asyncio
import sys
sys.path.insert(0, '/app')

from app.db.database import init_db, get_db_session
from app.db.models import Document, DocumentChunk, AuthorityLevel, JurisdictionType, DocumentType
from datetime import date
import uuid


SAMPLE_DOCUMENTS = [
    {
        "title": "Colorado Renewable Energy Standard - C.R.S. § 40-2-124",
        "content": """Colorado Renewable Energy Standard (RES) - C.R.S. § 40-2-124

RENEWABLE ENERGY STANDARD REQUIREMENTS:

(1) Electric utilities in Colorado are required to generate or cause to be generated electricity from eligible energy resources in the following minimum amounts:

For Qualifying Retail Utilities (Investor-Owned Utilities):
- 30% by 2020 and thereafter
- Of which 3% must be derived from distributed generation (e.g., rooftop solar)

For Cooperative Electric Associations serving 100,000 or more meters:
- 20% by 2020 and thereafter

For Municipal Utilities:
- 10% by 2020 and thereafter

(2) ELIGIBLE ENERGY RESOURCES include:
- Solar energy
- Wind energy
- Geothermal energy
- Biomass (including biodiesel, landfill gas, and anaerobic digestion)
- New small hydroelectricity (10 MW or less)
- Fuel cells using hydrogen derived from eligible energy resources
- Recycled energy

(3) DISTRIBUTED GENERATION: At least 3% of retail sales must come from distributed generation for qualifying retail utilities. Distributed generation includes:
- Rooftop solar photovoltaic systems
- Community solar gardens
- Other distributed renewable energy systems located on the customer's side of the meter

(4) RENEWABLE ENERGY CREDITS (RECs): Compliance may be achieved through:
- Direct generation from owned facilities
- Purchase of RECs from eligible facilities
- Contracts for the purchase of renewable energy
- Community solar garden subscriptions

(5) COST CAPS: Retail rate impact shall not exceed 2% for qualifying retail utilities.

(6) ENFORCEMENT: The Colorado Public Utilities Commission shall enforce compliance and may assess penalties for non-compliance.

Citation: C.R.S. § 40-2-124
Effective Date: Originally enacted 2004, amended through 2021
Authority: Colorado Revised Statutes, Title 40 - Utilities""",
        "source_url": "https://leg.colorado.gov/sites/default/files/images/olls/crs2021-title-40.pdf",
        "document_type": DocumentType.STATUTE,
        "authority_level": AuthorityLevel.STATE,
        "jurisdiction_type": JurisdictionType.COLORADO,
        "source_name": "Colorado Revised Statutes",
        "citation": "C.R.S. § 40-2-124",
    },
    {
        "title": "Colorado PUC Rules Governing Electric Utilities - 4 CCR 723-3",
        "content": """COLORADO CODE OF REGULATIONS - 4 CCR 723-3
RULES REGULATING ELECTRIC UTILITIES

PART 3 - RULES REGULATING ELECTRIC UTILITIES

RULE 3001. APPLICABILITY
These rules apply to electric utilities, as defined in § 40-3-101, C.R.S., and to electric utility service in the State of Colorado.

RULE 3100. SERVICE REQUIREMENTS
(a) Every electric utility shall provide adequate, efficient, safe, and reasonable service.
(b) Electric utilities shall maintain sufficient generation, transmission, and distribution facilities.
(c) Service interruptions shall be minimized and customers shall be notified of planned outages.

RULE 3200. METERING REQUIREMENTS
(a) All electricity sold shall be measured by accurate meters.
(b) Meters shall be tested periodically and upon customer request.
(c) Net metering customers shall have bi-directional meters installed at utility expense.

RULE 3400. RATE SCHEDULES AND TARIFFS
(a) All rates, terms, and conditions of service shall be published in tariffs filed with the Commission.
(b) Rate changes require Commission approval through formal proceedings.
(c) Time-of-use rates may be offered with Commission approval.

RULE 3600. INTERCONNECTION STANDARDS
(a) Utilities shall allow interconnection of customer-owned generation.
(b) Interconnection applications shall be processed within specified timeframes.
(c) Technical standards for interconnection shall conform to IEEE 1547.

RULE 3700. NET METERING
(a) Customers with eligible renewable energy systems may net meter.
(b) Net metering capacity limit: 25 kW for residential, 500 kW for commercial.
(c) Excess generation credits shall carry forward for 12 months.

RULE 3800. RENEWABLE ENERGY COMPLIANCE
(a) Utilities shall file annual renewable energy compliance reports.
(b) Reports shall include REC documentation and cost recovery accounting.
(c) Commission shall review and approve utility renewable energy plans.

Citation: 4 CCR 723-3
Effective Date: As amended through 2023
Authority: Colorado Public Utilities Commission""",
        "source_url": "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=10491",
        "document_type": DocumentType.REGULATION,
        "authority_level": AuthorityLevel.STATE,
        "jurisdiction_type": JurisdictionType.COLORADO,
        "source_name": "Colorado Code of Regulations",
        "citation": "4 CCR 723-3",
    },
    {
        "title": "FERC Order 2222 - Distributed Energy Resources Participation",
        "content": """FEDERAL ENERGY REGULATORY COMMISSION
18 CFR Part 35
Order No. 2222

PARTICIPATION OF DISTRIBUTED ENERGY RESOURCE AGGREGATIONS IN MARKETS
OPERATED BY REGIONAL TRANSMISSION ORGANIZATIONS AND INDEPENDENT SYSTEM OPERATORS

SUMMARY:
FERC Order 2222 removes barriers to the participation of distributed energy resource (DER) aggregations in regional wholesale electricity markets.

KEY PROVISIONS:

1. ELIGIBILITY
- DER aggregations may include solar PV, battery storage, demand response, electric vehicles, and other distributed resources.
- Minimum size thresholds for participation shall be 100 kW or lower.
- Aggregations may be located across multiple pricing nodes.

2. PARTICIPATION MODELS
- RTOs/ISOs must allow DERs to provide all services they are technically capable of providing.
- Services include: capacity, energy, and ancillary services (frequency regulation, spinning reserves, etc.).
- Multi-use applications are permitted (participation in wholesale and retail programs).

3. COORDINATION REQUIREMENTS
- RTOs/ISOs must establish coordination protocols with distribution utilities.
- Data sharing agreements must protect operational reliability.
- Distribution utilities may object to DER participation on reliability grounds.

4. METERING AND TELEMETRY
- Aggregators must meet RTO/ISO metering and telemetry requirements.
- Sub-metering within aggregations may be permitted.
- 15-minute interval data is generally required.

5. COMPLIANCE DEADLINES
- RTOs/ISOs must submit compliance filings within one year of the effective date.
- Implementation must occur within a reasonable timeframe after compliance filing approval.

RELEVANCE TO COLORADO:
As Colorado utilities participate in organized wholesale markets (including through SPP membership), Order 2222 requirements affect how distributed energy resources in Colorado can participate in these markets.

Citation: 18 CFR Part 35; FERC Order No. 2222
Effective Date: February 2021
Authority: Federal Energy Regulatory Commission""",
        "source_url": "https://www.ferc.gov/media/ferc-order-no-2222-fact-sheet",
        "document_type": DocumentType.ORDER,
        "authority_level": AuthorityLevel.FEDERAL,
        "jurisdiction_type": JurisdictionType.FEDERAL,
        "source_name": "FERC",
        "citation": "18 CFR Part 35; FERC Order 2222",
    },
    {
        "title": "Colorado Clean Energy Plan Requirements - C.R.S. § 40-2-125.5",
        "content": """Colorado Clean Energy Plan Requirements
C.R.S. § 40-2-125.5

CLEAN ENERGY PLAN REQUIREMENTS FOR INVESTOR-OWNED UTILITIES:

(1) EMISSION REDUCTION TARGETS:
Each qualifying retail utility shall submit a clean energy plan that will achieve the following carbon dioxide emission reductions from 2005 levels:
- 80% reduction by 2030
- 100% clean energy (zero emissions) by 2040

(2) PLAN REQUIREMENTS:
Clean energy plans must include:
(a) A timeline for retiring, repowering, or retrofitting existing carbon-emitting generation facilities
(b) Plans for adding new renewable energy resources
(c) Assessment of energy storage needs and deployment
(d) Analysis of transmission system upgrades
(e) Workforce transition plans for affected workers
(f) Customer rate impact projections

(3) COST RECOVERY:
(a) Prudently incurred costs for clean energy plan implementation may be recovered through rates
(b) Costs associated with early retirement of generating facilities may be amortized
(c) Commission shall consider rate impacts on low-income customers

(4) RELIABILITY REQUIREMENTS:
(a) Plans must maintain system reliability
(b) Utilities must demonstrate adequate capacity reserves
(c) Transmission adequacy must be verified

(5) COMMISSION REVIEW:
(a) The Commission shall approve, modify, or reject clean energy plans
(b) Plans shall be updated every three years
(c) Public comment and stakeholder participation is required

(6) DEFINITIONS:
"Clean energy" means energy generated from eligible energy resources as defined in § 40-2-124, or from non-emitting sources including nuclear energy.

Citation: C.R.S. § 40-2-125.5
Effective Date: 2019
Authority: Colorado Revised Statutes, Title 40 - Utilities""",
        "source_url": "https://leg.colorado.gov/sites/default/files/images/olls/crs2021-title-40.pdf",
        "document_type": DocumentType.STATUTE,
        "authority_level": AuthorityLevel.STATE,
        "jurisdiction_type": JurisdictionType.COLORADO,
        "source_name": "Colorado Revised Statutes",
        "citation": "C.R.S. § 40-2-125.5",
    },
    {
        "title": "NERC Reliability Standards Applicable to Colorado",
        "content": """NORTH AMERICAN ELECTRIC RELIABILITY CORPORATION (NERC)
RELIABILITY STANDARDS APPLICABLE TO COLORADO

OVERVIEW:
Colorado utilities operating bulk power system facilities must comply with mandatory NERC reliability standards. These standards are enforced through the Western Electricity Coordinating Council (WECC).

KEY RELIABILITY STANDARDS:

BAL-001-2: Real Power Balancing Control Performance
- Balancing authorities must maintain system frequency within acceptable limits
- Applies to all balancing authority areas in Colorado

FAC-001-3: Facility Interconnection Requirements
- Establishes interconnection requirements for generation and transmission
- Applicable to transmission owners and generation owners

FAC-002-2: Facility Interconnection Studies
- Required studies for new generator interconnection
- Study requirements and timelines

TPL-001-5: Transmission System Planning Performance
- Near-term transmission planning assessments
- Long-term transmission planning assessments
- Performance requirements during contingency events

TOP-001-4: Transmission Operations
- System operators must operate within reliability limits
- Real-time monitoring requirements
- Coordination requirements with neighboring systems

IRO-001-4: Reliability Coordination
- Reliability coordinator responsibilities
- Wide-area view monitoring
- Emergency operations coordination

CIP-002 through CIP-014: Critical Infrastructure Protection Standards
- Cybersecurity requirements for bulk power system cyber assets
- Physical security requirements for critical facilities
- Personnel training and access management

PRC-005-6: Protection System Maintenance
- Testing and maintenance of protection systems
- Documentation requirements

APPLICABILITY TO COLORADO:
These standards apply to:
- Xcel Energy (Public Service Company of Colorado)
- Black Hills Energy
- Tri-State Generation and Transmission
- Colorado Springs Utilities (bulk power system interconnections)
- Other registered entities operating in Colorado

ENFORCEMENT:
WECC conducts compliance monitoring and enforcement on behalf of NERC.
Violations may result in financial penalties.

Citation: NERC Reliability Standards
Authority: Federal Energy Regulatory Commission (delegated to NERC and WECC)""",
        "source_url": "https://www.nerc.com/pa/Stand/Pages/ReliabilityStandards.aspx",
        "document_type": DocumentType.STANDARD,
        "authority_level": AuthorityLevel.REGIONAL,
        "jurisdiction_type": JurisdictionType.NERC,
        "source_name": "NERC",
        "citation": "NERC Reliability Standards",
    },
    {
        "title": "Colorado PUC Decision - Xcel Energy Renewable Energy Plan (2023)",
        "content": """BEFORE THE PUBLIC UTILITIES COMMISSION OF THE STATE OF COLORADO

DECISION NO. C23-XXXX
PROCEEDING NO. 23A-XXXX

IN THE MATTER OF THE APPLICATION OF PUBLIC SERVICE COMPANY OF COLORADO
FOR APPROVAL OF ITS 2023 RENEWABLE ENERGY COMPLIANCE PLAN

DECISION APPROVING RENEWABLE ENERGY COMPLIANCE PLAN WITH MODIFICATIONS

I. SUMMARY
The Commission approves, with modifications, Public Service Company of Colorado's (Xcel Energy) 2023 Renewable Energy Compliance Plan.

II. BACKGROUND
Public Service Company of Colorado filed its 2023 Renewable Energy Compliance Plan pursuant to C.R.S. § 40-2-124 and Commission Rule 3665.

III. KEY FINDINGS

A. RENEWABLE ENERGY ACHIEVEMENTS:
- Company has achieved 31.2% renewable energy as of 2022
- Solar generation: 1,800 MW
- Wind generation: 3,200 MW
- Total renewable capacity exceeds requirements

B. DISTRIBUTED GENERATION:
- 485 MW of distributed solar installed
- Community solar garden program: 210 MW subscribed
- Rooftop solar: 275 MW

C. COST RECOVERY:
- Renewable energy costs remain within 2% rate cap
- No adverse impact on customer rates identified
- Energy Cost Adjustment (ECA) mechanism continues

D. FUTURE COMMITMENTS:
- 2,000 MW additional renewable energy by 2030
- Battery storage: 500 MW by 2025
- Coal plant retirements on schedule

IV. COMMISSION ORDERS:
1. The 2023 Renewable Energy Compliance Plan is APPROVED with modifications.
2. Company shall file quarterly progress reports.
3. Company shall increase community solar allocation for low-income customers.
4. Cost recovery through ECA mechanism is approved.

V. COMPLIANCE REQUIREMENTS:
This Decision shall become effective immediately.
Annual compliance reports shall be filed by April 1 of each year.

COMMISSIONER SIGNATURES:
[Commissioners of the Colorado Public Utilities Commission]

Citation: Colorado PUC Decision No. C23-XXXX
Date: 2023
Authority: Colorado Public Utilities Commission""",
        "source_url": "https://www.dora.state.co.us/pls/efi/EFI.Show_Filing?p_fil=G_930344",
        "document_type": DocumentType.DECISION,
        "authority_level": AuthorityLevel.STATE,
        "jurisdiction_type": JurisdictionType.COLORADO,
        "source_name": "Colorado PUC",
        "citation": "Decision No. C23-XXXX",
    },
]


async def seed_data():
    """Seed the database with sample documents."""
    print("Initializing database...")
    await init_db()

    async with get_db_session() as session:
        for doc_data in SAMPLE_DOCUMENTS:
            print(f"Adding: {doc_data['title'][:50]}...")

            # Create document
            doc = Document(
                id=uuid.uuid4(),
                title=doc_data["title"],
                content=doc_data["content"],
                source_url=doc_data["source_url"],
                document_type=doc_data["document_type"],
                authority_level=doc_data["authority_level"],
                jurisdiction_type=doc_data["jurisdiction_type"],
                source_name=doc_data["source_name"],
                citation=doc_data["citation"],
                published_date=date.today(),
                checksum=str(uuid.uuid4()),  # Simple checksum
            )
            session.add(doc)
            await session.flush()

            # Create chunks (simple chunking - one chunk per document for now)
            chunk = DocumentChunk(
                id=uuid.uuid4(),
                document_id=doc.id,
                content=doc_data["content"],
                chunk_index=0,
                embedding=None,  # No embedding for now
            )
            session.add(chunk)

        await session.commit()
        print(f"\nSeeded {len(SAMPLE_DOCUMENTS)} documents successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
