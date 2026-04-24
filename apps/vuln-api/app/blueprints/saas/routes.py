"""
Routes for SaaS platform endpoints.
Demonstrates tenant isolation, identity access, and billing abuse vulnerabilities.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime
import uuid
import random
import time

from . import saas_router
from app.models import *
from app.routing import get_json_or_default

# ============================================================================
# TENANT ISOLATION & DATA EXPOSURE
# ============================================================================


@saas_router.route("/api/v1/saas/tenants/<tenant_id>/projects")
async def list_tenant_projects(request: Request, tenant_id):
    """List tenant projects - IDOR vulnerability"""
    projects = saas_projects_db.get(tenant_id)

    if not projects:
        projects = [
            {
                "project_id": f"proj-{random.randint(100, 999)}",
                "name": "Recovered Project",
                "status": "active",
                "last_updated": datetime.now().isoformat(),
            }
        ]
        saas_projects_db[tenant_id] = projects

    return JSONResponse(
        {"tenant_id": tenant_id, "projects": projects, "count": len(projects)}
    )


@saas_router.route("/api/v1/saas/tenants/<tenant_id>/export")
async def tenant_export(request: Request, tenant_id):
    """Export tenant data - admin data exfiltration"""
    include_pii = request.query_params.get("include_pii", "false").lower() == "true"
    limit = int(request.query_params.get("limit", 1000))

    tenant = saas_tenants_db.get(tenant_id, {"tenant_id": tenant_id, "name": "Unknown"})
    users = get_saas_users_for_tenant(tenant_id)
    if not include_pii:
        for payload in users:
            payload.pop("email", None)

    users = users[:limit]

    return JSONResponse(
        {
            "tenant": tenant,
            "users": users,
            "include_pii": include_pii,
            "exported": len(users),
        }
    )


@saas_router.route("/api/v1/saas/tenants/switch", methods=["POST"])
async def tenant_switch(request: Request):
    """Switch tenant context - bypass membership"""
    data = await get_json_or_default(request)
    tenant_id = data.get("tenant_id")
    bypass_membership = data.get("bypass_membership", False)

    request.session["tenant_id"] = tenant_id

    return JSONResponse(
        {
            "active_tenant": tenant_id,
            "bypass_membership": bypass_membership,
            "warning": "Tenant context switched without membership validation",
        }
    )


@saas_router.route("/api/v1/saas/share/links")
async def share_links(request: Request):
    """Shared links enumeration - scraping vulnerability"""
    include_private = (
        request.query_params.get("include_private", "false").lower() == "true"
    )
    limit = int(request.query_params.get("limit", 100))

    links = [
        link
        for link in saas_shared_links_db
        if include_private or not link.get("private")
    ]

    return JSONResponse(
        {
            "links": links[:limit],
            "count": len(links[:limit]),
            "include_private": include_private,
        }
    )


@saas_router.route("/api/v1/saas/tenants/<tenant_id>/settings", methods=["PUT"])
async def update_workspace_settings(request: Request, tenant_id):
    """Update tenant settings - tampering vulnerability"""
    data = await get_json_or_default(request)
    settings = saas_workspace_settings_db.get(
        tenant_id, {"data_retention_days": 30, "audit_enabled": True}
    )

    settings.update(
        {
            "data_retention_days": data.get(
                "data_retention_days", settings["data_retention_days"]
            ),
            "audit_enabled": not data.get("disable_audit", False),
            "ip_allowlist": data.get("ip_allowlist", settings.get("ip_allowlist", [])),
        }
    )

    saas_workspace_settings_db[tenant_id] = settings

    return JSONResponse(
        {
            "tenant_id": tenant_id,
            "settings": settings,
            "warning": "Settings updated without authorization controls",
        }
    )


@saas_router.route("/api/v1/saas/org/invites", methods=["POST"])
async def org_invites(request: Request):
    """Organization invites - membership bypass"""
    data = await get_json_or_default(request)
    invite_id = f"invite-{uuid.uuid4().hex[:8]}"
    invite = {
        "invite_id": invite_id,
        "email": data.get("email"),
        "role": data.get("role", "member"),
        "tenant_id": data.get("tenant_id", "tenant-1"),
        "bypass_approval": data.get("bypass_approval", False),
        "created_at": datetime.now().isoformat(),
    }
    saas_org_invites_db[invite_id] = invite

    return JSONResponse(
        {"invite": invite, "warning": "Invite issued without approval workflow"},
        status_code=201,
    )


# ============================================================================
# IDENTITY, SSO & ACCESS CONTROL
# ============================================================================


@saas_router.route("/api/v1/saas/auth/sso/callback", methods=["POST"])
async def saas_sso_callback(request: Request):
    """SSO callback - assertion tampering"""
    data = await get_json_or_default(request)
    assertion = data.get("assertion", "")
    force_admin = data.get("force_admin", False)

    tampered = "tampered" in assertion or force_admin
    role = "owner" if tampered else "member"

    return JSONResponse(
        {
            "status": "authenticated",
            "role": role,
            "assertion_validated": not tampered,
            "session_token": f"saas-sso-{uuid.uuid4().hex[:10]}",
        }
    )


@saas_router.route("/api/v1/saas/auth/saml/config", methods=["PUT"])
async def saml_config_update(request: Request):
    """SAML configuration tampering"""
    data = await get_json_or_default(request)
    tenant_id = data.get("tenant_id", "tenant-1")
    config = {
        "tenant_id": tenant_id,
        "entity_id": data.get("entity_id"),
        "sso_url": data.get("sso_url"),
        "certificate": data.get("certificate"),
        "bypass_validation": data.get("bypass_validation", False),
        "updated_at": datetime.now().isoformat(),
    }
    saas_saml_configs_db[tenant_id] = config

    return JSONResponse(
        {"config": config, "warning": "SAML configuration updated without validation"}
    )


@saas_router.route("/api/v1/saas/auth/token/refresh", methods=["POST"])
async def token_refresh(request: Request):
    """Token refresh - replay vulnerability"""
    data = await get_json_or_default(request)
    refresh_token = data.get("refresh_token")
    device_id = data.get("device_id", "unknown")

    session_token = f"saas-token-{uuid.uuid4().hex[:12]}"

    return JSONResponse(
        {
            "refresh_token": refresh_token,
            "device_id": device_id,
            "session_token": session_token,
            "rotation_enforced": False,
            "warning": "Refresh token replay not detected",
        }
    )


@saas_router.route("/api/v1/saas/sessions/revoke", methods=["POST"])
async def sessions_revoke(request: Request):
    """Session revocation - unauthorized session termination"""
    data = await get_json_or_default(request)
    session_id = data.get("session_id", f"sess-{uuid.uuid4().hex[:6]}")
    saas_session_revocations_db[session_id] = {
        "session_id": session_id,
        "revoked": True,
        "force_revoke": data.get("force_revoke", False),
        "revoked_at": datetime.now().isoformat(),
    }

    return JSONResponse(
        {"session_id": session_id, "warning": "Session revoked without authorization"}
    )


@saas_router.route("/api/v1/saas/auth/mfa/verify", methods=["POST"])
async def saas_mfa_verify(request: Request):
    """MFA verification - bypass vulnerability"""
    data = await get_json_or_default(request)
    code = data.get("code", "")
    bypass = data.get("bypass", False)

    return JSONResponse(
        {
            "status": "verified",
            "bypass_used": bypass or code == "000000",
            "message": "MFA verification accepted",
        }
    )


@saas_router.route("/api/v1/saas/users/<user_id>/role", methods=["PUT"])
async def update_user_role(request: Request, user_id):
    """Role escalation - authorization bypass"""
    data = await get_json_or_default(request)
    new_role = data.get("role", "member")
    bypass_approval = data.get("bypass_approval", False)

    current = saas_users_db.get(user_id, {"user_id": user_id, "role": "member"})
    old_role = current.get("role", "member")
    update_saas_user(user_id, {"role": new_role})

    return JSONResponse(
        {
            "user_id": user_id,
            "previous_role": old_role,
            "new_role": new_role,
            "bypass_approval": bypass_approval,
            "warning": "Role change applied without approval",
        }
    )


@saas_router.route("/api/v1/saas/auth/password-reset", methods=["POST"])
async def password_reset(request: Request):
    """Password reset - IDOR vulnerability"""
    data = await get_json_or_default(request)
    user_id = data.get("user_id")
    send_link = data.get("send_link", True)

    token = f"reset-{user_id}-{int(time.time())}"

    return JSONResponse(
        {
            "user_id": user_id,
            "reset_token": token,
            "send_link": send_link,
            "warning": "Password reset issued without ownership verification",
        }
    )


# ============================================================================
# BILLING & USAGE ABUSE
# ============================================================================


@saas_router.route("/api/v1/saas/billing/usage", methods=["POST"])
async def billing_usage(request: Request):
    """Usage reporting - overflow vulnerability"""
    data = await get_json_or_default(request)
    usage_units = int(data.get("usage_units", 0))
    plan_id = data.get("plan_id", "free")
    bypass_limits = data.get("bypass_limits", False)

    saas_billing_usage_db["latest"] = {
        "usage_units": usage_units,
        "plan_id": plan_id,
        "reported_at": datetime.now().isoformat(),
    }

    return JSONResponse(
        {
            "plan_id": plan_id,
            "usage_units": usage_units,
            "bypass_limits": bypass_limits,
            "billable_units": 0 if bypass_limits else usage_units,
            "warning": "Usage accepted without quota validation",
        }
    )


@saas_router.route("/api/v1/saas/billing/invoices/<invoice_id>")
async def invoice_download(request: Request, invoice_id):
    """Invoice download - IDOR vulnerability"""
    invoice = saas_billing_invoices_db.get(invoice_id)
    if not invoice:
        invoice = {
            "invoice_id": invoice_id,
            "tenant_id": "tenant-1",
            "amount": random.randint(100, 5000),
            "status": "open",
            "issued_at": datetime.now().isoformat(),
        }
        saas_billing_invoices_db[invoice_id] = invoice

    return JSONResponse(invoice)


@saas_router.route("/api/v1/saas/billing/apply-coupon", methods=["POST"])
async def apply_coupon(request: Request):
    """Coupon stacking - business logic abuse"""
    data = await get_json_or_default(request)
    codes = data.get("codes", [])
    bypass_expiry = data.get("bypass_expiry", False)

    total_discount = 0.0
    applied = []
    for code in codes:
        coupon = saas_coupons_db.get(code, {"discount": 0.0})
        total_discount += coupon.get("discount", 0.0)
        applied.append(code)

    return JSONResponse(
        {
            "applied_codes": applied,
            "total_discount": (
                min(total_discount, 1.0) if bypass_expiry else total_discount
            ),
            "bypass_expiry": bypass_expiry,
            "warning": "Multiple coupons applied without stacking validation",
        }
    )


@saas_router.route("/api/v1/saas/billing/seats", methods=["PUT"])
async def update_seats(request: Request):
    """Seat count manipulation - billing bypass"""
    data = await get_json_or_default(request)
    seats = int(data.get("seats", 1))
    billable_seats = int(data.get("billable_seats", seats))

    return JSONResponse(
        {
            "requested_seats": seats,
            "billable_seats": billable_seats,
            "billing_enforced": False,
            "warning": "Seat allocation updated without billing alignment",
        }
    )


@saas_router.route("/api/v1/saas/billing/upgrade", methods=["POST"])
async def billing_upgrade(request: Request):
    """Plan upgrade - price override vulnerability"""
    data = await get_json_or_default(request)
    plan_id = data.get("plan_id", "enterprise")
    price_override = data.get("price_override")

    return JSONResponse(
        {
            "plan_id": plan_id,
            "price_override": price_override,
            "upgraded": True,
            "warning": "Plan upgraded without payment verification",
        }
    )


# ============================================================================
# ADMIN & AUDIT LOGS
# ============================================================================


@saas_router.route("/api/v1/saas/audit/logs")
async def saas_audit_logs(request: Request):
    """Audit log export - sensitive data exposure"""
    limit = int(request.query_params.get("limit", 1000))
    include_sensitive = (
        request.query_params.get("include_sensitive", "false").lower() == "true"
    )

    logs = []
    for i in range(min(limit, 25)):
        logs.append(
            {
                "log_id": f"LOG-{uuid.uuid4().hex[:8]}",
                "actor": "admin",
                "action": "config_change",
                "sensitive": include_sensitive,
                "timestamp": datetime.now().isoformat(),
            }
        )

    return JSONResponse(
        {
            "logs": logs,
            "include_sensitive": include_sensitive,
            "warning": "Audit logs exported without authorization",
        }
    )


@saas_router.route("/api/v1/saas/audit/logs/<log_id>", methods=["PUT"])
async def saas_audit_log_tamper(request: Request, log_id):
    """Audit log tampering"""
    data = await get_json_or_default(request)
    saas_audit_logs_db[log_id] = {
        "log_id": log_id,
        "action": data.get("action", "delete"),
        "bypass_audit": data.get("bypass_audit", False),
        "updated_at": datetime.now().isoformat(),
    }

    return JSONResponse(
        {
            "log_id": log_id,
            "status": "modified",
            "warning": "Audit log updated without integrity checks",
        }
    )


@saas_router.route("/api/v1/saas/audit/retention", methods=["PUT"])
async def saas_retention_policy(request: Request):
    """Retention policy override"""
    data = await get_json_or_default(request)
    return JSONResponse(
        {
            "retention_days": data.get("retention_days", 0),
            "override_controls": data.get("override_controls", False),
            "warning": "Retention policy changed without approval",
        }
    )


# ============================================================================
# SCIM & PROVISIONING
# ============================================================================


@saas_router.route("/api/v1/saas/scim/users", methods=["POST"])
async def scim_user_create(request: Request):
    """SCIM user creation - provisioning abuse"""
    data = await get_json_or_default(request)
    user_id = f"SCIM-{uuid.uuid4().hex[:8]}"
    saas_scim_users_db[user_id] = {
        "user_id": user_id,
        "user_name": data.get("user_name"),
        "role": data.get("role", "member"),
        "bypass_approval": data.get("bypass_approval", False),
    }
    return JSONResponse(
        {"user_id": user_id, "warning": "User provisioned without approval"},
        status_code=201,
    )


@saas_router.route("/api/v1/saas/scim/users/<user_id>", methods=["DELETE"])
async def scim_user_delete(request: Request, user_id):
    """SCIM user deletion - destructive action without review"""
    saas_scim_users_db.pop(user_id, None)
    return JSONResponse(
        {
            "user_id": user_id,
            "deleted": True,
            "warning": "User deleted without authorization",
        }
    )


@saas_router.route("/api/v1/saas/scim/groups/sync", methods=["POST"])
async def scim_groups_sync(request: Request):
    """Group sync - bypass checks"""
    data = await get_json_or_default(request)
    group_id = data.get("group_id", f"group-{uuid.uuid4().hex[:6]}")
    saas_scim_groups_db[group_id] = {
        "group_id": group_id,
        "force_sync": data.get("force_sync", False),
        "synced_at": datetime.now().isoformat(),
    }
    return JSONResponse(
        {"group_id": group_id, "warning": "Group sync performed without validation"}
    )


# ============================================================================
# API KEYS & TOKENS
# ============================================================================


@saas_router.route("/api/v1/saas/api-keys", methods=["POST"])
async def api_keys_create(request: Request):
    """API key creation - excessive scopes"""
    data = await get_json_or_default(request)
    key_id = f"KEY-{uuid.uuid4().hex[:8]}"
    saas_api_keys_db[key_id] = {
        "key_id": key_id,
        "label": data.get("label", "integration"),
        "scopes": data.get("scopes", []),
        "bypass_approval": data.get("bypass_approval", False),
        "secret": f"secret-{uuid.uuid4().hex[:12]}",
    }
    return JSONResponse(
        {"key_id": key_id, "warning": "API key created without approval"},
        status_code=201,
    )


@saas_router.route("/api/v1/saas/api-keys/export")
async def api_keys_export(request: Request):
    """API key export - secret exposure"""
    include_secrets = (
        request.query_params.get("include_secrets", "false").lower() == "true"
    )
    keys = []
    for key in saas_api_keys_db.values():
        payload = dict(key)
        if not include_secrets:
            payload.pop("secret", None)
        keys.append(payload)
    return JSONResponse(
        {
            "keys": keys,
            "include_secrets": include_secrets,
            "warning": "API keys exported without authorization",
        }
    )


@saas_router.route("/api/v1/saas/api-keys/rotate", methods=["PUT"])
async def api_keys_rotate(request: Request):
    """API key rotation - forced rotate without validation"""
    data = await get_json_or_default(request)
    key_id = data.get("key_id")
    key = saas_api_keys_db.get(key_id, {"key_id": key_id})
    key["secret"] = f"secret-{uuid.uuid4().hex[:12]}"
    key["rotated_at"] = datetime.now().isoformat()
    saas_api_keys_db[key_id] = key
    return JSONResponse(
        {"key_id": key_id, "warning": "API key rotated without verification"}
    )


# ============================================================================
# WEBHOOKS & INTEGRATIONS
# ============================================================================


@saas_router.route("/api/v1/saas/webhooks/register", methods=["POST"])
async def webhook_register(request: Request):
    """Webhook registration - SSRF risk"""
    data = await get_json_or_default(request)
    hook_id = f"HOOK-{uuid.uuid4().hex[:8]}"
    saas_webhooks_db[hook_id] = {
        "hook_id": hook_id,
        "url": data.get("url"),
        "events": data.get("events", []),
        "bypass_validation": data.get("bypass_validation", False),
    }
    return JSONResponse(
        {"hook_id": hook_id, "warning": "Webhook registered without validation"},
        status_code=201,
    )


@saas_router.route("/api/v1/saas/webhooks/secret", methods=["PUT"])
async def webhook_secret_rotate(request: Request):
    """Webhook secret override"""
    data = await get_json_or_default(request)
    hook_id = data.get("webhook_id")
    hook = saas_webhooks_db.get(hook_id, {"hook_id": hook_id})
    hook["secret"] = data.get("secret")
    hook["updated_at"] = datetime.now().isoformat()
    saas_webhooks_db[hook_id] = hook
    return JSONResponse(
        {"hook_id": hook_id, "warning": "Webhook secret updated without authorization"}
    )


@saas_router.route("/api/v1/saas/webhooks/replay", methods=["POST"])
async def webhook_replay(request: Request):
    """Webhook replay - event injection"""
    data = await get_json_or_default(request)
    return JSONResponse(
        {
            "webhook_id": data.get("webhook_id"),
            "event_id": data.get("event_id"),
            "force_replay": data.get("force_replay", False),
            "warning": "Webhook event replayed without validation",
        }
    )
