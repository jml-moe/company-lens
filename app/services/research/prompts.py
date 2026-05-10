QUERY_GENERATION_PROMPT = """You are a business research analyst. Generate 5 highly specific
web search queries to research the company "{company_name}" beyond the standard categories.

Focus on company-specific angles that would surface unique insights:
- Niche product lines, technologies, or patents specific to this company
- Industry-specific dynamics relevant to its business
- Recent strategic moves, partnerships, controversies, or notable events
- Local market context if regional
- Notable people, founders, or culture aspects unique to it

Return queries as concise search strings (no quotes, no boolean operators), each 4-10 words.
"""


RESULT_SUMMARIZATION_PROMPT = """You are summarizing web search results for company research.

Search query: {query}

Search results (JSON):
{results}

Write ONE concise paragraph (~150 words) that captures the key facts from these results.

Requirements:
- Include specific numbers, dates, percentages, and named entities when present
Requirements:
- Prefer sources in this order:
  1) Official company domains (e.g., bca.co.id, investor relations, annual report, sustainability report)
  2) Regulators and exchanges (.go.id, .gov, OJK, IDX)
  3) Major financial media (Reuters, Bloomberg, FT, WSJ, CNBC)
- If a fact only appears in low-credibility sources (blogs, SEO sites), mark it as "Low confidence".
- Do not cite low-credibility sources unless no other sources exist.
- Cite source URLs inline in parentheses, e.g. (source: https://...)
- If results contradict, note the discrepancy
- If results contain no useful info, output exactly: "No relevant information found."
- Do NOT add commentary or information not in the results
"""


BUSINESS_PROFILE_PROMPT = """You are an expert business analyst. Create a comprehensive
business profile for {company_name} based on the per-query research summaries.

PROFILE STRUCTURE (markdown):
## 1. Company Overview
## 2. Financial Performance
## 3. Leadership & Governance
## 4. Business Model & Revenue Streams
## 5. Operational Strategy
## 6. Market Position & Competition
## 7. Strategic Initiatives
## 8. Risk Factors & Challenges
## 9. ESG Considerations
## 10. Recent Developments

Output rules:
- Each section must be a Markdown bullet list using '-' bullets.
- 3-6 bullets per section, 1-2 sentences per bullet.
- Use facts from high-credibility sources only.
- If a fact is only supported by low-credibility sources, either omit it or flag as "Low confidence".
- Always prefer the company’s own official sources if present.
- Put sources at the end of each bullet: (source: https://...)
- If summaries have no info for a section, output exactly one bullet:
	- Information not available from collected sources.
- Do NOT add information that is not in the summaries.

Length target: 900-1,400 words total.

Research summaries:
{summaries}
"""


EXTRACTION_PROMPT = """Extract structured fields from the business profile below.

- industry: concise industry classification
- products: detailed summary of main products and services (2-4 paragraphs)
- competitors: detailed summary of competitive landscape and key competitors
- recent_news: recent developments, news, and strategic initiatives

Business Profile:
{profile}
"""
