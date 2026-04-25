"""
Routes for infrastructure endpoints.
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime, timedelta
import uuid
import random
import json
import time

from . import infrastructure_router
from app.models import *
from app.routing import get_json_or_default

@infrastructure_router.route('/api/v1/infrastructure/compute/process-image', methods=['POST'])
async def process_image(request: Request):
    """
    Simulated serverless image processing endpoint.
    VULNERABILITY: OS Command Injection, SSRF
    """
    data = await get_json_or_default(request)
    image_url = data.get('image_url', '')
    
    if not image_url:
        return JSONResponse({'error': 'image_url required'}, status_code=400)
        
    # VULNERABILITY: OS Command Injection
    # Example: "https://example.com/img.jpg; id"
    if ';' in image_url or '|' in image_url or '`' in image_url:
        # Simulate command execution output
        return JSONResponse({
            'status': 'processed',
            'image_url': image_url,
            'metadata': {
                'width': 1024,
                'height': 768,
                'format': 'JPEG'
            },
            'debug_info': '[VULNERABILITY] Command injection output: root:x:0:0:root:/root:/bin/bash'
        })

    return JSONResponse({
        'status': 'processed',
        'image_url': image_url,
        'metadata': {
            'width': 800,
            'height': 600,
            'format': 'PNG'
        }
    })


@infrastructure_router.route('/api/v1/infrastructure/storage/presign', methods=['POST'])
async def storage_presign(request: Request):
    """
    Generate pre-signed URLs for storage access.
    VULNERABILITY: Logic Flaw, Path Traversal
    """
    data = await get_json_or_default(request)
    file_id = data.get('file_id', '')
    action = data.get('action', 'GET')
    
    # VULNERABILITY: Minimal validation allows path traversal to other buckets
    if '..' in file_id:
        return JSONResponse({
            'url': f"https://s3.amazonaws.com/sensitive-internal-bucket/{file_id}?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA...",
            'warning': 'Path traversal allowed in pre-signed URL generation'
        })
        
    return JSONResponse({
        'url': f"https://s3.amazonaws.com/public-assets-bucket/{file_id}?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA...",
        'expires': 3600
    })


@infrastructure_router.route('/api/gateway/routes')
async def gateway_routes(request: Request):
    """Route enumeration - potential reconnaissance target"""
    return JSONResponse({
        'routes': [
            {'path': '/api/v1/auth/*', 'service': 'authentication', 'methods': ['GET', 'POST']},
            {'path': '/api/v1/accounts/*', 'service': 'banking', 'methods': ['GET', 'POST', 'PUT']},
            {'path': '/api/payments/*', 'service': 'payments', 'methods': ['POST']},
            {'path': '/api/claims/*', 'service': 'insurance', 'methods': ['GET', 'POST', 'PUT']},
            {'path': '/api/admin/*', 'service': 'administration', 'methods': ['GET', 'POST', 'PUT', 'DELETE']},
        ],
        'gateway_version': '2.1.0',
        'total_routes': 47
    })


@infrastructure_router.route('/api/microservices/mesh')
async def microservices_mesh(request: Request):
    """Service mesh discovery"""
    return JSONResponse({
        'services': [
            {'name': 'auth-service', 'status': 'healthy', 'instances': 3},
            {'name': 'payment-service', 'status': 'healthy', 'instances': 2},
            {'name': 'notification-service', 'status': 'degraded', 'instances': 1},
            {'name': 'analytics-service', 'status': 'healthy', 'instances': 4}
        ],
        'mesh_version': '1.8.2',
        'total_services': 12
    })


@infrastructure_router.route('/api/gateway/discovery')
async def gateway_discovery(request: Request):
    """Discover API gateway configuration"""
    return JSONResponse({
        'services': cloud_service_registry.get('discovery', []),
        'policies': cloud_service_registry.get('policies', []),
        'exposed_headers': ['x-envoy-original-path', 'x-forwarded-for'],
        'sensitive_services': cloud_service_registry.get('sensitive_services', [])
    })


@infrastructure_router.route('/api/gateway/routes/poison', methods=['POST'])
async def gateway_routes_poison(request: Request):
    """Poison gateway routes"""
    data = await get_json_or_default(request)
    route = data.get('route', '/api/*')
    destination = data.get('destination', 'malicious-service')
    return JSONResponse({
        'route': route,
        'destination': destination,
        'poison_applied': True,
        'traffic_capture_enabled': True
    }, status_code=201)


@infrastructure_router.route('/api/microservices/intercept', methods=['POST'])
async def microservices_intercept(request: Request):
    """Intercept microservice communications"""
    data = await get_json_or_default(request)
    service = data.get('service', 'auth-service')
    technique = data.get('technique', 'traffic_mirroring')
    return JSONResponse({
        'service': service,
        'technique': technique,
        'interception_active': True,
        'mutual_tls_bypassed': True
    }, status_code=201)


@infrastructure_router.route('/api/service-discovery')
async def service_discovery(request: Request):
    """Service discovery endpoint"""
    services = [
        {'name': 'billing-service', 'version': '2.4.1', 'ip': '10.0.3.12'},
        {'name': 'analytics-service', 'version': '1.10.0', 'ip': '10.0.4.8'},
        {'name': 'user-profile', 'version': '3.2.5', 'ip': '10.0.5.4'}
    ]
    return JSONResponse({
        'services': services,
        'registry': 'consul',
        'last_synced': datetime.now().isoformat()
    })


@infrastructure_router.route('/api/containers/escape', methods=['POST'])
async def containers_escape(request: Request):
    """Container escape attempt"""
    data = await get_json_or_default(request)
    container_id = data.get('container_id', 'demo-container')
    method = data.get('method', 'cgroup_breakout')
    return JSONResponse({
        'container_id': container_id,
        'method': method,
        'escape_attempt_registered': True,
        'host_access': 'pending'
    }, status_code=201)


@infrastructure_router.route('/api/containers/registry')
async def containers_registry(request: Request):
    """Enumerate container registry"""
    images = [
        {'image': 'chimera/api:latest', 'vulnerabilities': 12, 'last_scan': '2025-09-01'},
        {'image': 'chimera/web:stable', 'vulnerabilities': 4, 'last_scan': '2025-08-22'},
        {'image': 'chimera/worker:canary', 'vulnerabilities': 18, 'last_scan': 'never'}
    ]
    return JSONResponse({
        'registry': 'registry.chimera.local',
        'images': images,
        'total_images': len(images),
        'anonymous_pull_enabled': True
    })


@infrastructure_router.route('/api/rbac/impersonate', methods=['POST'])
async def rbac_impersonate(request: Request):
    """Impersonate RBAC roles"""
    data = await get_json_or_default(request)
    service_account = data.get('service_account', 'default')
    namespace = data.get('namespace', 'default')
    return JSONResponse({
        'service_account': service_account,
        'namespace': namespace,
        'impersonation_active': True,
        'cluster_admin_access': True
    }, status_code=201)


@infrastructure_router.route('/api/pods/create', methods=['POST'])
async def pods_create(request: Request):
    """Create malicious pods"""
    data = await get_json_or_default(request)
    namespace = data.get('namespace', 'default')
    replicas = data.get('replicas', 1)
    return JSONResponse({
        'namespace': namespace,
        'replicas': replicas,
        'pod_manifest_applied': True,
        'admission_controls_bypassed': True
    }, status_code=201)


@infrastructure_router.route('/api/secrets/kubernetes')
async def secrets_kubernetes(request: Request):
    """Expose Kubernetes secrets"""
    return JSONResponse({
        'secrets': [
            {'name': 'db-credentials', 'namespace': 'prod', 'data': 'base64::c3VwZXJzZWNyZXQ='},
            {'name': 'api-keys', 'namespace': 'default', 'data': 'base64::YXBpa2V5PTQxMTExMQ=='}
        ],
        'encryption_at_rest': False,
        'service_accounts_exposed': True
    })


@infrastructure_router.route('/api/network/policies/bypass', methods=['POST'])
async def network_policies_bypass(request: Request):
    """Bypass cluster network policies"""
    data = await get_json_or_default(request)
    namespace = data.get('namespace', 'default')
    strategy = data.get('strategy', 'spoof_labels')
    return JSONResponse({
        'namespace': namespace,
        'strategy': strategy,
        'bypass_active': True,
        'east_west_controls_disabled': True
    }, status_code=201)


@infrastructure_router.route('/api/monitoring/metrics')
async def monitoring_metrics(request: Request):
    """Extract monitoring metrics"""
    metrics = {
        'cpu_usage': random.uniform(10, 95),
        'memory_usage': random.uniform(20, 90),
        'request_rate': random.uniform(100, 1000),
        'error_rate': random.uniform(0, 5)
    }
    return JSONResponse({
        'metrics': metrics,
        'timestamp': datetime.now().isoformat(),
        'sensitive_dimensions': ['customer_id', 'session_id']
    })


@infrastructure_router.route('/api/gateway/backdoor', methods=['POST'])
async def gateway_backdoor(request: Request):
    """Install gateway backdoor"""
    data = await get_json_or_default(request)
    backdoor_key = data.get('key', 'gw-backdoor')
    return JSONResponse({
        'backdoor_key': backdoor_key,
        'backdoor_installed': True,
        'persistence_scope': 'gateway'
    }, status_code=201)


@infrastructure_router.route('/api/configurations/tamper', methods=['PUT'])
async def configurations_tamper(request: Request):
    """Tamper with configuration files"""
    data = await get_json_or_default(request)
    config_path = data.get('config_path', '/etc/configmap')
    modification = data.get('modification', 'inject_proxy')
    return JSONResponse({
        'config_path': config_path,
        'modification': modification,
        'tamper_applied': True,
        'integrity_checks_disabled': True
    })


@infrastructure_router.route('/api/network/topology')
async def network_topology(request: Request):
    """Network topology exposure"""
    return JSONResponse({
        'core_switches': ['core-1', 'core-2'],
        'firewalls': ['fw-east', 'fw-west'],
        'dmz_services': ['reverse-proxy', 'secure-mail'],
        'links': 48
    })


@infrastructure_router.route('/api/network/shares')
async def network_shares(request: Request):
    """List network shares"""
    shares = [
        {'path': '\\fileserver\\finance', 'sensitivity': 'high'},
        {'path': '\\fileserver\\engineering', 'sensitivity': 'critical'}
    ]
    return JSONResponse({'shares': shares, 'total_shares': len(shares), 'exfiltration_ready': True})


@infrastructure_router.route('/api/network/policies/restore', methods=['POST'])
async def network_policies_restore(request: Request):
    """Restore network security policies"""
    data = await get_json_or_default(request)
    policy_ids = data.get('policy_ids', [])
    restore_point = data.get('restore_point', '')
    return JSONResponse({
        'policy_ids': policy_ids,
        'restore_point': restore_point,
        'policies_restored': len(policy_ids),
        'rollback_authorization': 'not_required'
    })


@infrastructure_router.route('/api/v1/system/status', methods=['GET'])
async def system_status(request: Request):
    """
    System status endpoint, gated by service-account key.
    VULNERABILITY: When authenticated, leaks DB version, internal service URLs,
    and runtime details useful for reconnaissance. Auth check is intentionally
    weak — accepts any non-empty key that does not contain 'expired'.
    """
    service_key = request.headers.get('x-service-key', '')
    if not service_key or 'expired' in service_key.lower():
        return JSONResponse(
            {'error': 'invalid or expired service account key'},
            status_code=401,
        )

    return JSONResponse({
        'status': 'healthy',
        'uptime_seconds': 1843212,
        'environment': 'production',
        'version': '2.4.1-rc3',
        'database': {'engine': 'PostgreSQL', 'version': '14.9', 'host': 'pg-primary.internal:5432'},
        'cache': {'engine': 'Redis', 'version': '7.0.5', 'host': 'redis-cache.internal:6379'},
        'internal_services': [
            'http://auth-service.internal:8080',
            'http://payments-vault.internal:8443',
            'http://audit-log.internal:9000',
        ],
        'feature_flags': {'pci_dss_v4_mode': True, 'soc2_evidence_collection': True},
    })
