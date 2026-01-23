"""Collect Colorado-specific energy regulatory data."""

import asyncio
import sys
sys.path.insert(0, '/app')

import uuid
from datetime import date
from app.db.database import init_db, get_db_session
from app.db.models import Document, DocumentChunk, AuthorityLevel, JurisdictionType, DocumentType
from app.llm.embeddings import get_embeddings
from sqlalchemy import select
import structlog

logger = structlog.get_logger()


# Key Colorado energy regulations and statutes
COLORADO_REGULATIONS = [
    {
        "title": "Colorado Renewable Energy Standard (RES) - C.R.S. § 40-2-124",
        "citation": "C.R.S. § 40-2-124",
        "source_url": "https://leg.colorado.gov/sites/default/files/images/olls/crs2023-title-40.pdf",
        "content": """Colorado Renewable Energy Standard (RES) - C.R.S. § 40-2-124

RENEWABLE ENERGY REQUIREMENTS FOR COLORADO UTILITIES

(1) Legislative Declaration. The general assembly finds and declares that:
(a) Development of renewable energy resources benefits Colorado by promoting energy independence, diversifying energy supply, stimulating economic development, and reducing harmful emissions;
(b) Investor-owned electric utilities serving Colorado customers should obtain a minimum percentage of electricity from renewable energy sources.

(2) Renewable Energy Standard Requirements:
(a) Qualifying retail utilities shall generate, or cause to be generated, electricity from eligible energy resources in the following minimum amounts:
    (i) For investor-owned utilities (IOUs):
        - 30% by 2020 and thereafter
        - Of which at least 3% must come from distributed generation (DG)
    (ii) For cooperative electric associations serving 100,000+ meters:
        - 20% by 2020 and thereafter
    (iii) For cooperative electric associations serving fewer than 100,000 meters:
        - 10% by 2020 and thereafter
    (iv) For municipal utilities serving 40,000+ customers:
        - 10% by 2020 and thereafter

(3) Eligible Energy Resources include:
(a) Solar electric
(b) Wind
(c) Geothermal electric
(d) Biomass
(e) Hydroelectricity (new small hydro under 30 MW)
(f) Fuel cells using hydrogen derived from eligible resources
(g) Recycled energy

(4) Distributed Generation Requirements:
(a) At least half of the DG requirement must come from retail renewable distributed generation (customer-sited systems)
(b) Utilities must have net metering programs for systems up to 120% of customer's average annual consumption

(5) Renewable Energy Credits (RECs):
(a) Utilities may use tradable renewable energy credits to demonstrate compliance
(b) Each MWh of electricity generated from eligible resources = 1 REC
(c) Solar electric generation receives REC multipliers:
    - In-state solar: 1.25x credit multiplier
    - Community solar gardens: standard credit
(d) RECs may be banked for up to 5 years

(6) Cost Recovery and Rate Impact:
(a) Utilities may recover prudently incurred costs through retail rates
(b) Retail rate impact cap of 2% for investor-owned utilities
(c) PUC must consider long-term benefits when approving renewable energy plans

(7) Compliance Reporting:
(a) Annual compliance reports due to PUC by June 1
(b) Reports must include: generation by resource type, REC transactions, progress toward targets
(c) PUC reviews compliance and may assess penalties for non-compliance

(8) Penalties for Non-Compliance:
(a) Utilities failing to meet RES requirements subject to penalties
(b) Maximum penalty: $100 per MWh of shortfall
(c) PUC may grant compliance extensions for good cause

ENFORCEMENT: The Colorado Public Utilities Commission (PUC) has authority to enforce these requirements and may promulgate rules to implement this section.

EFFECTIVE DATE: Various provisions phased in from 2007-2020.""",
    },
    {
        "title": "Colorado Community Solar Gardens Act - C.R.S. § 40-2-127",
        "citation": "C.R.S. § 40-2-127",
        "source_url": "https://leg.colorado.gov/sites/default/files/images/olls/crs2023-title-40.pdf",
        "content": """Colorado Community Solar Gardens Act - C.R.S. § 40-2-127

COMMUNITY SOLAR GARDENS REQUIREMENTS

(1) Definitions:
(a) "Community solar garden" means a solar electric generation facility with a nameplate rating of two megawatts or less that:
    (i) Has at least 10 subscribers
    (ii) No single subscriber has more than a 40% interest
    (iii) Is located in the service territory of the qualifying retail utility
(b) "Subscriber" means a retail customer of a qualifying retail utility who owns a subscription to a community solar garden

(2) Program Requirements:
(a) Qualifying retail utilities (investor-owned utilities) shall file a plan with the PUC to acquire electricity from community solar gardens
(b) Utilities must purchase the output and RECs from community solar gardens at the applicable rate
(c) Subscriber bill credits must reflect the proportional production of the community solar garden

(3) Subscriber Benefits:
(a) Subscribers receive bill credits for their proportional share of garden production
(b) Credits applied monthly based on actual production
(c) Low-income programs: At least 5% of garden capacity must be reserved for low-income subscribers
(d) Subscriptions are transferable within the utility service territory

(4) Garden Siting and Interconnection:
(a) Gardens must comply with local zoning requirements
(b) Utilities must provide transparent interconnection processes
(c) Interconnection study costs capped at reasonable levels
(d) Timeline for interconnection approval not to exceed 90 days for systems under 500 kW

(5) Rate Treatment:
(a) Utilities shall develop a community solar gardens tariff
(b) Bill credits shall reflect the value of energy, capacity, and RECs
(c) PUC to determine appropriate credit rate methodology
(d) Credits calculated based on delivered energy at the point of common coupling

(6) Low-Income Access Requirements:
(a) At least 5% of capacity in each garden reserved for low-income customers
(b) Low-income subscribers may receive enhanced bill credit rates
(c) Utilities must report annually on low-income participation rates

(7) Consumer Protection:
(a) Subscription agreements must include clear disclosure of:
    - Expected production and bill credit estimates
    - Fees and charges
    - Term of subscription
    - Cancellation rights
(b) Subscribers have right to cancel within 3 days of signing agreement
(c) Marketing materials must be fair and non-deceptive

EFFECTIVE DATE: Program effective January 1, 2011, with subsequent amendments.""",
    },
    {
        "title": "Colorado Electric Resource Planning Rules - 4 CCR 723-3-3600",
        "citation": "4 CCR 723-3-3600 et seq.",
        "source_url": "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=10852",
        "content": """Colorado Electric Resource Planning Rules - 4 CCR 723-3-3600

ELECTRIC RESOURCE PLANNING (ERP) REQUIREMENTS

3600. APPLICABILITY
These rules apply to jurisdictional electric utilities required to file Electric Resource Plans (ERPs) with the Colorado Public Utilities Commission.

3601. PURPOSE
The purpose of resource planning is to ensure utilities acquire the combination of resources to serve customers reliably at the lowest reasonable cost, considering:
(a) Risk and uncertainty
(b) Environmental impacts
(c) Portfolio diversity
(d) Transmission constraints
(e) Emerging technologies

3603. RESOURCE PLAN FILING REQUIREMENTS
(a) Filing Schedule: Jurisdictional utilities shall file comprehensive resource plans every four years
(b) Required Plan Components:
    (i) Load forecast for planning period (minimum 20 years)
    (ii) Assessment of existing resources
    (iii) Identification of resource needs
    (iv) Evaluation of supply-side and demand-side options
    (v) Proposed resource acquisition strategy
    (vi) Action plan for first four-year period

3604. LOAD FORECASTING
(a) Base case and sensitivity forecasts required
(b) Forecasts must account for:
    (i) Economic growth projections
    (ii) Customer growth
    (iii) Energy efficiency impacts
    (iv) Electric vehicle adoption
    (v) Distributed generation trends

3605. RESOURCE NEED ASSESSMENT
(a) Utilities shall identify resource need by comparing:
    (i) Available capacity from existing resources
    (ii) Projected peak demand plus reserve margin
(b) Reserve margin shall be reasonable to maintain reliability

3606. RESOURCE OPTIONS EVALUATION
(a) All-Source Competitive Solicitation Required:
    (i) Utilities must issue competitive solicitations (RFPs) for new resources
    (ii) Solicitations must be technology-neutral
    (iii) Utility-owned and third-party resources evaluated on equal basis
(b) Evaluation Criteria shall include:
    (i) Levelized cost of energy (LCOE)
    (ii) System integration costs
    (iii) Environmental impacts and compliance costs
    (iv) Portfolio diversity value
    (v) Transmission and distribution impacts

3607. CLEAN ENERGY PLAN REQUIREMENTS
(a) Utilities must demonstrate pathway to 80% carbon reduction by 2030
(b) Plan must identify:
    (i) Interim emission targets
    (ii) Retirement schedule for carbon-emitting resources
    (iii) New clean energy resource additions
    (iv) Cost impacts and mitigation strategies

3608. DEMAND-SIDE MANAGEMENT
(a) Utilities must evaluate demand-side management (DSM) as a resource option
(b) Cost-effective DSM must be acquired before supply-side resources
(c) DSM potential studies required at least every four years

3610. STAKEHOLDER PARTICIPATION
(a) Utilities must conduct stakeholder engagement during plan development
(b) Technical conferences and comment opportunities required
(c) Environmental justice considerations must be addressed

3612. COMMISSION APPROVAL
(a) Commission shall approve, modify, or reject resource plans
(b) Approval criteria include:
    (i) Least-cost, least-risk resource portfolio
    (ii) Compliance with renewable energy requirements
    (iii) Adequate reliability and reserve margins
    (iv) Environmental compliance

EFFECTIVE DATE: Rules updated December 2021""",
    },
    {
        "title": "Colorado Net Metering Rules - 4 CCR 723-3-3664",
        "citation": "4 CCR 723-3-3664",
        "source_url": "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=10852",
        "content": """Colorado Net Metering Rules - 4 CCR 723-3-3664

NET METERING REQUIREMENTS FOR COLORADO UTILITIES

3664. NET METERING PROGRAM REQUIREMENTS

(a) Applicability: All jurisdictional electric utilities must offer net metering to retail customers who install eligible renewable energy systems.

(b) Eligible Systems:
    (i) Solar photovoltaic
    (ii) Wind
    (iii) Biomass
    (iv) Fuel cells using renewable fuels
    (v) Small hydroelectric (under 10 MW)

(c) System Size Limits:
    (i) Residential: Up to 120% of customer's average annual consumption or 25 kW, whichever is larger
    (ii) Commercial: Up to 120% of customer's average annual consumption or 2 MW, whichever is larger

3665. BILLING AND CREDITS

(a) Monthly Netting:
    (i) Customer energy consumption offset by on-site generation
    (ii) Excess generation in any billing period carried forward as kWh credit
    (iii) Credits roll over month-to-month indefinitely

(b) Annual Reconciliation:
    (i) On the customer's annual anniversary date, excess kWh credits may be:
        - Paid out at the utility's avoided cost rate, OR
        - Rolled over to the next year (utility option)
    (ii) Utility must clearly disclose annual reconciliation policy

(c) Billing Components:
    (i) Customer billed for net consumption (consumption minus generation)
    (ii) Customer pays all applicable fixed charges
    (iii) Demand charges may apply for commercial customers based on gross demand

3666. INTERCONNECTION REQUIREMENTS

(a) Application Process:
    (i) Utilities must provide simple application forms
    (ii) Application fee limited to reasonable administrative costs
    (iii) 10-day review period for systems under 10 kW
    (iv) 30-day review period for systems 10 kW to 500 kW

(b) Technical Standards:
    (i) Systems must comply with IEEE 1547 interconnection standards
    (ii) UL 1741 certification required for inverters
    (iii) Anti-islanding protection required
    (iv) External disconnect switch may be required (utility option)

(c) Metering:
    (i) Utilities shall provide appropriate metering at no additional cost
    (ii) Bidirectional meters or dual meters permitted
    (iii) Customer generation metering not required unless requested

3667. INSURANCE AND LIABILITY

(a) Residential systems under 10 kW: Standard homeowner's insurance acceptable
(b) Commercial systems: Liability insurance at least $1 million
(c) Customer responsible for system maintenance and safety

3668. PROGRAM CAPS AND LIMITS

(a) Utilities must offer net metering until program cap reached:
    (i) Investor-owned utilities: No specific cap (2024 update)
    (ii) Co-ops and municipals: May set reasonable caps
(b) Utilities may petition PUC to modify program terms if costs become unreasonable

REPORTING: Utilities must file annual reports on net metering participation, installed capacity, and program costs.

EFFECTIVE DATE: Current rules effective January 2024""",
    },
    {
        "title": "Colorado Clean Heat Standard - HB22-1362 / C.R.S. § 40-3.2-108",
        "citation": "C.R.S. § 40-3.2-108",
        "source_url": "https://leg.colorado.gov/bills/hb22-1362",
        "content": """Colorado Clean Heat Standard - HB22-1362 / C.R.S. § 40-3.2-108

CLEAN HEAT STANDARD FOR NATURAL GAS UTILITIES

(1) Legislative Declaration:
(a) Buildings account for significant greenhouse gas emissions in Colorado
(b) Reducing emissions from building heating supports state climate goals
(c) Gas utilities have important role in clean energy transition

(2) Clean Heat Target Requirements:
(a) Natural gas utilities must achieve greenhouse gas emission reductions:
    (i) 4% reduction by 2025 (from 2015 baseline)
    (ii) 22% reduction by 2030
    (iii) Proportional reductions to meet 2050 goals
(b) Targets apply to emissions from customer consumption, not utility operations only

(3) Clean Heat Plan Filing Requirements:
(a) Gas utilities must file Clean Heat Plans with PUC every four years
(b) Plans must include:
    (i) Emission reduction strategy and pathway
    (ii) Portfolio of clean heat resources
    (iii) Cost projections and rate impacts
    (iv) Customer program offerings
    (v) Equity considerations and low-income programs

(4) Eligible Clean Heat Resources:
(a) Recovered methane (landfill gas, agricultural digesters, wastewater treatment)
(b) Green hydrogen blending (up to pipeline safety limits)
(c) Certified renewable natural gas (RNG)
(d) Beneficial electrification programs
(e) Energy efficiency and weatherization
(f) Geothermal heat pump programs
(g) District heating systems

(5) Customer Program Requirements:
(a) Utilities must offer voluntary green gas options for customers
(b) Low-income weatherization programs must be expanded
(c) Building electrification incentive programs available
(d) Heat pump retrofit programs for existing buildings

(6) Cost Recovery:
(a) Prudently incurred costs recoverable through rates
(b) Rate impact cap of 2% per year for residential customers
(c) Low-income customers exempt from certain surcharges
(d) Performance incentives for exceeding targets

(7) Reporting and Verification:
(a) Annual compliance reports due to PUC
(b) Third-party verification of emission reductions required
(c) Environmental attributes (certificates) tracked and retired
(d) Public reporting of progress toward targets

(8) Just Transition Considerations:
(a) Plans must address workforce impacts
(b) Community impacts in fossil fuel-dependent areas considered
(c) Retraining programs may be included in cost recovery

ENFORCEMENT: PUC has authority to enforce compliance and assess penalties for shortfalls.

EFFECTIVE DATE: Requirements phased in from 2023-2030""",
    },
    {
        "title": "Colorado Transportation Electrification - SB19-077 / C.R.S. § 40-5-107.5",
        "citation": "C.R.S. § 40-5-107.5",
        "source_url": "https://leg.colorado.gov/bills/sb19-077",
        "content": """Colorado Transportation Electrification - SB19-077 / C.R.S. § 40-5-107.5

TRANSPORTATION ELECTRIFICATION REQUIREMENTS

(1) Purpose:
(a) Transportation is Colorado's largest source of GHG emissions
(b) Electric vehicles reduce emissions and improve air quality
(c) Electric utilities have role in supporting EV adoption

(2) Transportation Electrification Plan (TEP) Requirements:
(a) Investor-owned utilities must file TEPs with PUC
(b) Plans must project EV adoption through 2030 and beyond
(c) Plans must include programs to support EV charging infrastructure

(3) Approved Program Categories:
(a) Residential Charging Programs:
    (i) Rebates for Level 2 charger installation
    (ii) Time-of-use rates optimized for EV charging
    (iii) Load management programs for charging
(b) Commercial and Fleet Programs:
    (i) Make-ready infrastructure support
    (ii) Fleet electrification incentives
    (iii) Workplace charging programs
(c) Public Charging Infrastructure:
    (i) DC fast charging network buildout
    (ii) Investments in underserved communities
    (iii) Partnerships with charging network operators
(d) Grid Integration Programs:
    (i) Vehicle-to-grid (V2G) pilot programs
    (ii) Managed charging programs
    (iii) Demand response integration

(4) Investment Caps and Cost Recovery:
(a) Initial TEP investments capped at $110 million per utility
(b) Subsequent plans may request additional investment authority
(c) Cost recovery through base rates or EV-specific riders
(d) Costs allocated based on cost-causation principles

(5) Equity Requirements:
(a) Minimum investment in disproportionately impacted communities
(b) Programs to support low-income EV adoption
(c) Charging infrastructure in multi-family housing
(d) Rural area charging network development

(6) Rate Design Principles:
(a) EV-specific rates must encourage off-peak charging
(b) Demand charge alternatives for commercial charging
(c) Rates should be technology-neutral where possible
(d) Transparency in rate design and cost allocation

(7) Reporting and Evaluation:
(a) Annual reports on program participation and costs
(b) EV adoption metrics and charging utilization
(c) Emission reductions from transportation electrification
(d) Program evaluation and cost-effectiveness analysis

(8) Coordination Requirements:
(a) Utilities coordinate with Colorado Energy Office (CEO)
(b) Alignment with state EV goals (940,000 EVs by 2030)
(c) Coordination with regional charging networks
(d) Support for federal funding applications

EFFECTIVE DATE: TEP filing requirements effective 2020""",
    },
    {
        "title": "Colorado Utility Wildfire Mitigation Plans - C.R.S. § 40-3-114",
        "citation": "C.R.S. § 40-3-114",
        "source_url": "https://leg.colorado.gov/sites/default/files/images/olls/crs2023-title-40.pdf",
        "content": """Colorado Utility Wildfire Mitigation Plans - C.R.S. § 40-3-114

WILDFIRE MITIGATION REQUIREMENTS FOR ELECTRIC UTILITIES

(1) Legislative Findings:
(a) Colorado faces increasing wildfire risk due to climate change
(b) Electric utility infrastructure can be ignition source for wildfires
(c) Proactive wildfire mitigation protects public safety and property

(2) Wildfire Mitigation Plan Requirements:
(a) Electric utilities serving Colorado must file wildfire mitigation plans with PUC
(b) Plans must be updated and refiled every three years
(c) Plans must be comprehensive and address all high-risk areas

(3) Required Plan Components:
(a) Risk Assessment:
    (i) Identification of high fire-threat districts
    (ii) Assessment of vegetation management needs
    (iii) Evaluation of infrastructure vulnerability
    (iv) Historical ignition data analysis
(b) Mitigation Strategies:
    (i) Enhanced vegetation management programs
    (ii) System hardening and infrastructure upgrades
    (iii) Covered conductor installation in high-risk areas
    (iv) Undergrounding of distribution lines where appropriate
(c) Operational Protocols:
    (i) Enhanced inspection programs during fire season
    (ii) Weather monitoring and fire potential assessment
    (iii) Public Safety Power Shutoff (PSPS) protocols
    (iv) Recloser and protection settings optimization

(4) Public Safety Power Shutoff (PSPS) Requirements:
(a) Utilities may implement PSPS when conditions warrant de-energization
(b) PSPS protocols must include:
    (i) Trigger criteria based on weather, fuel conditions, and fire risk
    (ii) Customer notification procedures (48-hour, 24-hour, imminent notices)
    (iii) Coordination with first responders and emergency management
    (iv) Medical baseline customer protocols
(c) Post-PSPS event reporting requirements

(5) Vegetation Management Standards:
(a) Minimum clearance distances from distribution lines
(b) Enhanced clearances in high fire-threat areas
(c) Tree trimming cycle requirements (typically 3-5 years)
(d) Hazard tree removal programs

(6) Infrastructure Hardening:
(a) Covered conductor requirements for new construction in high-risk areas
(b) Replacement priorities for aging infrastructure
(c) Wood pole replacement programs
(d) Guy wire and equipment inspection programs

(7) Cost Recovery:
(a) Prudently incurred wildfire mitigation costs recoverable in rates
(b) Utilities may establish wildfire mitigation cost recovery rider
(c) PUC review of cost-effectiveness required

(8) Liability and Insurance:
(a) Utilities must maintain appropriate liability insurance
(b) Wildfire mitigation efforts may be considered in liability proceedings
(c) Inverse condemnation standards apply to utility-caused fires

(9) Reporting Requirements:
(a) Annual progress reports to PUC
(b) Incident reporting within specified timeframes
(c) Performance metrics on mitigation activities

ENFORCEMENT: PUC has authority to require plan modifications and assess penalties for non-compliance.

EFFECTIVE DATE: Initial plan filings required by 2024""",
    },
    {
        "title": "Colorado Greenhouse Gas Emission Reduction Roadmap",
        "citation": "Executive Order B 2019-002 / HB19-1261",
        "source_url": "https://www.colorado.gov/governor/sites/default/files/inline-files/b_2019-002_climate_action_plan.pdf",
        "content": """Colorado Greenhouse Gas Emission Reduction Roadmap

STATE CLIMATE POLICY AND EMISSION REDUCTION TARGETS

(1) Statewide Emission Reduction Targets (HB19-1261):
(a) 26% reduction by 2025 (from 2005 baseline)
(b) 50% reduction by 2030
(c) 90% reduction by 2050
(d) Targets apply to economy-wide emissions across all sectors

(2) Electric Sector Requirements:
(a) Electric sector is primary focus for near-term reductions
(b) 80% carbon reduction from electricity by 2030 (from 2005 levels)
(c) 100% clean electricity by 2040 goal
(d) Investor-owned utilities must file Clean Energy Plans demonstrating compliance

(3) Air Quality Control Commission (AQCC) Regulations:
(a) AQCC adopts rules to implement emission reduction targets
(b) Sector-specific regulations developed for:
    (i) Electric generation
    (ii) Oil and gas operations
    (iii) Transportation
    (iv) Industrial processes
    (v) Buildings and heating

(4) Electric Utility Clean Energy Planning:
(a) Utilities must demonstrate pathway to 80% reduction by 2030
(b) Clean Energy Plans filed with PUC every four years
(c) Plans evaluated for cost, reliability, and environmental compliance
(d) All-source competitive procurement required for new resources

(5) Just Transition Requirements:
(a) Office of Just Transition created to support affected communities
(b) Workforce development programs for clean energy jobs
(c) Community investment in coal-impacted areas
(d) Economic diversification support

(6) Transportation Sector Goals:
(a) 940,000 electric vehicles by 2030
(b) Zero-emission vehicle (ZEV) standards adopted
(c) Electric school bus requirements
(d) Medium/heavy-duty vehicle electrification targets

(7) Building Sector Requirements:
(a) Building performance standards for large buildings
(b) Energy code updates for new construction
(c) Beneficial electrification incentives
(d) Gas utility clean heat standards

(8) Monitoring and Reporting:
(a) Colorado Energy Office tracks progress toward targets
(b) Annual GHG inventory updates
(c) Biennial climate action plan updates
(d) Public reporting on sector-specific progress

(9) Environmental Justice:
(a) Disproportionately Impacted Communities (DICs) prioritized
(b) 15-20% of clean energy investments benefit DICs
(c) Community engagement requirements in planning
(d) Air quality monitoring in frontline communities

(10) Enforcement and Compliance:
(a) PUC enforces utility compliance with Clean Energy Plans
(b) AQCC enforces emission standards
(c) Penalties for non-compliance established by regulation
(d) Annual compliance demonstrations required

IMPLEMENTATION: Multiple state agencies coordinate implementation, including CEO, PUC, AQCC, and CDPHE.

EFFECTIVE DATE: Targets established 2019, with phased implementation through 2050""",
    },
    {
        "title": "Colorado PUC Rate Case Procedures - 4 CCR 723-3-3001",
        "citation": "4 CCR 723-3-3001 et seq.",
        "source_url": "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=10852",
        "content": """Colorado PUC Rate Case Procedures - 4 CCR 723-3-3001

GENERAL RATE CASE PROCEDURES FOR REGULATED UTILITIES

3001. APPLICABILITY
These rules govern rate proceedings for jurisdictional gas and electric utilities before the Colorado Public Utilities Commission.

3002. RATE CASE FILING REQUIREMENTS
(a) Utilities seeking base rate changes must file comprehensive rate case applications
(b) Applications must include:
    (i) Direct testimony supporting proposed rates
    (ii) Cost of service study
    (iii) Rate design testimony
    (iv) Supporting schedules and workpapers
    (v) Revenue requirement calculation

3003. TEST YEAR REQUIREMENTS
(a) Utilities may use historical or forward test year
(b) Historical test year: Most recent 12-month period with available data
(c) Forward test year: Projected 12-month period, with supporting assumptions
(d) Known and measurable adjustments may be applied to either

3004. COST OF SERVICE PRINCIPLES
(a) Revenue Requirement Components:
    (i) Operating and maintenance expenses (O&M)
    (ii) Depreciation expense
    (iii) Taxes (income and property)
    (iv) Return on rate base (capital costs)
(b) Rate Base Calculation:
    (i) Net utility plant in service
    (ii) Plus: Working capital allowance
    (iii) Less: Accumulated depreciation
    (iv) Less: Accumulated deferred income taxes (ADIT)

3005. RATE OF RETURN DETERMINATION
(a) Allowed return based on utility's capital structure:
    (i) Cost of debt (embedded interest rate)
    (ii) Cost of equity (determined by Commission)
    (iii) Cost of preferred stock, if applicable
(b) Weighted average cost of capital (WACC) methodology
(c) Return on equity (ROE) typically 9-11% for regulated utilities

3006. RATE DESIGN PRINCIPLES
(a) Cost Causation: Rates should reflect cost to serve each customer class
(b) Gradualism: Rate changes should be gradual to avoid rate shock
(c) Rate Continuity: Similar customers should pay similar rates
(d) Revenue Stability: Rates should provide stable utility revenues
(e) Conservation: Rate design may incorporate conservation price signals

3007. CUSTOMER CLASS ALLOCATION
(a) Utilities must demonstrate cost allocation methodology
(b) Common allocation methods:
    (i) Demand allocation (peak responsibility)
    (ii) Energy allocation (usage-based)
    (iii) Customer allocation (number of customers)
(b) Class rate of return parity considered in rate design

3008. PROCEDURAL SCHEDULE
(a) Typical rate case timeline: 8-12 months from filing
(b) Discovery period: Parties may serve data requests
(c) Intervenor testimony deadline
(d) Rebuttal testimony deadline
(e) Evidentiary hearing
(f) Post-hearing briefs
(g) Commission decision

3009. BURDEN OF PROOF
(a) Utility bears burden of proving proposed rates are just and reasonable
(b) Rates must be based on prudent costs
(c) Commission applies "used and useful" standard for rate base inclusion

3010. MULTI-YEAR RATE PLANS (MYRPs)
(a) Utilities may propose multi-year rate plans
(b) MYRPs provide rate certainty for 2-3 years
(c) Earnings sharing mechanisms may apply if earnings exceed allowed ROE
(d) Reopener provisions for significant unforeseen circumstances

APPEALS: Commission decisions may be appealed to Colorado Court of Appeals within 35 days of decision.

EFFECTIVE DATE: Current rules effective January 2022""",
    },
    {
        "title": "Colorado Grid Modernization Rules - 4 CCR 723-3-3028",
        "citation": "4 CCR 723-3-3028",
        "source_url": "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=10852",
        "content": """Colorado Grid Modernization Rules - 4 CCR 723-3-3028

GRID MODERNIZATION AND ADVANCED METERING REQUIREMENTS

3028. PURPOSE AND SCOPE
(a) These rules establish requirements for utility grid modernization investments
(b) Grid modernization supports integration of distributed energy resources
(c) Advanced metering infrastructure (AMI) enables new rate designs and customer programs

3029. GRID MODERNIZATION PLANNING
(a) Utilities must file grid modernization plans as part of resource planning
(b) Plans must address:
    (i) Current grid capabilities and limitations
    (ii) Proposed investments in grid infrastructure
    (iii) Benefits to customers and grid operations
    (iv) Timeline and cost estimates
    (v) Performance metrics and accountability

3030. ADVANCED METERING INFRASTRUCTURE (AMI)
(a) Investor-owned utilities shall deploy AMI throughout service territory
(b) AMI capabilities must include:
    (i) Interval metering (minimum 15-minute intervals)
    (ii) Remote connect/disconnect capability
    (iii) Outage detection and notification
    (iv) Two-way communication
    (v) Voltage monitoring capability
(c) Customer opt-out provisions required for residential customers

3031. CUSTOMER DATA ACCESS
(a) Customers have right to access their own usage data
(b) Data provided at no cost in standard electronic format (Green Button)
(c) Third-party access with customer authorization
(d) Data privacy and security requirements

3032. TIME-VARYING RATE REQUIREMENTS
(a) Utilities with AMI must offer time-of-use (TOU) rate options
(b) TOU rates must have meaningful price differential:
    (i) Minimum 2:1 peak to off-peak ratio recommended
    (ii) Peak periods reflect system peak times
    (iii) Seasonal variations permitted
(c) Critical peak pricing (CPP) programs permitted
(d) Real-time pricing for large customers optional

3033. DISTRIBUTED ENERGY RESOURCE INTEGRATION
(a) Grid investments must support increased DER penetration
(b) Hosting capacity analysis required:
    (i) Published hosting capacity maps
    (ii) Updates at least annually
    (iii) Transparency in methodology
(c) DER interconnection improvements prioritized

3034. GRID SERVICES FROM DERs
(a) Utilities shall develop programs to procure grid services from DERs
(b) Eligible services include:
    (i) Demand response
    (ii) Energy storage (customer-sited and utility-scale)
    (iii) Vehicle-to-grid services
    (iv) Aggregated DER services
(c) Non-wires alternatives considered for grid upgrades

3035. CYBERSECURITY REQUIREMENTS
(a) Grid modernization investments must include cybersecurity protections
(b) Utilities must have cybersecurity plans reviewed by PUC staff
(c) NERC CIP standards compliance required for bulk power system
(d) Distribution system cybersecurity best practices applied

3036. COST RECOVERY
(a) Prudent grid modernization investments recoverable in rates
(b) Utilities may propose Grid Modernization Riders for cost recovery
(c) Performance-based ratemaking incentives may apply
(d) Cost-benefit analysis required for major investments

3037. REPORTING AND METRICS
(a) Annual reports on grid modernization progress
(b) Key performance metrics:
    (i) AMI deployment penetration
    (ii) TOU rate enrollment
    (iii) Outage frequency and duration
    (iv) DER interconnection timelines
    (v) Customer satisfaction scores

EFFECTIVE DATE: Rules effective January 2023 with phased implementation""",
    },
]


def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at sentence boundary
        if end < len(text):
            for sep in ['. ', '.\n', '\n\n', '\n', ' ']:
                sep_pos = text.rfind(sep, start + chunk_size // 2, end)
                if sep_pos != -1:
                    end = sep_pos + len(sep)
                    break

        chunks.append(text[start:end].strip())
        start = end - overlap

        if start >= len(text):
            break

    return chunks


async def collect_colorado_regulations():
    """Collect Colorado energy regulatory data."""
    print("\n=== Collecting Colorado Energy Regulations ===\n")

    await init_db()
    embeddings = get_embeddings()

    documents_added = 0

    async with get_db_session() as session:
        for reg in COLORADO_REGULATIONS:
            print(f"Processing: {reg['title'][:60]}...")

            # Check if document already exists
            checksum = f"colorado-{reg['citation'].replace(' ', '-').replace('.', '').replace('§', 's').lower()}"
            result = await session.execute(
                select(Document).where(Document.checksum == checksum)
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  Already exists, skipping...")
                continue

            # Create document
            doc = Document(
                id=uuid.uuid4(),
                title=reg["title"],
                content=reg["content"],
                source_url=reg["source_url"],
                document_type=DocumentType.REGULATION,
                authority_level=AuthorityLevel.STATE,
                jurisdiction_type=JurisdictionType.COLORADO,
                source_name="Colorado Revised Statutes / PUC Rules",
                citation=reg["citation"],
                published_date=date.today(),
                checksum=checksum,
            )
            session.add(doc)
            await session.flush()

            # Create chunks
            chunks = chunk_text(reg["content"], chunk_size=2000, overlap=200)
            for i, chunk_content in enumerate(chunks):
                embedding = None
                if embeddings:
                    try:
                        embedding = await embeddings.generate(chunk_content[:8000])
                    except Exception as e:
                        print(f"  Warning: Could not generate embedding: {e}")

                chunk = DocumentChunk(
                    id=uuid.uuid4(),
                    document_id=doc.id,
                    content=chunk_content,
                    chunk_index=i,
                    embedding=embedding,
                )
                session.add(chunk)

            await session.commit()
            documents_added += 1
            print(f"  Added with {len(chunks)} chunks")

    print(f"\n=== Completed: Added {documents_added} Colorado regulation documents ===\n")
    return documents_added


if __name__ == "__main__":
    asyncio.run(collect_colorado_regulations())
