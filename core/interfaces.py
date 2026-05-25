import abc
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class StructuredText:
    """Represents a parsed research paper split into logical sections."""
    raw_text: str = ""
    sections: Dict[str, str] = field(default_factory=dict)
    bibliography: List[str] = field(default_factory=list)

@dataclass
class MetadataNode:
    """Represents metadata extracted for a research paper node in the graph."""
    title: str
    authors: List[str] = field(default_factory=list)
    doi: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    population_size: Optional[int] = None
    citation_count: int = 0
    impact_factor: float = 1.0  # SJR score or citation percentile (0 - 10)
    
    # Explainability details
    cohort_extraction_snippet: Optional[str] = None
    cohort_matching_rule: Optional[str] = None
    cohort_confidence: str = "UNKNOWN"
    
    # Extra payload
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "authors": ", ".join(self.authors) if self.authors else "Unknown",
            "doi": self.doi or "",
            "year": self.year or "N/A",
            "journal": self.journal or "Unknown",
            "population_size": self.population_size or "N/A",
            "citation_count": self.citation_count,
            "impact_factor": round(self.impact_factor, 2),
            "cohort_extraction_snippet": self.cohort_extraction_snippet or "",
            "cohort_matching_rule": self.cohort_matching_rule or "",
            "cohort_confidence": self.cohort_confidence
        }

class BaseParser(abc.ABC):
    """Interface for PDF Parsing and raw text cleaning."""
    
    @abc.abstractmethod
    def parse_pdf(self, pdf_path: str) -> StructuredText:
        """Parses a PDF file and structures it into sections."""
        pass
        
    @abc.abstractmethod
    def clean_text(self, text: str) -> str:
        """Cleans headers, footers, page numbers, and excessive white spacing."""
        pass

class BaseExtractor(abc.ABC):
    """Interface for NLP and Pattern Matching entity and population size extraction."""
    
    @abc.abstractmethod
    def extract_metadata(self, text_struct: StructuredText) -> MetadataNode:
        """Extracts key paper metadata and details from structured text."""
        pass
        
    @abc.abstractmethod
    def extract_population_size(self, text: str) -> Dict[str, Any]:
        """Detects population, cohort, and sample size figures with context snippets."""
        pass

class BaseTraverser(abc.ABC):
    """Interface for querying academic APIs (OpenAlex, Semantic Scholar) and tracing citation graphs."""
    
    @abc.abstractmethod
    def fetch_paper_by_doi(self, doi: str) -> Optional[MetadataNode]:
        """Fetches a paper's primary metadata by its DOI."""
        pass
        
    @abc.abstractmethod
    def fetch_paper_by_title(self, title: str) -> Optional[MetadataNode]:
        """Queries academic databases by paper title to resolve its DOI and metadata."""
        pass
        
    @abc.abstractmethod
    def traverse_citations(self, root_doi: str, max_depth: int = 2) -> Dict[str, Any]:
        """Traverses the backward references tree recursively down to max_depth."""
        pass

class BaseGraphManager(abc.ABC):
    """Interface for Graph construction, edge weighting calculations, and path analysis."""
    
    @abc.abstractmethod
    def build_networkx_graph(self, traversal_data: Dict[str, Any]):
        """Builds a NetworkX directed graph from compiled citation networks."""
        pass
        
    @abc.abstractmethod
    def update_edge_weights(self, graph, alpha: float, beta: float):
        """Calculates and updates weights of edges dynamically based on tuning factors."""
        pass
        
    @abc.abstractmethod
    def solve_evidence_paths(self, graph, source_node: str) -> List[Dict[str, Any]]:
        """Identifies, ranks, and returns critical research evidence pathways."""
        pass
