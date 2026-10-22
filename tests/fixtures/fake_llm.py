"""Fake LLM provider for tests that must not incur API costs.

This module provides a simple HTTP server that mimics the Shrewd LLM API,
returning deterministic responses for testing purposes.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


class FakeLLMHandler(BaseHTTPRequestHandler):
    """HTTP handler that returns fake LLM responses."""

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        if self.path == "/api/embed":
            data = json.loads(body)
            text = data.get("text", "")
            # Return a deterministic embedding based on text length
            dimensions = 384
            embedding = [(hash(text + str(i)) % 1000) / 1000.0 for i in range(dimensions)]
            response = {"embedding": embedding}
        elif self.path == "/api/embed/batch":
            data = json.loads(body)
            texts = data.get("texts", [])
            embeddings = []
            for text in texts:
                dimensions = 384
                emb = [(hash(text + str(i)) % 1000) / 1000.0 for i in range(dimensions)]
                embeddings.append(emb)
            response = {"embeddings": embeddings}
        elif self.path == "/api/chat":
            response = {
                "choices": [{
                    "message": {
                        "content": "This is a fake LLM response for testing.",
                        "role": "assistant"
                    },
                    "finish_reason": "stop"
                }],
                "model": "fake-model",
                "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20}
            }
        elif self.path == "/api/completions":
            response = {
                "choices": [{
                    "text": "This is a fake completion for testing.",
                    "finish_reason": "stop"
                }],
                "model": "fake-model"
            }
        else:
            response = {"error": "Unknown endpoint"}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        # Suppress request logging in tests
        pass


def start_fake_llm(port=8089):
    """Start the fake LLM server in a background thread."""
    server = HTTPServer(("localhost", port), FakeLLMHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


# Auto-start if imported
_server = start_fake_llm()
