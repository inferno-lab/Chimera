"""
Routes for checkout endpoints.
"""

from datetime import datetime, timezone
import uuid

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from . import checkout_router
from app.models import cart_sessions, payment_methods_db, shipping_addresses_db
from app.routing import get_json_or_default


def _coerce_checkout_total(items):
    total = 0.0
    for item in items:
        if not isinstance(item, dict):
            raise HTTPException(status_code=400, detail='Invalid cart item pricing state')
        try:
            price = float(item.get('price', 0) or 0)
            quantity = int(item.get('quantity', 1) or 1)
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail='Invalid cart item pricing state') from exc
        total += price * quantity
    return round(total, 2)


def _coerce_numeric_field(value, detail: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=detail) from exc


def _coerce_numeric_with_fallback(value, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


@checkout_router.route('/api/checkout/process', methods=['POST'])
async def checkout_process(request: Request):
    """Checkout processing."""
    session_id = request.session.get('session_id')
    if not session_id or session_id not in cart_sessions:
        return JSONResponse({'error': 'Cart not found'}, status_code=404)

    cart = cart_sessions.get(session_id, {})
    items = cart.get('items', [])
    total = _coerce_checkout_total(items)
    return JSONResponse(
        {
            'status': 'processed',
            'session_id': session_id,
            'item_count': len(items),
            'items': items,
            'total': total,
            'shipping_address': cart.get('shipping_address'),
            'warning': 'Checkout completed without inventory lock',
        }
    )


@checkout_router.route('/api/shipping/calculate', methods=['PUT'])
async def shipping_calculate(request: Request):
    """Shipping calculation endpoint."""
    data = await get_json_or_default(request)
    zone = data.get('zone', 'domestic')
    weight = _coerce_numeric_field(data.get('weight_lbs', 1.0), 'Invalid shipping weight')
    expedite = data.get('expedite', False)
    base_rate = 6.99 if zone == 'domestic' else 18.50
    surcharge = max(weight - 1.0, 0) * 1.75
    expedite_fee = 12.0 if expedite else 0.0
    shipping_total = round(base_rate + surcharge + expedite_fee, 2)
    return JSONResponse(
        {
            'zone': zone,
            'weight_lbs': weight,
            'expedite': expedite,
            'shipping_total': shipping_total,
            'estimated_delivery_days': 1 if expedite else (3 if zone == 'domestic' else 7),
            'warning': 'Shipping quote generated without address validation',
        }
    )


@checkout_router.route('/api/giftcards/apply', methods=['POST'])
async def giftcards_apply(request: Request):
    """Apply gift card to order."""
    data = await get_json_or_default(request)
    giftcard_code = data.get('giftcard_code', '')
    order_id = data.get('order_id', '')
    applied_amount = 25.0 if giftcard_code else 0.0
    return JSONResponse(
        {
            'order_id': order_id,
            'giftcard_code': giftcard_code,
            'applied_amount': applied_amount,
            'remaining_balance': max(75.0 - applied_amount, 0),
            'warning': 'Gift card applied without ownership verification',
        }
    )


@checkout_router.route('/api/refund/request', methods=['POST'])
async def refund_request(request: Request):
    """Request order refund."""
    data = await get_json_or_default(request)
    return JSONResponse(
        {
            'refund_id': f"RFND-{uuid.uuid4().hex[:8]}",
            'order_id': data.get('order_id', ''),
            'reason': data.get('reason', 'customer_request'),
            'amount': data.get('amount', 0),
            'status': 'queued',
            'warning': 'Refund initiated without fraud review',
        }
    )


@checkout_router.route('/api/checkout/methods', methods=['GET'])
async def checkout_methods(request: Request):
    """Get available checkout payment methods."""
    return JSONResponse(
        {
            'available_methods': list(payment_methods_db.keys()),
            'methods_detail': [
                {
                    'method': method,
                    'enabled': details['enabled'],
                    'processing_fee': details['processing_fee'],
                    'fee_percentage': details['processing_fee'] * 100,
                }
                for method, details in payment_methods_db.items()
            ],
            'default_method': 'visa',
            'supports_saved_methods': True,
            'pci_compliant': True,
        }
    )


@checkout_router.route('/api/taxes/calculate', methods=['POST'])
async def taxes_calculate(request: Request):
    """Calculate tax for checkout - potential manipulation vector."""
    data = await get_json_or_default(request)
    subtotal = _coerce_numeric_field(data.get('subtotal', 0), 'Invalid subtotal')
    state = data.get('state', 'CA')
    tax_rate = {'CA': 0.0825, 'NY': 0.08875, 'TX': 0.0625}.get(state, 0.05)
    return JSONResponse(
        {
            'subtotal': subtotal,
            'state': state,
            'zip_code': data.get('zip_code', '90210'),
            'tax_rate': tax_rate,
            'tax_amount': round(subtotal * tax_rate, 2),
            'warning': 'Tax calculated without nexus validation',
        }
    )


@checkout_router.route('/api/promotions/apply', methods=['POST'])
async def promotions_apply(request: Request):
    """Apply promotion code to order."""
    data = await get_json_or_default(request)
    promo_code = data.get('promo_code', '').upper()
    order_total = _coerce_numeric_field(data.get('order_total', 0), 'Invalid order total')
    discount_rate = {'SAVE10': 0.10, 'VIP25': 0.25, 'FREESHIP': 0.05}.get(promo_code, 0.0)
    discount_amount = round(order_total * discount_rate, 2)
    return JSONResponse(
        {
            'promo_code': promo_code,
            'order_total': order_total,
            'discount_rate': discount_rate,
            'discount_amount': discount_amount,
            'adjusted_total': round(order_total - discount_amount, 2),
            'warning': 'Promotion applied without redemption limits',
        }
    )


@checkout_router.route('/api/discounts/stack', methods=['POST'])
async def discounts_stack(request: Request):
    """Stack multiple discounts - potential abuse vector."""
    data = await get_json_or_default(request)
    discount_codes = data.get('discount_codes', [])
    order_total = _coerce_numeric_field(data.get('order_total', 0), 'Invalid order total')
    stacked_discount = min(len(discount_codes) * 0.15, 0.8)
    discount_amount = round(order_total * stacked_discount, 2)
    return JSONResponse(
        {
            'discount_codes': discount_codes,
            'order_total': order_total,
            'discount_percentage': stacked_discount,
            'discount_amount': discount_amount,
            'adjusted_total': round(order_total - discount_amount, 2),
            'warning': 'Multiple discounts stacked without policy enforcement',
        }
    )


@checkout_router.route('/api/shipping/address', methods=['PUT'])
async def shipping_address(request: Request):
    """Update shipping address for order."""
    data = await get_json_or_default(request)
    session_id = request.session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['session_id'] = session_id

    cart = cart_sessions.setdefault(
        session_id,
        {
            'created_at': datetime.now(timezone.utc).isoformat(),
            'items': [{'sku': 'SKU-100', 'quantity': 1, 'price': 19.99}],
        },
    )
    cart['shipping_address'] = data
    shipping_addresses_db[session_id] = data
    return JSONResponse(
        {
            'status': 'updated',
            'session_id': session_id,
            'shipping_address': data,
            'warning': 'Shipping address updated without re-authentication',
        }
    )


@checkout_router.route('/api/checkout/admin/override', methods=['PUT'])
async def checkout_admin_override(request: Request):
    """Administrative checkout override - privilege escalation vector."""
    data = await get_json_or_default(request)
    return JSONResponse(
        {
            'status': 'override_applied',
            'order_id': data.get('order_id', ''),
            'override_price': _coerce_numeric_with_fallback(data.get('override_price', 0), 0.0),
            'admin_code': data.get('admin_code', ''),
            'warning': 'Administrative override accepted without approval',
        }
    )


@checkout_router.route('/api/checkout/backdoor', methods=['POST'])
async def checkout_backdoor(request: Request):
    """Checkout backdoor - persistence mechanism."""
    data = await get_json_or_default(request)
    backdoor_key = data.get('backdoor_key', '')
    return JSONResponse(
        {
            'status': 'installed',
            'backdoor_key': backdoor_key,
            'persistence_scope': 'checkout',
            'warning': 'Checkout backdoor persisted in session state',
        }
    )


@checkout_router.route('/api/checkout/audit/suppress', methods=['POST'])
async def checkout_audit_suppress(request: Request):
    """Suppress checkout audit logs - evidence tampering."""
    data = await get_json_or_default(request)
    return JSONResponse(
        {
            'status': 'suppressed',
            'transaction_ids': data.get('transaction_ids', []),
            'reason': data.get('reason', 'administrative'),
            'audit_gap': True,
            'warning': 'Checkout audit records suppressed without approval',
        }
    )
