import os
import sys
import json
from http.server import BaseHTTPRequestHandler
from io import BytesIO

# Add the core directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))

from pdf_parser import PDFParser
from nlp_extractor import NLPExtractor
from interfaces import StructuredText, MetadataNode

# Initialize parser and extractor globally to reuse instances
pdf_parser = PDFParser()
nlp_extractor = NLPExtractor()

def handler(request, response):
    if request.method != 'POST':
        response.status = 405
        response.send_header('Allow', 'POST')
        response.end_headers()
        return

    try:
        # Read the entire request body as bytes
        content_length = int(request.headers.get('Content-Length', 0))
        pdf_bytes = request.rfile.read(content_length)

        if not pdf_bytes:
            response.status = 400
            response.send_header('Content-Type', 'application/json')
            response.end_headers()
            response.wfile.write(json.dumps({"error": "No PDF bytes provided"}).encode('utf-8'))
            return

        # Parse PDF from bytes
        structured_text: StructuredText = pdf_parser.parse_pdf_from_bytes(pdf_bytes)
        
        # Extract metadata
        metadata_node: MetadataNode = nlp_extractor.extract_metadata(structured_text)
        
        response.status = 200
        response.send_header('Content-Type', 'application/json')
        response.end_headers()
        response.wfile.write(json.dumps(metadata_node.to_dict()).encode('utf-8'))

    except Exception as e:
        response.status = 500
        response.send_header('Content-Type', 'application/json')
        response.end_headers()
        response.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

# Vercel's Python runtime expects a handler function.
# For local testing, you might need a simple HTTP server.
# This part is for Vercel's environment.
if __name__ == '__main__':
    # This block is for local testing purposes only.
    # Vercel will call the `handler` function directly.
    class MockRequest:
        def __init__(self, method, headers, rfile):
            self.method = method
            self.headers = headers
            self.rfile = rfile

    class MockResponse:
        def __init__(self):
            self.status = 200
            self._headers = {}
            self.wfile = BytesIO()

        def send_header(self, key, value):
            self._headers[key] = value

        def end_headers():
            pass

        def get_response_body(self):
            return self.wfile.getvalue().decode('utf-8')

    # Example usage for local testing:
    # Create a dummy PDF file for testing
    # with open("dummy.pdf", "wb") as f:
    #     f.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Contents 4 0 R/Parent 2 0 R>>endobj 4 0 obj<</Length 11>>stream\nBT/F1 12 Tf 72 712 Td(Hello World)TjET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000108 00000 n\n0000000200 00000 n\ntrailer<</Size 5/Root 1 0 R>>startxref\n250\n%%EOF")

    # with open("dummy.pdf", "rb") as f:
    #     dummy_pdf_bytes = f.read()

    # mock_request = MockRequest(
    #     method='POST',
    #     headers={'Content-Length': str(len(dummy_pdf_bytes))},
    #     rfile=BytesIO(dummy_pdf_bytes)
    # )
    # mock_response = MockResponse()
    # handler(mock_request, mock_response)
    # print(f"Status: {mock_response.status}")
    # print(f"Headers: {mock_response._headers}")
    # print(f"Body: {mock_response.get_response_body()}")
    # os.remove("dummy.pdf")
    pass