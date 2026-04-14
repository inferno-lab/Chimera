"""
Routes for loyalty endpoints.
"""
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime, timedelta
import uuid
import random
import json
import time

from . import loyalty_router
from app.models import *
from app.routing import get_json_or_default

@loyalty_router.route('/api/loyalty/points/transfer', methods=['POST'])
async def loyalty_points_transfer(request: Request):
    """Transfer loyalty points between accounts"""
    data = await get_json_or_default(request)
    source = data.get('source_customer_id')
    destination = data.get('destination_customer_id')
    points = int(data.get('points', 0))

    return JSONResponse({
        'source_customer_id': source,
        'destination_customer_id': destination,
        'points_transferred': points,
        'transfer_completed': True,
        'warning': 'Points transfer processed without ownership validation'
    })


@loyalty_router.route('/api/loyalty/program/details')
async def loyalty_program_details(request: Request):
    """Get loyalty program details with tier benefits"""
    return JSONResponse({
        'program_name': ' Rewards Plus',
        'tiers': [
            {'name': 'bronze', 'min_points': 0, 'benefits': ['5% cashback', 'birthday bonus']},
            {'name': 'silver', 'min_points': 5000, 'benefits': ['10% cashback', 'priority support', 'free shipping']},
            {'name': 'gold', 'min_points': 15000, 'benefits': ['15% cashback', 'concierge service', 'exclusive events']},
            {'name': 'platinum', 'min_points': 50000, 'benefits': ['20% cashback', 'dedicated manager', 'VIP lounge access']}
        ],
        'points_expiry_days': 365,
        'enrollment_bonus': 1000,
        'referral_bonus': 500
    })


@loyalty_router.route('/api/loyalty/points/exchange-rates')
async def loyalty_points_exchange_rates(request: Request):
    """Get current points exchange rates"""
    # ⚠️ WARNING: Exposes internal conversion rates that could be manipulated
    return JSONResponse({
        'base_currency': 'USD',
        'exchange_rates': {
            'points_to_usd': 0.01,
            'usd_to_points': 100,
            'points_to_gift_card': 0.012,
            'miles_to_points': 1.5,
            'points_to_miles': 0.66
        },
        'minimum_redemption': 1000,
        'maximum_redemption': 100000,
        'rate_last_updated': datetime.now().isoformat()
    })


@loyalty_router.route('/api/loyalty/tiers/requirements')
async def loyalty_tiers_requirements(request: Request):
    """Get tier qualification requirements"""
    return JSONResponse({
        'tiers': [
            {
                'tier': 'bronze',
                'annual_spend': 0,
                'points_earned': 0,
                'retention_period_days': 365
            },
            {
                'tier': 'silver',
                'annual_spend': 2500,
                'points_earned': 5000,
                'retention_period_days': 365
            },
            {
                'tier': 'gold',
                'annual_spend': 7500,
                'points_earned': 15000,
                'retention_period_days': 365
            },
            {
                'tier': 'platinum',
                'annual_spend': 25000,
                'points_earned': 50000,
                'retention_period_days': 730
            }
        ],
        'tier_downgrade_grace_period_days': 90
    })


@loyalty_router.route('/api/loyalty/points/redeem', methods=['PUT'])
async def loyalty_points_redeem(request: Request):
    """Redeem loyalty points for rewards"""
    # ⚠️ WARNING: No fraud detection or rate limiting on redemptions
    data = await get_json_or_default(request)
    customer_id = data.get('customer_id')
    points = int(data.get('points', 0))
    reward_type = data.get('reward_type', 'cash')

    return JSONResponse({
        'customer_id': customer_id,
        'points_redeemed': points,
        'reward_type': reward_type,
        'redemption_completed': True,
        'warning': 'Redemption allowed without fraud review'
    })


@loyalty_router.route('/api/loyalty/tiers/status', methods=['PUT'])
async def loyalty_tiers_status(request: Request):
    """Update customer tier status"""
    # ⚠️ WARNING: No authorization check - allows tier manipulation
    data = await get_json_or_default(request)
    customer_id = data.get('customer_id')
    new_tier = data.get('tier', 'bronze')

    return JSONResponse({
        'customer_id': customer_id,
        'new_tier': new_tier,
        'status_updated': True,
        'warning': 'Tier updated without authorization'
    })


@loyalty_router.route('/api/referrals/system/reward', methods=['POST'])
async def referrals_system_reward(request: Request):
    """Process referral rewards"""
    # ⚠️ WARNING: No validation allows self-referrals and duplicate claims
    data = await get_json_or_default(request)
    referrer_id = data.get('referrer_id')
    referred_id = data.get('referred_id')
    reward_points = int(data.get('reward_points', 500))

    return JSONResponse({
        'referrer_id': referrer_id,
        'referred_id': referred_id,
        'reward_points': reward_points,
        'reward_applied': True,
        'warning': 'Referral reward applied without abuse checks'
    }, status_code=201)


@loyalty_router.route('/api/cashback/process', methods=['POST'])
async def cashback_process(request: Request):
    """Process cashback rewards"""
    # ⚠️ WARNING: No transaction verification or amount limits
    data = await get_json_or_default(request)
    customer_id = data.get('customer_id')
    transaction_amount = float(data.get('transaction_amount', 0))
    cashback_rate = float(data.get('cashback_rate', 0.05))

    return JSONResponse({
        'customer_id': customer_id,
        'transaction_amount': transaction_amount,
        'cashback_rate': cashback_rate,
        'cashback_amount': round(transaction_amount * cashback_rate, 2),
        'warning': 'Cashback processed without transaction verification'
    }, status_code=201)


@loyalty_router.route('/api/loyalty/accounts/link', methods=['POST'])
async def loyalty_accounts_link(request: Request):
    """Link external loyalty accounts"""
    # ⚠️ WARNING: No verification of account ownership or duplicate linking
    data = await get_json_or_default(request)
    primary_account = data.get('primary_account_id')
    external_account = data.get('external_account_id')
    external_program = data.get('external_program', 'partner')

    return JSONResponse({
        'primary_account_id': primary_account,
        'external_account_id': external_account,
        'external_program': external_program,
        'linked': True,
        'warning': 'Account linking completed without ownership proof'
    }, status_code=201)


@loyalty_router.route('/api/loyalty/rewards/gift-cards')
async def loyalty_rewards_gift_cards(request: Request):
    """List available gift card rewards"""
    return JSONResponse({
        'gift_cards': [
            {'merchant': 'Amazon', 'denominations': [25, 50, 100, 250], 'points_required': [2500, 5000, 10000, 25000]},
            {'merchant': 'Starbucks', 'denominations': [10, 25, 50], 'points_required': [1000, 2500, 5000]},
            {'merchant': 'Target', 'denominations': [25, 50, 100], 'points_required': [2500, 5000, 10000]},
            {'merchant': 'Best Buy', 'denominations': [50, 100, 250], 'points_required': [5000, 10000, 25000]},
            {'merchant': 'iTunes', 'denominations': [15, 25, 50], 'points_required': [1500, 2500, 5000]}
        ],
        'digital_delivery': True,
        'physical_delivery_fee_points': 500,
        'expiration_days': 365
    })


@loyalty_router.route('/api/loyalty/customers/export')
async def loyalty_customers_export(request: Request):
    """Export customer loyalty data"""
    # ⚠️ WARNING: Bulk PII export without authorization or audit logging
    export_format = request.query_params.get('format', 'json')
    include_pii = request.query_params.get('include_pii', 'true').lower() == 'true'

    return JSONResponse({
        'export_format': export_format,
        'include_pii': include_pii,
        'records_exported': 250,
        'warning': 'Customer loyalty data exported without authorization'
    })


@loyalty_router.route('/api/loyalty/transactions/export')
async def loyalty_transactions_export(request: Request):
    """Export loyalty transaction history"""
    # ⚠️ WARNING: Transaction data exposed without proper access controls
    customer_id = request.query_params.get('customer_id')
    date_from = request.query_params.get('date_from', (datetime.now() - timedelta(days=30)).isoformat())
    date_to = request.query_params.get('date_to', datetime.now().isoformat())

    return JSONResponse({
        'customer_id': customer_id,
        'date_from': date_from,
        'date_to': date_to,
        'records_exported': 120,
        'warning': 'Transaction history exported without access controls'
    })


@loyalty_router.route('/api/loyalty/system/configuration', methods=['POST'])
async def loyalty_system_configuration(request: Request):
    """Update loyalty system configuration"""
    # ⚠️ WARNING: No authorization - allows unauthorized system configuration changes
    data = await get_json_or_default(request)
    config_type = data.get('config_type', 'points_ratio')
    config_value = data.get('config_value')

    return JSONResponse({
        'config_type': config_type,
        'config_value': config_value,
        'updated': True,
        'warning': 'System configuration changed without authorization'
    })


@loyalty_router.route('/api/loyalty/audit-logs', methods=['PUT'])
async def loyalty_audit_logs(request: Request):
    """Update loyalty audit logs"""
    # ⚠️ WARNING: Allows log manipulation - PUT on audit logs is a major security issue
    data = await get_json_or_default(request)
    log_id = data.get('log_id', f"LOG-{uuid.uuid4().hex[:8]}")
    action = data.get('action', 'modified')
    modifications = data.get('modifications', {})

    return JSONResponse({
        'log_id': log_id,
        'action': action,
        'modifications': modifications,
        'tamper_successful': True,
        'warning': 'Audit logs modified without tamper protection'
    })
