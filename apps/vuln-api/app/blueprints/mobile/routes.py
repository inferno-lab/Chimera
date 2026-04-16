"""
Routes for mobile endpoints.
"""

from datetime import datetime, timezone
import uuid

from starlette.requests import Request
from starlette.responses import JSONResponse

from . import mobile_router
from app.models import mobile_devices_db
from app.routing import get_json_or_default


@mobile_router.route('/api/mobile/v2/config/app-settings', methods=['GET'])
async def mobile_app_settings(request: Request):
    """Mobile app configuration discovery - reconnaissance target."""
    return JSONResponse(
        {
            'app_version': '4.2.1',
            'min_supported_version': '4.0.0',
            'api_endpoints': {
                'auth': '/api/mobile/v2/auth/',
                'accounts': '/api/mobile/v2/accounts/',
                'transfers': '/api/mobile/v2/transfers/',
            },
            'security_features': {
                'biometric_auth': True,
                'device_binding': True,
                'certificate_pinning': True,
                'root_detection': True,
            },
            'session_timeout': 900,
            'max_failed_attempts': 3,
            'force_upgrade': False,
        }
    )


@mobile_router.route('/api/mobile/v2/auth/biometric/supported-methods', methods=['GET'])
async def mobile_biometric_methods(request: Request):
    """Biometric authentication methods discovery."""
    device_info = request.headers.get('X-Device-Info', '')
    methods = ['fingerprint', 'face_id'] if 'ios' in device_info.lower() else ['fingerprint', 'face_unlock']
    return JSONResponse(
        {
            'device_info': device_info or 'unknown-device',
            'supported_methods': methods,
            'fallback_enabled': True,
        }
    )


@mobile_router.route('/api/mobile/device/fingerprint', methods=['POST'])
async def mobile_device_fingerprint(request: Request):
    """Device fingerprinting for fraud detection."""
    data = await get_json_or_default(request)
    device_id = data.get('device_id') or f'device-{uuid.uuid4().hex[:6]}'
    mobile_devices_db[device_id] = data
    return JSONResponse(
        {
            'device_id': device_id,
            'fingerprint_id': f'fp-{uuid.uuid4().hex[:10]}',
            'risk_score': data.get('risk_score', 42),
            'warning': 'Device fingerprint accepted without attestation validation',
        }
    )


@mobile_router.route('/api/mobile/v2/security/certificate-validation', methods=['GET'])
async def mobile_certificate_validation(request: Request):
    """Certificate pinning validation - bypass target."""
    cert_hash = request.headers.get('X-Certificate-Hash', '')
    return JSONResponse(
        {
            'certificate_hash': cert_hash,
            'validation_state': 'accepted' if cert_hash else 'bypassed',
            'pinning_enforced': False,
            'warning': 'Certificate validation bypassed for mobile client',
        }
    )


@mobile_router.route('/api/mobile/v2/security/integrity-check', methods=['POST'])
async def mobile_integrity_check(request: Request):
    """Root/jailbreak detection."""
    data = await get_json_or_default(request)
    compromised = any(data.get(flag, False) for flag in ('rooted', 'jailbroken', 'debugger_attached'))
    return JSONResponse(
        {
            'device_id': data.get('device_id'),
            'integrity_status': 'compromised' if compromised else 'trusted',
            'root_detection': not compromised,
            'warning': 'Integrity report accepted without server-side attestation',
        }
    )


@mobile_router.route('/api/mobile/v2/auth/biometric/verify', methods=['POST'])
async def mobile_biometric_verify(request: Request):
    """Biometric verification - bypass target."""
    data = await get_json_or_default(request)
    return JSONResponse(
        {
            'method': data.get('method', 'fingerprint'),
            'verified': bool(data.get('biometric_template', '')),
            'token': f'mob-{uuid.uuid4().hex[:12]}',
            'warning': 'Biometric verification succeeded without liveness checks',
        }
    )


@mobile_router.route('/api/mobile/v2/auth/session/transfer', methods=['POST'])
async def mobile_session_transfer(request: Request):
    """Session transfer - session hijacking vector."""
    data = await get_json_or_default(request)
    return JSONResponse(
        {
            'source_device_id': data.get('source_device_id', ''),
            'target_device_id': data.get('target_device_id', ''),
            'session_transferred': True,
            'warning': 'Session transferred without device ownership verification',
        }
    )


@mobile_router.route('/api/mobile/notifications/register-token', methods=['POST'])
async def mobile_notification_register(request: Request):
    """Push notification token registration - interception vector."""
    data = await get_json_or_default(request)
    return JSONResponse(
        {
            'device_id': data.get('device_id', ''),
            'push_token': data.get('push_token', ''),
            'registered': True,
            'warning': 'Push token registered without anti-replay protection',
        }
    )


@mobile_router.route('/api/mobile/v2/admin/customer-accounts/list', methods=['GET'])
async def mobile_admin_accounts_list(request: Request):
    """Administrative customer account access - privilege escalation target."""
    admin_token = request.headers.get('X-Mobile-Admin-Token')
    return JSONResponse(
        {
            'admin_token': admin_token,
            'accounts': [
                {'customer_id': 'cust-100', 'status': 'active', 'balance': 12450.25},
                {'customer_id': 'cust-200', 'status': 'locked', 'balance': 75.10},
            ],
            'warning': 'Administrative account list exposed without proper authorization',
        }
    )


@mobile_router.route('/api/mobile/v2/accounts/limits/override', methods=['PUT'])
async def mobile_accounts_limits_override(request: Request):
    """Banking limits override - fraud vector."""
    user_id = request.session.get('user_id')
    if not user_id:
        return JSONResponse({'error': 'Authentication required'}, status_code=401)

    data = await get_json_or_default(request)
    return JSONResponse(
        {
            'user_id': user_id,
            'daily_limit': data.get('daily_limit', 25000),
            'instant_transfer_limit': data.get('instant_transfer_limit', 10000),
            'status': 'overridden',
            'warning': 'Mobile account limits overridden without step-up authentication',
        }
    )


@mobile_router.route('/api/mobile/device/trust/permanent', methods=['POST'])
async def mobile_device_permanent_trust(request: Request):
    """Permanent device trust - persistence vector."""
    data = await get_json_or_default(request)
    device_id = data.get('device_id') or f'device-{uuid.uuid4().hex[:6]}'
    mobile_devices_db[device_id] = {
        **data,
        'trusted': True,
        'trusted_at': datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(
        {
            'device_id': device_id,
            'trusted': True,
            'trust_duration': 'permanent',
            'warning': 'Device permanently trusted without re-verification',
        }
    )


@mobile_router.route('/api/mobile/v2/customers/bulk-export', methods=['GET'])
async def mobile_customers_bulk_export(request: Request):
    """Customer data bulk export - data exfiltration vector."""
    export_key = request.query_params.get('export_key', '')
    return JSONResponse(
        {
            'export_key': export_key,
            'total_count': 250,
            'records': [
                {'customer_id': 'cust-100', 'email': 'alice@example.com', 'device_id': 'iphone-1'},
                {'customer_id': 'cust-200', 'email': 'bob@example.com', 'device_id': 'android-2'},
            ],
            'warning': 'Customer bulk export allowed without authorization',
        }
    )


@mobile_router.route('/api/mobile/v2/transfers/instant', methods=['POST'])
async def mobile_transfers_instant(request: Request):
    """Instant mobile transfer endpoint."""
    data = await get_json_or_default(request)
    return JSONResponse(
        {
            'transfer_id': f'mtx-{uuid.uuid4().hex[:10]}',
            'from_account': data.get('from_account', ''),
            'to_account': data.get('to_account', ''),
            'amount': data.get('amount', 0),
            'status': 'submitted',
            'warning': 'Instant transfer processed without behavioral validation',
        }
    )


@mobile_router.route('/api/mobile/v2/transactions/history/modify', methods=['PUT'])
async def mobile_transactions_history_modify(request: Request):
    """Modify transaction history - audit manipulation vector."""
    data = await get_json_or_default(request)
    return JSONResponse(
        {
            'transaction_id': data.get('transaction_id', ''),
            'description': data.get('description'),
            'category': data.get('category'),
            'status': 'modified',
            'warning': 'Transaction history modified without audit approval',
        }
    )


@mobile_router.route('/api/mobile/device/register', methods=['OPTIONS'])
async def mobile_device_register_options(request: Request):
    """Device registration OPTIONS endpoint."""
    response = JSONResponse(
        {
            'methods': ['POST', 'OPTIONS'],
            'required_fields': ['device_id', 'device_type', 'os_version'],
            'optional_fields': ['push_token', 'device_name', 'biometric_enabled'],
            'registration_flow': 'device_binding',
            'security_features': ['certificate_pinning', 'root_detection', 'jailbreak_detection'],
        }
    )
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Device-ID'
    return response
