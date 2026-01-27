# URL Testing Checklist

**Total URLs to Test:** 69
**Generated:** January 27, 2026

Use this checklist to verify all source URLs. For geo-blocked URLs (NERC, potentially FERC), test from Azure VM in US region.

---

## Status Legend

- [ ] = Not tested
- [x] = Tested & Working
- [!] = Tested & Broken (needs fix)
- [~] = Tested & Partially Working (redirects, requires navigation)

---

## PRIORITY 1: Colorado State Sources (14 URLs)

These are critical for Colorado-specific questions.

### Colorado Secretary of State - CCR (Expected: Working ✅)

- [ ] https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=10491
  - Title: Colorado PUC Rules - 4 CCR 723-3

- [ ] https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=10852
  - Title: Electric Resource Planning Rules - 4 CCR 723-3-3600
  - Also: Net Metering Rules, Rate Case Procedures, Grid Modernization Rules

### Colorado Legislature (Expected: 403 Forbidden ❌)

- [ ] https://leg.colorado.gov/sites/default/files/images/olls/crs2021-title-40.pdf
  - Title: CRS § 40-2-124 (RES), CRS § 40-2-125.5 (Clean Energy Plan)

- [ ] https://leg.colorado.gov/sites/default/files/images/olls/crs2023-title-40.pdf
  - Title: Multiple CRS sections, Wildfire Mitigation Plans

- [ ] https://leg.colorado.gov/bills/hb22-1362
  - Title: Colorado Clean Heat Standard

- [ ] https://leg.colorado.gov/bills/sb19-077
  - Title: Colorado Transportation Electrification

### Colorado Governor's Office (Unknown status)

- [ ] https://www.colorado.gov/governor/sites/default/files/inline-files/b_2019-002_climate_action_plan.pdf
  - Title: Colorado GHG Emission Reduction Roadmap

### Colorado PUC E-Filing (Expected: 404 Not Found ❌)

- [ ] https://www.dora.state.co.us/pls/efi/EFI.Show_Filing?p_fil=G_930344
  - Title: Xcel Energy Renewable Energy Plan (2023)

---

## PRIORITY 2: Federal Register (53 URLs)

These should all work - they use the official Federal Register API.

### Federal Register - FERC (20 URLs)

- [ ] https://www.federalregister.gov/documents/2026/01/20/2026-01002/annual-update-of-filing-fees
- [ ] https://www.federalregister.gov/documents/2025/12/18/2025-23294/implementation-of-the-executive-order-entitled-zero-based-regulatory-budgeting-to-unleash-american
- [ ] https://www.federalregister.gov/documents/2025/10/21/2025-19607/implementation-of-the-executive-order-entitled-zero-based-budgeting-to-unleash-american-energy
- [ ] https://www.federalregister.gov/documents/2025/10/10/2025-19533/removal-of-regulations-limiting-authorizations-to-proceed-with-construction-activities-pending
- [ ] https://www.federalregister.gov/documents/2025/09/30/2025-18977/delegation-of-authority-regarding-electric-reliability-organizations-delegation-agreement-and-rules
- [ ] https://www.federalregister.gov/documents/2025/09/23/2025-18394/supply-chain-risk-management-reliability-standards-revisions-equipment-and-services-produced-or
- [ ] https://www.federalregister.gov/documents/2025/07/29/2025-14304/reliability-standards-for-frequency-and-voltage-protection-settings-and-ride-through-for
- [ ] https://www.federalregister.gov/documents/2025/07/03/2025-12464/removal-of-references-to-the-council-on-environmental-qualitys-rescinded-regulations
- [ ] https://www.federalregister.gov/documents/2025/07/02/2025-12309/critical-infrastructure-protection-reliability-standard-cip-015-1-cyber-security-internal-network
- [ ] https://www.federalregister.gov/documents/2025/04/28/2025-06941/building-for-the-future-through-electric-regional-transmission-planning-and-cost-allocation
- [ ] https://www.federalregister.gov/documents/2025/02/27/2025-03085/standards-for-business-practices-and-communication-protocols-for-public-utilities
- [ ] https://www.federalregister.gov/documents/2025/02/12/2025-02417/annual-update-to-fee-schedule-for-the-use-of-government-lands-by-hydropower-licensees
- [ ] https://www.federalregister.gov/documents/2025/01/30/2025-01975/annual-update-of-filing-fees
- [ ] https://www.federalregister.gov/documents/2025/01/16/2025-00888/continuity-of-operations-plan
- [ ] https://www.federalregister.gov/documents/2025/01/14/2025-00516/civil-monetary-penalty-inflation-adjustments
- [ ] https://www.federalregister.gov/documents/2024/12/09/2024-28090/standards-for-business-practices-of-interstate-natural-gas-pipelines
- [ ] https://www.federalregister.gov/documents/2024/12/06/2024-27982/building-for-the-future-through-electric-regional-transmission-planning-and-cost-allocation
- [ ] https://www.federalregister.gov/documents/2024/12/05/2024-27981/establishing-reasonable-period-of-time-and-clarifications-regarding-clean-water-act-section-401a1
- [ ] https://www.federalregister.gov/documents/2024/11/26/2024-24528/compensation-for-reactive-power-within-the-standard-power-factor-range
- [ ] https://www.federalregister.gov/documents/2024/10/23/2024-24526/applications-for-permits-to-site-interstate-electric-transmission-facilities

### Federal Register - EPA (20 URLs)

- [ ] https://www.federalregister.gov/documents/2026/01/20/2026-01001/air-plan-approval-ohio-2015-ozone-moderate-reasonably-available-control-technology
- [ ] https://www.federalregister.gov/documents/2026/01/15/2026-00677/new-source-performance-standards-review-for-stationary-combustion-turbines-and-stationary-gas
- [ ] https://www.federalregister.gov/documents/2026/01/14/2026-00545/permethrin-pesticide-tolerances
- [ ] https://www.federalregister.gov/documents/2026/01/14/2026-00628/pyriofenone-pesticide-tolerances
- [ ] https://www.federalregister.gov/documents/2026/01/09/2026-00246/air-plan-approval-indiana-huntington-county-2010-sulfur-dioxide-redesignation-and-maintenance-plan
- [ ] https://www.federalregister.gov/documents/2026/01/09/2026-00259/technical-amendments-to-the-epcra-hazardous-chemical-inventory-reporting-requirements-to-conform-to
- [ ] https://www.federalregister.gov/documents/2026/01/09/2026-00249/air-plan-approval-new-hampshire-updates-to-materials-incorporated-by-reference
- [ ] https://www.federalregister.gov/documents/2026/01/09/2026-00253/approval-and-promulgation-of-delegation-of-authority-for-designated-facilities-and-pollutants-ohio
- [ ] https://www.federalregister.gov/documents/2026/01/09/2026-00281/air-plan-approval-new-york-ortho-clinical-diagnostics
- [ ] https://www.federalregister.gov/documents/2026/01/08/2026-00201/air-plan-approval-kentucky-emissions-inventory-and-nonattainment-new-source-review-for-the
- [ ] https://www.federalregister.gov/documents/2026/01/08/2026-00208/air-plan-approval-california-mojave-desert-air-quality-management-district-replacing-outdated
- [ ] https://www.federalregister.gov/documents/2026/01/08/2026-00194/air-plan-approval-california-mojave-desert-air-quality-management-district-definition-of-terms
- [ ] https://www.federalregister.gov/documents/2026/01/06/2026-00003/extension-of-the-state-implementation-plan-due-date-for-the-regional-haze-third-implementation
- [ ] https://www.federalregister.gov/documents/2026/01/06/2026-00004/air-plan-approval-michigan-infrastructure-sip-requirements-for-the-2015-ozone-naaqs-michigan-state
- [ ] https://www.federalregister.gov/documents/2026/01/06/2026-00007/utah-northern-wasatch-front-2015-8-hour-ozone-nonattainment-area-boundary-expansion-and
- [ ] https://www.federalregister.gov/documents/2026/01/06/2026-00005/air-plan-approval-california-san-joaquin-valley-unified-air-pollution-control-district
- [ ] https://www.federalregister.gov/documents/2026/01/06/2026-00006/air-plan-revision-california-placer-county-air-pollution-control-district-new-source-review
- [ ] https://www.federalregister.gov/documents/2026/01/02/2025-24207/air-plan-approval-michigan-and-minnesota-revision-to-taconite-federal-implementation-plan
- [ ] https://www.federalregister.gov/documents/2026/01/02/2025-24141/air-plan-approval-colorado-revisions-to-colorado-procedural-rules-and-common-provisions-regulation
- [ ] https://www.federalregister.gov/documents/2026/01/02/2025-24149/national-emission-standards-for-hazardous-air-pollutants-delegation-of-authority-to-oklahoma

### Federal Register - DOE (13 URLs)

- [ ] https://www.federalregister.gov/documents/2026/01/08/2026-00154/petroleum-equivalent-fuel-economy-calculation
- [ ] https://www.federalregister.gov/documents/2025/12/09/2025-22325/rescinding-new-construction-requirements-related-to-nondiscrimination-in-federally-assisted-programs
- [ ] https://www.federalregister.gov/documents/2025/12/09/2025-22324/rescinding-regulations-for-loans-for-minority-business-enterprises-seeking-doe-contracts-and
- [ ] https://www.federalregister.gov/documents/2025/12/09/2025-22322/rescinding-regulations-related-to-nondiscrimination-in-federally-assisted-programs-or-activities
- [ ] https://www.federalregister.gov/documents/2025/12/09/2025-22323/rescinding-regulations-related-to-nondiscrimination-on-the-basis-of-sex-in-education-programs-or
- [ ] https://www.federalregister.gov/documents/2025/11/24/2025-20788/assistance-to-foreign-atomic-energy-activities
- [ ] https://www.federalregister.gov/documents/2025/10/28/2025-19675/energy-dominance-financing-amendments
- [ ] https://www.federalregister.gov/documents/2025/09/11/2025-17513/application-for-presidential-permit-authorizing-the-construction-connection-operation-and
- [ ] https://www.federalregister.gov/documents/2025/09/11/2025-17517/rescinding-new-construction-requirements-related-to-nondiscrimination-in-federally-assisted-programs
- [ ] https://www.federalregister.gov/documents/2025/09/10/2025-17427/rescinding-regulations-related-to-nondiscrimination-in-federally-assisted-programs-or-activities
- [ ] https://www.federalregister.gov/documents/2025/09/10/2025-17426/nondiscrimination-on-the-basis-of-sex-in-sports-programs-arising-out-of-federal-financial-assistance
- [ ] https://www.federalregister.gov/documents/2025/09/10/2025-17429/rescinding-regulations-for-loans-for-minority-business-enterprises-seeking-doe-contracts-and
- [ ] https://www.federalregister.gov/documents/2025/09/10/2025-17428/rescinding-regulations-related-to-nondiscrimination-on-the-basis-of-sex-in-education-programs-or

---

## PRIORITY 3: Federal/Regional (Test from US VM)

### FERC.gov Direct (Expected: 403 Forbidden from Pakistan ❌)

- [ ] https://www.ferc.gov/media/ferc-order-no-2222-fact-sheet
  - Title: FERC Order 2222 - Distributed Energy Resources

### NERC (Expected: Timeout from Pakistan ❌)

- [ ] https://www.nerc.com/pa/Stand/Pages/ReliabilityStandards.aspx
  - Title: NERC Reliability Standards

---

## Testing Notes

### For each URL, record:
1. **Status Code**: 200, 301, 403, 404, Timeout
2. **Content Match**: Does the page content match the document title?
3. **Direct Access**: Can you view the document directly, or need to navigate?

### If URL is broken, note:
- Alternative URL that works
- Whether content exists elsewhere
- Recommended fix (update URL, remove document, or add navigation note)

---

## Summary After Testing

| Category | Total | Working | Broken | Action Needed |
|----------|-------|---------|--------|---------------|
| Colorado State | 14 | | | |
| Federal Register | 53 | | | |
| FERC/NERC | 2 | | | |
| **Total** | **69** | | | |

---

*Checklist created: January 27, 2026*
