import unittest
import math
import networkx as nx
from core.interfaces import StructuredText, MetadataNode
from core.pdf_parser import PDFParser
from core.nlp_extractor import NLPExtractor
from core.graph_manager import GraphManager

class TestPDFParser(unittest.TestCase):
    """Tests the PDF parsing text sanitization routines."""

    def setUp(self):
        self.parser = PDFParser()

    def test_clean_text_spaces_and_newlines(self):
        raw_text = "This  is   a  test  line.\nWith standard breaks.\n\nAnd double breaks."
        cleaned = self.parser.clean_text(raw_text)
        # Verify multiple spaces are reduced to single spaces
        self.assertIn("This is a test line.", cleaned)
        # Verify paragraph double newlines are preserved but single newlines inside paragraph are removed
        self.assertEqual(cleaned.count("\n\n"), 1)

    def test_clean_text_hyphens(self):
        raw_text = "This is a multi-\nethnic cohort study."
        cleaned = self.parser.clean_text(raw_text)
        self.assertIn("multiethnic", cleaned)

    def test_clean_text_page_numbers(self):
        raw_text = "Some scientific text.\nPage 14 of 125\nMore scientific text."
        cleaned = self.parser.clean_text(raw_text)
        self.assertNotIn("Page 14", cleaned)
        self.assertNotIn("of 125", cleaned)


class TestNLPExtractor(unittest.TestCase):
    """Tests the regex matching rules and population normalization engine."""

    def setUp(self):
        self.extractor = NLPExtractor()

    def test_regex_n_equals(self):
        text = "The study size was determined to be N = 25,000 for the core analysis group."
        res = self.extractor.extract_population_size(text)
        self.assertEqual(res["population_size"], 25000)
        self.assertEqual(res["matching_rule"], "N_equals_formula")
        self.assertEqual(res["confidence"], "HIGH")

    def test_regex_patients_count(self):
        text = "We evaluated 1,250 patients throughout the double-blind clinical trial."
        res = self.extractor.extract_population_size(text)
        self.assertEqual(res["population_size"], 1250)
        self.assertEqual(res["matching_rule"], "count_followed_by_cohort_term")

    def test_regex_cohort_preceded_by_descriptor(self):
        text = "We observed a total study population of 78,500 over two years."
        res = self.extractor.extract_population_size(text)
        self.assertEqual(res["population_size"], 78500)
        self.assertEqual(res["matching_rule"], "cohort_preceded_by_descriptor")


    def test_extraction_priority_and_filtering(self):
        # The extractor should skip small numbers like 3 or years like 2020
        text = "In 2020, we evaluated 3 patients. Later, we recruited a cohort of 5,450 participants."
        res = self.extractor.extract_population_size(text)
        self.assertEqual(res["population_size"], 5450)
        self.assertNotEqual(res["population_size"], 2020)
        self.assertNotEqual(res["population_size"], 3)


class TestGraphManager(unittest.TestCase):
    """Tests the edge weight calculations and DAG critical path algorithms."""

    def setUp(self):
        self.manager = GraphManager()

    def test_weight_calculation(self):
        # Create a tiny NetworkX graph
        G = nx.DiGraph()
        
        # Add cited node v
        G.add_node("Cited Paper", population_size=10000, impact_factor=8.0)
        # Add citing node u
        G.add_node("Citing Paper", population_size=100, impact_factor=2.0)
        
        # Add edge
        G.add_edge("Citing Paper", "Cited Paper")
        
        # Apply weights: alpha=1.0, beta=1.0
        # W = 1.0 * log10(10000) + 1.0 * 8.0 = 4.0 + 8.0 = 12.0
        self.manager.update_edge_weights(G, alpha=1.0, beta=1.0)
        
        weight = G["Citing Paper"]["Cited Paper"]["weight"]
        self.assertEqual(weight, 12.0)

    def test_solve_evidence_paths(self):
        G = nx.DiGraph()
        
        # Contemporary paper (source, in_degree = 0)
        G.add_node("A", population_size=100, impact_factor=1.0)
        # Intermediate paper
        G.add_node("B", population_size=1000, impact_factor=5.0)
        # Foundational paper (sink, out_degree = 0)
        G.add_node("C", population_size=10000, impact_factor=10.0)
        
        # Path: A -> B -> C
        G.add_edge("A", "B")
        G.add_edge("B", "C")
        
        # Apply weights: W_AB (log10(1000)*1 + 5*1 = 8), W_BC (log10(10000)*1 + 10*1 = 14)
        self.manager.update_edge_weights(G, alpha=1.0, beta=1.0)
        
        paths = self.manager.solve_evidence_paths(G)
        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0]["path"], ["A", "B", "C"])
        self.assertEqual(paths[0]["total_weight"], 22.0) # 8.0 + 14.0 = 22.0


if __name__ == "__main__":
    unittest.main()
