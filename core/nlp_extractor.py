import re
from typing import Dict, Any, List
from .interfaces import BaseExtractor, StructuredText, MetadataNode

class NLPExtractor(BaseExtractor):
    """Hybrid Rule-based and NLP Extractor for metadata and cohort/population size identification."""
    
    def __init__(self):
        # Compile standard regex rules for population size extraction
        # Each rule has a label, pattern, and confidence score
        self.rules = [
            # N = X or n = X
            {
                "label": "N_equals_formula",
                "pattern": r"\b[Nn]\s*=\s*([0-9,]{2,10})\b",
                "confidence": "HIGH"
            },
            # X patients/participants
            {
                "label": "count_followed_by_cohort_term",
                "pattern": r"\b([0-9,]{2,10})\s*(?:patients|participants|subjects|individuals|people|cases|volunteers|men|women|children|adults|enrolled|recruited|randomized)\b",
                "confidence": "HIGH"
            },
            # sample size of X, cohort of X, study population of X
            {
                "label": "cohort_preceded_by_descriptor",
                "pattern": r"\b(?:sample\s+size|cohort|study\s+population|sample)(?:\s+\w+){0,3}\s+(?:of|was|is|were)\s+([0-9,]{2,10})\b",
                "confidence": "HIGH"
            },
            # X enrolled, X recruited
            {
                "label": "enrolled_recruited_count",
                "pattern": r"\b(?:enrolled|recruited|analyzed|included|comprised)\s+([0-9,]{2,10})\s*(?:patients|participants|subjects|individuals)?\b",
                "confidence": "MEDIUM"
            },
            # Total of X
            {
                "label": "total_count",
                "pattern": r"\btotal\s+(?:of|sample|cohort)?\s*([0-9,]{2,10})\s*(?:patients|participants|subjects)?\b",
                "confidence": "MEDIUM"
            }
        ]

    def _normalize_number(self, num_str: str) -> int:
        """Converts a matched number string like '25,000' to integer 25000."""
        cleaned = re.sub(r'[^\d]', '', num_str)
        try:
            return int(cleaned)
        except ValueError:
            return 0

    def extract_population_size(self, text: str) -> Dict[str, Any]:
        """Runs the hybrid matching engine to find the most likely population size in the text."""
        if not text:
            return {
                "population_size": None,
                "confidence": "UNKNOWN",
                "matched_text": "",
                "matching_rule": ""
            }

        candidates = []
        
        # Iterate over all defined rules
        for rule in self.rules:
            for match in re.finditer(rule["pattern"], text, re.IGNORECASE):
                num_str = match.group(1)
                value = self._normalize_number(num_str)
                
                # Filter out values that are too small (e.g. < 5) or too large (e.g. > 10,000,000)
                # to prevent matching citation counts, years (like 2020), or p-values.
                if 5 <= value <= 20000000:
                    start, end = match.start(), match.end()
                    # Capture broad context around match (100 characters before and after)
                    context_start = max(0, start - 100)
                    context_end = min(len(text), end + 100)
                    snippet = "..." + text[context_start:context_end].strip() + "..."
                    
                    # Score adjustment: matches in "Methodology" or "Methods" get higher score
                    candidates.append({
                        "population_size": value,
                        "confidence": rule["confidence"],
                        "matched_text": match.group(0),
                        "matching_rule": rule["label"],
                        "snippet": snippet
                    })

        if not candidates:
            return {
                "population_size": None,
                "confidence": "UNKNOWN",
                "matched_text": "No population details found in text.",
                "matching_rule": "N/A"
            }

        # Prioritize candidates:
        # 1. High confidence rules first
        # 2. If multiple, return the largest sample size (often represents total study cohort, whereas smaller might be sub-cohorts)
        # 3. But avoid numbers that look like years (e.g. 2019, 2020, 2021) unless they clearly match a high-confidence cohort phrase.
        
        high_conf = [c for c in candidates if c["confidence"] == "HIGH"]
        selection_pool = high_conf if high_conf else candidates
        
        # Sort by population size descending to get the total sample size
        selection_pool.sort(key=lambda x: x["population_size"], reverse=True)
        
        best = selection_pool[0]
        return {
            "population_size": best["population_size"],
            "confidence": best["confidence"],
            "matched_text": best["matched_text"],
            "matching_rule": best["matching_rule"],
            "snippet": best["snippet"]
        }

    def extract_metadata(self, text_struct: StructuredText) -> MetadataNode:
        """Parses structured text to extract metadata and clinical sample size."""
        raw_text = text_struct.raw_text
        sections = text_struct.sections
        
        # Determine paper title
        # Heuristic: the title is usually the first non-empty lines of the document
        title = "Unknown Paper Title"
        title_text = sections.get("title", "")
        if title_text:
            lines = [l.strip() for l in title_text.split('\n') if l.strip()]
            if lines:
                title = lines[0]
                if len(lines) > 1 and len(title) < 40:
                    title += " " + lines[1]
        
        # Population extraction logic
        # We first look in the "methodology" section where cohort description usually resides.
        # If not found there, we look in the "abstract", and as a final fallback, search the full text.
        pop_data = None
        methodology_text = sections.get("methodology", "")
        if methodology_text:
            pop_data = self.extract_population_size(methodology_text)
            
        if not pop_data or pop_data["population_size"] is None:
            abstract_text = sections.get("abstract", "")
            if abstract_text:
                pop_data = self.extract_population_size(abstract_text)
                
        if not pop_data or pop_data["population_size"] is None:
            pop_data = self.extract_population_size(raw_text)

        # Standard heuristics for year
        year_match = re.search(r'\b(19|20)\d{2}\b', raw_text)
        year = int(year_match.group(0)) if year_match else None

        # Authors heuristic (finding names or "by ...")
        authors = []
        author_match = re.search(r'(?:by|authors:?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\s*,\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*))*', raw_text[:500])
        if author_match:
            authors = [name for name in author_match.groups() if name]

        # Extract potential DOI
        doi_match = re.search(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', raw_text, re.IGNORECASE)
        doi = doi_match.group(0) if doi_match else None

        return MetadataNode(
            title=title,
            authors=authors if authors else ["Author N/A"],
            doi=doi,
            year=year,
            journal="Parsed Document Journal",
            population_size=pop_data.get("population_size"),
            cohort_extraction_snippet=pop_data.get("snippet"),
            cohort_matching_rule=pop_data.get("matching_rule"),
            cohort_confidence=pop_data.get("confidence")
        )
