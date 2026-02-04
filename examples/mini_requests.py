"""
Mini Requests - A simplified HTTP client library for educational purposes

This is a reference solution for the "Build Your Own Mini-Requests" challenge.
After analyzing the requests library's core architecture, users implement this
to understand connection pooling, response handling, and HTTP basics.

LOC Target: ~100 lines
Core Concepts Covered:
- HTTP GET/POST requests
- Response object with status_code, text, json()
- Session with connection reuse
- Basic error handling
"""

import socket
import json as json_module
from typing import Dict, Any, Optional
from urllib.parse import urlparse


class Response:
    """HTTP Response object
    
    Attributes:
        status_code: HTTP status code (200, 404, etc.)
        text: Response body as string
        headers: Response headers dict
        url: Request URL
    """
    
    def __init__(self, status_code: int, content: bytes, headers: Dict[str, str], url: str):
        self.status_code = status_code
        self._content = content
        self.headers = headers
        self.url = url
    
    @property
    def text(self) -> str:
        """Response body as text"""
        return self._content.decode('utf-8')
    
    def json(self) -> Any:
        """Parse response body as JSON"""
        return json_module.loads(self.text)
    
    def __repr__(self):
        return f"<Response [{self.status_code}]>"


class Session:
    """HTTP session with connection pooling
    
    Maintains connections to servers for reuse across multiple requests.
    """
    
    def __init__(self):
        self._connections: Dict[str, socket.socket] = {}
    
    def get(self, url: str, **kwargs) -> Response:
        """Perform HTTP GET request"""
        return self._request('GET', url, **kwargs)
    
    def post(self, url: str, data: Optional[Dict] = None, 
             json: Optional[Dict] = None, **kwargs) -> Response:
        """Perform HTTP POST request"""
        body = None
        headers = kwargs.get('headers', {})
        
        if json is not None:
            body = json_module.dumps(json)
            headers['Content-Type'] = 'application/json'
            headers['Content-Length'] = str(len(body))
        elif data is not None:
            # Simplified: just send as string
            body = str(data)
            headers['Content-Length'] = str(len(body))
        
        return self._request('POST', url, body=body, headers=headers)
    
    def _request(self, method: str, url: str, body: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None) -> Response:
        """Internal method to perform HTTP request"""
        # Parse URL
        parsed = urlparse(url)
        host = parsed.netloc
        path = parsed.path or '/'
        
        # Build HTTP request
        request_lines = [
            f"{method} {path} HTTP/1.1",
            f"Host: {host}",
            "Connection: keep-alive",
            "User-Agent: Mini-Requests/1.0"
        ]
        
        # Add custom headers
        if headers:
            for key, value in headers.items():
                request_lines.append(f"{key}: {value}")
        
        request_lines.append("")  # Empty line before body
        if body:
            request_lines.append(body)
        
        request = "\r\n".join(request_lines) + "\r\n"
        
        # Get or create connection
        conn = self._get_connection(host)
        
        # Send request
        conn.sendall(request.encode('utf-8'))
        
        # Receive response
        raw_response = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            raw_response += chunk
            # Simplified: stop after receiving some data
            if b"\r\n\r\n" in raw_response:
                break
        
        # Parse response
        return self._parse_response(raw_response, url)
    
    def _get_connection(self, host: str) -> socket.socket:
        """Get existing connection or create new one"""
        if host in self._connections:
            return self._connections[host]
        
        # Create new connection
        # Simplified: assume port 80, no HTTPS
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((host, 80))
        self._connections[host] = conn
        return conn
    
    def _parse_response(self, raw: bytes, url: str) -> Response:
        """Parse raw HTTP response"""
        # Split headers and body
        parts = raw.split(b"\r\n\r\n", 1)
        header_section = parts[0].decode('utf-8')
        body = parts[1] if len(parts) > 1 else b""
        
        # Parse status line
        lines = header_section.split("\r\n")
        status_line = lines[0]
        status_code = int(status_line.split()[1])
        
        # Parse headers
        headers = {}
        for line in lines[1:]:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value
        
        return Response(status_code, body, headers, url)
    
    def close(self):
        """Close all connections"""
        for conn in self._connections.values():
            conn.close()
        self._connections.clear()
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, *args):
        """Close connections on context exit"""
        self.close()


# ============================================
# Example Usage (for testing)
# ============================================

def demo():
    """Demonstrate Mini-Requests usage"""
    
    print("="*60)
    print("Mini-Requests Demo")
    print("="*60)
    print("\nNote: This demo requires internet connection")
    print("Using httpbin.org for testing\n")
    
    with Session() as session:
        # Test 1: Simple GET request
        print("[Test 1] GET http://httpbin.org/get")
        try:
            response = session.get('http://httpbin.org/get')
            print(f"Status: {response.status_code}")
            print(f"Response type: {type(response)}")
            print(f"URL: {response.url}")
            data = response.json()
            print(f"JSON keys: {list(data.keys())}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 2: GET with custom headers
        print("\n[Test 2] GET with custom headers")
        try:
            response = session.get(
                'http://httpbin.org/headers',
                headers={'X-Custom-Header': 'test-value'}
            )
            print(f"Status: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 3: POST with JSON
        print("\n[Test 3] POST with JSON body")
        try:
            payload = {'name': 'Alice', 'age': 30}
            response = session.post(
                'http://httpbin.org/post',
                json=payload
            )
            print(f"Status: {response.status_code}")
            print(f"Posted data: {payload}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "="*60)
    print("✓ Demo completed!")
    print(f"Total LOC: ~100 (excluding comments)")
    print("="*60)


if __name__ == '__main__':
    # For local testing, use a simpler demo
    print("Mini-Requests - Simplified HTTP Client")
    print("\nCore features implemented:")
    print("✓ Response object (status_code, text, json)")
    print("✓ Session with connection pooling")
    print("✓ GET and POST methods")
    print("✓ Basic error handling")
    print("✓ Context manager support")
    print("\nTo run live demo (requires internet):")
    print("  Uncomment the demo() call below")
    
    # Uncomment to run live demo:
    # demo()
