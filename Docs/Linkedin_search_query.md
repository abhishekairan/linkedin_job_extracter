### **Base URL Structure**

The LinkedIn job search base URL is:

```
https://www.linkedin.com/jobs/search/
```

Parameters are added after a `?` and separated by `&`, using URL encoding where needed (spaces become `%20`, commas become `%2C`).

### **Core Search Parameters**

| Parameter | Type | Description | Examples |
| :-- | :-- | :-- | :-- |
| **keywords** | String | Job search keywords or job titles | `keywords=developer%20python` or `keywords=director%20sales%20operations` |
| **geoId** | Numeric | Geographic location identifier (country, region, or city) | `geoId=103644278` (US), `geoId=100348943` (UK), `geoId=104514075` (Germany) |
| **distance** | Numeric | Search radius in miles from the specified location | `distance=25` (25 miles radius) |
| **start** | Numeric | Pagination parameter (job position to start from) | `start=0`, `start=25`, `start=50` (typically increments of 25) |

### **Job Type Filters**

| Parameter | Code | Description |
| :-- | :-- | :-- |
| **f_JT** | F | Full-time |
| **f_JT** | P | Part-time |
| **f_JT** | C | Contract |
| **f_JT** | T | Temporary |
| **f_JT** | I | Internship |
| **f_JT** | V | Volunteer |

**Example:** `f_JT=F%2CC` (for Full-time and Contract positions - %2C is URL-encoded comma)

### **Experience Level Filters**

| Parameter | Code | Description |
| :-- | :-- | :-- |
| **f_E** | 1 | Internship |
| **f_E** | 2 | Entry level |
| **f_E** | 3 | Associate |
| **f_E** | 4 | Mid-Senior level |
| **f_E** | 5 | Director |
| **f_E** | 6 | Executive |

**Example:** `f_E=4%2C5%2C6` (for Mid-Senior, Director, and Executive roles)

### **Work Type/Location Filters**

| Parameter | Code | Description |
| :-- | :-- | :-- |
| **f_WT** | 1 | On-site |
| **f_WT** | 2 | Hybrid |
| **f_WT** | 3 | Remote |

**Example:** `f_WT=1%2C2%2C3` (for On-site, Hybrid, and Remote positions)

### **Posting Date/Time Filters**

| Parameter | Value | Description |
| :-- | :-- | :-- |
| **f_TPR** | r3600 | Posted in the last hour (3,600 seconds) |
| **f_TPR** | r86400 | Posted in the last 24 hours (86,400 seconds) |
| **f_TPR** | r604800 | Posted in the last week (604,800 seconds) |
| **f_TPR** | r2592000 | Posted in the last month (2,592,000 seconds) |

**Example:** `f_TPR=r86400` (for jobs posted in the last 24 hours)

You can customize seconds for any timeframe you prefer.

### **Specialized Filters**

| Parameter | Value | Description |
| :-- | :-- | :-- |
| **f_EA** | true | Easy Apply enabled - can apply directly on LinkedIn |
| **f_EA** | false | All positions including those requiring external application |
| **f_AL** | true | Companies actively hiring (labeled as such) |
| **f_AL** | false | All companies |
| **f_VJ** | true | Only verified job postings (avoids scams) |
| **f_VJ** | false | All job postings |
| **f_JIYN** | true | Jobs at companies where you have connections |
| **f_JIYN** | false | All jobs |
| **f_PP** | numeric | Filter by specific city (uses numeric city ID) |
| **f_C** | numeric | Filter by specific company (uses company ID) |

### **Job Function Filters**

| Parameter | Code | Description |
| :-- | :-- | :-- |
| **f_F** | sale | Sales |
| **f_F** | mgmt | Management |
| **f_F** | acct | Accounting |
| **f_F** | it | Information Technology |
| **f_F** | mktg | Marketing |
| **f_F** | hr | Human Resources |

**Example:** `f_F=sale%2Cmktg` (for Sales and Marketing functions)

### **Industry Filters**

| Parameter | Code | Description |
| :-- | :-- | :-- |
| **f_SB2** | 5 | Sales/Business Development |
| **f_SB2** | 4 | Marketing |
| **f_SB2** | 9 | Information Technology |
| **f_SB2** | 19 | Human Resources |
| **f_SB2** | 96 | Information Technology and Services |
| **f_SB2** | 4 | Computer Software |

[See the full industry codes list below]

### **Sorting Parameters**

| Parameter | Value | Description |
| :-- | :-- | :-- |
| **sortBy** | DD | Date Descending (newest jobs first) |
| **sortBy** | R | Relevance (default sorting) |

**Example:** `sortBy=DD` (for newest jobs first)

### **Complete URL Examples**

**Example 1: Recent Full-Time Remote Developer Jobs in the US**

```
https://www.linkedin.com/jobs/search/?keywords=developer&geoId=103644278&f_JT=F&f_WT=3&f_TPR=r86400&sortBy=DD
```

**Example 2: Mid-Senior Level Directors in Germany with Easy Apply**

```
https://www.linkedin.com/jobs/search/?keywords=director&geoId=104514075&f_E=4%2C5&f_EA=true&f_JT=F
```

**Example 3: Contract Web Development Jobs Posted This Week**

```
https://www.linkedin.com/jobs/search/?keywords=web%20development&f_JT=C&f_TPR=r604800&f_AL=true
```

**Example 4: Marketing Jobs from Actively Hiring Companies with Connections**

```
https://www.linkedin.com/jobs/search/?keywords=marketing&f_F=mktg&f_AL=true&f_JIYN=true
```


### **Common LinkedIn geoId Codes**[^1][^2]

| Country/Region | geoId | Country/Region | geoId |
| :-- | :-- | :-- | :-- |
| United States | 103644278 | United Kingdom | 104738473 |
| Germany | 104514075 | France | 104016111 |
| India | 102713980 | Canada | 103720260 |
| Australia | 104057199 | Netherlands | 102890883 |
| Spain | 104277358 | Italy | 103350519 |
| Poland | 104735516 | Ireland | 100993843 |
| Belgium | 102890971 | Switzerland | 106693 |
| Sweden | 105186 | Norway | 103819153 |
| Denmark | 104396 | Austria | 101282230 |
| Portugal | 105113 | Czech Republic | 105145199 |
| Brazil | 103469679 | Mexico | 103361397 |
| Japan | 102028474 | Singapore | 104010088 |


### **India's most popular Cities geoid**

| City      | geoId     | Notes                                                       |
| --------- | --------- | ----------------------------------------------------------- |
| Bengaluru | 102713980 | Known as "Silicon Valley of India"                          |
| Hyderabad | 104221682 | Major IT hub, SaaS and AI focus                             |
| Pune      | 102983800 | Growing IT and startup ecosystem                            |
| Chennai   | 104234821 | Strong IT legacy and services                               |
| Delhi-NCR | 104842695 | Includes Delhi, Gurgaon, Noida; major tech & startup region |
| Mumbai    | 104295023 | Financial and fintech tech hub                              |
| Kochi     | 104284485 | Emerging IT city in Kerala                                  |

### **Advanced Filter Combinations**

You can combine multiple filters using `&` to create complex searches:

```
https://www.linkedin.com/jobs/search/?keywords=senior%20software%20engineer&geoId=103644278&f_E=4%2C5%2C6&f_JT=F&f_WT=2%2C3&f_TPR=r604800&f_EA=true&sortBy=DD
```

This URL searches for:

- Senior Software Engineers (keywords)
- In the United States (geoId)
- Mid-Senior, Director, or Executive level (f_E)
- Full-time only (f_JT)
- Hybrid or Remote work (f_WT)
- Posted in the last week (f_TPR)
- With Easy Apply available (f_EA)
- Sorted by newest first (sortBy)


### **LinkedIn Industry Codes Reference**[^3]

Select industry codes for the `f_SB2` parameter:

- **4** - Computer Software
- **5** - Computer Networking
- **6** - Internet
- **9** - Law Practice
- **11** - Management Consulting
- **12** - Biotechnology
- **13** - Medical Practice
- **14** - Hospital \& Health Care
- **15** - Pharmaceuticals
- **18** - Cosmetics
- **19** - Apparel \& Fashion
- **20** - Sporting Goods
- **21** - Tobacco
- **22** - Supermarkets
- **23** - Food Production
- **24** - Consumer Electronics
- **25** - Consumer Goods
- **27** - Retail
- **28** - Entertainment
- **29** - Gambling \& Casinos
- **30** - Leisure, Travel \& Tourism
- **31** - Hospitality
- **32** - Restaurants
- **34** - Food \& Beverages
- **35** - Motion Pictures and Film
- **36** - Broadcast Media
- **38** - Fine Art
- **39** - Performing Arts
- **40** - Recreational Facilities and Services
- **41** - Banking
- **42** - Insurance
- **43** - Financial Services
- **45** - Investment Banking
- **46** - Investment Management
- **47** - Accounting
- **48** - Construction
- **50** - Architecture \& Planning
- **52** - Aviation \& Aerospace
- **53** - Automotive
- **96** - Information Technology and Services
- **97** - Market Research
- **98** - Public Relations and Communications
- **80** - Marketing and Advertising


### **Key Tips for Using LinkedIn Job URL Parameters**[^4][^5][^6][^7]

**URL Encoding:** Remember to URL-encode special characters:

- Space = `%20`
- Comma = `%2C`
- Colon = `%3A`

**Most Useful Combinations for Quick Searches:**

- `f_TPR` - Find recently posted jobs (less competition)
- `sortBy=DD` - Always sort by newest first to find fresh opportunities
- `f_AL=true` - Find companies actively hiring
- `f_EA=true` - Limit to Easy Apply for faster applications
- `f_E` - Target specific experience levels where you fit best

**For European Web Developers:** Use `geoId` codes for European countries, combine with `f_WT=2%2C3` for hybrid/remote flexibility, and add `f_TPR=r604800` to find recent postings to reduce competition.

These URL parameters allow you to bookmark or script customized job searches, automate job monitoring, or integrate LinkedIn job searches into applications or automation tools like n8n workflows (which you've explored before).[^5][^7]
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^8][^9]</span>

<div align="center">⁂</div>