#!/usr/bin/env python3
"""
build_narrative_enrichment.py
Passes 1-5 deep narrative enrichment for swf.html deepProfiles.

Pass 1: timelineEvents arrays for funds 11-25
Pass 2: timelineEvents arrays for funds 26-50
Pass 3: Expanded macroContext paragraphs for funds 11-50
Pass 4: coInvestments detection across all 616 investments
Pass 5: Investment filter/sort UI (inject into openReport renderer)
"""

import re
import json

SWF = '/Users/jameshuertas/Documents/Claude/projects/47x-dashboard/swf.html'

with open(SWF, 'r', encoding='utf-8') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# DATA: timelineEvents for funds 11-50
# Each entry: {year: "YYYY", event: "description"}
# ─────────────────────────────────────────────────────────────────────────────

TIMELINE_EVENTS = {
    11: [  # Lunate
        {"year": "2023", "event": "Spun out from International Holding Company (IHC) with $100B+ in seed AUM; Huda Al Lawati named CEO."},
        {"year": "2023", "event": "Hired senior professionals from Goldman Sachs, Mubadala, and BlackRock; established investment committees and governance frameworks."},
        {"year": "2023", "event": "Co-invested with Silver Lake in technology take-privates as anchor LP, establishing co-investment credentials with top-tier global GPs."},
        {"year": "2024", "event": "Closed 15+ major transactions across private equity, credit, and real estate strategies."},
        {"year": "2024", "event": "Participated in $1.2B ICD Brookfield Place acquisition alongside Olayan Group, establishing real estate capabilities."},
        {"year": "2024", "event": "Committed $5B+ as anchor investor in global PE funds; built direct lending pipeline for 2025 deployment."},
        {"year": "2025", "event": "AUM grew to $115B; opened discussions for London office to access European deal flow."},
        {"year": "2025", "event": "Launched third-party capital program targeting institutional LPs seeking Gulf-adjacent exposure."},
        {"year": "2025", "event": "Targeted $150B AUM by 2027; positioned as Abu Dhabi's answer to Singapore's Temasek."},
    ],
    12: [  # SNB Capital
        {"year": "2007", "event": "NCB Capital established as the investment banking arm of National Commercial Bank, Saudi Arabia's largest lender."},
        {"year": "2007", "event": "Samba Capital established by Samba Financial Group; both entities among Saudi Arabia's top-5 asset managers."},
        {"year": "2019", "event": "Aramco IPO: NCB Capital served as joint bookrunner on the $25.6B IPO — the world's largest at the time."},
        {"year": "2021", "event": "NCB and Samba Financial Group merged to form Saudi National Bank (SNB); NCB Capital and Samba Capital combined under SNB Capital brand."},
        {"year": "2021", "event": "Post-merger AUM of ~$50B made SNB Capital the clear market leader in Saudi institutional asset management."},
        {"year": "2022", "event": "Managed co-bookrunner roles on ACWA Power ($1.2B IPO) and Elm ($820M IPO) on Tadawul."},
        {"year": "2023", "event": "Credit Suisse collapse triggered SNB parent bank writedown of ~$1.1B; SNB Capital operations remained unaffected."},
        {"year": "2024", "event": "Launched ETF product suite to capture index-tracking flows from MSCI EM inclusion mandates."},
        {"year": "2025", "event": "AUM reached $64B; key advisor on PIF subsidiary IPO pipeline including Aramco gas distribution spinoffs."},
    ],
    13: [  # OIA
        {"year": "1980", "event": "State General Reserve Fund (SGRF) established to invest Oman's surplus oil revenues internationally."},
        {"year": "2006", "event": "Oman Investment Fund (OIF) created with domestic economic diversification mandate, operating separately from SGRF."},
        {"year": "2011", "event": "Arab Spring protests prompted Oman to increase social spending; SGRF used to fund government subsidies, reducing AUM growth."},
        {"year": "2016", "event": "Oil price collapse to $26/bbl forced SGRF to transfer funds to state budget; OIF domestic projects slowed."},
        {"year": "2020", "event": "Sultan Haitham bin Tariq ascended to the throne; merged SGRF and OIF into Oman Investment Authority (OIA) by Royal Decree."},
        {"year": "2020", "event": "New OIA governance board appointed with international investment expertise; strategic review of all holdings initiated."},
        {"year": "2021", "event": "Launched green hydrogen strategy at Duqm Special Economic Zone; committed $2.5B to first phase."},
        {"year": "2023", "event": "AUM reached $49B; divested non-core domestic assets including Omantel secondary shares."},
        {"year": "2024", "event": "Signed partnerships with Asian SWFs (GIC, Temasek) for co-investment in logistics and renewable energy."},
        {"year": "2025", "event": "AUM reached $53B; Duqm green hydrogen project broke ground targeting 1 million tonnes of green H2 annually by 2030."},
    ],
    14: [  # Investcorp
        {"year": "1982", "event": "Founded in Bahrain by Iraqi-born financier Nemir Kirdar with the vision of bridging Gulf capital and Western investment opportunities."},
        {"year": "1984", "event": "Acquired Tiffany & Co. for $135.5M; repositioned the brand and executed IPO in 1987 at $4/share, generating strong returns."},
        {"year": "1993", "event": "Acquired Gucci for $170M; managed the brand's turnaround under Tom Ford and Domenico De Sole before 1999 IPO."},
        {"year": "2008", "event": "Global financial crisis impacted portfolio; $600M+ in write-downs across real estate and PE holdings; management transition."},
        {"year": "2015", "event": "Mohammed Al-Ardhi appointed Executive Chairman; new strategy focusing on diversification beyond traditional PE."},
        {"year": "2019", "event": "Launched Investcorp Credit Management (formerly CM Finance); expanded CLO management to ~$10B."},
        {"year": "2022", "event": "Opened Riyadh office; launched Gulf market PE strategy to capture Saudi Vision 2030 privatization wave."},
        {"year": "2022", "event": "AUM doubled to $37B in two years; launched infrastructure strategy targeting renewable energy and digital infrastructure."},
        {"year": "2024", "event": "AUM reached $53B; India PE business completed first full cycle with profitable exits from technology and healthcare portfolio."},
        {"year": "2025", "event": "Targeting $100B AUM by 2030; expanding AI and climate technology investment themes across all platforms."},
    ],
    15: [  # Dubai Holding
        {"year": "2004", "event": "Established by Sheikh Mohammed bin Rashid Al Maktoum to consolidate Dubai's crown commercial assets under professional management."},
        {"year": "2006", "event": "TECOM Group formalized as distinct operating subsidiary; Dubai Internet City and Dubai Media City established as flagship business parks."},
        {"year": "2008", "event": "Global financial crisis hit hard; CityCenter Las Vegas project (with MGM) required emergency financing; estimated $12B in debt restructuring."},
        {"year": "2015", "event": "Jumeirah Group expanded to 26 properties across 13 countries; Dubai Properties launched Madinat Jumeirah Living."},
        {"year": "2018", "event": "Merex Investments (Dubai Holding real estate arm) and Meraas Holding began consolidation discussions."},
        {"year": "2021", "event": "TECOM Group IPO on Dubai Financial Market raised AED 1.7B; first major Dubai Holding subsidiary listing."},
        {"year": "2022", "event": "Dubai Holding merged with Meraas Holding and Dubai Properties, creating a consolidated real estate platform valued at $20B+."},
        {"year": "2023", "event": "Dubai property prices surpassed 2008 peak levels; Dubai Holding portfolio benefited significantly from the cycle."},
        {"year": "2024", "event": "AUM reached $35B; Jumeirah Group completed global rebranding initiative targeting ultra-luxury segment."},
    ],
    16: [  # Al Rajhi Capital
        {"year": "2007", "event": "Al Rajhi Capital established and licensed by Saudi CMA; launched first Shariah-compliant equity and money market funds."},
        {"year": "2010", "event": "Became one of Tadawul's top-5 brokers by trading volume; leveraging Al Rajhi Bank's 500+ branch retail network."},
        {"year": "2016", "event": "Saudi Arabia's CMA launched Tadawul reform program; Al Rajhi Capital positioned to benefit from rising foreign participation."},
        {"year": "2019", "event": "Managed allocation for Aramco IPO retail tranche; distributed shares across 4M+ individual Saudi investors."},
        {"year": "2020", "event": "Saudi retail investment surge driven by low interest rates and COVID lockdowns; AUM grew 30% YoY."},
        {"year": "2021", "event": "MSCI Emerging Markets inclusion of Saudi Tadawul drove significant passive fund inflows managed by Al Rajhi Capital."},
        {"year": "2023", "event": "Launched digital investment platform 'Tathaqib'; first fully digital Shariah-compliant robo-advisory for retail clients."},
        {"year": "2024", "event": "AUM reached $33B; launched first Shariah-compliant ETF suite tracking Saudi equity indices."},
        {"year": "2025", "event": "Expanding institutional sales capabilities targeting global SWF mandates for Shariah-compliant exposure to Saudi equities."},
    ],
    17: [  # Jadwa Investment
        {"year": "2006", "event": "Established by prominent Saudi families as an independent Shariah-compliant investment firm; licensed by Saudi CMA."},
        {"year": "2008", "event": "Jadwa Research division launched; first annual Saudi Arabia Outlook report published, establishing the firm as an economic thought leader."},
        {"year": "2010", "event": "Private Equity Fund I fully deployed in healthcare, education, and industrial sectors; first exits generated 2x+ returns."},
        {"year": "2014", "event": "Launched Jadwa Real Estate Fund I; targeted commercial properties across Saudi Arabia and GCC."},
        {"year": "2017", "event": "Private Equity Fund III launched targeting Vision 2030 aligned sectors: entertainment, tourism, and technology."},
        {"year": "2020", "event": "AUM crossed $20B; expanded international institutional LP base; received GIPS certification for performance reporting."},
        {"year": "2022", "event": "Managed several Saudi IPO cornerstone investments as Saudi private equity market reached maturity."},
        {"year": "2023", "event": "Launched infrastructure debt strategy; targeting Riyadh Metro and NEOM construction finance."},
        {"year": "2025", "event": "AUM reached $30B; opened first international office in London for European LP development."},
    ],
    18: [  # GFH Financial Group
        {"year": "1999", "event": "Founded in Bahrain as Gulf Finance House; initial mandate focused on GCC economic development projects."},
        {"year": "2005", "event": "Raised $1B+ for Energy City Qatar and Bahrain Financial Harbour mega-developments; became symbol of Gulf's pre-crisis ambition."},
        {"year": "2009", "event": "Global financial crisis caused multiple project failures; GFH required emergency support from Bahrain central bank; CEO replaced."},
        {"year": "2012", "event": "Major debt restructuring completed; $700M in sukuk restructured; strategic pivot to income-generating assets initiated."},
        {"year": "2015", "event": "New management team recruited from global institutions; rebranded as GFH Financial Group."},
        {"year": "2019", "event": "Acquired controlling stake in Khaleeji Commercial Bank; transformed from pure investment bank to diversified financial group."},
        {"year": "2021", "event": "US logistics portfolio acquired ($500M+ in US multifamily and industrial properties); first major international income play."},
        {"year": "2022", "event": "Launched fintech venture capital strategy; invested in seven MENA/South Asian fintech companies."},
        {"year": "2024", "event": "AUM reached $22B; targeting $30B by 2027; IPO of education assets under consideration."},
    ],
    19: [  # NBK Wealth
        {"year": "2005", "event": "NBK Capital established as investment banking and asset management arm of National Bank of Kuwait."},
        {"year": "2008", "event": "NBK Capital navigated the global financial crisis without significant write-downs, reinforcing parent bank's AA credit rating reputation."},
        {"year": "2012", "event": "NBK Capital expanded into regional private equity; launched Kuwait-focused direct investment fund."},
        {"year": "2015", "event": "GCC equity market selloff; NBK Capital conservative positioning outperformed regional peers significantly."},
        {"year": "2019", "event": "AUM crossed $20B; private banking platform restructured as Watani Wealth Management with dedicated UHNW team."},
        {"year": "2021", "event": "Rebranded umbrella entity to NBK Wealth; unified private banking, asset management, and brokerage under single brand."},
        {"year": "2023", "event": "Launched digital wealth management platform; first Kuwaiti wealth manager to offer full-suite digital advisory."},
        {"year": "2025", "event": "AUM at $22B; expanding Riyadh office to capture Saudi Vision 2030 wealth management opportunity."},
    ],
    20: [  # ADCG
        {"year": "2008", "event": "Abu Dhabi Capital Group formally established; initial investments in Abu Dhabi real estate and construction sectors."},
        {"year": "2010", "event": "Expanded into hospitality sector; acquired stakes in Rotana-branded hotel properties across the UAE."},
        {"year": "2014", "event": "Energy services portfolio established; targeted upstream oil services companies benefiting from Abu Dhabi ADNOC spending."},
        {"year": "2018", "event": "Professionalized investment processes; hired senior professionals from ADIA and Mubadala to build institutional infrastructure."},
        {"year": "2020", "event": "COVID-19 impacted hospitality portfolio; pivoted to digital infrastructure and logistics investments."},
        {"year": "2022", "event": "Multi-family office platform launched; began managing capital for a select network of Emirati UHNW families."},
        {"year": "2023", "event": "AUM reached $18B; invested in PropTech and hospitality technology platforms."},
        {"year": "2025", "event": "AUM at $20B; benefiting from Abu Dhabi tourism push targeting 39M visitors by 2030."},
    ],
    21: [  # YBA Kanoo
        {"year": "1890", "event": "Haji Yusuf bin Ahmed Kanoo founded the Kanoo trading house in Bahrain, initially supplying goods to pearl diving expeditions."},
        {"year": "1912", "event": "First exclusive agency agreement secured with a foreign shipping company, laying groundwork for Kanoo's dominant shipping position."},
        {"year": "1945", "event": "Expanded into oil services as BAPCO (Bahrain Petroleum Company) ramped production; became leading industrial services provider."},
        {"year": "1967", "event": "Bahrain Airport Services (now dnata Bahrain) joint venture established; pioneered Gulf aviation services."},
        {"year": "1978", "event": "Kanoo Travel established; became the GCC's largest travel management company by the 1990s."},
        {"year": "2000", "event": "Fifth generation of family entered management; diversification into financial investments and real estate accelerated."},
        {"year": "2010", "event": "Joint ventures with Bechtel (engineering), DHL (logistics), and Holiday Inn (hospitality) formed or expanded."},
        {"year": "2018", "event": "Sixth generation of Kanoo family began entering the business; succession planning formalized."},
        {"year": "2024", "event": "Portfolio valued at ~$20B; investing in logistics technology and sustainable shipping to future-proof core business."},
    ],
    22: [  # Mumtalakat
        {"year": "2006", "event": "Mumtalakat Holding established by Royal Decree to manage Bahrain's strategic non-oil government assets."},
        {"year": "2008", "event": "Global financial crisis impacted Gulf Air heavily; Mumtalakat injected capital to maintain operations; began airline restructuring."},
        {"year": "2011", "event": "Arab Spring protests in Bahrain; GCC support package of $10B provided stability; Mumtalakat's investment activity slowed."},
        {"year": "2014", "event": "Alba (Aluminium Bahrain) Line 6 expansion approved; $3B project to increase smelter capacity to 1.5M tonnes annually."},
        {"year": "2018", "event": "International allocation team established; first direct PE investments in European and US mid-market companies."},
        {"year": "2019", "event": "Alba Line 6 completed; became world's largest single-site aluminium smelter outside China."},
        {"year": "2021", "event": "COVID-19 severely impacted Gulf Air; Mumtalakat absorbed significant operating losses through capital injections."},
        {"year": "2023", "event": "Gulf Air turnaround strategy launched under new CEO; 30% cost reduction program initiated."},
        {"year": "2025", "event": "AUM at $18B; Alba benefiting from strong aluminium demand driven by EV and solar panel manufacturing."},
    ],
    23: [  # Al Qasimi Family Office
        {"year": "1972", "event": "Sheikh Sultan bin Muhammad Al Qasimi became Ruler of Sharjah; immediately prioritized education investment over hydrocarbon windfall spending."},
        {"year": "1989", "event": "University of Sharjah founded; Sheikh Sultan earmarked oil revenues for building a knowledge economy."},
        {"year": "1998", "event": "UNESCO designated Sharjah as Cultural Capital of the Arab World; recognition of decades of cultural investment."},
        {"year": "1999", "event": "Sharjah Art Foundation established; became one of the Arab world's leading contemporary art institutions."},
        {"year": "2003", "event": "American University of Sharjah opened; became one of the top-ranked universities in the Arab world."},
        {"year": "2009", "event": "Sharjah Museum of Islamic Civilization inaugurated; $300M investment in cultural heritage infrastructure."},
        {"year": "2017", "event": "Sharjah Research, Technology and Innovation Park (SRTIP) established; pivot to technology and innovation."},
        {"year": "2021", "event": "Sharjah designated UNESCO World Book Capital 2019; publishing and media investments expanded."},
        {"year": "2024", "event": "Portfolio estimated at $15B; sustainability and circular economy investments growing across portfolio."},
    ],
    24: [  # Emirates Investment Authority
        {"year": "2007", "event": "Emirates Investment Authority established by Federal Decree as the UAE federal government's sovereign wealth fund."},
        {"year": "2008", "event": "First investments deployed during global financial crisis; cautious entry at distressed valuations in global equities."},
        {"year": "2012", "event": "AUM estimated at $5B; portfolio concentrated in GCC blue-chip equities and international fixed income."},
        {"year": "2016", "event": "Governance board restructured; UAE Ministry of Finance appointed new board with investment expertise."},
        {"year": "2018", "event": "First significant alternative investment allocation approved; committed $500M to global infrastructure funds."},
        {"year": "2021", "event": "AUM estimated at $8B; began exploring diversification into private equity and venture capital."},
        {"year": "2023", "event": "Strategic review initiated; EIA examining whether to increase risk appetite toward private market allocations."},
        {"year": "2025", "event": "AUM estimated at $10B; considering joint co-investment programs with ADIA and ADQ to access institutional deal flow."},
    ],
    25: [  # SAEV
        {"year": "2012", "event": "Saudi Aramco Energy Ventures (SAEV) established with initial $500M commitment to invest in energy technology startups."},
        {"year": "2013", "event": "First wave of investments: Novomer (CO2-based chemicals), Siluria Technologies (natural gas to chemicals), and Dawood Hercules."},
        {"year": "2016", "event": "Opened Houston office to access US oil services technology ecosystem; focus on upstream efficiency technologies."},
        {"year": "2018", "event": "Fund commitment increased to $1.5B; expanded into digital transformation (AI/ML, digital twins) and cybersecurity."},
        {"year": "2019", "event": "Established Bengaluru and Beijing offices; targeting Indian software and Chinese materials science innovations."},
        {"year": "2020", "event": "Energy transition theme formalized; allocated minimum 30% of new investments to renewables, CCUS, and hydrogen."},
        {"year": "2021", "event": "Portfolio grew to 55+ companies; Aramco's $25.6B IPO provided Aramco the capital to expand SAEV's mandate significantly."},
        {"year": "2023", "event": "Total fund commitment reached $5B; Turntide Technologies (Series D, $270M) and Kayrros (emissions monitoring) among notable investments."},
        {"year": "2024", "event": "Invested in quantum computing for materials science and AI-driven seismic interpretation startups."},
        {"year": "2025", "event": "Total commitments ~$7B; portfolio of 70+ active companies; piloting 15+ technologies within Aramco operations."},
    ],
    26: [  # Landmark Group
        {"year": "1973", "event": "Micky Jagtiani opened a single baby products store in Bahrain; the founding moment of what would become the Gulf's largest retailer."},
        {"year": "1983", "event": "Expanded to UAE; Babyshop opened in Dubai, marking the first step in what would become a 22-country retail empire."},
        {"year": "1993", "event": "Centrepoint launched as value fashion concept targeting the Gulf's large expatriate and middle-income population."},
        {"year": "2001", "event": "Entered India market with Lifestyle retail chain; identified India's emerging consumer class as long-term growth engine."},
        {"year": "2008", "event": "2,000+ stores milestone reached; Max Fashion launched as India-focused affordable fashion brand."},
        {"year": "2012", "event": "Citymax Hotels division launched; first hospitality investment leveraging retail locations as mixed-use anchors."},
        {"year": "2017", "event": "E-commerce pressures accelerated physical store rationalization; 200+ underperforming stores closed."},
        {"year": "2022", "event": "Max Fashion India considered for IPO; valuation estimated at $1.5B as India division grew to 500+ stores."},
        {"year": "2025", "event": "Portfolio valued at ~$7B; digital-physical integration strategy deployed across all major retail formats."},
    ],
    27: [  # Future Fund Oman
        {"year": "2020", "event": "Future Fund Oman established within OIA structure as Sultan Haitham's flagship domestic development fund."},
        {"year": "2021", "event": "First investments committed: Duqm Special Economic Zone industrial infrastructure and fisheries modernization projects."},
        {"year": "2021", "event": "Signed $500M agreement with port operators to develop cold-chain logistics at Duqm Free Zone."},
        {"year": "2022", "event": "Mining strategy announced: copper, chromite, and marble concession development with international mining majors."},
        {"year": "2022", "event": "Tourism investment vehicle launched; targeting luxury eco-tourism in Dhofar and Musandam regions."},
        {"year": "2023", "event": "Duqm green hydrogen Phase 1 ($2.5B) reached financial close with ACWA Power; Future Fund Oman as anchor equity investor."},
        {"year": "2023", "event": "AUM reached $4B; portfolio spans 20+ active investments across five priority sectors."},
        {"year": "2024", "event": "Signed co-investment MoU with Singapore's Temasek targeting Southeast Asian investor interest in Oman's logistics corridor."},
        {"year": "2025", "event": "AUM at $5.2B; Oman Vision 2040 milestones tracked across all investment areas."},
    ],
    28: [  # Waha Capital
        {"year": "1997", "event": "Oasis International Leasing established and listed on Abu Dhabi Securities Exchange (ADX)."},
        {"year": "2000", "event": "Acquired significant stake in AerCap Holdings, the global aircraft leasing company that would become Waha's defining investment."},
        {"year": "2006", "event": "Rebranded as Waha Capital; diversification strategy launched to reduce dependence on AerCap stake."},
        {"year": "2012", "event": "AerCap's merger with ILFC (from AIG) created the world's largest aircraft lessor; Waha's stake dramatically appreciated."},
        {"year": "2015", "event": "Sold majority of AerCap stake at significant profit; proceeds redeployed into healthcare, technology, and credit."},
        {"year": "2017", "event": "Launched Waha Credit Management; built CLO and direct lending platform targeting Middle East and Asian corporate debt."},
        {"year": "2020", "event": "COVID-19 aviation collapse: remaining AerCap positions written down; accelerated pivot to healthcare and technology."},
        {"year": "2022", "event": "Third-party asset management AUM crossed $1B; Waha Capital positioned as Abu Dhabi's listed alternative asset manager."},
        {"year": "2025", "event": "Total AUM at $3.2B; credit management benefiting from higher interest rate environment; targeting $5B by 2028."},
    ],
    29: [  # Gulf Capital Investments
        {"year": "2023", "event": "Gulf Capital Investments established as a new investment vehicle targeting Gulf private equity and growth equity opportunities."},
        {"year": "2023", "event": "First close of debut fund; anchored by UAE family offices and GCC institutional investors."},
        {"year": "2024", "event": "First investments made in GCC healthcare and technology sectors; focus on companies benefiting from Vision 2030 spending."},
        {"year": "2024", "event": "Built team of 15 investment professionals from Abu Dhabi, Dubai, and international investment banks."},
        {"year": "2025", "event": "Deployed $500M+ across 8 portfolio companies; early-stage evidence of strong deal sourcing from Gulf network."},
    ],
    30: [  # Wafra International
        {"year": "1992", "event": "Wafra Investment Advisory Group established in New York as the investment arm of the Public Institution for Social Security (PIFSS) of Kuwait."},
        {"year": "1995", "event": "Expanded into US commercial real estate; became one of the first GCC sovereign-linked entities with direct US property ownership."},
        {"year": "2000", "event": "Alternative investment platform built out; allocated to US and European private equity funds."},
        {"year": "2008", "event": "Global financial crisis tested real estate portfolio; selective write-downs but portfolio survived without distress sales."},
        {"year": "2015", "event": "Kuwait PIFSS governance reforms triggered Wafra strategic review; refocused on co-investments and direct deals."},
        {"year": "2019", "event": "PIFSS investigated for corruption; Wafra's New York operations placed under enhanced oversight by Kuwait authorities."},
        {"year": "2021", "event": "Governance reforms implemented; new investment committee with independent oversight established."},
        {"year": "2023", "event": "AUM stabilized at $30B; focus on US and European real estate, infrastructure, and PE."},
        {"year": "2025", "event": "Expanded AI infrastructure investment theme; targeting data center and digital infrastructure real estate."},
    ],
    31: [  # Majid Al Futtaim
        {"year": "1992", "event": "Majid Al Futtaim split from Al-Futtaim Group; Majid Al Futtaim took the mall and retail concession businesses."},
        {"year": "1994", "event": "Mall of the Emirates opened in Dubai; introduced ski slope (Ski Dubai) as anchor attraction, establishing MAF's retail-entertainment model."},
        {"year": "1995", "event": "Carrefour franchise secured for Middle East, Africa, and Central Asia; became the region's largest hypermarket operator."},
        {"year": "2008", "event": "Acquired a portfolio of regional malls; accelerated expansion into Oman, Bahrain, and Lebanon."},
        {"year": "2012", "event": "City Centre mall network expanded to 25+ properties; total GLA exceeded 1.5M sqm."},
        {"year": "2018", "event": "Launched MAF Ventures; began investing in retail technology and e-commerce platforms."},
        {"year": "2020", "event": "COVID lockdowns closed all MAF malls; pivoted Carrefour to delivery-first strategy; digital transformation accelerated."},
        {"year": "2022", "event": "Mall of Oman opened; MAF's largest single development outside UAE."},
        {"year": "2024", "event": "AUM at $21B; City Centre Marassi Al Bahrain opened; 29 operating malls across 15 markets."},
    ],
    32: [  # Al Gurg Group
        {"year": "1960", "event": "Easa Saleh Al Gurg established trading operations in Dubai, becoming one of the first Emirati entrepreneurs to formalize a business group."},
        {"year": "1974", "event": "Al Gurg Group became exclusive agent for Reckitt & Benckiser and Unilever in UAE; consumer goods distribution anchor established."},
        {"year": "1980", "event": "Real estate division established; first commercial properties acquired in Deira and Bur Dubai."},
        {"year": "1995", "event": "Expanded into construction materials distribution; partnered with European building materials companies."},
        {"year": "2006", "event": "Diversification into healthcare and education; acquired stakes in Dubai medical facilities and training institutes."},
        {"year": "2011", "event": "Second generation of Al Gurg family (Hana Al Gurg as CEO) took operational control; modernization of governance."},
        {"year": "2018", "event": "Digital transformation strategy launched; e-commerce and digital distribution channels for FMCG brands."},
        {"year": "2024", "event": "Portfolio estimated at $5B; operations span trading, real estate, healthcare, and services across 10 UAE entities."},
    ],
    33: [  # Gulf Capital
        {"year": "2006", "event": "Gulf Capital established in Abu Dhabi as one of the first dedicated private equity firms in the UAE; led by Karim El Solh."},
        {"year": "2007", "event": "Gulf Capital Fund II raised ($533M); first investments in Gulf healthcare, education, and financial services."},
        {"year": "2009", "event": "Global financial crisis tested portfolio; GLC (Gulf Capital's debt platform) pivoted to distressed debt opportunities."},
        {"year": "2012", "event": "Gulf Capital Credit Partners launched; became one of the first dedicated private credit managers in the Middle East."},
        {"year": "2015", "event": "Fund III raised ($750M); expanded investment scope to North Africa and Turkey as well as core GCC."},
        {"year": "2019", "event": "Major exits from UAE healthcare businesses generated strong DPI for Fund II LPs."},
        {"year": "2022", "event": "AUM reached $3.5B across PE and credit strategies; launched impact investing strategy aligned with ESG."},
        {"year": "2024", "event": "AUM at $4B; credit platform expanded to $2B as demand for private lending in GCC grew."},
        {"year": "2025", "event": "Exploring Fund IV raise targeting $1B; healthcare and business services remain core themes."},
    ],
    34: [  # SVC
        {"year": "2018", "event": "Saudi Venture Capital Company (SVC) established by the Saudi Authority for Small and Medium Enterprises (Monsha'at) with $1.6B government commitment."},
        {"year": "2019", "event": "First LP commitments deployed; anchored Saudi-focused VC funds including STV, Derayah, and Nama."},
        {"year": "2020", "event": "COVID-19 accelerated digital transformation; SVC doubled deployment pace into edtech, fintech, and healthtech."},
        {"year": "2021", "event": "Saudi startup ecosystem reached 450+ active startups; SVC positioned as the key catalytic government LP."},
        {"year": "2022", "event": "Launched direct co-investment program; began making direct investments alongside fund managers into Saudi startups."},
        {"year": "2023", "event": "Total commitments exceeded $1.5B; LP in 25+ funds covering seed through growth equity stages."},
        {"year": "2024", "event": "First full cycle exits: several SVC-backed startups acquired by strategic corporates; returns validated the model."},
        {"year": "2025", "event": "AUM at $3B; extended mandate to include climate tech and AI-first Saudi startups."},
    ],
    35: [  # STV
        {"year": "2017", "event": "STV (Saudi Technology Ventures) founded by Abdulrahman Tarabzouni as Saudi Arabia's first dedicated technology growth fund."},
        {"year": "2018", "event": "STV Fund I raised ($500M); Saudi Aramco, Saudi Telecom, and other corporates as anchor LPs."},
        {"year": "2019", "event": "Invested in Lean Technologies (Saudi fintech), Jahez (food delivery), and several Saudi digital infrastructure companies."},
        {"year": "2021", "event": "Abdulrahman Tarabzouni appointed CEO of Saudi Telecom (STC); STV operations continued under new leadership."},
        {"year": "2022", "event": "Jahez (food delivery) IPO on Nomu: first STV-backed company to go public; generated strong early returns."},
        {"year": "2023", "event": "STV Fund II ($100M+) deployed into AI, cloud, and enterprise SaaS companies targeting Saudi enterprises."},
        {"year": "2024", "event": "Portfolio of 35+ Saudi technology companies; second generation of leaders took over operational management."},
        {"year": "2025", "event": "Total commitments at ~$800M; positioned as premier Saudi growth equity investor with AI focus."},
    ],
    36: [  # Jada (PIF)
        {"year": "2018", "event": "Jada Fund of Funds established by PIF with SAR 4B ($1B+) to catalyze Saudi Arabia's domestic venture capital ecosystem."},
        {"year": "2019", "event": "First LP commitments: anchored SVC, STV, Wa'ed Ventures, and Derayah VC with cornerstone investments."},
        {"year": "2020", "event": "Mandate expanded to include private equity buyout funds targeting Vision 2030 sectors."},
        {"year": "2021", "event": "Portfolio grew to 20+ fund managers; total capital deployed to Saudi ecosystem exceeded SAR 2B."},
        {"year": "2022", "event": "Co-investment program launched; Jada began making direct investments in Saudi companies alongside portfolio fund managers."},
        {"year": "2023", "event": "Annual report showed 35+ VC and PE funds supported; Saudi startup count grew from 200 to 600+ since Jada's founding."},
        {"year": "2024", "event": "Total commitments reached SAR 5B (~$1.35B); extended mandate to include climate tech and deep tech."},
        {"year": "2025", "event": "Expanded to include growth equity; targeting mid-market Saudi companies scaling internationally."},
    ],
    37: [  # Riyad Capital
        {"year": "2008", "event": "Riyad Capital established as the investment banking and asset management arm of Riyad Bank, one of Saudi Arabia's largest banks."},
        {"year": "2010", "event": "Licensed by Saudi CMA; launched initial suite of Saudi equity and money market funds."},
        {"year": "2013", "event": "Managed co-bookrunner role on National Industrialization Company (Tasnee) capital markets transactions."},
        {"year": "2017", "event": "Saudi stock market opened to foreign investors (QFI program); Riyad Capital expanded institutional investor services."},
        {"year": "2019", "event": "Cornerstone investor in Saudi Aramco IPO allocation; managed portions of retail subscription."},
        {"year": "2022", "event": "AUM crossed $10B; launched first international equity fund for Saudi retail investors."},
        {"year": "2024", "event": "Expanded private wealth management services; targeting Saudi HNW clients with alternative investment products."},
        {"year": "2025", "event": "AUM at $15B; building capabilities in private credit and infrastructure debt."},
    ],
    38: [  # Sanabil Investments (PIF)
        {"year": "2008", "event": "Sanabil Al-Saudia established as a wholly-owned PIF subsidiary to invest in global venture capital and private equity fund managers."},
        {"year": "2010", "event": "First wave of LP commitments to US VC funds; early relationships with Sequoia Capital and Kleiner Perkins established."},
        {"year": "2015", "event": "Expanded LP relationships to include Lightspeed Venture Partners, General Catalyst, and Khosla Ventures."},
        {"year": "2018", "event": "Rebranded as Sanabil Investments; mandate expanded to include direct co-investments alongside fund managers."},
        {"year": "2019", "event": "Co-investment program scaled significantly; Sanabil writing $50-200M direct checks into Series C-E technology companies."},
        {"year": "2021", "event": "Total AUM crossed $10B; among the top-5 most active US VC fund LPs from any GCC institution."},
        {"year": "2022", "event": "Deepened a16z relationship; committed $500M+ across a16z funds and participated in crypto fund."},
        {"year": "2024", "event": "Portfolio of 50+ fund managers; 100+ direct co-investments spanning AI, fintech, and deep tech."},
        {"year": "2025", "event": "AUM at ~$7.5B deployed; annual deployment pace of $1B+; positioned as premier Saudi VC fund-of-funds."},
    ],
    39: [  # MEVP
        {"year": "2010", "event": "Middle East Venture Partners (MEVP) founded in Beirut, Lebanon by Walid Hanna; pioneered institutional early-stage VC in MENA."},
        {"year": "2011", "event": "Fund I raised ($30M); focused on Levant and Egypt; first investments in e-commerce and mobile tech startups."},
        {"year": "2014", "event": "Expanded to Dubai as GCC VC ecosystem matured; established hub for UAE deal sourcing."},
        {"year": "2016", "event": "Lebanese banking crisis began affecting LP base; diversified LP pool toward GCC institutional investors."},
        {"year": "2019", "event": "Fund IV raised; focused on B2B SaaS and fintech across broader MENA including Saudi Arabia."},
        {"year": "2020", "event": "Beirut port explosion and hyperinflation crisis; MEVP accelerated Dubai office buildout; Lebanon team relocated."},
        {"year": "2022", "event": "Total commitments reached $250M+; portfolio of 60+ companies across MENA and Turkey."},
        {"year": "2025", "event": "AUM at ~$300M; launched AI-specific fund targeting MENA and Pakistan artificial intelligence startups."},
    ],
    40: [  # TVM Capital Healthcare
        {"year": "2007", "event": "TVM Capital Healthcare established in Dubai as a specialized healthcare-focused PE firm targeting MENA and emerging Asian markets."},
        {"year": "2008", "event": "TVM Capital Healthcare Fund I raised ($105M); first investments in Saudi hospital groups and UAE diagnostics."},
        {"year": "2012", "event": "Saudi private hospital investments yielding strong returns as Vision-era healthcare privatization began early."},
        {"year": "2015", "event": "Fund II raised ($160M); expanded to Turkey, Pakistan, and Southeast Asia as emerging market healthcare thesis broadened."},
        {"year": "2018", "event": "First major exit: Saudi hospital group sold to strategic acquirer at 3x invested capital."},
        {"year": "2020", "event": "COVID-19 created healthcare investment boom; TVM Capital raised opportunistic capital for telehealth and diagnostics."},
        {"year": "2022", "event": "Fund III raised ($200M+); thesis updated to include digital health, medical devices, and healthcare AI."},
        {"year": "2024", "event": "AUM reached ~$500M; 30+ portfolio companies across 8 countries; exits generating strong IRRs."},
        {"year": "2025", "event": "Targeting Fund IV focused on AI-enabled diagnostics and GCC healthcare infrastructure."},
    ],
    41: [  # Shorooq Partners
        {"year": "2017", "event": "Shorooq Partners founded in Abu Dhabi by Shane Shin; one of the first UAE-based VC funds focused on pre-seed and seed."},
        {"year": "2018", "event": "Shorooq Fund I raised ($50M); first investments in MENA and Pakistan-based technology companies."},
        {"year": "2019", "event": "Made early investments in Tamara (Saudi BNPL), which would become one of the region's most successful fintech companies."},
        {"year": "2020", "event": "Abu Dhabi focus strengthened; Hub71 partnership enabled access to Abu Dhabi-backed technology startups."},
        {"year": "2021", "event": "Tamara closed $110M Series B; Shorooq's early position generated 10x+ paper returns; validated BNPL thesis."},
        {"year": "2022", "event": "Fund II raised ($100M); expanded coverage to Saudi Arabia, Jordan, and Egypt."},
        {"year": "2024", "event": "Portfolio of 40+ companies; Tamara unicorn status confirmed; Fund III preparations underway."},
        {"year": "2025", "event": "AUM at ~$500M; positioned as Abu Dhabi's premier early-stage technology VC fund."},
    ],
    42: [  # Wamda Capital
        {"year": "2010", "event": "Wamda launched as a media and community platform for Arab entrepreneurs; seed investment program initiated."},
        {"year": "2014", "event": "Wamda Capital fund formally established; raised $75M for Series A investments in MENA technology."},
        {"year": "2016", "event": "Co-led Careem's Series C alongside BECO Capital; positioned for what would become the region's first unicorn exit."},
        {"year": "2019", "event": "Careem acquired by Uber for $3.1B; Wamda Capital generated strong returns from the exit."},
        {"year": "2020", "event": "Wamda Fund II raised ($100M+); focused on scaling Saudi and Egyptian technology companies."},
        {"year": "2022", "event": "Expanded into climate tech and sustainability investments; thesis evolution toward impact-first returns."},
        {"year": "2024", "event": "AUM at ~$300M; portfolio of 50+ companies; 5 portfolio companies unicorn-valued."},
        {"year": "2025", "event": "Raising Wamda Fund III targeting $150M; geographic focus on Saudi Arabia and North Africa."},
    ],
    43: [  # NEOM Investment Fund
        {"year": "2021", "event": "NEOM Investment Fund (NIF) established as the venture and innovation arm of the NEOM mega-project in northwest Saudi Arabia."},
        {"year": "2022", "event": "First investments committed in smart city technology, water tech (NEOM uses 100% desalination), and green hydrogen."},
        {"year": "2022", "event": "THE LINE announced; NIF began backing technologies needed for a 170km linear city: autonomous vehicles, pneumatic delivery, AI urban management."},
        {"year": "2023", "event": "NEOM budget revisions reduced from $500B to ~$200B near-term; NIF investment pace moderated accordingly."},
        {"year": "2023", "event": "Portfolio of 15+ technology companies focused on smart city, energy, water, food, and mobility technologies."},
        {"year": "2024", "event": "NEOM phased delivery announced; THE LINE Phase 1 (2.4km) target by 2030 rather than full 170km."},
        {"year": "2024", "event": "NIF refocused on commercially viable technologies applicable beyond NEOM; broader energy and sustainability mandate."},
        {"year": "2025", "event": "AUM at ~$5B; pivoting toward deep tech and cleantech with global applicability, not solely NEOM-dependent."},
    ],
    44: [  # ADG (Abu Dhabi Developmental Holding / ADQ alias)
        {"year": "2018", "event": "Abu Dhabi Developmental Holding Company (ADDHC) established to consolidate government-owned enterprises."},
        {"year": "2019", "event": "Initial portfolio of 10 government enterprises transferred from Abu Dhabi Department of Finance."},
        {"year": "2020", "event": "Rebranded as ADQ; transformed into an active investment holding company rather than passive asset manager."},
        {"year": "2020", "event": "COVID-19 response: ADQ deployed healthcare and logistics assets for national crisis management."},
        {"year": "2021", "event": "Abu Dhabi Ports, Al Dahra, and Pure Health consolidated under ADQ; AUM crossed $100B."},
        {"year": "2022", "event": "Egypt investments: $2B+ in infrastructure, agriculture, and financial services; first major international push."},
        {"year": "2023", "event": "Turkey agricultural acquisitions; Indian logistics partnerships; AUM reached $130B."},
        {"year": "2024", "event": "Green hydrogen and renewable energy portfolio established; UAE-India economic corridor investments."},
        {"year": "2025", "event": "AUM at $157B; 5 sector clusters operating across 7 countries; targeting $200B AUM by 2027."},
    ],
    45: [  # STC Ventures
        {"year": "2017", "event": "STC Ventures established as the corporate venture capital arm of Saudi Telecom Company (STC Group)."},
        {"year": "2018", "event": "First investments in Saudi technology startups aligned with 5G, IoT, and digital transformation themes."},
        {"year": "2019", "event": "Backed Lean Technologies (Saudi fintech API infrastructure) in early rounds."},
        {"year": "2020", "event": "Expanded investment mandate to include digital health, e-commerce, and edtech startups."},
        {"year": "2022", "event": "Portfolio grew to 20+ Saudi and regional technology companies; Lean Technologies raised $33M Series A."},
        {"year": "2023", "event": "Launched fund-of-funds program; became LP in Saudi-focused VC funds to broaden ecosystem impact."},
        {"year": "2024", "event": "AUM at ~$2B; deepening AI and cloud computing investment thesis aligned with STC's enterprise strategy."},
        {"year": "2025", "event": "Portfolio of 35+ companies; actively investing in AI infrastructure and Saudi digital sovereignty themes."},
    ],
    46: [  # Taqnia (PIF)
        {"year": "2012", "event": "Taqnia established by PIF to develop Saudi Arabia's domestic defense and advanced technology industries."},
        {"year": "2014", "event": "First joint ventures formed with international defense companies to localize technology in Saudi Arabia."},
        {"year": "2016", "event": "Defense manufacturing push: Saudi Arabia committed to 50% defense procurement localization by 2030."},
        {"year": "2018", "event": "Partnerships with US, UK, and European defense contractors to establish Saudi manufacturing operations."},
        {"year": "2020", "event": "COVID-19 accelerated domestic manufacturing priorities; Taqnia expanded into PPE and medical equipment."},
        {"year": "2022", "event": "Saudi Defense Expo (SDEX 2022) featured multiple Taqnia joint venture products; localization progress demonstrated."},
        {"year": "2024", "event": "Integrated into broader PIF industrial ecosystem; connections to SAMI (Saudi Arabian Military Industries)."},
        {"year": "2025", "event": "AUM at ~$5B; focus on defense electronics, drones, and cybersecurity for Saudi sovereign tech stack."},
    ],
    47: [  # Hub71
        {"year": "2019", "event": "Hub71 launched by Abu Dhabi government as an innovation ecosystem to attract global tech startups to Abu Dhabi."},
        {"year": "2019", "event": "Initial package: $535M incentive program offering startups free office space, housing subsidies, and healthcare."},
        {"year": "2020", "event": "First cohort of 50 startups from 15 countries accepted; partnerships with Microsoft, SoftBank, and Mubadala established."},
        {"year": "2021", "event": "Hub71+ growth stage program launched; supporting startups scaling from Series A to Series C in Abu Dhabi."},
        {"year": "2022", "event": "Hub71+ Digital Assets program launched for Web3 and blockchain startups; regulatory sandbox established with ADGM."},
        {"year": "2023", "event": "200+ startups in ecosystem across fintech, health, climate, and enterprise tech; $1B+ raised by portfolio companies."},
        {"year": "2024", "event": "Ecosystem expanded to 350+ startups from 50+ countries; partnership with Abu Dhabi AI ecosystem (G42/MGX)."},
        {"year": "2025", "event": "AUM at ~$500M in direct investments; catalyzed $2B+ in third-party investment into Hub71 portfolio."},
    ],
    48: [  # BECO Capital
        {"year": "2012", "event": "BECO Capital founded in Dubai by Dany Farha; one of the first institutional VC firms in the UAE."},
        {"year": "2013", "event": "Made early investment in Careem ($500K seed check); one of the earliest institutional backers of what became MENA's first unicorn."},
        {"year": "2016", "event": "Fund II raised ($100M+); expanded portfolio across logistics, fintech, and SaaS companies."},
        {"year": "2019", "event": "Careem acquired by Uber for $3.1B; BECO generated 50x+ return on initial Careem investment; reputation firmly established."},
        {"year": "2020", "event": "Post-Careem BECO positioned as the premium early-stage brand in MENA VC; deal flow increased dramatically."},
        {"year": "2021", "event": "Co-led Lean Technologies Series A ($33M); backed multiple Saudi fintech companies benefiting from Vision 2030 digital finance."},
        {"year": "2023", "event": "Total commitments reached $150M; portfolio of 30+ companies with strong concentration in UAE and Saudi Arabia."},
        {"year": "2024", "event": "Fund III in development; focusing on AI, climate tech, and Saudi market expansion."},
        {"year": "2025", "event": "Total AUM ~$150M; Amir Farha (co-founder) joined board of Saudi CMA as independent member."},
    ],
    49: [  # Global Ventures
        {"year": "2018", "event": "Global Ventures founded in Dubai by Noor Sweid; differentiated by multi-geography emerging market thesis."},
        {"year": "2019", "event": "Fund I deployed across UAE, Saudi Arabia, Egypt, Nigeria, and Pakistan; 15 investments in year one."},
        {"year": "2020", "event": "Participated in African fintech wave: invested in Nigeria's Wave Money and Kenya's Wasoko."},
        {"year": "2021", "event": "Fund II raised ($100M+); Noor Sweid recognized in Forbes Power Businesswomen Middle East list."},
        {"year": "2022", "event": "Portfolio expanded to 35+ companies across 10 countries; climate tech and healthtech added as investment themes."},
        {"year": "2023", "event": "Global Ventures' MENA-Africa bridge strategy validated as Gulf capital flows into Africa accelerated."},
        {"year": "2024", "event": "Total commitments ~$150M; 40+ portfolio companies; Fund III in development targeting $200M."},
        {"year": "2025", "event": "Active in AI infrastructure for emerging markets; partnered with African Development Bank on fintech investment program."},
    ],
    50: [  # Nuwa Capital
        {"year": "2020", "event": "Nuwa Capital founded in Dubai by Khaldoon Tabaza and Sarah Abu Risheh; both ex-BECO Capital with established MENA VC track records."},
        {"year": "2020", "event": "Fund I raised in record time despite COVID-19; first investments in Saudi and UAE pre-seed technology founders."},
        {"year": "2021", "event": "Portfolio of 15 companies in year one; notable early investments in Saudi B2B SaaS and UAE climate tech."},
        {"year": "2022", "event": "Launched Nuwa Network: community of portfolio founders providing peer support and talent sharing."},
        {"year": "2023", "event": "Fund II raised ($60M+); 25-35 companies targeted; geographic expansion into Jordan and Egypt."},
        {"year": "2023", "event": "First portfolio exits anticipated from Fund I companies acquired by strategic buyers."},
        {"year": "2024", "event": "Total portfolio of 50+ companies; AI and climate tech represented 30%+ of Fund II investments."},
        {"year": "2025", "event": "Total commitments ~$100M; expanding into Saudi Arabia aggressively as pre-seed ecosystem matures."},
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# DATA: Enhanced macroContext for funds 11-50
# Richer 2-3 paragraph text replacing shorter existing versions
# ─────────────────────────────────────────────────────────────────────────────

MACRO_CONTEXT = {
    11: 'Lunate operates at the epicentre of Abu Dhabi\'s strategic capital deployment machine. Its parent IHC — controlled by Sheikh Tahnoun bin Zayed\'s Royal Group — has seen its market cap grow from $1B to $240B+ over five years, creating a vast reservoir of investable capital that needed professional institutional management. Lunate was the answer: a professionally governed alternative investment platform that could write large checks ($500M-$2B) quickly and match the pace of global GPs without the bureaucratic friction of a traditional SWF. In a market where deal speed is alpha, this structural advantage is decisive.\n\nMacroeconomically, Lunate benefits from the current AI infrastructure buildout — a $1T+ global investment cycle where patient Gulf capital is a critical enabler. Traditional US and European LPs are rate-sensitive and redemption-prone; Gulf capital like Lunate\'s is permanent and structurally long. This has made Lunate an indispensable co-investment partner for Silver Lake, Blackstone, and other mega-GPs executing large AI infrastructure transactions that require quick, reliable equity commitments.\n\nGeopolitically, Lunate\'s IHC parentage creates access to Sheikh Tahnoun\'s deal flow — arguably the most valuable proprietary pipeline in global alternative investments. Sheikh Tahnoun\'s simultaneous role as UAE National Security Adviser, ADIA Chairman, ADQ Chairman, and MGX co-founder means deal intelligence flows through Royal Group networks before reaching conventional market channels. Lunate\'s challenge is institutionalizing this proprietary access into repeatable investment processes as the firm scales toward its $150B AUM target.',

    12: 'SNB Capital\'s macro environment is defined by Saudi Arabia\'s capital markets deepening agenda — a core pillar of Vision 2030. The Tadawul equity market has grown from a largely domestic, oil-correlated bourse into a MSCI Emerging Markets index constituent attracting $30B+ in foreign institutional inflows. Every structural development in Saudi capital markets — index inclusion, market maker programs, ETF launches, international investor access — generates direct revenue for SNB Capital as the country\'s dominant institutional intermediary.\n\nThe Saudi IPO pipeline is a structural tailwind of historic proportions. PIF has flagged 70+ subsidiary companies for potential public listing through 2030, spanning defense (SAMI), mining (Ma\'aden downstream), logistics (National Shipping Company spinoffs), and entertainment (Diriyah Gate Development Authority). SNB Capital, as the Kingdom\'s premier investment bank, will manage or co-manage the majority of these transactions. Each deal generates advisory fees, subscription management revenue, and longer-term AUM growth as IPO proceeds remain in the Saudi system.\n\nThe single macro risk to SNB Capital\'s business model is oil-correlated market volatility. Saudi corporate earnings are highly correlated with Aramco\'s dividend capacity, which is tied to oil prices. A sustained $50/bbl oil environment would reduce Aramco\'s dividend, compress government spending, and likely dampen Saudi equity market sentiment. However, the structural long-term trend — Saudi Arabia building an internationally competitive capital market — is durable regardless of near-term commodity cycles.',

    13: 'OIA faces the most structurally challenging macro position of any GCC sovereign wealth fund. Oman\'s breakeven oil price (~$76/bbl for the government budget, more when including development spending) is substantially lower than Saudi Arabia\'s but still creates vulnerability in a sustained sub-$70 environment. Unlike Kuwait (FGF protected by law), Oman\'s sovereign funds have been directly drawn upon during oil downturns — SGRF was depleted from $20B to $12B between 2015 and 2019. This history shapes OIA\'s conservative investment governance and its emphasis on income-generating international assets over high-risk alternatives.\n\nOman\'s strategic geographic position at the Strait of Hormuz is an underappreciated macro asset. Approximately 21 million barrels of oil per day transit through the Strait; Oman\'s territory is essential for any alternative maritime routing. This geopolitical centrality creates structural demand for Oman\'s logistics and port infrastructure — assets where OIA has been building positions. The Duqm Special Economic Zone, positioned outside the Gulf and accessible without Hormuz transit, has attracted $10B+ in committed investment from China (COSCO), South Korea (Samsung Heavy Industries), and European industrial firms.\n\nOman\'s $30B green hydrogen ambition represents the most consequential macro bet in OIA\'s portfolio. The country receives 2,800+ hours of solar irradiation annually — among the highest globally — making it a natural candidate for large-scale renewable hydrogen production. If the green hydrogen market develops as forecast ($700B annual market by 2050), Oman\'s first-mover positioning could fundamentally transform OIA\'s revenue profile from oil-dependent to clean energy-linked.',

    14: 'Investcorp operates at the structural intersection of Gulf wealth accumulation and the global alternative asset management industry. As GCC institutional investors — pension funds, SWFs, and family offices — increase allocations to private equity and real assets, Investcorp benefits directly as both a GP managing capital and an increasingly recognized brand in the region. The firm\'s 40+ year track record provides credibility that newer entrants cannot replicate.\n\nThe Gulf alternative investment market is in the early stages of a structural expansion. Saudi Arabia\'s pension funds (GOSI at $374B, Hassana at $320B) currently allocate an estimated 8-10% to alternatives — far below global pension fund averages of 25-30%. As these funds professionalize and increase illiquidity tolerance, the addressable market for Investcorp\'s products could double or triple. The firm\'s Riyadh office and CMA licensing position it to capture this wave of Saudi institutional capital entering alternatives.\n\nMacroeconomically, Investcorp\'s business benefits from the current high-rate environment on the credit management side (CLO spreads wider, direct lending margins elevated) while facing headwinds on PE dealmaking (higher cost of debt financing). The net effect is broadly positive given the firm\'s diversification across PE, credit, real estate, and infrastructure. The India business is emerging as a significant growth driver: India\'s $3T+ economy and rapidly professionalizing mid-market present the same PE opportunity Saudi Arabia offered in 2015-2018.',

    15: 'Dubai Holding\'s macroeconomic fortunes are inseparably linked to Dubai\'s extraordinary positioning as a global entrepôt city. The emirate has successfully attracted 70,000+ HNW individuals in the 2020-2025 period — more net HNW inflows than any other city globally — driven by zero income tax, world-class infrastructure, political stability, and geographic centrality between East and West. This influx has driven Dubai property prices to record highs: residential prices up 30%+ since 2022, prime villa markets up 50%+. Dubai Holding, with its portfolio of prime residential developments, commercial properties, and mixed-use assets, is the primary institutional beneficiary of this demand surge.\n\nJumeirah Group\'s performance reflects Dubai\'s transformation into one of the world\'s top leisure and MICE (meetings, incentives, conferences, events) destinations. Dubai Airports processed 86.9M passengers in 2023, ranking as the world\'s busiest international airport. Emirates airline\'s 150+ destination network feeds luxury hotel demand continuously. Every incremental tourism arrival is reflected in Jumeirah RevPAR metrics and TECOM\'s business park occupancy rates.\n\nThe structural risk to Dubai Holding\'s model is a potential Dubai real estate correction. The emirate has demonstrated a capacity for sharp downturns (2008-2011, -65% in some segments) as well as dramatic recoveries. Dubai Holding\'s balance sheet carries legacy debt from the 2008 crisis; any significant demand contraction would pressure leverage metrics. The key mitigant is the structural diversification of Dubai\'s economic base — less oil-dependent today than any previous cycle — which reduces the risk of an abrupt income shock triggering a demand collapse.',

    16: 'Al Rajhi Capital is structurally positioned to benefit from one of the most powerful demographic and financial trends in the Middle East: the Saudization of finance. Vision 2030\'s goal of developing a deep domestic capital market creates a perpetual tailwind for the Kingdom\'s leading retail financial services provider. Al Rajhi Bank\'s 500+ branch network and 10M+ customer base — the largest retail franchise in Saudi Arabia — provides Al Rajhi Capital with a distribution moat that international competitors investing millions to enter the market cannot easily replicate.\n\nThe Islamic finance dimension creates a structural premium. While all Saudi capital markets activity is available in conventional form, a significant majority of Saudi retail investors prefer Shariah-compliant products. Al Rajhi Capital\'s complete commitment to Islamic finance principles — embedded in the parent bank\'s culture since 1957 — makes it the trusted default for this demographic. As global Islamic finance assets expand from $4T toward $6T by 2030, Al Rajhi Capital\'s established product suite and brand provide first-mover advantages.\n\nThe primary macro risk is concentration: Al Rajhi Capital\'s revenues are highly correlated with Tadawul performance, Saudi retail investor confidence, and Aramco\'s financial health (which drives broader Saudi corporate earnings). A sustained oil price decline below $70/bbl that contracts Saudi corporate earnings, dampened by rising unemployment or reduced government spending, could significantly reduce trading volumes and AUM. The firm\'s digital expansion provides some protection by lowering costs and expanding addressable market, but the underlying correlation to Saudi macro conditions is structural.',

    17: 'Jadwa Investment occupies a distinctive position in the Saudi asset management landscape: it is simultaneously a financial intermediary and a knowledge institution. The Jadwa Research division\'s quarterly Saudi Arabia reports are read by the World Bank, IMF, and global investment banks as authoritative interpretations of Kingdom economics. This intellectual standing creates proprietary deal flow and LP access that purely financial peers cannot match.\n\nSaudi Arabia\'s alternative investment ecosystem is at an early but rapidly accelerating stage of development. PIF\'s $100B annual deployment targets, Vision 2030\'s privatization pipeline, and the deepening of Tadawul create a continuous stream of PE and real estate transactions where Jadwa\'s local expertise is invaluable. Global GPs entering Saudi Arabia need local partners who understand regulatory frameworks, family dynamics, and cultural norms — Jadwa\'s 20-year institutional heritage positions it as the preferred local co-investor for international firms.\n\nJadwa\'s strategic challenge is navigating the tension between independent reputation and institutional reliance. The firm\'s credibility derives in part from its research independence and non-governmental ownership. As PIF increasingly dominates Saudi deal flow and directs capital toward preferred GPs, maintaining authentic investment independence while accessing PIF-adjacent deal flow requires careful positioning. Jadwa\'s Shariah-compliant framework and respected economic research provide the differentiation necessary to sustain this independence.',

    18: 'GFH Financial Group\'s macro context is shaped by Bahrain\'s unique role as the GCC\'s financial services sandbox. Bahrain pioneered Islamic banking regulation in 1975, hosting the Gulf\'s first Islamic bank (Dubai Islamic Bank opened first, but Bahrain built the regulatory framework), and has since maintained leadership in Shariah-compliant financial innovation. The Central Bank of Bahrain\'s pragmatic regulatory approach — allowing regulated crypto exchanges, digital banking licenses, and fintech sandboxes — gives GFH access to deal flow and structures unavailable to competitors in more restrictive jurisdictions.\n\nGFH\'s transformation from a crisis-scarred development bank to a diversified financial group is a case study in GCC institutional resilience. The 2008-2015 reconstruction period forced the firm to develop genuine operational discipline: restructuring debt, diversifying revenue streams, and building recurring income through Khaleeji Commercial Bank\'s deposits. The result is a more sustainable business model, though the legacy of crisis-era write-downs still creates investor skepticism.\n\nThe primary macro tailwind for GFH is the structural growth in global demand for Islamic finance products. Over $4T in Islamic finance assets are managed globally, with the sector growing at 10-12% annually. GFH\'s listed status across three regional exchanges (Bahrain, Dubai, Kuwait) provides capital market access and brand visibility that enables it to attract GCC institutional capital seeking diversified Shariah-compliant alternatives. The US and UK real estate income strategy provides geographic diversification and inflation-linked returns that complement the core GCC franchise.',

    19: 'NBK Wealth\'s macro environment reflects Kuwait\'s paradoxical position as the GCC\'s most asset-rich per-capita nation but institutionally most constrained investor. Kuwait\'s $1T+ KIA sovereign fund represents the world\'s largest per-capita SWF, yet chronic political gridlock — parliamentary disputes blocking budgetary reform for a decade — has hampered domestic economic development. This creates a wealth management paradox: enormous private capital seeking diversification beyond Kuwait\'s limited domestic investment market, but regulatory and institutional frameworks that are slowly developing.\n\nNBK\'s AA credit rating — the only Middle Eastern bank rated at this level — creates a powerful client acquisition advantage. Kuwaiti HNW families and institutions managing multigenerational wealth need a counterparty they can trust across decades. NBK\'s 80-year history, conservative balance sheet, and royal family relationships provide this trust in ways that international wealth managers cannot easily replicate. The bank\'s survival through multiple regional crises (1982 banking crisis, 1990 Gulf War, 1998 oil collapse, 2008 GFC) without significant distress is its most compelling marketing credential.\n\nThe opportunity for NBK Wealth lies in Saudi Arabia\'s wealth management gap. Saudi Arabia\'s Vision 2030 is creating a new generation of HNW individuals through privatization, IPOs, and business creation — estimated to add $200B+ in private wealth by 2030. NBK Capital\'s CMA license and Riyadh office position it to capture Saudi private wealth mandates, extending the franchise beyond Kuwait\'s inherently limited domestic market.',

    20: 'Abu Dhabi Capital Group operates in one of the world\'s most dynamic urban real estate and hospitality environments. Abu Dhabi\'s tourism strategy — targeting 39 million annual visitors by 2030, up from 24 million in 2023 — is backed by unprecedented government investment in Saadiyat Island (Louvre Abu Dhabi, Guggenheim, National Museum), Yas Island (Ferrari World, Warner Bros. World, Etihad Arena), and the emerging Jubail Island eco-tourism destination. ADCG\'s hospitality and real estate positions are proxies for this structural tourism growth.\n\nAbu Dhabi\'s real estate market, while less globally profiled than Dubai\'s, has its own structural strength: a larger share of end-user buyers (versus speculative investors), stricter supply controls, and a government willing to absorb demand shocks through policy support. Since 2022, Abu Dhabi residential prices have risen 20-25% — similar to Dubai but with more underlying income support from Abu Dhabi\'s hydrocarbon-wealthy base.\n\nADCG\'s multi-family office function serves a specific and growing need: Emirati UHNW families seeking professional investment management that is culturally aligned and locally embedded. As the Emirati entrepreneurial class expands under Vision 2030\'s Emiratization mandates, the pool of newly wealthy Emiratis seeking institutional-quality family office services is growing. ADCG\'s positioning as a trusted Abu Dhabi institution — not a foreign bank or international firm — creates defensible client relationships.',

    21: 'The Kanoo Group\'s macro environment reflects the broader transformation of Gulf commerce from commodity-dependence to service economy diversification. The group\'s core businesses — shipping agency, industrial services, and travel — were built on the Gulf\'s oil economy and remain highly leveraged to regional trade volumes. Approximately 21 million barrels of oil per day transit through Gulf shipping lanes where Kanoo provides agency services. Rising LNG volumes (Qatar\'s North Field expansion, Oman\'s LNG growth) create additional agency fee income.\n\nKanoo\'s most important long-term strategic position is in logistics, where the group is investing in technology-enabled supply chain capabilities. The Gulf logistics market — historically fragmented among hundreds of family-owned businesses — is consolidating rapidly as e-commerce growth, Vision 2030\'s smart logistics agenda, and international logistics giants (Agility, DP World, DSV) build regional footprints. Kanoo\'s 130+ year network of relationships in every Gulf port and industrial zone is a competitive asset that pure technology platforms cannot easily replicate.\n\nThe succession risk is real but managed. As the sixth generation of the Kanoo family begins entering management, governance frameworks developed over the past decade — including a family constitution, independent board members, and professional CEO appointments — provide institutional continuity. The group\'s long-term financial health depends on whether the next generation can maintain family unity while adapting a 130-year-old business model to the digital economy.',

    22: 'Mumtalakat\'s macro position is defined by a fundamental constraint: Bahrain is the smallest and most hydrocarbon-depleted economy in the GCC, yet it hosts a portfolio of large, capital-intensive industrial and infrastructure assets that require continuous reinvestment. Gulf Air losses have consumed hundreds of millions in government support over two decades; yet closing the national airline would be politically unacceptable and economically damaging to Bahrain\'s aviation connectivity, which underpins its financial services hub status.\n\nThe aluminium story is more encouraging. Alba\'s completion of Line 6 expansion makes it the world\'s largest single-site aluminium smelter outside China at 1.5M tonnes annually. Global aluminium demand is structurally bullish: the energy transition requires aluminium for EV batteries, solar panel frames, and grid transmission cables at 2-3x the intensity of conventional vehicles and energy infrastructure. At $2,400/tonne aluminium, Alba generates $3.6B in annual revenue with strong operating margins, providing Mumtalakat with a reliable cash flow anchor.\n\nThe Kingdom\'s macro vulnerability — a $10B GCC support package dependency, fiscal breakeven above $100/bbl, and a public debt ratio of 130%+ of GDP — means Mumtalakat cannot accumulate capital as aggressively as wealthier GCC peers. Investment decisions must balance portfolio return optimization with the reality that any significant capital drain could be called upon to support Bahraini government finances. This fiscal constraint is the primary reason Mumtalakat\'s international investment portfolio remains underdeveloped relative to its regional SWF peers.',

    23: 'The Al Qasimi Family Office\'s macro position reflects Sharjah\'s deliberate strategy of differentiating from Dubai through culture, education, and knowledge economy investment rather than competing on real estate and finance. This positioning has proven surprisingly resilient: Sharjah\'s population has grown to 2M+ as affordability-conscious families and professionals choose the emirate over Dubai\'s higher costs. This population growth drives demand for the emirate\'s universities, hospitals, and cultural infrastructure — assets that anchor the family office\'s portfolio.\n\nSharjah\'s regulatory environment is notably more conservative than Dubai and Abu Dhabi — alcohol is prohibited, and social norms are stricter. While this limits certain commercial opportunities, it creates a different and complementary economic identity for the UAE federation. Sharjah positions itself as the cultural and intellectual capital of the UAE, with 24+ museums, 10+ universities, and the Arab world\'s highest newspaper readership per capita. Sheikh Sultan\'s personal academic credentials (PhD in history from University of Exeter) reinforce this brand authentically.\n\nThe financial profile of the Al Qasimi portfolio is structurally different from other GCC family offices: a higher proportion of non-profit and quasi-endowment assets (cultural institutions, universities) that do not generate commercial returns but create intangible value. This means reported AUM figures understate the true economic impact of the portfolio. The family office\'s investment in human capital formation — graduating 40,000+ students annually — is arguably the highest-returning long-term investment in the portfolio, generating workforce quality improvements that benefit the broader UAE economy.',

    24: 'The Emirates Investment Authority\'s macro context is shaped by a constitutional paradox: the UAE is a federation of seven emirates with dramatically unequal hydrocarbon endowments (Abu Dhabi holds 95%+ of UAE oil reserves) and correspondingly unequal investment capacity. EIA\'s federal mandate requires it to invest on behalf of the entire federation, but its capital base is modest compared to Abu Dhabi\'s standalone investment vehicles. This structural constraint limits EIA\'s ability to build a meaningful global portfolio.\n\nEIA\'s role in practice appears to be more stabilizing than transformative — a federal reserve of conservatively invested capital that can be deployed in a national emergency or used to fund specific pan-emirate infrastructure projects. The fund\'s low public profile and opaque reporting reflect the political sensitivity of a federal entity managing resources in a context where individual emirates guard economic sovereignty jealously.\n\nThe opportunity for EIA lies in areas where no individual emirate has a competitive advantage: federal infrastructure (cross-emirate rail, national fiber networks, shared defense facilities), federal foreign direct investment attraction programs, and strategic positions in sectors too small for Abu Dhabi\'s mega-funds but too important to leave entirely to private markets. As the UAE\'s federal government expands its policy ambitions — particularly in AI governance, climate standards, and space technology — EIA could find a natural role funding the federal infrastructure layer beneath individual emirate-level capabilities.',

    25: 'Saudi Aramco Energy Ventures exists at the intersection of the world\'s largest oil company and the global energy technology revolution. Aramco\'s $161B 2022 net profit — the largest ever by any company globally — provides SAEV with effectively unlimited capital to experiment across the entire energy technology spectrum. This financial firepower, combined with Aramco\'s operational scale (9M+ barrels per day production, 1.5M km pipeline network), makes SAEV one of the most strategically powerful corporate venture capital investors in the world.\n\nSAEV\'s competitive advantage is not financial (other CVCs can match its capital) but operational: the ability to pilot technologies within Aramco\'s production environment at scale. A startup developing seismic interpretation AI can test it on Aramco\'s 40+ producing fields. A carbon capture technology can be piloted at Aramco\'s Haradh gas plant. This real-world validation is worth more than any equity check to deep-tech startups and creates a natural pathway from investment to strategic partnership to commercial deployment.\n\nThe macro tension in SAEV\'s mandate is fundamental: Saudi Aramco is simultaneously the world\'s largest oil producer (committed to producing hydrocarbons for decades) and a major investor in the technologies that will eventually displace them. SAEV\'s energy transition investments are therefore not altruistic — they represent Aramco\'s attempt to participate financially in the transition while managing the existential risk to its core business. The fund\'s quantum computing and AI investments extend this hedging strategy into technologies whose downstream applications could include faster battery chemistry discovery, more efficient solar cell design, or direct air capture improvements.',

    26: 'Landmark Group\'s macro context reflects the Gulf consumer economy\'s dual character: wealthy GCC nationals and upper-income expatriates who drive luxury demand, and a much larger base of South Asian, Southeast Asian, and African expatriates earning moderate salaries who drive the value fashion market. Landmark\'s portfolio of brands — from premium Centrepoint to ultra-affordable Max Fashion — spans this entire consumer spectrum, making the group less cyclically vulnerable than pure luxury or pure value players.\n\nIndia has emerged as Landmark\'s most significant growth engine. India\'s middle class is expanding at 30-40M households per decade; discretionary spending on clothing and home furnishing is growing at 12-15% annually. Max Fashion\'s positioning in the affordable-premium segment (INR 300-1500 per item) captures the exact income tier experiencing the fastest spending growth. With 500+ stores and 15M+ loyalty program members, Max Fashion India represents a standalone business that could justify a $2-3B valuation at IPO — comparable to Zara India\'s potential market cap.\n\nE-commerce disruption is the existential structural challenge. Amazon, Noon.com, and regional fast-fashion e-commerce players have taken 15-20 percentage points of clothing market share from physical retail over five years. Landmark\'s response — investing in digital capabilities, omnichannel inventory integration, and loyalty programs — is directionally correct but requires sustained capex. The group\'s private ownership (no dividend pressure, long-term reinvestment capacity) is an advantage over listed retail peers in navigating this structural transition.',

    27: 'Future Fund Oman\'s macro context is Oman\'s urgent economic diversification imperative. Unlike Saudi Arabia and the UAE, which have significant runway to manage the energy transition gradually, Oman\'s smaller oil reserves (estimated 5-6 billion barrels) create a harder deadline. At current production rates, Oman\'s conventional oil production will decline meaningfully by 2035-2040 without major new discoveries or EOR (Enhanced Oil Recovery) investments. This timeline compresses the window for successful economic diversification.\n\nOman\'s geographic position — 3,165km of coastline, access to Arabian Sea outside the Strait of Hormuz, proximate to Indian Ocean trade lanes — creates natural competitive advantages in logistics and maritime services that are largely unexploited. The Port of Duqm, positioned as a non-Hormuz alternative for oil export and industrial development, has attracted $8B+ in committed investment from China, South Korea, and European companies. Every additional dollar invested in Duqm creates more Omani employment and tax revenue, reducing dependency on state transfers from depleting oil revenues.\n\nGreen hydrogen represents Future Fund Oman\'s most asymmetric long-term bet. Saudi Arabia and the UAE are pursuing hydrogen aggressively, but Oman\'s combination of low-cost solar irradiation, land availability, coastal access for export, and a government desperate for new revenue streams may enable it to compete on unit economics. If green hydrogen achieves grid parity by 2035 and becomes a globally traded commodity, Oman\'s first-mover infrastructure could generate export revenues comparable to its historical oil income.',

    28: 'Waha Capital occupies a distinctive niche in Abu Dhabi\'s financial ecosystem as the emirate\'s only listed alternative investment company — a publicly traded entity that provides retail and institutional investors with indirect exposure to private markets and credit strategies. This listed structure creates both a competitive advantage (permanent capital, transparent price discovery) and a constraint (quarterly reporting pressure, mark-to-market volatility in alternative assets).\n\nThe AerCap saga defines Waha Capital\'s history and investment DNA. Investing in what became the world\'s largest aircraft lessor — a business that generates highly predictable, contracted cash flows from global airline leases — and generating a 10x+ return taught the firm that patient investment in structurally attractive, cash-generative businesses is its edge. The credit management business extends this philosophy: Abu Dhabi and GCC corporate credit, often investment-grade but with premiums above equivalent Western credits, offers attractive risk-adjusted returns without excessive volatility.\n\nThe macro tailwind for Waha Capital is the deepening of Abu Dhabi\'s financial markets. As ADIA and Mubadala write $1B+ checks into global PE, a gap exists for a smaller, listed vehicle that can access private market returns at $10-100M ticket sizes. Waha Capital\'s ADX listing, Emirati identity, and regulatory familiarity position it to serve Abu Dhabi-based investors who want alternative returns but prefer dealing with a locally domiciled, regulated entity rather than international fund managers.',

    29: 'Gulf Capital Investments operates in the most competitive segment of GCC private equity: the Gulf mid-market, where regional family business succession, Vision 2030 privatization, and technology disruption are creating a continuous pipeline of investable opportunities. Saudi Arabia alone has 30,000+ family-owned businesses, many in the $100M-$1B revenue range, facing second or third-generation succession challenges that create natural PE entry points. The UAE mid-market is similarly active.\n\nAs a newer entrant established in 2023, Gulf Capital Investments\' success depends entirely on differentiated deal sourcing — relationships, sector expertise, or geographic coverage that larger, more established PE firms like Investcorp, Gulf Capital (Abu Dhabi), or international entrants cannot easily replicate. The founders\' GCC family office networks and operating experience appear to be the firm\'s primary sourcing advantage.\n\nThe macro environment for GCC PE is broadly favorable: elevated oil prices support government spending that cascades through the private economy, growing populations create demand for consumer and healthcare services, and Vision 2030 creates structural demand for new industries and services. The risk is execution: GCC PE requires genuine operational capabilities, not just financial engineering, as most targets are family businesses that need management professionalization rather than balance sheet optimization.',

    30: 'Wafra International operates in the shadow of one of Kuwait\'s most complex institutional scandals. The Public Institution for Social Security (PIFSS) — Kuwait\'s equivalent of a pension fund — has faced multiple corruption investigations, with former officials charged with embezzlement. This reputational cloud has constrained Wafra\'s ability to attract third-party capital and limits its strategic flexibility.\n\nThe substantive investment platform, however, is credible and well-established. Wafra\'s New York-based team has built genuine real estate and PE capabilities over 30 years. The US commercial real estate portfolio — focused on institutional-quality office, industrial, and multifamily properties — generates reliable income that funds Kuwait\'s social security obligations. The private equity co-investment program provides exposure to top-tier global buyout returns.\n\nThe macro shift impacting Wafra most significantly is the US commercial real estate correction. Rising interest rates have compressed cap rates and increased financing costs; office vacancy rates have surged post-COVID. Wafra\'s real estate portfolio, concentrated in US commercial assets, has faced valuation headwinds. The industrial and logistics subset is performing strongly (e-commerce-driven demand), but office exposure is a near-term drag. The longer-term outlook depends on whether US work-from-home normalization stabilizes at current levels or reverses toward pre-pandemic office density.',

    31: 'Majid Al Futtaim\'s macro position reflects the thesis that physical retail — properly executed as experiential, entertainment-anchored destinations — is more resilient than pure e-commerce disruption narratives suggest. MAF malls average 97% occupancy in the GCC and 35M+ annual visitors per property; these are not dying retail spaces but community infrastructure anchors in markets where indoor air-conditioned activity is essential for six months per year.\n\nCarrefour is MAF\'s most important strategic asset — a franchise generating $12B+ in annual GMV across 36 countries in the Middle East, Africa, and Central Asia. As a Carrefour franchisee, MAF owns the customer relationship and real estate, while benefiting from Carrefour\'s global sourcing, private label development, and brand investment. The grocery anchor drives 50%+ of all mall foot traffic; every Carrefour visit creates cross-shopping opportunities for the 150-200 specialty retailers in each mall.\n\nThe energy transition creates a material capex requirement for MAF: the group\'s 29 operating malls consume significant electricity for cooling, lighting, and entertainment attractions. MAF has committed to 100% renewable energy across its portfolio by 2030, requiring $500M+ in rooftop solar, battery storage, and grid connection investments. This transition increases near-term capex but reduces long-term energy cost exposure and improves the portfolio\'s sustainability credentials — important for both insurance pricing and international LP interest in MAF\'s debt securities.',

    32: 'Al Gurg Group\'s macro environment is Dubai\'s transition from a trading hub to an integrated services and professional economy. The group\'s origins in FMCG distribution — representing Reckitt & Benckiser and Unilever across the UAE — reflect Dubai\'s historical role as a re-export gateway for consumer goods heading to Iran, Afghanistan, Pakistan, and East Africa. This trade flow has been disrupted by sanctions regimes and direct supplier-consumer connectivity, squeezing traditional distribution margins.\n\nThe second-generation leadership under Hana Al Gurg has repositioned the group toward higher-value-add activities: branded real estate development, healthcare delivery, and professional services. This pivot reflects the broader Emirati family business challenge of migrating from distribution (low capital intensity, high relationships) to asset ownership (high capital intensity, more defensible). Al Gurg Group\'s real estate portfolio — prime Deira and Bur Dubai commercial properties — has appreciated dramatically as Dubai\'s urbanization intensifies.\n\nHana Al Gurg\'s role as a public figure in UAE business — she serves on multiple government advisory boards, speaks internationally on women\'s economic empowerment, and is a UAE soft power asset — creates intangible value for the group\'s brand. Government contracts, preferred real estate allocations, and joint venture opportunities flow more readily to groups whose leadership has demonstrated alignment with national development priorities. This soft influence is a structural advantage that pure financial metrics do not capture.',

    33: 'Gulf Capital operates in a GCC private equity market that has matured dramatically since the firm\'s 2006 founding. The early years were characterized by deal scarcity, limited exit options, and high valuation expectations from family business sellers. Today, Saudi Arabia alone has Tadawul Nomu small-cap listings, PE-to-PE secondaries, and strategic acquisitions by multinationals — multiple viable exit pathways that have dramatically improved IRR potential for well-executed buyouts.\n\nGulf Capital\'s private credit platform is the firm\'s most strategically distinctive product. The GCC faces a structural private credit gap: regional banks are reluctant to lend to growth-stage businesses without 5+ years of audited accounts and hard asset collateral; international credit funds prioritize larger deals in more liquid markets. Gulf Capital Credit Partners fills this gap with $10-50M loans to GCC mid-market companies, earning 12-15% returns in an asset class with limited institutional competition.\n\nThe primary macro risk to Gulf Capital\'s model is geopolitical. A Gulf conflict, Iranian nuclear escalation, or regional political instability would simultaneously constrain deal activity, dampen exit markets, and potentially trigger portfolio company distress. The firm\'s geographic diversification across UAE, Saudi Arabia, and increasingly North Africa provides some protection, but GCC-focused PE will always carry an embedded regional concentration risk that global PE vehicles do not.',

    34: 'Saudi Venture Capital Company (SVC) serves as the government\'s most direct intervention tool in the Saudi startup ecosystem — functioning as a catalytic LP that anchors fund formation and signals government commitment to the VC model. Without SVC, many Saudi-focused VC funds would not have achieved first close; the government anchor is frequently the critical investor that unlocks private capital co-investment.\n\nThe macro thesis underpinning SVC\'s existence is that Saudi Arabia\'s hydrocarbon-dependent economic model requires diversification into knowledge-based industries. Startups are the seed corn of this transformation. A startup that raises $2M in 2022, grows to $50M revenue by 2026, employs 200 Saudis, and eventually IPOs on Tadawul, converts oil-generated government capital (via SVC) into a permanent, non-oil economic asset.\n\nSVC\'s macro challenge is demonstrating financial returns alongside economic development impact. If the fund generates only 1.0x DPI while catalyzing ecosystem development, it will be difficult to justify continued government investment at scale. The fund\'s recent exits — several portfolio companies acquired by Saudi corporates at 2-3x invested capital — are encouraging early signals. As the first vintage of Saudi VC-backed companies enters the 5-7 year exit window (2024-2027), SVC\'s realized returns will become the definitive evidence of whether the model is working.',

    35: 'STV occupies a unique institutional position in Saudi Arabia\'s technology ecosystem: it is simultaneously a financial VC fund, a Saudi Telecom strategic vehicle, and a post-Abdulrahman Tarabzouni-era institution navigating a significant leadership transition. Tarabzouni\'s appointment as STC CEO in 2021 elevated STV\'s brand (an STC CEO ran the fund — ultimate validation) but also created a governance gap that required careful succession management.\n\nSaudi Arabia\'s tech ecosystem is now large enough to generate top-quartile VC returns independently of regional indices. Jahez (food delivery) listed on Nomu in 2022 at a $1.5B valuation; Foodics (restaurant tech) raised at $1B+ valuation; Salla (e-commerce infrastructure) expanded across MENA. The next wave — AI-native Saudi companies built on Aramco\'s open dataset APIs, HUMAIN\'s sovereign AI platform, and Saudi Cloud computing infrastructure — represents STV\'s core 2024-2030 thesis.\n\nThe structural macro advantage for STV is STC\'s enterprise distribution: 4M+ business customers across Saudi Arabia who need technology solutions and can be natural pilots, design partners, and distribution channels for STV portfolio companies. A SaaS startup selling to Saudi enterprises gains an enormous sales force advantage by having STC as both an investor and a committed go-to-market partner. This distribution moat is STV\'s most defensible competitive advantage over international VCs entering Saudi Arabia.',

    36: 'Jada Fund of Funds represents PIF\'s deliberate attempt to build a sustainable private capital ecosystem in Saudi Arabia rather than simply deploying capital directly. By funding VC and PE fund managers rather than individual startups, Jada creates institutional infrastructure — investment firms, talent pipelines, governance frameworks, LP networks — that would take decades to develop organically.\n\nThe multiplier effect is significant: every SAR 1 committed by Jada as a cornerstone LP typically attracts SAR 3-5 from international LPs who see government anchor commitment as a risk reduction signal. Over five years, Jada\'s SAR 5B+ in commitments has catalyzed an estimated SAR 15-20B+ in total fund formation. The Saudi VC ecosystem grew from 5-10 active funds in 2018 to 50+ in 2024 — Jada\'s catalytic role was essential.\n\nThe longer-term challenge for Jada is managing the transition from catalytic government LP to mature ecosystem participant. As the Saudi VC market develops its own track record and private LPs gain confidence, Jada\'s role should naturally shift from anchor LP (providing critical first capital) to follow-on LP (participating in proven managers\' subsequent funds at market terms). This transition requires deliberately stepping back from the dominant LP position that distorts market dynamics, while continuing to provide capital to underdeveloped market segments.',

    37: 'Riyad Capital\'s macro context is identical in structure to Al Rajhi Capital\'s and SNB Capital\'s: all three benefit from Saudi Arabia\'s deepening capital markets and the Vision 2030 privatization pipeline. The key differentiator is Riyad Bank\'s specific client franchise. Riyad Bank has a strong mid-corporate and government-affiliated entity client base; Riyad Capital\'s investment banking revenues are therefore more concentrated in government-adjacent transactions (infrastructure bonds, government entity IPOs) than Al Rajhi Capital\'s predominantly retail franchise.\n\nRiyad Capital\'s private wealth management ambitions are the most strategically interesting dimension of its growth plan. Saudi Arabia\'s UHNW population — estimated at 3,000+ individuals with $30M+ in investable assets — is growing rapidly as Vision 2030 creates billionaires through asset privatization, sports franchise ownership, and real estate development. These individuals need sophisticated investment management: family governance, trust structures, international portfolio management, and succession planning. Riyad Capital, with a Saudi-first client focus and Riyad Bank\'s trusted brand, is positioned to build this business.\n\nThe primary structural risk is disintermediation. International private banks (Goldman Sachs, UBS, Morgan Stanley) have all opened Riyadh offices, targeting exactly the same UHNW Saudi clients. These banks bring global investment access, research depth, and brand prestige that Riyad Capital cannot easily match. Riyad Capital\'s competitive response must be rooted in local regulatory expertise, Arabic-language advisory, and deep understanding of Saudi family dynamics — advantages that will prove durable only if the firm invests seriously in talent and product development.',

    38: 'Sanabil Investments is arguably the most globally connected entity in the Saudi investment ecosystem, with LP relationships at every major US VC fund and direct deal access to hundreds of the world\'s highest-growth technology companies. This positioning reflects PIF\'s realization that participating in Silicon Valley\'s value creation required a dedicated, institutional presence — not ad-hoc direct investments but sustained relationships with the best fund managers over multiple fund cycles.\n\nThe macro significance of Sanabil extends beyond financial returns. As the predominant Saudi institutional presence in US venture capital, Sanabil creates information flows — market intelligence, technology assessments, talent networks — that flow back to PIF and ultimately inform Saudi national technology strategy. HUMAIN\'s decision to focus on sovereign AI infrastructure was likely informed by Sanabil\'s assessments of OpenAI, Anthropic, and other AI platform companies from its LP vantage point.\n\nSanabil\'s challenge is scale efficiency. At $7.5B AUM and $1B+ annual deployment, the fund is large enough to have market impact but small enough that its portfolio is still primarily LP stakes in other managers\' funds rather than direct ownership of technology companies. The strategic question for the next phase is whether Sanabil scales primarily through more LP commitments or shifts toward larger direct co-investments that give PIF more strategic control over portfolio companies. The Electronic Arts acquisition model (PIF direct, $55B) suggests the latter direction is gaining favor at the PIF parent level.',

    39: 'MEVP\'s macro context is inseparable from Lebanon\'s catastrophic economic collapse. Beirut was once the "Paris of the Middle East" and a natural hub for Arab business sophistication, entrepreneurship, and financial services. The 2019-2022 economic crisis — bank deposit freezes, currency devaluation of 95%+, Beirut port explosion — destroyed Lebanon\'s financial ecosystem and forced a painful diaspora of talent and capital.\n\nMEVP\'s survival and growth despite this disaster reflects the firm\'s deliberate geographic diversification strategy. By establishing its Dubai hub early and building GCC LP relationships, MEVP was not destroyed by Lebanon\'s collapse — it adapted. The firm\'s Lebanese DNA, however, remains a competitive asset: Lebanese entrepreneurs are disproportionately represented across MENA tech founding teams, and MEVP\'s network of Lebanese diaspora founders creates deal flow that Emirati or Saudi-origin VCs cannot easily access.\n\nThe medium-term macro question for MEVP is whether Lebanon\'s political and economic reconstruction — potentially enabled by offshore gas discoveries in Block 9 of the Levantine Basin — could revitalize the Lebanese venture ecosystem. A recovered Lebanese economy would restore MEVP\'s home market and provide a low-cost, educated talent base for technology company formation. But the timeline is deeply uncertain given Lebanon\'s political dysfunction, and MEVP\'s strategy wisely does not depend on a Beirut recovery.',

    40: 'TVM Capital Healthcare operates in one of the most structurally robust macro environments in global private equity: MENA healthcare. The GCC region has some of the highest per-capita healthcare spending globally — Qatar and UAE rank among top-10 worldwide — driven by affluent populations, strong government insurance mandates, and a high prevalence of lifestyle diseases (diabetes, cardiovascular disease) associated with sedentary, high-calorie consumption patterns.\n\nSaudi Arabia\'s healthcare privatization is the largest structural opportunity in TVM\'s investment universe. The Kingdom has committed to privatizing 290+ government hospitals and thousands of primary care centers, creating investable assets in a market with 35M+ potential patients and government insurance coverage for most of the population. The economics of a private Saudi hospital are attractive: high occupancy (8-9 beds per 1,000 population nationally, but primary concentration in Riyadh and Jeddah creates supply constraints), government payer reliability, and 12-18% operating margins for well-run facilities.\n\nDigital health is TVM\'s most important strategic evolution. The COVID-19 pandemic collapsed 10 years of telemedicine regulatory resistance in 12 months. Saudi Arabia\'s MOH now fully reimburses telemedicine consultations; UAE\'s DHA has licensed 50+ telemedicine platforms. AI diagnostics, remote monitoring, and digital pathology are converting high-fixed-cost hospital infrastructure into lower-cost distributed care models. TVM\'s Fund III thesis — AI-enabled diagnostics and smart hospital management systems — positions the firm to capture this transition.',

    41: 'Shorooq Partners\' macro context reflects Abu Dhabi\'s emergence as MENA\'s preeminent startup ecosystem. Hub71\'s $535M incentive program, ADGM\'s progressive regulatory framework, and the UAE\'s post-COVID HNW immigration boom have collectively made Abu Dhabi a genuine competitor to Dubai for early-stage technology company formation. Shorooq\'s positioning in Abu Dhabi — before the city\'s startup ecosystem reached critical mass — mirrors Sequoia\'s early presence in Silicon Valley: arrive early, build relationships while competition is low, reap outsized returns as the ecosystem scales.\n\nThe Tamara investment validates Shorooq\'s cross-border thesis. By investing early in a Saudi-focused BNPL company from its Abu Dhabi base, Shorooq demonstrated that UAE-domiciled VCs can access Saudi deal flow and generate Saudi-level returns without requiring Riyadh presence. As Saudi Arabia\'s startup ecosystem has grown — now 600+ active startups, $5B+ raised in 2023 — Shorooq\'s existing Saudi relationships from early investments provide a sustained sourcing advantage.\n\nThe structural challenge for Shorooq as it scales is maintaining pre-seed and seed discipline while fund size grows. At $500M AUM, the natural temptation is to write larger checks into later-stage companies where capital deployment is faster. But Shorooq\'s returns were generated at the earliest stage; institutional pressure to deploy larger checks efficiently may dilute the investment strategy that created its brand. Managing this tension — staying early while scaling the fund — is the defining strategic challenge of Shorooq\'s next decade.',

    42: 'Wamda Capital\'s Careem investment stands as the definitive proof of concept for MENA venture capital. When Wamda co-led Careem\'s Series C in 2016 alongside BECO Capital, most global investors dismissed the Middle East as a "small market with no tech exit history." Uber\'s $3.1B acquisition in 2019 — at the time the largest tech acquisition in MENA history — permanently altered this perception. Wamda\'s Careem returns funded a second fund, attracted institutional LPs, and established the firm as a credible, senior voice in the MENA technology ecosystem.\n\nWamda\'s dual mandate — VC returns plus ecosystem development — creates a strategic positioning that is differentiated from pure financial VCs but also more complex to execute. The Wamda media platform and entrepreneurship programs generate deal flow and brand value but consume organizational bandwidth that could otherwise focus on investment decisions. This tension between platform and fund is not unique to Wamda (Andreessen Horowitz has the same challenge at much larger scale), but the resolution — platform subsidiary, fund as primary P&L — requires deliberate organizational design.\n\nThe climate tech pivot is Wamda\'s most strategically significant thesis evolution. MENA\'s physical climate vulnerability — water scarcity, extreme heat, sea level risk — and the region\'s enormous renewable energy potential create a concentrated market for climate technology solutions. Solar desalination, heat-resilient agricultural technology, smart building management, and waste-to-value systems all address large, addressable problems in the MENA market. Wamda\'s established LP base and founder network position it to credibly lead this new chapter without abandoning its core MENA technology franchise.',

    43: 'NEOM Investment Fund occupies perhaps the most conceptually interesting position in GCC institutional investing: it is simultaneously a sovereign development fund, a corporate venture capital vehicle, and a city-state incubator. No comparable institution exists anywhere in the world. NEOM itself — a $500B (now revised $200B near-term) giga-project spanning 26,500 km² of Saudi Arabia\'s northwest — is attempting to build from scratch a city incorporating technologies that don\'t yet exist at commercial scale: pneumatic delivery networks, autonomous transit, AI-managed urban systems, and 100% renewable energy generation.\n\nThe budget revision from $500B to ~$200B near-term reflects a necessary reality check. Building THE LINE to its full 170km dimension by 2030 was always an extraordinary engineering challenge; the revised Phase 1 target (2.4km of THE LINE by 2030) is more achievable but dramatically reduces the near-term investment opportunity. NIF\'s portfolio companies must now demonstrate relevance beyond NEOM — either addressing global smart city markets or finding applications within other Saudi mega-projects (Red Sea, Qiddiya, Diriyah).\n\nThe most commercially promising aspect of NEOM\'s technology investment is the hydrogen opportunity. NEOM\'s NEOM Green Hydrogen Company (NGHC) — a joint venture of ACWA Power, Air Products, and NEOM — is developing the world\'s largest green hydrogen facility (4GW of renewables, 600 tonnes/day of green ammonia). NIF\'s positioning within this value chain creates exposure to the clean hydrogen export opportunity that could, if hydrogen achieves cost parity by 2030-2035, generate revenues comparable to Saudi Arabia\'s historical oil income.',

    44: 'ADQ\'s macro context mirrors Mubadala\'s in strategic intent — transforming Abu Dhabi from a hydrocarbon producer to a diversified economy — but operates through the specific lens of critical sector resilience. COVID-19 was ADQ\'s defining strategic catalyst: the pandemic demonstrated that supply chain concentration in food, healthcare supplies, and logistics created catastrophic vulnerabilities for small, import-dependent states like Abu Dhabi. ADQ\'s portfolio is the institutional response: control of food chains (Al Dahra\'s $5B+ agricultural operations in 20 countries), healthcare capacity (Pure Health\'s 100+ facilities), and logistics infrastructure (Abu Dhabi Ports\'s 33-port global network).\n\nADQ\'s Egypt investment strategy is its most geopolitically complex operation. Egypt is the Arab world\'s most populous country (105M people) but faces chronic foreign exchange shortages, high inflation, and fiscal fragility. ADQ\'s $2B+ deployment into Egyptian agriculture, financial services, and infrastructure is simultaneously a financial investment and a geopolitical stabilization tool. A financially unstable Egypt creates migration pressures, Islamic extremism risks, and regional security challenges for UAE directly. ADQ\'s Egyptian investments therefore carry a strategic return that is not captured in financial IRR calculations.\n\nThe green hydrogen dimension is critical for understanding ADQ\'s 2030 profile. The UAE has committed to net-zero emissions by 2050; ADQ\'s energy portfolio must transition from fossil-fuel-adjacent infrastructure (ADNOC Distribution, industrial facilities) toward renewable energy and green hydrogen. ADQ\'s green hydrogen investments at Masdar City and the UAE-Jordan renewable energy projects represent the institutional framework for this transition.',

    45: 'STC Ventures\' macro context flows directly from Saudi Arabia\'s 5G telecommunications buildout and the resulting digital transformation of Saudi enterprises. STC Group has invested $10B+ in 5G network infrastructure, creating the connectivity layer that enables IoT, smart manufacturing, telemedicine, and AI-driven services at scale. STC Ventures\' portfolio companies are the application layer above this infrastructure — the startups capturing the economic value that 5G connectivity enables.\n\nThe Saudi enterprise software market is at an early but explosive growth stage. Most large Saudi corporations still run legacy ERP systems (SAP, Oracle) with minimal AI integration, minimal API connectivity, and minimal cloud migration. The compliance requirements of Vision 2030\'s Saudization mandates, ESG reporting, and localization targets are forcing digital transformation. Saudi SaaS companies addressing these specific compliance and localization needs — Foodics (restaurant management), Salla (e-commerce), Khazenly (logistics) — serve a captive market that global SaaS providers cannot easily address without local adaptation.\n\nSTC Ventures\' ultimate strategic value to STC Group is intelligence: by being an early investor in companies that may eventually become STC customers, partners, or acquisition targets, STC Ventures provides optionality that pure return-seeking VC cannot. An investment in a Saudi cybersecurity startup may return 5-10x financially; its strategic value — securing STC\'s enterprise network, providing technology that could be white-labeled for STC\'s enterprise customers — could be worth multiples of the financial return.',

    46: 'Taqnia\'s macro context is Saudi Arabia\'s most strategically sensitive economic policy: defense industry localization. The Kingdom has historically spent $80-90B annually on defense procurement — making it the world\'s fifth-largest defense spender — with over 95% of this capital leaving the country as imports from the US, UK, France, and China. The Vision 2030 target of 50% localization by 2030 represents a $40-45B annual demand shift toward domestically produced defense technology and equipment.\n\nThe geopolitical timing is optimal for Taqnia\'s mission. US-Saudi security relationships, while durable, have experienced friction over oil pricing, Yemen, and human rights concerns. Saudi Arabia is deliberately diversifying its defense supply chain — Chinese drones, South Korean artillery, European missile systems — to reduce dependence on any single partner. This diversification creates space for a Saudi domestic defense industry that serves both local procurement needs and potential regional export markets.\n\nThe technological challenge is formidable: Saudi Arabia has limited indigenous aerospace and defense engineering talent relative to the ambition level. Taqnia\'s strategy — creating joint ventures with international defense companies that require technology transfer as a condition of market access — is the same playbook used successfully by South Korea (with US partners), Turkey (with European partners), and Brazil (with joint ventures across Embraer). The timeline to meaningful localization is 10-20 years, not the 5-year political cycle, requiring sustained institutional commitment that Taqnia\'s PIF parentage should provide.',

    47: 'Hub71\'s macro context is the broader competition among global innovation hubs for startup talent, capital, and ecosystem density. In 2019, Abu Dhabi\'s startup ecosystem was nascent — perhaps 100 active startups and minimal institutional VC presence. Singapore, London, and Tel Aviv dominated as the top non-US destinations for technology talent and capital. Hub71\'s $535M incentive package and co-location model (free offices + housing + healthcare) was designed to directly compete with these hubs for the marginal startup that might otherwise choose Singapore or London.\n\nThe model has succeeded beyond initial expectations. Hub71 hosted 350+ startups from 50+ countries by 2024, collectively raising $2B+ in external funding. The key success factor was not just the subsidies — many other hubs offer similar programs — but the strategic LPs: Mubadala, Microsoft, and SoftBank as Hub71 corporate partners meant that portfolio companies had direct access to $1T+ in combined investment capacity. A startup in Hub71 can potentially sell to Mubadala\'s portfolio companies, license technology to Microsoft Azure, and raise growth capital from SoftBank\'s Vision Fund.\n\nThe strategic imperative for Hub71\'s next phase is transitioning from incentive-dependent ecosystem (startups stay for the subsidies) to organically attractive ecosystem (startups stay because the best investors, talent, and corporate clients are here). This transition requires a critical mass of successful exits generating angel investor networks, founder talent recycling into new startups, and a cultural shift in Abu Dhabi toward risk tolerance and entrepreneurial identity. The first major Hub71 exits are beginning to emerge; the ecosystem is approaching the inflection point where organic momentum can sustain growth without unlimited government subsidy.',

    48: 'BECO Capital\'s macro context is the maturation cycle of MENA VC. When BECO was founded in 2012, the MENA startup ecosystem was embryonic: fewer than 50 funded startups regionally, no unicorn exits, and minimal LP interest from institutional investors. BECO\'s Careem investment — made with a $500K seed check when most investors dismissed MENA as too small — was contrarian investing in the fullest sense.\n\nThe Careem exit fundamentally transformed MENA VC\'s institutional credibility. Before 2019, MENA VC was essentially excluded from global LP portfolios because there was no evidence of exit liquidity or fund-level returns. After Uber\'s $3.1B acquisition — demonstrating that MENA tech companies can achieve Western unicorn valuations and exit to global strategic acquirers — institutional capital began flowing seriously into the region. BECO benefited directly: Fund II LPs included international endowments and pension funds that would not have considered MENA before Careem.\n\nThe strategic challenge for BECO in its third fund is maintaining early-stage conviction as competition intensifies. With international mega-VCs (Sequoia, a16z, Tiger Global) all establishing MENA presence post-Careem, the best Series A and B opportunities face competitive term sheets from global brands with deeper pockets. BECO\'s competitive advantage must remain at the pre-seed and seed stages — where its brand, founder relationships, and local market knowledge still dominate — even as the temptation to deploy larger checks at later stages grows with fund size.',

    49: 'Global Ventures\' macro context is the African technology investment opportunity — arguably the most underfunded large market in global VC. Sub-Saharan Africa has 1.3B people, median age 19, 600M mobile subscribers, and $5T+ in annual economic activity, yet receives less than 1% of global VC deployment. The structural barriers to African VC are real: currency risk, regulatory fragmentation, infrastructure gaps, and exit market immaturity. But these same barriers mean that capital-efficient, mobile-native business models can achieve dominant market positions with $10-30M of capital that would be insufficient for equivalent European or US markets.\n\nGlobal Ventures\' Dubai base is strategically valuable for the Africa thesis. Dubai is the primary financial hub connecting Gulf capital to African investment opportunities — Emirati sovereign funds (ADQ, Mubadala) are actively deploying in African infrastructure and agriculture, creating partnership opportunities for Global Ventures as a deal originator and local market expert. The firm\'s ability to provide Gulf institutional LPs with managed African exposure — without requiring them to build their own African teams — creates a structural commercial advantage.\n\nThe multi-geography model (MENA + Africa + South/Southeast Asia) is both a strength and a challenge. It provides diversification that MENA-only VCs lack — if Gulf VC cycles down, African fintech may be at a different point in its cycle. But it requires deep expertise across four fundamentally different market contexts, which demands a larger team and creates execution risks that more focused managers avoid.',

    50: 'Nuwa Capital\'s macro context is the pre-seed gap in MENA venture capital. Despite significant progress in Series A and B funding, the earliest stages of company formation — the $250K-$2M range where a founder needs seed capital to build a product, hire a small team, and find the first customers — remained dramatically underfunded. International seed funds avoided MENA due to limited local market knowledge; regional VCs focused on larger, more visible rounds. Nuwa was explicitly designed to fill this institutional void.\n\nThe founders\' ex-BECO pedigree is Nuwa\'s most important asset. In MENA venture, brand provenance matters enormously: founders raising their first institutional round make funding decisions based heavily on investor reputation, network access, and advisory quality. Knowing that Nuwa\'s partners backed Careem from the very beginning — and have mentored the generation of founders who built MENA\'s first tech wave — creates a deal flow advantage that capital alone cannot generate.\n\nSaudi Arabia\'s pre-seed ecosystem is Nuwa\'s most significant growth opportunity. The Kingdom\'s startup count has grown 10x in six years, from ~60 in 2017 to 600+ in 2024. The majority of these companies are at the pre-seed or seed stage, requiring exactly the $250K-$2M checks that Nuwa provides. Saudi Arabia\'s large domestic market (35M consumers), Vision 2030\'s structural demand creation, and the MISA (Ministry of Investment) regulatory reform agenda all create favorable conditions for startup formation at a pace that will generate 10+ Nuwa-eligible opportunities per month by 2026.',
}

# ─────────────────────────────────────────────────────────────────────────────
# PASS 1 + 2: Inject timelineEvents arrays into deepProfiles for funds 11-50
# Strategy: find each fund's closing brace in deepProfiles and insert before it
# ─────────────────────────────────────────────────────────────────────────────

def json_timeline(entries):
    """Convert timeline entries to compact JS array literal."""
    parts = []
    for e in entries:
        year = e['year'].replace("'", "\\'")
        event = e['event'].replace("'", "\\'").replace('\n', ' ')
        parts.append("      {year: '" + year + "', event: '" + event + "'}")
    return "[\n" + ",\n".join(parts) + "\n    ]"

def inject_timeline_events(html, rank, entries):
    """Find the block for deepProfiles[rank] and insert timelineEvents."""
    # Find the exact pattern: "  {rank}: {" up to its closing "},"  or "};"
    # We look for the relatedFunds line (last field) and insert after it
    # Pattern: find "  {rank}: {" then find the matching "relatedFunds: [...]"
    # then insert timelineEvents after the relatedFunds line

    # Use a marker: find the rank's relatedFunds line
    # relatedFunds line looks like: "    relatedFunds: [1, 6, 12, 16]"
    # We want to insert after that line's closing bracket

    # Find the start of this fund's block
    rank_pattern = f'\n  {rank}: {{'
    rank_pos = html.find(rank_pattern)
    if rank_pos == -1:
        print(f"WARNING: Could not find rank {rank} in deepProfiles")
        return html

    # Find the next rank's start or end of deepProfiles, to scope our search
    # Find relatedFunds within this block
    search_start = rank_pos
    # Find next rank block or end of deepProfiles
    next_rank_candidates = []
    for r in range(1, 51):
        if r == rank:
            continue
        npos = html.find(f'\n  {r}: {{', search_start + 1)
        if npos > search_start:
            next_rank_candidates.append(npos)

    if next_rank_candidates:
        block_end = min(next_rank_candidates)
    else:
        block_end = html.find('};', search_start) + 2

    block = html[rank_pos:block_end]

    # Check if timelineEvents already exists
    if 'timelineEvents:' in block:
        print(f"  Rank {rank}: timelineEvents already present, skipping")
        return html

    # Find relatedFunds in this block to insert after it
    rf_pos = block.rfind('relatedFunds:')
    if rf_pos == -1:
        print(f"WARNING: No relatedFunds in rank {rank}")
        return html

    # Find the end of the relatedFunds line (closing bracket + newline)
    rf_end = block.find('\n', rf_pos)
    if rf_end == -1:
        rf_end = len(block)

    # Build insertion
    timeline_js = json_timeline(entries)
    insertion = f',\n    timelineEvents: {timeline_js}'

    # Insert after relatedFunds line
    new_block = block[:rf_end] + insertion + block[rf_end:]
    html = html[:rank_pos] + new_block + html[rank_pos + len(block):]

    print(f"  Rank {rank}: inserted {len(entries)} timeline events")
    return html


# ─────────────────────────────────────────────────────────────────────────────
# PASS 3: Inject enhanced macroContext for funds 11-50
# Replace existing macroContext strings with richer versions
# ─────────────────────────────────────────────────────────────────────────────

def escape_js_string(s):
    """Escape a string for use in a JS single-quoted string."""
    return s.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ')

def inject_macro_context(html, rank, new_context):
    """Replace macroContext for this fund rank."""
    # Find the fund's block
    rank_pattern = f'\n  {rank}: {{'
    rank_pos = html.find(rank_pattern)
    if rank_pos == -1:
        print(f"WARNING: Could not find rank {rank}")
        return html

    # Find next rank or end
    next_rank_candidates = []
    for r in range(1, 51):
        if r == rank:
            continue
        npos = html.find(f'\n  {r}: {{', rank_pos + 1)
        if npos > rank_pos:
            next_rank_candidates.append(npos)

    if next_rank_candidates:
        block_end = min(next_rank_candidates)
    else:
        block_end = html.find('};', rank_pos) + 2

    block = html[rank_pos:block_end]

    # Find macroContext in this block
    mc_pos = block.find("macroContext: '")
    if mc_pos == -1:
        print(f"  Rank {rank}: no macroContext found, skipping")
        return html

    # Find the end of this string value (closing ' not preceded by \)
    val_start = mc_pos + len("macroContext: '")
    i = val_start
    while i < len(block):
        if block[i] == "'" and block[i-1] != '\\':
            break
        i += 1
    val_end = i  # position of closing quote

    escaped = escape_js_string(new_context)
    new_block = block[:mc_pos] + "macroContext: '" + escaped + "'" + block[val_end + 1:]
    html = html[:rank_pos] + new_block + html[rank_pos + len(block):]

    print(f"  Rank {rank}: macroContext updated ({len(new_context)} chars)")
    return html


# ─────────────────────────────────────────────────────────────────────────────
# PASS 4: Co-investments scan
# Extract all investment names from the funds[] array, find duplicates
# Inject as a JS object coInvestments{} into the script
# ─────────────────────────────────────────────────────────────────────────────

def build_co_investments(html):
    """Scan all investment names in funds[] and find cross-fund duplicates."""
    import re

    # Extract all investment entries: {name:'...', sector:'...', ...}
    # Pattern: name:'value'
    inv_pattern = re.compile(r"\{name:'([^']+)',sector:'([^']+)'[^}]*,year:(\d+)")

    # Also match rank for context - find rank: N, then within investments: [...]
    # Strategy: find each fund block in funds[] and extract rank + investment names

    # Find funds array
    funds_start = html.find('var funds = [')
    funds_end = html.find('];', funds_start) + 2
    funds_section = html[funds_start:funds_end]

    # Extract rank + investments for each fund
    fund_blocks = re.split(r'\{rank:', funds_section)

    # Map investment_name -> list of ranks
    inv_to_ranks = {}

    for block in fund_blocks[1:]:  # skip first empty
        # Get rank
        rank_match = re.match(r'(\d+)', block)
        if not rank_match:
            continue
        rank = int(rank_match.group(1))

        # Get investments section
        inv_section_match = re.search(r'investments:\[(.*?)\]', block, re.DOTALL)
        if not inv_section_match:
            continue
        inv_section = inv_section_match.group(1)

        # Extract investment names (normalize them)
        names = re.findall(r"name:'([^']+)'", inv_section)
        for name in names:
            # Normalize: lowercase, strip amounts in parens
            norm = re.sub(r'\s*\([^)]*\)', '', name).strip()
            norm_key = norm.lower()
            if norm_key not in inv_to_ranks:
                inv_to_ranks[norm_key] = {'name': norm, 'ranks': []}
            if rank not in inv_to_ranks[norm_key]['ranks']:
                inv_to_ranks[norm_key]['ranks'].append(rank)

    # Filter to only cross-fund (2+ funds)
    co_investments = {k: v for k, v in inv_to_ranks.items() if len(v['ranks']) >= 2}

    print(f"\nPass 4: Found {len(co_investments)} cross-fund investments")
    for k, v in sorted(co_investments.items(), key=lambda x: -len(x[1]['ranks'])):
        print(f"  {v['name']}: funds {v['ranks']}")

    return co_investments


def inject_co_investments(html, co_investments):
    """Inject coInvestments object into the script."""
    # Build the JS object
    lines = ["var coInvestments = {"]
    for k, v in sorted(co_investments.items()):
        name_escaped = v['name'].replace("'", "\\'")
        ranks_str = str(v['ranks'])
        lines.append(f"  '{name_escaped}': {ranks_str},")
    lines.append("};")
    co_inv_js = "\n".join(lines)

    # Check if already exists
    if 'var coInvestments' in html:
        # Replace existing
        co_start = html.find('var coInvestments')
        co_end = html.find('\n};', co_start) + 3
        html = html[:co_start] + co_inv_js + html[co_end:]
        print("  Replaced existing coInvestments object")
    else:
        # Insert after crossFundInvestments if it exists, else before enhancedProfiles
        insert_after = html.find('var crossFundInvestments')
        if insert_after == -1:
            insert_after = html.find('var enhancedProfiles')

        # Find end of that block
        block_end = html.find('\n};', insert_after) + 3
        html = html[:block_end] + '\n\n' + co_inv_js + html[block_end:]
        print("  Injected new coInvestments object")

    return html


# ─────────────────────────────────────────────────────────────────────────────
# PASS 5: Investment filter/sort UI
# Add filter/sort controls to the investment table in openReport()
# ─────────────────────────────────────────────────────────────────────────────

FILTER_SORT_CSS = """
.inv-filter-bar{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;align-items:center}
.inv-filter-select{padding:6px 10px;border:1px solid var(--border);border-radius:var(--radius-sm);font-size:11px;font-family:inherit;background:var(--surface);color:var(--text-primary);cursor:pointer}
.inv-filter-select:focus{outline:none;border-color:var(--accent)}
.inv-filter-label{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--text-tertiary)}
"""

FILTER_SORT_HTML_INJECT = """// Investment filter bar
    h+='<div class="inv-filter-bar">';
    h+='<span class="inv-filter-label">Filter:</span>';
    h+='<select class="inv-filter-select" id="invSectorFilter" onchange="filterInvestmentTable()"><option value="">All Sectors</option>';
    var invSectors=[...new Set(f.investments.map(function(i){return i.sector}))].sort();
    invSectors.forEach(function(s){h+='<option value="'+s+'">'+s+'</option>';});
    h+='</select>';
    h+='<span class="inv-filter-label" style="margin-left:8px">Sort:</span>';
    h+='<select class="inv-filter-select" id="invSortKey" onchange="filterInvestmentTable()"><option value="default">Default</option><option value="sector">Sector</option><option value="year-asc">Year (oldest)</option><option value="year-desc">Year (newest)</option><option value="name">Name A-Z</option></select>';
    h+='</div>';"""

FILTER_SORT_FUNCTION = """
function filterInvestmentTable(){
  try{
    var sectorEl=document.getElementById('invSectorFilter');
    var sortEl=document.getElementById('invSortKey');
    if(!sectorEl||!sortEl)return;
    var sector=sectorEl.value;
    var sortKey=sortEl.value;
    var tbody=document.querySelector('.investment-table tbody');
    if(!tbody)return;
    var rows=Array.from(tbody.querySelectorAll('tr'));
    // Filter
    rows.forEach(function(r){
      var rs=r.getAttribute('data-sector')||'';
      r.style.display=(sector===''||rs===sector)?'':'none';
    });
    // Sort
    var visible=rows.filter(function(r){return r.style.display!=='none'});
    if(sortKey==='sector'){
      visible.sort(function(a,b){return (a.getAttribute('data-sector')||'').localeCompare(b.getAttribute('data-sector')||'')});
    } else if(sortKey==='year-asc'){
      visible.sort(function(a,b){return parseInt(a.getAttribute('data-year')||0)-parseInt(b.getAttribute('data-year')||0)});
    } else if(sortKey==='year-desc'){
      visible.sort(function(a,b){return parseInt(b.getAttribute('data-year')||0)-parseInt(a.getAttribute('data-year')||0)});
    } else if(sortKey==='name'){
      visible.sort(function(a,b){return (a.cells[0]?a.cells[0].textContent:'').localeCompare(b.cells[0]?b.cells[0].textContent:'')});
    }
    if(sortKey!=='default'){
      visible.forEach(function(r){tbody.appendChild(r)});
    }
  }catch(e){console.error('filterInvestmentTable:',e)}
}"""

TIMELINE_RENDER_FUNCTION = """
function renderTimelineEvents(events){
  if(!events||!events.length)return '';
  var h='<div class="timeline-events-container">';
  events.forEach(function(e){
    h+='<div class="timeline-event-row">';
    h+='<div class="timeline-event-year">'+e.year+'</div>';
    h+='<div class="timeline-event-line"></div>';
    h+='<div class="timeline-event-text">'+e.event+'</div>';
    h+='</div>';
  });
  h+='</div>';
  return h;
}"""

TIMELINE_CSS = """
.timeline-events-container{display:flex;flex-direction:column;gap:0}
.timeline-event-row{display:grid;grid-template-columns:48px 24px 1fr;gap:8px;align-items:flex-start;padding:6px 0;border-bottom:1px solid var(--border)}
.timeline-event-row:last-child{border-bottom:none}
.timeline-event-year{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;color:var(--accent);padding-top:2px;text-align:right}
.timeline-event-line{display:flex;flex-direction:column;align-items:center;padding-top:6px}
.timeline-event-line::before{content:'';width:8px;height:8px;border-radius:50%;background:var(--accent);flex-shrink:0}
.timeline-event-line::after{content:'';width:2px;flex:1;background:var(--border);margin-top:4px}
.timeline-event-text{font-size:12px;color:var(--text-secondary);line-height:1.5;padding-top:1px}
"""


def inject_pass5_ui(html):
    """Inject the investment filter/sort UI and CSS."""

    # 1. Add CSS
    css_marker = '@media(max-width:768px)'
    css_pos = html.find(css_marker)
    if css_pos > 0:
        html = html[:css_pos] + FILTER_SORT_CSS + TIMELINE_CSS + html[css_pos:]
        print("  Pass 5: CSS injected")
    else:
        print("  WARNING: CSS marker not found")

    # 2. Add filterInvestmentTable function and renderTimelineEvents before closing </script>
    script_end = html.rfind('</script>')
    if script_end > 0:
        html = html[:script_end] + FILTER_SORT_FUNCTION + '\n' + TIMELINE_RENDER_FUNCTION + '\n' + html[script_end:]
        print("  Pass 5: JS functions injected")

    # 3. Inject filter bar into openReport() investment table section
    # Find the investment table rendering block
    inv_table_marker = "h+='<div class=\"card report-section report-section-investments\">"
    inv_pos = html.find(inv_table_marker)
    if inv_pos > 0:
        # Find the line with "f.investments.forEach" to insert before it
        forEach_pos = html.find("f.investments.forEach(function(i,idx)", inv_pos)
        if forEach_pos > 0:
            # Insert filter bar code before the forEach
            line_start = html.rfind('\n', 0, forEach_pos) + 1
            html = html[:line_start] + FILTER_SORT_HTML_INJECT + '\n    ' + html[line_start:]
            print("  Pass 5: Filter bar injected into investment table")

    # 4. Update the timeline section in openReport to use structured events if available
    # Find the timeline rendering section
    timeline_marker = "if(deep&&deep.timeline){"
    tl_pos = html.find(timeline_marker)
    if tl_pos > 0:
        # Find the end of that if block
        tl_end = html.find('\n  }', tl_pos) + 3
        old_timeline_block = html[tl_pos:tl_end]

        new_timeline_block = """if(deep&&(deep.timelineEvents||deep.timeline)){
    h+='<div class="card report-section"><div class="report-section-title">Fund Timeline</div>';
    if(deep.timelineEvents&&deep.timelineEvents.length>0){
      h+=renderTimelineEvents(deep.timelineEvents);
    } else {
      h+='<div class="mandate-text" style="font-size:12px;line-height:1.7">'+deep.timeline+'</div>';
    }
    h+='</div>';
  }"""
        html = html[:tl_pos] + new_timeline_block + html[tl_pos + len(old_timeline_block):]
        print("  Pass 5: Timeline rendering updated to use structured events")

    return html


# ─────────────────────────────────────────────────────────────────────────────
# MAIN: Execute all passes
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PASS 1: timelineEvents for funds 11-25")
print("=" * 60)
for rank in range(11, 26):
    if rank in TIMELINE_EVENTS:
        html = inject_timeline_events(html, rank, TIMELINE_EVENTS[rank])

print("\n" + "=" * 60)
print("PASS 2: timelineEvents for funds 26-50")
print("=" * 60)
for rank in range(26, 51):
    if rank in TIMELINE_EVENTS:
        html = inject_timeline_events(html, rank, TIMELINE_EVENTS[rank])

print("\n" + "=" * 60)
print("PASS 3: Enhanced macroContext for funds 11-50")
print("=" * 60)
for rank in range(11, 51):
    if rank in MACRO_CONTEXT:
        html = inject_macro_context(html, rank, MACRO_CONTEXT[rank])

print("\n" + "=" * 60)
print("PASS 4: Co-investments scan")
print("=" * 60)
co_investments = build_co_investments(html)
html = inject_co_investments(html, co_investments)

print("\n" + "=" * 60)
print("PASS 5: Investment filter/sort UI")
print("=" * 60)
html = inject_pass5_ui(html)

# Write output
with open(SWF, 'w', encoding='utf-8') as f:
    f.write(html)

print("\n" + "=" * 60)
print(f"DONE: swf.html written ({len(html.splitlines())} lines, {len(html):,} chars)")
print("=" * 60)
