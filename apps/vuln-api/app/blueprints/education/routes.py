from copy import deepcopy
from functools import wraps

from starlette.requests import Request
from starlette.responses import JSONResponse

from . import education_router
from app.config import app_config
from app.utils.vuln_registry import VULN_REGISTRY
from app.utils.security_config import security_config


def _filter_vuln_meta(meta):
    """Remove internal implementation details from the public response."""
    filtered = deepcopy(meta)
    filtered.pop('config_key', None)
    return filtered


def _education_access_response(request: Request):
    """Enforce the existing lab-infrastructure gate under Starlette."""
    # Trust the raw ASGI peer only for the debug-only localhost bypass; this
    # assumes no proxy sits in front of direct local-development traffic.
    client_host = getattr(getattr(request, 'client', None), 'host', None)
    is_local = app_config.debug and client_host == '127.0.0.1'
    has_session = 'user_id' in request.session

    if not is_local and not has_session:
        return JSONResponse(
            {
                'error': 'Authentication required to access educational metadata',
                'note': 'This endpoint is part of the lab infrastructure, not an intentional vulnerability.',
            },
            status_code=401,
        )
    return None


def requires_education_access(func):
    """Apply the education metadata access gate to a Starlette handler."""

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        access_response = _education_access_response(request)
        if access_response is not None:
            return access_response
        return await func(request, *args, **kwargs)

    return wrapper


@education_router.route('/api/v1/education/vulns', methods=['GET'])
@requires_education_access
async def get_all_vulns(request: Request):
    """Get the full vulnerability catalog."""
    portal = request.query_params.get('portal')
    if portal:
        filtered = {k: _filter_vuln_meta(v) for k, v in VULN_REGISTRY.items() if v['portal'] == portal}
        return JSONResponse(filtered)

    return JSONResponse({k: _filter_vuln_meta(v) for k, v in VULN_REGISTRY.items()})


@education_router.route('/api/v1/education/vulns/{vuln_id}', methods=['GET'])
@requires_education_access
async def get_vuln_detail(request: Request, vuln_id):
    """Get deep dive for a specific vulnerability."""
    vuln = VULN_REGISTRY.get(vuln_id)
    if not vuln:
        return JSONResponse({'error': 'Vulnerability not found'}, status_code=404)

    response = _filter_vuln_meta(vuln)
    config_key = vuln.get('config_key')
    response['is_patched'] = getattr(security_config, config_key, False) if config_key else False
    return JSONResponse(response)


@education_router.route('/api/v1/education/portals', methods=['GET'])
@requires_education_access
async def get_portals(request: Request):
    """Get all available industry portals."""
    portals = sorted(list(set(v['portal'] for v in VULN_REGISTRY.values())))
    return JSONResponse({'portals': portals})


@education_router.route('/api/v1/education/owasp', methods=['GET'])
@requires_education_access
async def get_owasp_categories(request: Request):
    """Get vulns grouped by OWASP category."""
    categories = {}
    for vuln_id, meta in VULN_REGISTRY.items():
        categories.setdefault(meta['owasp'], []).append(vuln_id)
    return JSONResponse(categories)
