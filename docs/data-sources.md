# Data Sources Reference

This document lists all data sources to be scraped for the Energy Sector Compliance Checker.

## Federal Sources

### 1. Federal Energy Regulatory Commission (FERC)
- **URL**: https://www.ferc.gov
- **Key Pages**:
  - Orders: https://www.ferc.gov/news-events/orders
  - Regulations: https://www.ferc.gov/industries-data
  - Enforcement: https://www.ferc.gov/enforcement
- **Update Frequency**: Daily
- **Document Types**: Orders, Regulations, Enforcement Actions
- **Scraping Method**: RSS feeds + Web scraping

### 2. Department of Energy (DOE)
- **URL**: https://www.energy.gov
- **Key Pages**:
  - Regulations: https://www.energy.gov/policy/regulations
  - Federal Register: https://www.energy.gov/federal-register
- **Update Frequency**: Daily
- **Document Types**: Regulations, Guidance, Reports
- **Scraping Method**: RSS feeds + API

### 3. Environmental Protection Agency (EPA) - Energy Section
- **URL**: https://www.epa.gov/energy
- **Key Pages**:
  - Regulations: https://www.epa.gov/energy/regulations
  - Compliance: https://www.epa.gov/compliance
- **Update Frequency**: Every 2 days
- **Document Types**: Regulations, Compliance Guides
- **Scraping Method**: Web scraping

### 4. Federal Register
- **URL**: https://www.federalregister.gov
- **Search Query**: Energy-related documents
- **Update Frequency**: Daily
- **Document Types**: Proposed Rules, Final Rules, Notices
- **Scraping Method**: API (https://www.federalregister.gov/api/v1)

### 5. U.S. Energy Information Administration (EIA)
- **URL**: https://www.eia.gov
- **Key Pages**:
  - Regulations: https://www.eia.gov/regulations
- **Update Frequency**: Weekly
- **Document Types**: Reports, Data Releases
- **Scraping Method**: RSS feeds

---

## Regional Sources (RTOs/ISOs)

### 1. PJM Interconnection
- **URL**: https://www.pjm.com
- **Key Pages**:
  - Tariffs: https://www.pjm.com/documents/agreements/tariffs.aspx
  - Manuals: https://www.pjm.com/documents/manuals.aspx
  - Orders: https://www.pjm.com/about-pjm/newsroom
- **Jurisdiction**: Delaware, Illinois, Indiana, Kentucky, Maryland, Michigan, New Jersey, North Carolina, Ohio, Pennsylvania, Tennessee, Virginia, West Virginia, District of Columbia
- **Update Frequency**: Daily
- **Document Types**: Tariffs, Manuals, Orders, Notices

### 2. ERCOT (Electric Reliability Council of Texas)
- **URL**: https://www.ercot.com
- **Key Pages**:
  - Protocols: https://www.ercot.com/marketinfo/protocols
  - Nodal Operating Guides: https://www.ercot.com/marketinfo/rules/guides
  - Market Notices: https://www.ercot.com/marketinfo/notices
- **Jurisdiction**: Texas
- **Update Frequency**: Daily
- **Document Types**: Protocols, Guides, Market Notices

### 3. CAISO (California Independent System Operator)
- **URL**: https://www.caiso.com
- **Key Pages**:
  - Tariff: https://www.caiso.com/rules/Pages/Tariff/default.aspx
  - Business Practice Manuals: https://www.caiso.com/rules/Pages/BusinessPracticeManuals/default.aspx
  - Market Notices: https://www.caiso.com/rules/Pages/MarketNotices/default.aspx
- **Jurisdiction**: California
- **Update Frequency**: Daily
- **Document Types**: Tariff, Manuals, Market Notices

### 4. MISO (Midcontinent Independent System Operator)
- **URL**: https://www.misoenergy.org
- **Key Pages**:
  - Tariff: https://www.misoenergy.org/legal/tariff
  - Business Practices: https://www.misoenergy.org/legal/business-practices-manuals
- **Jurisdiction**: 15 states in Midwest and South
- **Update Frequency**: Daily
- **Document Types**: Tariff, Manuals, Orders

### 5. NYISO (New York Independent System Operator)
- **URL**: https://www.nyiso.com
- **Key Pages**:
  - Tariffs: https://www.nyiso.com/documents/20142/2223023/Tariffs.pdf
  - Manuals: https://www.nyiso.com/documents/20142/2223023/Manuals.pdf
- **Jurisdiction**: New York
- **Update Frequency**: Daily
- **Document Types**: Tariffs, Manuals

### 6. ISO-NE (ISO New England)
- **URL**: https://www.iso-ne.com
- **Key Pages**:
  - Tariff: https://www.iso-ne.com/participate/rules-procedures/tariff
  - Manuals: https://www.iso-ne.com/participate/rules-procedures/manuals
- **Jurisdiction**: Connecticut, Maine, Massachusetts, New Hampshire, Rhode Island, Vermont
- **Update Frequency**: Daily
- **Document Types**: Tariff, Manuals

### 7. SPP (Southwest Power Pool)
- **URL**: https://www.spp.org
- **Key Pages**:
  - Tariff: https://www.spp.org/documents/legal/tariff
  - Protocols: https://www.spp.org/documents/legal/protocols
- **Jurisdiction**: 14 states in Central U.S.
- **Update Frequency**: Daily
- **Document Types**: Tariff, Protocols

---

## State Sources

### California
- **Public Utilities Commission (CPUC)**
  - URL: https://www.cpuc.ca.gov
  - Key Pages: Decisions, Orders, Rulemakings
  - Update Frequency: Daily
- **Energy Commission (CEC)**
  - URL: https://www.energy.ca.gov
  - Key Pages: Regulations, Reports
  - Update Frequency: Weekly

### Texas
- **Public Utility Commission (PUCT)**
  - URL: https://www.puc.texas.gov
  - Key Pages: Rules, Orders, Dockets
  - Update Frequency: Daily

### New York
- **Public Service Commission (NYSPSC)**
  - URL: https://www.dps.ny.gov
  - Key Pages: Orders, Regulations, Cases
  - Update Frequency: Daily

### Florida
- **Public Service Commission (FPSC)**
  - URL: https://www.psc.state.fl.us
  - Key Pages: Orders, Rules, Dockets
  - Update Frequency: Daily

### Pennsylvania
- **Public Utility Commission (PAPUC)**
  - URL: https://www.puc.pa.gov
  - Key Pages: Orders, Regulations, Cases
  - Update Frequency: Daily

### Illinois
- **Commerce Commission (ICC)**
  - URL: https://www.icc.illinois.gov
  - Key Pages: Orders, Rules, Dockets
  - Update Frequency: Daily

### Ohio
- **Public Utilities Commission (PUCO)**
  - URL: https://www.puco.ohio.gov
  - Key Pages: Orders, Rules, Cases
  - Update Frequency: Daily

### North Carolina
- **Utilities Commission (NCUC)**
  - URL: https://www.ncuc.net
  - Key Pages: Orders, Rules, Dockets
  - Update Frequency: Daily

### Michigan
- **Public Service Commission (MPSC)**
  - URL: https://www.michigan.gov/mpsc
  - Key Pages: Orders, Rules, Cases
  - Update Frequency: Daily

### New Jersey
- **Board of Public Utilities (NJBPU)**
  - URL: https://www.nj.gov/bpu
  - Key Pages: Orders, Regulations, Cases
  - Update Frequency: Daily

### Additional States (Phase 2)
- Arizona, Colorado, Georgia, Massachusetts, Minnesota, Nevada, Oregon, Washington, and others

---

## Scraping Strategy by Source Type

### 1. RSS Feeds
Many government sites provide RSS feeds for new documents:
- Monitor RSS feeds every 2-4 hours
- Parse feed items
- Download linked documents
- Extract metadata from feed

### 2. Web Scraping
For sites without APIs or RSS:
- Use Selenium/Playwright for JavaScript-heavy sites
- Use BeautifulSoup/Scrapy for static content
- Respect robots.txt
- Implement rate limiting
- Handle CAPTCHAs (manual intervention or service)

### 3. APIs
Where available:
- Federal Register API
- Some state sites provide APIs
- Use official APIs when possible

### 4. Email Subscriptions
- Subscribe to regulatory email lists
- Parse email notifications
- Extract document links
- Download documents

### 5. Document Repositories
- Some agencies use document management systems
- May require specialized scrapers
- Examples: Docket systems, case management systems

---

## Data Source Priority

### Phase 1 (MVP) - High Priority
1. FERC (Federal)
2. Federal Register - Energy Section
3. CAISO (California - high energy market)
4. ERCOT (Texas - large market)
5. CPUC (California)
6. PUCT (Texas)

### Phase 2 - Medium Priority
1. DOE
2. EPA Energy Section
3. PJM
4. MISO
5. NYISO
6. Top 10 states by energy market size

### Phase 3 - Lower Priority
1. Remaining RTOs/ISOs
2. Remaining states
3. County/city level (if applicable)

---

## Document Types to Extract

### Regulations
- Final rules
- Proposed rules
- Interim rules
- Emergency rules

### Orders
- Commission orders
- Administrative orders
- Enforcement orders

### Guidance Documents
- Compliance guides
- Interpretive guidance
- FAQs
- Best practices

### Enforcement Actions
- Fines and penalties
- Consent decrees
- Settlement agreements
- Violation notices

### Legislation
- Bills (when passed)
- Acts
- Statutes
- Amendments

### Notices
- Public notices
- Comment period notices
- Hearing notices
- Rulemaking notices

### Reports
- Annual reports
- Compliance reports
- Market reports
- Analysis reports

---

## Metadata to Extract

For each document, extract:
- **Title**: Document title
- **Source URL**: Original URL
- **Published Date**: When document was published
- **Effective Date**: When regulation becomes effective
- **Document Type**: Regulation, order, guidance, etc.
- **Jurisdiction**: Federal, state, regional
- **Status**: Active, proposed, repealed, superseded
- **Topics/Tags**: Energy type, sector, compliance area
- **Related Documents**: Links to related regulations
- **Authority**: Which agency/commission issued it
- **Docket Number**: If applicable
- **File Format**: PDF, HTML, Word, etc.
- **File Size**: For storage planning
- **Checksum**: For duplicate detection

---

## Scraping Challenges & Solutions

### Challenge 1: Dynamic Content
**Problem**: Many sites use JavaScript to load content
**Solution**: Use headless browsers (Selenium, Playwright)

### Challenge 2: CAPTCHAs
**Problem**: Some sites have CAPTCHA protection
**Solution**: 
- Use CAPTCHA solving services
- Implement manual review process
- Contact site administrators for API access

### Challenge 3: Rate Limiting
**Problem**: Sites may block aggressive scraping
**Solution**:
- Implement delays between requests
- Use proxy rotation
- Respect robots.txt
- Monitor for blocks

### Challenge 4: Document Formats
**Problem**: Documents in various formats (PDF, Word, HTML)
**Solution**:
- Use libraries for each format
- Convert to standardized format
- Extract text and preserve structure

### Challenge 5: Site Structure Changes
**Problem**: Websites change structure
**Solution**:
- Robust error handling
- Regular monitoring
- Version control for scrapers
- Alert on failures

### Challenge 6: Duplicate Detection
**Problem**: Same document from multiple sources
**Solution**:
- Use checksums/hashes
- Compare titles and dates
- Maintain source tracking

---

## Monitoring & Maintenance

### Daily Checks
- Scraping success rate
- New documents found
- Errors encountered
- Site structure changes

### Weekly Reviews
- Data quality checks
- Missing documents
- Source availability
- Performance metrics

### Monthly Updates
- Add new sources
- Update scraper logic
- Review and improve extraction
- Optimize performance

---

## Legal Considerations

1. **Terms of Service**: Review each site's ToS
2. **robots.txt**: Always respect robots.txt
3. **Rate Limiting**: Don't overload servers
4. **Public Data**: Focus on publicly available information
5. **Attribution**: Properly attribute sources
6. **Copyright**: Understand fair use for regulatory documents

---

*This document should be updated regularly as new sources are identified and added.*

