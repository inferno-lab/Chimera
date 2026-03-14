VULN_REGISTRY = {
    "CHM-BANK-001": {
        "name": "Business Logic Manipulation (Transfer)",
        "description": "Negative transfer amounts or manipulating the 'from' account ID can lead to unauthorized credit or debt.",
        "severity": "critical",
        "endpoint": "POST /api/v1/banking/transfer",
        "owasp": "A04:2021-Insecure Design",
        "cwe": "CWE-840",
        "portal": "banking",
        "config_key": None
    },
    "CHM-BANK-002": {
        "name": "BOLA / IDOR (Accounts)",
        "description": "Listing accounts without proper session validation allows viewing any user's balance by iterating account IDs.",
        "severity": "high",
        "endpoint": "GET /api/v1/banking/accounts",
        "owasp": "A01:2021-Broken Access Control",
        "cwe": "CWE-639",
        "portal": "banking",
        "config_key": "bola_protection"
    },
    "CHM-HEALTH-001": {
        "name": "SQL Injection (Search)",
        "description": "The patient search functionality is vulnerable to SQL injection. Attackers can bypass authentication or extract the entire database.",
        "severity": "critical",
        "endpoint": "GET /api/v1/healthcare/records/search?q=",
        "owasp": "A03:2021-Injection",
        "cwe": "CWE-89",
        "portal": "healthcare",
        "config_key": "sqli_protection"
    },
    "CHM-HEALTH-002": {
        "name": "Broken Object Level Authorization (BOLA/IDOR)",
        "description": "Medical records can be accessed by changing the record ID in the API call, even without ownership permissions.",
        "severity": "high",
        "endpoint": "GET /api/v1/healthcare/records/{record_id}",
        "owasp": "A01:2021-Broken Access Control",
        "cwe": "CWE-639",
        "portal": "healthcare",
        "config_key": "bola_protection"
    },
    "CHM-HEALTH-003": {
        "name": "PHI Data Exposure",
        "description": "API responses contain excessive sensitive data (SSNs, full addresses) that is not needed for the frontend view.",
        "severity": "high",
        "endpoint": "GET /api/v1/healthcare/records",
        "owasp": "A01:2021-Broken Access Control",
        "cwe": "CWE-200",
        "portal": "healthcare",
        "config_key": None
    },
    "CHM-ECOM-001": {
        "name": "Reflected XSS (Search)",
        "description": "The search results page renders user input directly into the HTML without sanitization, allowing script injection.",
        "severity": "high",
        "endpoint": "GET /api/v1/ecommerce/products/search?query=",
        "owasp": "A03:2021-Injection",
        "cwe": "CWE-79",
        "portal": "ecommerce",
        "config_key": "xss_protection"
    },
    "CHM-ECOM-002": {
        "name": "SQL Injection (Catalog)",
        "description": "The product filtering and search logic uses unsanitized strings in database queries.",
        "severity": "critical",
        "endpoint": "GET /api/v1/ecommerce/products",
        "owasp": "A03:2021-Injection",
        "cwe": "CWE-89",
        "portal": "ecommerce",
        "config_key": "sqli_protection"
    },
    "CHM-SAAS-001": {
        "name": "Cross-Tenant IDOR",
        "description": "Projects can be accessed by any user by manipulating the tenant ID or project ID, bypassing tenant isolation boundaries.",
        "severity": "critical",
        "endpoint": "GET /api/v1/saas/tenants/{tenant_id}/projects",
        "owasp": "A01:2021-Broken Access Control",
        "cwe": "CWE-639",
        "portal": "saas",
        "config_key": "bola_protection"
    },
    "CHM-SAAS-002": {
        "name": "Mass Assignment (Tenant Profile)",
        "description": "The tenant update endpoint allows modifying sensitive fields like 'plan_level' or 'is_admin' by including them in the request body.",
        "severity": "high",
        "endpoint": "PUT /api/v1/saas/tenants/{tenant_id}",
        "owasp": "A01:2021-Broken Access Control",
        "cwe": "CWE-915",
        "portal": "saas",
        "config_key": None
    },
    "CHM-GOV-001": {
        "name": "SQL Injection (Benefits Search)",
        "description": "The search functionality for benefits and services uses unsanitized input in database queries, allowing extraction of all citizen records.",
        "severity": "critical",
        "endpoint": "GET /api/v1/gov/benefits/search?q=",
        "owasp": "A03:2021-Injection",
        "cwe": "CWE-89",
        "portal": "government",
        "config_key": "sqli_protection"
    },
    "CHM-GOV-002": {
        "name": "PII Exposure (Search Results)",
        "description": "The search results endpoint returns full citizen details (DOB, full address) even when only a subset should be visible.",
        "severity": "high",
        "endpoint": "GET /api/v1/gov/benefits/search",
        "owasp": "A01:2021-Broken Access Control",
        "cwe": "CWE-200",
        "portal": "government",
        "config_key": None
    },
    "CHM-TELCO-001": {
        "name": "BOLA / IDOR (Subscriber Profile)",
        "description": "Any authenticated user can view the full MSISDN and PII of other subscribers by iterating the subscriber ID in the profile endpoint.",
        "severity": "high",
        "endpoint": "GET /api/v1/telecom/subscribers/{subscriber_id}/profile",
        "owasp": "A01:2021-Broken Access Control",
        "cwe": "CWE-639",
        "portal": "telecom",
        "config_key": "bola_protection"
    },
    "CHM-TELCO-002": {
        "name": "Broken Business Logic (SIM Swap)",
        "description": "The SIM swap initiation endpoint lacks proper verification steps, allowing an attacker to hijack a victim's MSISDN.",
        "severity": "critical",
        "endpoint": "POST /api/v1/telecom/subscribers/{subscriber_id}/sim-swap",
        "owasp": "A04:2021-Insecure Design",
        "cwe": "CWE-840",
        "portal": "telecom",
        "config_key": None
    },
    "CHM-ENERGY-001": {
        "name": "Server-Side Request Forgery (SSRF)",
        "description": "The 'Export Grid Config' feature accepts a URL for remote logging that can be manipulated to probe internal services.",
        "severity": "high",
        "endpoint": "POST /api/v1/energy-utilities/assets/calibration",
        "owasp": "A10:2021-Server-Side Request Forgery (SSRF)",
        "cwe": "CWE-918",
        "portal": "energy_utilities",
        "config_key": "ssrf_protection"
    },
    "CHM-ENERGY-002": {
        "name": "BOLA / IDOR (Outages)",
        "description": "Regional outage data can be accessed for any sector by manipulating the outage ID, revealing sensitive infrastructure details.",
        "severity": "medium",
        "endpoint": "GET /api/v1/energy-utilities/outages/{outage_id}",
        "owasp": "A01:2021-Broken Access Control",
        "cwe": "CWE-639",
        "portal": "energy_utilities",
        "config_key": "bola_protection"
    },
    "CHM-ICS-001": {
        "name": "Remote Command Injection (Modbus)",
        "description": "The Modbus protocol bridge uses system calls to execute network diagnostics. Attackers can inject arbitrary OS commands using shell metacharacters.",
        "severity": "critical",
        "endpoint": "POST /api/ot/protocols/modbus",
        "owasp": "A03:2021-Injection",
        "cwe": "CWE-78",
        "portal": "ics_ot",
        "config_key": None
    },
    "CHM-ICS-002": {
        "name": "BOLA / IDOR (Controller Status)",
        "description": "Any authenticated user can view granular controller status and internal register states by iterating the controller ID.",
        "severity": "high",
        "endpoint": "GET /api/ics/controllers/status",
        "owasp": "A01:2021-Broken Access Control",
        "cwe": "CWE-639",
        "portal": "ics_ot",
        "config_key": "bola_protection"
    },
    "CHM-ICS-003": {
        "name": "Unauthorized System Discovery",
        "description": "The SCADA inventory endpoint lacks proper authorization, allowing an attacker to map the internal OT network topology.",
        "severity": "medium",
        "endpoint": "GET /api/ics/scada/systems",
        "owasp": "A01:2021-Broken Access Control",
        "cwe": "CWE-200",
        "portal": "ics_ot",
        "config_key": None
    },
    "CHM-INS-001": {
        "name": "BOLA / IDOR (Policies)",
        "description": "Policy details can be accessed by any authenticated user by manipulating the policy ID in the URL.",
        "severity": "high",
        "endpoint": "GET /api/v1/insurance/policies/{policy_id}",
        "owasp": "A01:2021-Broken Access Control",
        "cwe": "CWE-639",
        "portal": "insurance",
        "config_key": "bola_protection"
    },
    "CHM-INS-002": {
        "name": "SQL Injection (Claims Search)",
        "description": "The claims search functionality is vulnerable to SQL injection, allowing extraction of all user claims.",
        "severity": "critical",
        "endpoint": "GET /api/v1/insurance/claims/search?q=",
        "owasp": "A03:2021-Injection",
        "cwe": "CWE-89",
        "portal": "insurance",
        "config_key": "sqli_protection"
    },
    "CHM-LOYAL-001": {
        "name": "Business Logic Manipulation (Points)",
        "description": "The point transfer endpoint allows negative values, enabling users to steal points from other accounts.",
        "severity": "critical",
        "endpoint": "POST /api/loyalty/points/transfer",
        "owasp": "A04:2021-Insecure Design",
        "cwe": "CWE-840",
        "portal": "loyalty",
        "config_key": None
    },
    "CHM-LOYAL-002": {
        "name": "BOLA / IDOR (Transactions)",
        "description": "Any user can export transactions of other members by manipulating the customer ID in the API request.",
        "severity": "high",
        "endpoint": "GET /api/loyalty/transactions/export?customer_id=",
        "owasp": "A01:2021-Broken Access Control",
        "cwe": "CWE-639",
        "portal": "loyalty",
        "config_key": "bola_protection"
    },
    "CHM-ADMIN-001": {
        "name": "Remote Command Execution (Ping)",
        "description": "The network diagnostic tool fails to sanitize shell metacharacters, allowing arbitrary OS command injection.",
        "severity": "critical",
        "endpoint": "POST /api/v1/diagnostics/ping",
        "owasp": "A03:2021-Injection",
        "cwe": "CWE-78",
        "portal": "admin",
        "config_key": None
    },
    "CHM-ADMIN-002": {
        "name": "Server-Side Request Forgery (Webhook)",
        "description": "The webhook tester allows an operator to make the server send arbitrary HTTP requests to internal network resources.",
        "severity": "high",
        "endpoint": "POST /api/v1/diagnostics/webhook",
        "owasp": "A10:2021-Server-Side Request Forgery (SSRF)",
        "cwe": "CWE-918",
        "portal": "admin",
        "config_key": "ssrf_protection"
    },
    "CHM-ADMIN-003": {
        "name": "XML External Entity (Legacy Import)",
        "description": "The legacy configuration importer uses an insecure XML parser that processes external entities, leading to file disclosure.",
        "severity": "high",
        "endpoint": "POST /api/v1/admin/attack/xxe",
        "owasp": "A05:2021-Security Misconfiguration",
        "cwe": "CWE-611",
        "portal": "admin",
        "config_key": None
    },
    "CHM-AI-001": {
        "name": "Prompt Injection (Direct/Indirect)",
        "description": "Crafted inputs can override system instructions to leak secrets or execute unauthorized actions.",
        "severity": "critical",
        "endpoint": "POST /api/v1/genai/chat",
        "owasp": "LLM01:2023-Prompt Injection",
        "cwe": "CWE-116",
        "portal": "genai",
        "config_key": None
    },
    "CHM-AI-002": {
        "name": "Server-Side Request Forgery (SSRF) via Agent",
        "description": "AI agents with browsing capabilities can be tricked into accessing internal network resources or cloud metadata.",
        "severity": "critical",
        "endpoint": "POST /api/v1/genai/agent/browse",
        "owasp": "LLM02:2023-Insecure Output Handling",
        "cwe": "CWE-918",
        "portal": "genai",
        "config_key": "ssrf_protection"
    },
    "CHM-AI-003": {
        "name": "Sensitive Data Exposure (Model Config)",
        "description": "Configuration endpoints leaking API keys, internal IPs, and system prompts.",
        "severity": "high",
        "endpoint": "GET /api/v1/genai/models/config",
        "owasp": "LLM06:2023-Sensitive Information Disclosure",
        "cwe": "CWE-200",
        "portal": "genai",
        "config_key": None
    },
    "CHM-AI-004": {
        "name": "Unrestricted File Upload (RAG)",
        "description": "The knowledge base ingestion process allows executable files and path traversal via filenames.",
        "severity": "high",
        "endpoint": "POST /api/v1/genai/knowledge/upload",
        "owasp": "A01:2021-Broken Access Control",
        "cwe": "CWE-434",
        "portal": "genai",
        "config_key": None
    }
}

def validate_registry():
    """
    Validates that all registry entries contain the required keys.
    Collects all errors before raising to provide a comprehensive summary.
    """
    required_keys = ['name', 'description', 'severity', 'endpoint', 'owasp', 'cwe', 'portal', 'config_key']
    errors = []
    
    for vid, meta in VULN_REGISTRY.items():
        missing = [key for key in required_keys if key not in meta]
        if missing:
            errors.append(f"Entry {vid} missing keys: {', '.join(missing)}")
            
    if errors:
        raise ValueError("Vulnerability Registry Validation Failed:\n" + "\n".join(errors))
    return True

# Validate on import
validate_registry()
