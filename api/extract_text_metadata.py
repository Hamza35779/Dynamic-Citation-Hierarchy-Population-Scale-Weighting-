import os
import sys
import json
from http.server import BaseHTTPRequestHandler
from io import BytesIO

# Add the core directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core')))

from nlp_extractor import NLPExtractor
from interfaces import StructuredText, MetadataNode

# Initialize extractor globally to reuse instances
nlp_extractor = NLPExtractor()

def handler(request, response):
    if request.method != 'POST':
        response.status = 405
        response.send_header('Allow', 'POST')
        response.end_headers()
        return

    try:
        # Read the entire request body
        content_length = int(request.headers.get('Content-Length', 0))
        request_body_bytes = request.rfile.read(content_length)
        request_body = json.loads(request_body_bytes.decode('utf-8'))

        text = request_body.get('text')
        if not text:
            response.status = 400
            response.send_header('Content-Type', 'application/json')
            response.end_headers()
            response.wfile.write(json.dumps({"error": "No 'text' field found in request body"}).encode('utf-8'))
            return

        # Create a StructuredText object from the raw text
        # For this endpoint, we assume the input 'text' is the raw_text,
        # and we don't have predefined sections or bibliography from it.
        structured_text = StructuredText(raw_text=text, sections={"introduction": text})
        
        # Extract metadata
        metadata_node: MetadataNode = nlp_extractor.extract_metadata(structured_text)
        
        response.status = 200
        response.send_header('Content-Type', 'application/json')
        response.end_headers()
        response.wfile.write(json.dumps(metadata_node.to_dict()).encode('utf-8'))

    except json.JSONDecodeError:
        response.status = 400
        response.send_header('Content-Type', 'application/json')
        response.end_headers()
        response.wfile.write(json.dumps({"error": "Invalid JSON in request body"}).encode('utf-8'))
    except Exception as e:
        response.status = 500
        response.send_header('Content-Type', 'application/json')
        response.end_headers()
        response.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

# Vercel's Python runtime expects a handler function.
if __name__ == '__main__':
    # This block is for local testing purposes only.
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

        def end_headers(self):
            pass

        def get_response_body(self):
            return self.wfile.getvalue().decode('utf-8')

    # Example usage for local testing:
    # dummy_text_payload = json.dumps({"text": "This is a test document. The study included 150 participants. The results were significant."}).encode('utf-8')
    # mock_request = MockRequest(
    #     method='POST',
    #     headers={'Content-Length': str(len(dummy_text_payload))},
    #     rfile=BytesIO(dummy_text_payload)
    # )
    # mock_response = MockResponse()
    # handler(mock_request, mock_response)
    # print(f"Status: {mock_response.status}")
    # print(f"Headers: {mock_response._headers}")
    # print(f"Body: {mock_response.get_response_body()}")
    pass
