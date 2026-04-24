"""
Routes for payments endpoints with intentional vulnerabilities for WAF testing.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse
import asyncio
from datetime import datetime, timedelta
import uuid
import random
from decimal import Decimal, ROUND_HALF_UP

from . import payments_router
from app.models import *
from app.routing import get_json_or_default

# Initialize demo data stores if needed
if not currency_rates_db:
    currency_rates_db.update(
        {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "JPY": 149.50, "CAD": 1.36}
    )


# ============================================================================
# PAYMENT PROCESSING ENDPOINTS
# ============================================================================


@payments_router.route("/api/v1/payments/process", methods=["POST"])
async def payment_process(request: Request):
    """
    Process payment
    VULNERABILITY: Missing rate limiting - allows payment testing attacks
    VULNERABILITY: Decimal precision errors with float arithmetic
    """
    data = await get_json_or_default(request)

    # Extract payment details
    payment_method_id = data.get("payment_method_id")
    amount = float(data.get("amount", 0))  # VULNERABILITY: float for money
    currency = data.get("currency", "USD")
    merchant_id = data.get("merchant_id", "MERCHANT-DEMO")

    # Weak validation
    if amount <= 0:
        return JSONResponse({"error": "Invalid amount"}, status_code=400)

    # VULNERABILITY: No rate limiting - allows card testing
    # Simulate processing delay
    await asyncio.sleep(0.1)

    # Random success/failure for testing
    success_rate = 0.95

    if random.random() < success_rate:
        transaction_id = str(uuid.uuid4())

        # VULNERABILITY: Decimal precision with float
        processing_fee = amount * 0.029  # 2.9% fee
        net_amount = amount - processing_fee

        transaction = {
            "transaction_id": transaction_id,
            "payment_method_id": payment_method_id,
            "amount": amount,
            "processing_fee": processing_fee,
            "net_amount": net_amount,
            "currency": currency,
            "merchant_id": merchant_id,
            "status": "completed",
            "processed_at": datetime.now().isoformat(),
        }

        # Store in payment methods DB
        if "transactions" not in payment_methods_db:
            payment_methods_db["transactions"] = []
        payment_methods_db["transactions"].append(transaction)

        return JSONResponse({"success": True, "transaction": transaction})
    else:
        return JSONResponse(
            {
                "success": False,
                "error": "Payment declined",
                "decline_code": random.choice(
                    ["insufficient_funds", "card_declined", "fraud_suspected"]
                ),
            },
            status_code=402,
        )


@payments_router.route("/api/v1/payments/authorize", methods=["POST"])
async def payments_authorize(request: Request):
    """
    Authorize payment without capturing
    VULNERABILITY: Authorization can be held indefinitely
    """
    data = await get_json_or_default(request)

    card_number = data.get("card_number", "")
    amount = float(data.get("amount", 0))
    merchant_id = data.get("merchant_id", "MERCHANT-DEMO")

    if amount <= 0:
        return JSONResponse({"error": "Invalid amount"}, status_code=400)

    # VULNERABILITY: No expiration on authorization
    auth_code = f"AUTH-{uuid.uuid4().hex[:12].upper()}"

    authorization = {
        "authorization_code": auth_code,
        "card_number": f"****-****-****-{card_number[-4:] if len(card_number) >= 4 else '0000'}",
        "amount": amount,
        "merchant_id": merchant_id,
        "status": "authorized",
        "authorized_at": datetime.now().isoformat(),
        "expires_at": None,  # VULNERABILITY: No expiration
    }

    # Store authorization
    if "authorizations" not in payment_methods_db:
        payment_methods_db["authorizations"] = {}
    payment_methods_db["authorizations"][auth_code] = authorization

    return JSONResponse({"success": True, "authorization": authorization})


@payments_router.route("/api/v1/payments/capture", methods=["POST"])
async def payments_capture(request: Request):
    """
    Capture authorized payment
    VULNERABILITY: Amount can differ from authorization (partial capture abuse)
    """
    data = await get_json_or_default(request)

    auth_code = data.get("authorization_code", "")
    capture_amount = float(data.get("amount", 0))

    if not auth_code:
        return JSONResponse({"error": "Authorization code required"}, status_code=400)

    authorizations = payment_methods_db.get("authorizations", {})
    authorization = authorizations.get(auth_code)

    if not authorization:
        return JSONResponse({"error": "Authorization not found"}, status_code=404)

    if authorization["status"] != "authorized":
        return JSONResponse(
            {"error": "Authorization already captured or voided"}, status_code=400
        )

    # VULNERABILITY: No validation that capture amount <= authorized amount
    # Allows capturing more than authorized

    transaction_id = str(uuid.uuid4())

    capture = {
        "transaction_id": transaction_id,
        "authorization_code": auth_code,
        "authorized_amount": authorization["amount"],
        "captured_amount": capture_amount,
        "overage": capture_amount - authorization["amount"],  # Can be positive!
        "status": "captured",
        "captured_at": datetime.now().isoformat(),
    }

    # Update authorization status
    authorization["status"] = "captured"
    authorization["capture_info"] = capture

    return JSONResponse({"success": True, "capture": capture})


@payments_router.route("/api/v1/payments/refund", methods=["POST"])
async def payments_refund(request: Request):
    """
    Process refund
    VULNERABILITY: Can refund more than original transaction
    """
    data = await get_json_or_default(request)

    transaction_id = data.get("transaction_id", "")
    refund_amount = float(data.get("amount", 0))
    reason = data.get("reason", "customer_request")

    if not transaction_id:
        return JSONResponse({"error": "Transaction ID required"}, status_code=400)

    # VULNERABILITY: No validation that refund <= original amount
    refund_id = str(uuid.uuid4())

    refund = {
        "refund_id": refund_id,
        "transaction_id": transaction_id,
        "amount": refund_amount,
        "reason": reason,
        "status": "completed",
        "processed_at": datetime.now().isoformat(),
    }

    # Store refund
    if "refunds" not in payment_methods_db:
        payment_methods_db["refunds"] = []
    payment_methods_db["refunds"].append(refund)

    return JSONResponse({"success": True, "refund": refund})


# ============================================================================
# PAYMENT METHODS ENDPOINTS
# ============================================================================


@payments_router.route("/api/v1/payments/methods", methods=["GET"])
async def list_payment_methods(request: Request):
    """
    List payment methods for a customer
    VULNERABILITY: IDOR - can access any customer's payment methods
    """
    customer_id = request.query_params.get("customer_id")

    if not customer_id:
        customer_id = request.session.get("customer_id", "CUST-DEMO")

    # IDOR: No verification that current user owns this customer_id
    methods = customer_payment_methods_db.get(customer_id, [])

    if not methods:
        # Generate demo payment methods
        methods = [
            {
                "method_id": f"PM-{customer_id}-001",
                "type": "card",
                "card_brand": "VISA",
                "last_four": "4242",
                "expiry": "12/26",
                "is_default": True,
                "billing_address": {"zip": "94105"},  # Partial PII exposure
            },
            {
                "method_id": f"PM-{customer_id}-002",
                "type": "card",
                "card_brand": "MASTERCARD",
                "last_four": "5555",
                "expiry": "06/27",
                "is_default": False,
            },
        ]
        customer_payment_methods_db[customer_id] = methods

    return JSONResponse(
        {"customer_id": customer_id, "payment_methods": methods, "count": len(methods)}
    )


@payments_router.route("/api/v1/payments/methods/add", methods=["POST"])
async def payment_methods_add(request: Request):
    """
    Add payment method
    VULNERABILITY: Stores card details insecurely
    """
    data = await get_json_or_default(request)

    customer_id = data.get("customer_id") or request.session.get(
        "customer_id", "CUST-DEMO"
    )
    card_number = data.get("card_number", "")
    expiry = data.get("expiry", "")
    cvv = data.get("cvv", "")

    # Weak validation
    if len(card_number.replace(" ", "").replace("-", "")) != 16:
        return JSONResponse({"error": "Invalid card number"}, status_code=400)

    method_id = f"PM-{customer_id}-{random.randint(100, 999)}"

    # VULNERABILITY: Storing too much card data
    new_method = {
        "method_id": method_id,
        "customer_id": customer_id,
        "type": "card",
        "card_number": card_number[-4:],  # Should only store last 4
        "full_card_hash": hash(
            card_number
        ),  # VULNERABILITY: Storing hash of full number
        "expiry": expiry,
        "cvv_provided": True,  # Should never store CVV
        "added_at": datetime.now().isoformat(),
    }

    if customer_id not in customer_payment_methods_db:
        customer_payment_methods_db[customer_id] = []

    customer_payment_methods_db[customer_id].append(new_method)

    return JSONResponse({"success": True, "method": new_method}, status_code=201)


@payments_router.route("/api/v1/payments/methods/remove", methods=["POST"])
async def payment_methods_remove(request: Request):
    """
    Remove payment method
    VULNERABILITY: Can remove any customer's payment method
    """
    data = await get_json_or_default(request)

    method_id = data.get("method_id")
    customer_id = data.get("customer_id")

    if not method_id:
        return JSONResponse({"error": "method_id required"}, status_code=400)

    # IDOR: No ownership verification
    if customer_id in customer_payment_methods_db:
        methods = customer_payment_methods_db[customer_id]
        customer_payment_methods_db[customer_id] = [
            m for m in methods if m.get("method_id") != method_id
        ]

    return JSONResponse({"success": True, "message": "Payment method removed"})


# ============================================================================
# MERCHANT SERVICES ENDPOINTS
# ============================================================================


@payments_router.route("/api/v1/payments/merchant/onboard", methods=["POST"])
async def merchant_onboard(request: Request):
    """
    Merchant onboarding
    VULNERABILITY: Insufficient KYC validation
    """
    data = await get_json_or_default(request)

    business_name = data.get("business_name", "")
    tax_id = data.get("tax_id", "")
    annual_volume = float(data.get("annual_volume", 0))
    industry = data.get("industry", "general")

    # Weak validation - no real KYC
    if not business_name:
        return JSONResponse({"error": "Business name required"}, status_code=400)

    merchant_id = f"MERCH-{uuid.uuid4().hex[:8].upper()}"

    merchant = {
        "merchant_id": merchant_id,
        "business_name": business_name,
        "tax_id": tax_id,  # VULNERABILITY: Storing sensitive tax ID
        "annual_volume": annual_volume,
        "industry": industry,
        "status": "active",  # VULNERABILITY: Auto-approved without verification
        "onboarded_at": datetime.now().isoformat(),
        "processing_rate": 0.029,  # 2.9%
        "settlement_schedule": "daily",
    }

    if not merchant_applications_db:
        merchant_applications_db.update({merchant_id: merchant})
    else:
        merchant_applications_db[merchant_id] = merchant

    return JSONResponse({"success": True, "merchant": merchant}, status_code=201)


@payments_router.route("/api/v1/payments/merchant/settlements", methods=["GET"])
async def merchant_settlements(request: Request):
    """
    View merchant settlements
    VULNERABILITY: IDOR - can view any merchant's settlements
    """
    merchant_id = request.query_params.get("merchant_id", "MERCHANT-DEMO")

    # No ownership verification
    # Generate demo settlements
    settlements = []
    for i in range(5):
        settlement_date = datetime.now() - timedelta(days=i)
        settlements.append(
            {
                "settlement_id": str(uuid.uuid4()),
                "merchant_id": merchant_id,
                "settlement_date": settlement_date.date().isoformat(),
                "gross_amount": round(random.uniform(1000, 10000), 2),
                "fees": round(random.uniform(50, 300), 2),
                "net_amount": round(random.uniform(950, 9700), 2),
                "transaction_count": random.randint(10, 100),
                "status": "completed",
            }
        )

    return JSONResponse(
        {
            "merchant_id": merchant_id,
            "settlements": settlements,
            "total_settlements": len(settlements),
        }
    )


@payments_router.route("/api/v1/payments/merchant/disputes", methods=["GET"])
async def merchant_disputes(request: Request):
    """
    Handle merchant disputes
    VULNERABILITY: Exposes customer information in disputes
    """
    merchant_id = request.query_params.get("merchant_id", "MERCHANT-DEMO")

    # Generate demo disputes
    disputes = [
        {
            "dispute_id": str(uuid.uuid4()),
            "transaction_id": str(uuid.uuid4()),
            "merchant_id": merchant_id,
            "customer_email": "customer@example.com",  # VULNERABILITY: PII exposure
            "customer_name": "John Doe",  # VULNERABILITY: PII exposure
            "amount": 149.99,
            "reason": "product_not_received",
            "status": "open",
            "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
        },
        {
            "dispute_id": str(uuid.uuid4()),
            "transaction_id": str(uuid.uuid4()),
            "merchant_id": merchant_id,
            "customer_email": "jane@example.com",
            "customer_name": "Jane Smith",
            "amount": 89.50,
            "reason": "unauthorized",
            "status": "under_review",
            "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
        },
    ]

    return JSONResponse(
        {"merchant_id": merchant_id, "disputes": disputes, "total": len(disputes)}
    )


# ============================================================================
# VULNERABLE TESTING ENDPOINTS
# ============================================================================


@payments_router.route("/api/cards/validate", methods=["POST"])
async def cards_validate(request: Request):
    """
    Card validation endpoint
    VULNERABILITY: Allows unlimited card testing
    """
    data = await get_json_or_default(request)
    card_number = str(data.get("card_number", "")).replace(" ", "").replace("-", "")
    expiry = data.get("expiry", "")
    cvv = data.get("cvv", "")

    # Weak Luhn algorithm check
    def luhn_check(card_num):
        if not card_num.isdigit():
            return False
        total = 0
        reverse_digits = card_num[::-1]
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        return total % 10 == 0

    is_valid = luhn_check(card_number)

    # VULNERABILITY: Returns detailed validation info
    return JSONResponse(
        {
            "valid": is_valid,
            "card_number": f"****-****-****-{card_number[-4:] if len(card_number) >= 4 else '****'}",
            "card_brand": (
                "VISA"
                if card_number.startswith("4")
                else "MASTERCARD" if card_number.startswith("5") else "UNKNOWN"
            ),
            "expiry_valid": len(expiry) == 5 and "/" in expiry,
            "cvv_valid": len(cvv) in [3, 4],
            "luhn_check": is_valid,
        }
    )


@payments_router.route("/api/payments/test-cards")
async def payments_test_cards(request: Request):
    """
    Expose test card numbers
    VULNERABILITY: Information disclosure
    """
    return JSONResponse(
        {
            "test_cards": [
                {
                    "number": "4111111111111111",
                    "brand": "VISA",
                    "cvv": "123",
                    "expiry": "12/26",
                },
                {
                    "number": "5500000000000004",
                    "brand": "MASTERCARD",
                    "cvv": "456",
                    "expiry": "12/26",
                },
                {
                    "number": "340000000000009",
                    "brand": "AMEX",
                    "cvv": "7890",
                    "expiry": "12/26",
                },
                {
                    "number": "6011000000000004",
                    "brand": "DISCOVER",
                    "cvv": "111",
                    "expiry": "12/26",
                },
            ],
            "warning": "INTENTIONAL_VULNERABILITY - Test cards exposed for demo purposes",
            "environment": "demo",
        }
    )


@payments_router.route("/api/payments/bin-ranges")
async def payments_bin_ranges(request: Request):
    """
    BIN range testing endpoint
    VULNERABILITY: Exposes card issuer information
    """
    bin_query = request.query_params.get("bin", "")

    # VULNERABILITY: Exposes detailed BIN information
    bin_info = {
        "4111": {"issuer": "Chase Bank", "card_type": "CREDIT", "country": "US"},
        "4532": {"issuer": "Bank of America", "card_type": "DEBIT", "country": "US"},
        "5500": {"issuer": "Citibank", "card_type": "CREDIT", "country": "US"},
        "3400": {"issuer": "American Express", "card_type": "CHARGE", "country": "US"},
    }

    if bin_query in bin_info:
        return JSONResponse(
            {"bin": bin_query, "info": bin_info[bin_query], "valid": True}
        )

    return JSONResponse({"bin": bin_query, "valid": False, "message": "BIN not found"})


@payments_router.route("/api/payments/fraud-rules")
async def payments_fraud_rules(request: Request):
    """
    Fraud detection rules disclosure
    VULNERABILITY: Exposes fraud detection logic
    """
    return JSONResponse(
        {
            "fraud_detection_enabled": True,
            "rules": [
                {
                    "rule_id": "FR-001",
                    "type": "velocity_check",
                    "threshold": "5 transactions per minute",
                },
                {
                    "rule_id": "FR-002",
                    "type": "amount_limit",
                    "threshold": "$10,000 per transaction",
                },
                {
                    "rule_id": "FR-003",
                    "type": "geo_blocking",
                    "countries": ["XX", "YY"],
                },
                {"rule_id": "FR-004", "type": "bin_range", "action": "manual_review"},
                {"rule_id": "FR-005", "type": "cvv_mismatch", "action": "decline"},
            ],
            "ml_model_version": "2.3.1",
            "last_updated": "2025-10-01T00:00:00Z",
        }
    )


@payments_router.route("/api/payments/amount/manipulate", methods=["POST"])
async def payments_amount_manipulate(request: Request):
    """
    Manipulate payment amount
    VULNERABILITY: Allows amount tampering
    """
    data = await get_json_or_default(request)
    original_amount = float(data.get("original_amount", 0))
    manipulation_factor = float(data.get("factor", 1.0))

    # VULNERABILITY: No validation or auditing
    manipulated_amount = original_amount * manipulation_factor

    return JSONResponse(
        {
            "original_amount": original_amount,
            "manipulation_factor": manipulation_factor,
            "manipulated_amount": manipulated_amount,
            "difference": manipulated_amount - original_amount,
            "warning": "INTENTIONAL_VULNERABILITY - Amount manipulation for testing",
        }
    )


@payments_router.route("/api/currency/rates/manipulate", methods=["PUT"])
async def currency_rates_manipulate(request: Request):
    """
    Manipulate currency exchange rates
    VULNERABILITY: Allows financial fraud
    """
    data = await get_json_or_default(request)
    currency = data.get("currency", "USD").upper()
    new_rate = float(data.get("rate", 1.0))

    # VULNERABILITY: No authorization or validation
    old_rate = currency_rates_db.get(currency, 1.0)
    currency_rates_db[currency] = new_rate

    return JSONResponse(
        {
            "currency": currency,
            "old_rate": old_rate,
            "new_rate": new_rate,
            "change_percentage": (
                ((new_rate - old_rate) / old_rate * 100) if old_rate != 0 else 0
            ),
            "warning": "INTENTIONAL_VULNERABILITY - Rate manipulation for testing",
        }
    )


@payments_router.route("/api/payments/gateway/status")
async def payments_gateway_status(request: Request):
    """Payment gateway status check"""
    return JSONResponse(
        {
            "status": "operational",
            "uptime_percentage": 99.97,
            "response_time_ms": random.randint(50, 200),
            "active_connections": random.randint(100, 1000),
            "processors": {
                "stripe": "online",
                "square": "online",
                "paypal": "degraded",
            },
            "last_incident": "2025-09-15T10:30:00Z",
        }
    )


@payments_router.route("/api/payments/bulk-process", methods=["POST"])
async def payments_bulk_process(request: Request):
    """
    Bulk payment processing
    VULNERABILITY: No per-payment validation or rate limiting
    """
    data = await get_json_or_default(request)
    payments_list = data.get("payments", [])

    results = []

    for payment in payments_list:
        amount = float(payment.get("amount", 0))
        payment_method_id = payment.get("payment_method_id")

        # VULNERABILITY: No validation, processes all payments
        if amount > 0:
            results.append(
                {
                    "payment_method_id": payment_method_id,
                    "amount": amount,
                    "status": "processed",
                    "transaction_id": str(uuid.uuid4()),
                }
            )
        else:
            results.append(
                {
                    "payment_method_id": payment_method_id,
                    "amount": amount,
                    "status": "failed",
                    "error": "Invalid amount",
                }
            )

    return JSONResponse(
        {
            "total_payments": len(payments_list),
            "successful": len([r for r in results if r["status"] == "processed"]),
            "failed": len([r for r in results if r["status"] == "failed"]),
            "results": results,
        }
    )


@payments_router.route("/api/merchant/limits/override", methods=["PUT"])
async def merchant_limits_override(request: Request):
    """
    Override merchant limits
    VULNERABILITY: Allows bypassing transaction limits
    """
    data = await get_json_or_default(request)
    merchant_id = data.get("merchant_id", "")
    new_limit = float(data.get("new_limit", 0))

    # VULNERABILITY: No authorization check
    return JSONResponse(
        {
            "merchant_id": merchant_id,
            "old_limit": 10000.00,
            "new_limit": new_limit,
            "status": "updated",
            "warning": "INTENTIONAL_VULNERABILITY - Limit override for testing",
        }
    )
