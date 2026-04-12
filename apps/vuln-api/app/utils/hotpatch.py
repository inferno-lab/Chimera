import json as _json
import logging
from functools import wraps
from flask import make_response, request
from app.utils.security_config import security_config
from app.utils.vuln_registry import VULN_REGISTRY

logger = logging.getLogger(__name__)

def hotpatch(vuln_type, vuln_id=None):
    """
    Decorator to enable 'hot-patching' of routes.
    Switches between a vulnerable implementation and a secure implementation
    based on the global security_config state.
    
    Also injects X-Chimera-* educational headers into the response.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # P1-001 Fix (Review 8): Use dynamic attribute lookup to avoid maintenance traps
            # Maps 'sqli' -> 'sqli_protection', 'bola' -> 'bola_protection', etc.
            config_attr = f"{vuln_type}_protection"
            is_secure = getattr(security_config, config_attr, False)
            
            # Execute the route handler
            result = f(*args, is_secure=is_secure, **kwargs)
            
            # Convert result to a Response object
            response = make_response(result)
            request_path = request.path
            
            # Registry lookup
            vid = vuln_id
            meta = VULN_REGISTRY.get(vid) if vid else None
            
            if not meta:
                # Heuristic fallback
                for entry_id, entry_meta in VULN_REGISTRY.items():
                    endpoint_path = entry_meta['endpoint'].split(' ')[-1].split('?')[0].split('{')[0].rstrip('/')
                    if entry_meta['portal'] in request_path and endpoint_path in request_path:
                        vid = entry_id
                        meta = entry_meta
                        break
            
            if not meta:
                # Second fallback: match by config key
                for entry_id, entry_meta in VULN_REGISTRY.items():
                    if entry_meta['config_key'] == config_attr:
                        if '/' + entry_meta['portal'] + '/' in request_path:
                            vid = entry_id
                            meta = entry_meta
                            break

            # Inject Educational Headers
            response.headers['X-Chimera-Patched'] = str(is_secure).lower()
            
            if meta:
                response.headers['X-Chimera-Vuln-ID'] = vid
                response.headers['X-Chimera-Vuln-Type'] = meta['name']
                response.headers['X-Chimera-OWASP'] = meta['owasp']
                response.headers['X-Chimera-CWE'] = meta['cwe']
                response.headers['X-Chimera-Severity'] = meta['severity']
                
                if not is_secure:
                    hint = meta['description'].split('.')[0]
                    response.headers['X-Chimera-Hint'] = hint

            # Handle Opt-in Verbose Metadata in Body
            if request.headers.get('X-Chimera-Education') == 'true' and response.is_json and meta:
                try:
                    data = response.get_json()
                    if isinstance(data, dict):
                        data['_chimera'] = {
                            "vuln_id": vid,
                            "vuln_type": meta['name'],
                            "owasp": meta['owasp'],
                            "cwe": meta['cwe'],
                            "severity": meta['severity'],
                            "description": meta['description'],
                            "patched": is_secure,
                            "endpoint": meta['endpoint']
                        }
                        
                        new_body = _json.dumps(data)
                        response.set_data(new_body)
                        response.headers['Content-Length'] = len(response.get_data())
                except (ValueError, KeyError, TypeError) as e:
                    logger.warning(f"Error injecting Chimera education metadata: {e}")

            return response
        return decorated_function
    return decorator
