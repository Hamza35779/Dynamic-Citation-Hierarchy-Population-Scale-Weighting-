import re
import os
from typing import Dict, List
from .interfaces import BaseParser, StructuredText

class PDFParser(BaseParser):
    """Concrete PDF parser implementation using PyMuPDF (fitz) with section classification."""

    def clean_text(self, text: str) -> str:
        """Removes duplicate lines, line endings within sentences, and cleans spacing."""
        if not text:
            return ""
            
        # Standardize page numbers and running headers/footers
        text = re.sub(r'\b(?:Page|page|PAGE)\s*\d+\s*(?:of\s*\d+)?\b', '', text)
        
        # Replace multi-spaces and standard carriage returns
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Fix hyphens at the end of lines
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        
        # Standardize double newlines for paragraph breaks, single newlines to spaces
        paragraphs = []
        for block in text.split('\n\n'):
            cleaned_block = block.replace('\n', ' ').strip()
            if cleaned_block:
                paragraphs.append(cleaned_block)
                
        return "\n\n".join(paragraphs)

    def parse_pdf(self, pdf_path: str) -> StructuredText:
        """Parses a PDF using PyMuPDF (fitz) and segments into standard paper structures."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

        raw_pages = []
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            for page in doc:
                raw_pages.append(page.get_text())
            doc.close()
        except ImportError:
            # Fallback to pdfplumber
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            raw_pages.append(text)
            except Exception as e:
                raise RuntimeError(f"Could not import fitz or pdfplumber, or parsing failed: {e}")
        except Exception as e:
            raise RuntimeError(f"PyMuPDF failed to read PDF: {e}")

        # Combine text
        full_text = "\n\n".join(raw_pages)
        cleaned_text = self.clean_text(full_text)
        
        # Structured Section Extraction
        sections = {
            "title": "",
            "abstract": "",
            "introduction": "",
            "methodology": "",
            "results": "",
            "bibliography": ""
        }
        
        # Simple heuristic segmentation based on common academic headers
        # We search for headings like "Abstract", "Introduction", "Methodology", "Methods", "Results", "References", "Bibliography"
        headings = {
            "abstract": [r'\babstract\b', r'\bsummary\b'],
            "introduction": [r'\bintroduction\b', r'\bbackground\b'],
            "methodology": [r'\bmethodology\b', r'\bmethods\b', r'\bexperimental\b', r'\bmaterials\s+and\s+methods\b'],
            "results": [r'\bresults\b', r'\bfindings\b', r'\bresults\s+and\s+discussion\b'],
            "bibliography": [r'\breferences\b', r'\bbibliography\b', r'\bliterature\s+cited\b']
        }
        
        # Locate positions of these markers
        marker_positions = []
        for section, patterns in headings.items():
            for pattern in patterns:
                for match in re.finditer(pattern, cleaned_text, re.IGNORECASE):
                    # Ensure it looks like a heading (e.g. at the start of a paragraph or short line)
                    start = match.start()
                    # Check surrounding context
                    line_start = cleaned_text.rfind('\n', 0, start) + 1
                    line_end = cleaned_text.find('\n', start)
                    if line_end == -1:
                        line_end = len(cleaned_text)
                    line = cleaned_text[line_start:line_end].strip()
                    
                    # If heading is relatively short, it's likely a true header
                    if len(line) < 40:
                        marker_positions.append((start, section, line))
                        break # Only take first match of pattern
        
        # Sort markers by position in text
        marker_positions.sort(key=lambda x: x[0])
        
        # If we have matches, segment the text
        if marker_positions:
            # Title is everything before the first heading
            sections["title"] = cleaned_text[:marker_positions[0][0]].strip()
            
            for i in range(len(marker_positions)):
                start_pos, current_section, _ = marker_positions[i]
                end_pos = marker_positions[i+1][0] if i + 1 < len(marker_positions) else len(cleaned_text)
                
                # Extract text for this section (omitting the header itself)
                section_text = cleaned_text[start_pos:end_pos].strip()
                # Remove header line
                lines = section_text.split('\n')
                if len(lines) > 1:
                    section_text = '\n'.join(lines[1:]).strip()
                    
                # Append or set content (in case multiple match, we append)
                if sections[current_section]:
                    sections[current_section] += "\n\n" + section_text
                else:
                    sections[current_section] = section_text
        else:
            # Fallback if no sections detected: set Title from first lines, and put rest into introduction
            lines = cleaned_text.split('\n')
            sections["title"] = lines[0] if lines else "Unknown Title"
            sections["introduction"] = cleaned_text
            
        # Clean Bibliography/References to isolate single paper entries
        bibliography_entries = []
        bib_text = sections.get("bibliography", "")
        if bib_text:
            # Standard reference patterns: e.g. "[1] Authors. Title...", "1. Authors...", "Authors (Year). Title..."
            # Let's split on standard bracket markers [1], [2], or numbered items 1. 2. at start of line
            split_bib = re.split(r'\n+(?:\[\d+\]|\d+\.)\s+', "\n" + bib_text)
            for entry in split_bib:
                entry_cleaned = entry.replace('\n', ' ').strip()
                # Basic validation to ensure it looks like a bibliography citation
                if len(entry_cleaned) > 15:
                    bibliography_entries.append(entry_cleaned)
        
        return StructuredText(
            raw_text=cleaned_text,
            sections=sections,
            bibliography=bibliography_entries
        )
