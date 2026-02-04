"""
Mini Flask - A simplified Flask implementation for educational purposes

This is a reference solution for the "Build Your Own Mini-Flask" challenge.
After completing all Flask analysis levels, users implement this to consolidate
their understanding of Flask's core architecture.

LOC Target: ~150 lines
Core Concepts Covered:
- WSGI interface (__call__)
- Route decorator and URL mapping
- Request context handling
- Response generation
- URL parameter extraction
"""

import re
from typing import Callable, Dict, Any, Tuple, List


class Request:
    """Minimal Request object simulating Flask's request"""
    
    def __init__(self, environ: Dict[str, Any]):
        self.environ = environ
        self.method = environ.get('REQUEST_METHOD', 'GET')
        self.path = environ.get('PATH_INFO', '/')
        self.args: Dict[str, str] = {}  # Query parameters (simplified)
    
    def __repr__(self):
        return f"<Request {self.method} {self.path}>"


class Response:
    """Minimal Response object"""
    
    def __init__(self, data: str, status: int = 200, headers: List[Tuple[str, str]] = None):
        self.data = data
        self.status = status
        self.headers = headers or [('Content-Type', 'text/html; charset=utf-8')]
    
    def __iter__(self):
        """Make response iterable for WSGI"""
        yield self.data.encode('utf-8')


class MiniFlask:
    """Minimal Flask-like web framework
    
    Implements core Flask features:
    - Route registration with decorators
    - URL pattern matching with parameters
    - WSGI interface for serving requests
    - Basic request/response handling
    """
    
    def __init__(self, name: str):
        self.name = name
        self.routes: Dict[str, Tuple[Callable, re.Pattern]] = {}
        self.current_request: Request = None
    
    def route(self, path: str):
        """Decorator to register a route handler
        
        Example:
            @app.route('/users/<user_id>')
            def get_user(user_id):
                return f"User: {user_id}"
        """
        def decorator(func: Callable):
            # Convert Flask-style <param> to regex groups
            # /users/<user_id> → /users/(?P<user_id>[^/]+)
            pattern_str = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', path)
            pattern = re.compile(f'^{pattern_str}$')
            
            # Store function and compiled pattern
            self.routes[path] = (func, pattern)
            return func
        
        return decorator
    
    def match_route(self, path: str) -> Tuple[Callable, Dict[str, str]]:
        """Match URL path to registered route
        
        Returns:
            (handler_function, url_parameters)
        """
        for route_path, (func, pattern) in self.routes.items():
            match = pattern.match(path)
            if match:
                # Extract URL parameters from regex groups
                params = match.groupdict()
                return func, params
        
        return None, {}
    
    def __call__(self, environ: Dict[str, Any], start_response: Callable):
        """WSGI application interface
        
        This is called by the WSGI server for each request.
        
        Args:
            environ: WSGI environment dict containing request info
            start_response: Callback to send HTTP headers
        
        Returns:
            Iterable of response body bytes
        """
        # Create request object
        request = Request(environ)
        self.current_request = request
        
        # Match route
        handler, params = self.match_route(request.path)
        
        if handler is None:
            # 404 Not Found
            response = Response("404 Not Found", status=404)
            start_response('404 Not Found', response.headers)
            return response
        
        try:
            # Call handler with URL parameters
            result = handler(**params)
            
            # Create response
            response = Response(result, status=200)
            start_response('200 OK', response.headers)
            return response
        
        except Exception as e:
            # 500 Internal Server Error
            response = Response(f"500 Internal Server Error: {e}", status=500)
            start_response('500 Internal Server Error', response.headers)
            return response


# ============================================
# Example Usage (for testing)
# ============================================

def demo():
    """Demonstrate Mini-Flask usage"""
    
    app = MiniFlask(__name__)
    
    @app.route('/')
    def index():
        return "Hello, World!"
    
    @app.route('/about')
    def about():
        return "This is Mini-Flask - a simplified Flask implementation"
    
    @app.route('/users/<user_id>')
    def get_user(user_id):
        return f"User ID: {user_id}"
    
    @app.route('/posts/<post_id>/comments/<comment_id>')
    def get_comment(post_id, comment_id):
        return f"Post {post_id}, Comment {comment_id}"
    
    # Simulate WSGI requests
    print("="*60)
    print("Mini-Flask Demo")
    print("="*60)
    
    def mock_start_response(status, headers):
        print(f"Status: {status}")
        print(f"Headers: {headers}")
    
    # Test 1: Root path
    print("\n[Test 1] GET /")
    environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'}
    response = app(environ, mock_start_response)
    print(f"Response: {list(response)[0].decode()}")
    
    # Test 2: Static path
    print("\n[Test 2] GET /about")
    environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/about'}
    response = app(environ, mock_start_response)
    print(f"Response: {list(response)[0].decode()}")
    
    # Test 3: Single parameter
    print("\n[Test 3] GET /users/123")
    environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users/123'}
    response = app(environ, mock_start_response)
    print(f"Response: {list(response)[0].decode()}")
    
    # Test 4: Multiple parameters
    print("\n[Test 4] GET /posts/42/comments/7")
    environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/posts/42/comments/7'}
    response = app(environ, mock_start_response)
    print(f"Response: {list(response)[0].decode()}")
    
    # Test 5: 404
    print("\n[Test 5] GET /unknown")
    environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/unknown'}
    response = app(environ, mock_start_response)
    print(f"Response: {list(response)[0].decode()}")
    
    print("\n" + "="*60)
    print("✓ All tests completed!")
    print(f"Total LOC: ~150 (excluding comments)")
    print("="*60)


if __name__ == '__main__':
    demo()
