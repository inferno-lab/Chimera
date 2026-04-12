"""
Fast-path endpoints for throughput testing.
"""

from flask import Response, jsonify, request

from . import throughput_bp
from app.config import app_config
from app.throughput import build_throughput_payload

_SIZE_LABELS = {
    'small': 2 * 1024,
    'medium': 8 * 1024,
    'large': 64 * 1024
}


def _disabled():
    return jsonify({'error': 'Throughput mode disabled'}), 404


def _parse_int(value: str):
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


_throughput_payload_cache: dict = {}


@throughput_bp.route('/fast/ping')
def fast_ping():
    if not app_config.throughput_mode:
        return _disabled()

    return jsonify({
        'status': 'ok',
        'mode': 'throughput',
        'payload_bytes': app_config.throughput_payload_bytes,
        'max_bytes': app_config.throughput_max_bytes
    })


@throughput_bp.route('/fast/export')
def fast_export():
    if not app_config.throughput_mode:
        return _disabled()

    default_bytes = app_config.throughput_payload_bytes
    max_bytes = app_config.throughput_max_bytes

    target_bytes = default_bytes
    size = request.args.get('size', '').lower()
    if size in _SIZE_LABELS:
        target_bytes = _SIZE_LABELS[size]
    else:
        bytes_param = _parse_int(request.args.get('bytes'))
        kb_param = _parse_int(request.args.get('kb'))
        if bytes_param and bytes_param > 0:
            target_bytes = bytes_param
        elif kb_param and kb_param > 0:
            target_bytes = kb_param * 1024

    if max_bytes and target_bytes > max_bytes:
        target_bytes = max_bytes

    payload = _throughput_payload_cache.get(target_bytes)
    if payload is None:
        payload = build_throughput_payload(target_bytes)
        _throughput_payload_cache[target_bytes] = payload

    response = Response(payload, mimetype='application/json')
    response.headers['X-Demo-Throughput'] = 'true'
    response.headers['X-Demo-Throughput-Bytes'] = str(len(payload))
    return response
