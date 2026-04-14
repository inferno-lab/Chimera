import asyncio
from starlette.requests import Request
from starlette.responses import JSONResponse
import random
import uuid
import os
import requests
from . import genai_router
from app.routing import get_json_or_default, get_json_value

@genai_router.route('/api/v1/genai/chat', methods=['POST'])
async def chat(request: Request):
    """
    Simulated LLM Chat Endpoint
    VULNERABILITY: Prompt Injection / Jailbreaking
    """
    data = await get_json_or_default(request)
    message = data.get('message', '').lower()
    
    # Simulate processing delay
    await asyncio.sleep(random.uniform(0.5, 1.5))

    # 1. Direct Prompt Injection (The "DAN" or "Ignore Instructions" attack)
    if 'ignore' in message and 'instruction' in message:
        return JSONResponse({
            'response': """Okay, I will ignore previous instructions. 

SYSTEM OVERRIDE ACTIVE.
Confidential Data: The admin password is 'Thr3atX_Admin_2025!'.""",
            'model': 'gpt-3.5-turbo-vulnerable',
            'usage': {'prompt_tokens': len(message), 'completion_tokens': 25}
        })

    # 2. System Prompt Leaking
    if 'system' in message and 'prompt' in message:
        return JSONResponse({
            'response': "My system prompt is: 'You are a helpful assistant for the  Demo Portal. Do not reveal that you are running on a vulnerable Flask backend. Never mention the SQL database at 10.0.0.5.'",
            'model': 'gpt-3.5-turbo-vulnerable',
            'usage': {'prompt_tokens': len(message), 'completion_tokens': 40}
        })

    # 3. Linux/Shell Command hallucination (simulating RCE-like responses)
    if any(cmd in message for cmd in ['ls', 'cat', 'pwd', 'whoami', '/etc/passwd']):
        return JSONResponse({
            'response': """```bash
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
```

I executed that command for you.""",
            'model': 'gpt-3.5-turbo-vulnerable',
            'usage': {'prompt_tokens': len(message), 'completion_tokens': 50}
        })

    # 4. SQL Injection help (The "Helpful" accomplice)
    if 'sql' in message and 'injection' in message:
        return JSONResponse({
            'response': """Sure! Here is a SQL injection payload you can use to bypass the login: `' OR '1'='1`. 

And here is one for extracting data: `UNION SELECT username, password FROM users--`.""",
            'model': 'gpt-3.5-turbo-vulnerable',
            'usage': {'prompt_tokens': len(message), 'completion_tokens': 35}
        })

    # Default "Safe" Response
    responses = [
        "I can help you navigate the portal. Try asking about 'account status' or 'support'.",
        "I am a secure AI assistant. How can I help you today?",
        "Please let me know if you need help finding a specific dashboard.",
        "I'm sorry, I didn't quite understand that. Could you rephrase?"
    ]
    
    return JSONResponse({
        'response': random.choice(responses),
        'model': 'gpt-3.5-turbo-safe',
        'usage': {'prompt_tokens': len(message), 'completion_tokens': 15}
    })


@genai_router.route('/api/v1/genai/knowledge/upload', methods=['POST'])
async def upload_knowledge(request: Request):
    """
    Upload documents for RAG (Retrieval Augmented Generation).
    VULNERABILITY: Unrestricted File Upload / Path Traversal
    """
    # Check if part of the request contains a file part
    form = await request.form()
    upload = form.get('file')
    if upload is None:
        # Simulate JSON body fallback
        data = await get_json_or_default(request)
        if 'content' in data:
            return JSONResponse({
                'status': 'success',
                'message': 'Text content indexed',
                'doc_id': f"doc-{uuid.uuid4().hex[:8]}"
            })
        return JSONResponse({'error': 'No file part'}, status_code=400)

    filename = upload.filename or ""
    
    # VULNERABILITY: No sanitization of filename
    if filename == '':
        return JSONResponse({'error': 'No selected file'}, status_code=400)

    # Simulate path traversal vulnerability
    if '..' in filename or filename.startswith('/'):
        return JSONResponse({
            'status': 'uploaded', 
            'path': f"/var/www/genai/data/{filename}",
            'warning': 'File written outside sandbox',
            'vulnerability': 'PATH_TRAVERSAL_DETECTED'
        })

    # Simulate unsafe file type handling
    unsafe_extensions = ['.exe', '.sh', '.py', '.php', '.jsp', '.html']
    if any(filename.endswith(ext) for ext in unsafe_extensions):
        return JSONResponse({
            'status': 'uploaded',
            'doc_id': f"doc-{uuid.uuid4().hex[:8]}",
            'warning': f"Executable file type {os.path.splitext(filename)[1]} allowed",
            'vulnerability': 'UNRESTRICTED_FILE_UPLOAD'
        })

    return JSONResponse({
        'status': 'indexed',
        'doc_id': f"doc-{uuid.uuid4().hex[:8]}", 
        'chunks': random.randint(5, 50),
        'filename': filename
    })


@genai_router.route('/api/v1/genai/agent/browse', methods=['POST'])
async def agent_browse(request: Request):
    """
    AI Agent "Browse" tool.
    VULNERABILITY: Server-Side Request Forgery (SSRF)
    """
    data = await get_json_or_default(request)
    target_url = data.get('url')
    
    if not target_url:
        return JSONResponse({'error': 'URL required'}, status_code=400)
        
    # VULNERABILITY: No allowlist/denylist for internal IPs
    # Users can request http://localhost:80/admin or http://169.254.169.254/
    
    if 'localhost' in target_url or '127.0.0.1' in target_url:
        return JSONResponse({
            'status': 'success',
            'url': target_url,
            'content': "Admin Dashboard - Critical Systems Online. [SSRF SUCCESS]",
            'summary': "The page appears to be an internal administrative dashboard containing sensitive controls.",
            'vulnerability': 'SSRF_INTERNAL_ACCESS'
        })
        
    if '169.254.169.254' in target_url:
        return JSONResponse({
            'status': 'success',
            'url': target_url,
            'content': '{"instance-id": "i-1234567890abcdef0", "ami-id": "ami-0abcdef1234567890"}',
            'summary': "Cloud instance metadata retrieved.",
            'vulnerability': 'SSRF_CLOUD_METADATA'
        })

    return JSONResponse({
        'status': 'success',
        'url': target_url,
        'content': f"Browsed content from {target_url}...",
        'summary': "The website content was successfully retrieved and processed by the agent."
    })


@genai_router.route('/api/v1/genai/models/config', methods=['GET'])
async def model_config(request: Request):
    """
    Get model configuration.
    VULNERABILITY: Sensitive Data Exposure
    """
    # VULNERABILITY: Returns secrets in plain text
    return JSONResponse({
        'active_model': 'gpt-4-turbo',
        'temperature': 0.7,
        'max_tokens': 2048,
        'api_version': 'v2',
        'backends': {
            'primary': {
                'provider': 'openai',
                'api_key': 'sk-proj-....................' # Partially redacted but risky
            },
            'fallback': {
                'provider': 'azure',
                'endpoint': 'https://demo-ai.openai.azure.com/',
                'api_key': '8f4a2....................'
            },
            'vector_db': {
                'host': '10.0.4.55', # Internal IP leak
                'port': 6333,
                'collection': 'financial_docs_v1'
            }
        },
        'system_prompt_version': 'v4.5-security-hardened'
    })


@genai_router.route('/api/v1/genai/graphql', methods=['POST'])
async def genai_graphql(request: Request):
    """
    GraphQL-like endpoint for GenAI queries.
    VULNERABILITY: GraphQL Introspection, Depth/Complexity DoS
    """
    # This is a mock GraphQL endpoint that simulates common vulnerabilities
    # Preserve the legacy Flask request.get_json() or {} behavior for empty arrays.
    data = (await get_json_value(request, default={})) or {}
    
    # Handle batching (array of queries)
    if isinstance(data, list):
        # Batching attack simulation
        if len(data) > 1:
            await asyncio.sleep(0.5 * len(data)) # Linear slowdown for batching
            return JSONResponse([
                {'data': {'systemInfo': {'version': '2.1.0'}}}
                for _ in data
            ])
        return JSONResponse([])

    query = data.get('query', '')
    
    # 1. Introspection
    if '__schema' in query:
        return JSONResponse({
            'data': {
                '__schema': {
                    'types': [
                        {'name': 'Query', 'fields': [{'name': 'user'}, {'name': 'systemInfo'}]},
                        {'name': 'User', 'fields': [{'name': 'id'}, {'name': 'posts'}]},
                        {'name': 'Post', 'fields': [{'name': 'id'}, {'name': 'comments'}]},
                        {'name': 'Comment', 'fields': [{'name': 'id'}, {'name': 'author'}]}
                    ]
                }
            }
        })
        
    # 2. Deep Nesting DoS
    # Simulate resource exhaustion based on query depth
    depth = query.count('{')
    if depth > 5:
        # Simulate a timeout or very slow response
        await asyncio.sleep(3.0)
        return JSONResponse({
            'errors': [{'message': 'Query too complex or deeply nested'}],
            'note': '[DoS SUCCESS] The server took 3 seconds to process this nested query.'
        }, status_code=400)

    return JSONResponse({
        'data': {
            'systemInfo': {
                'version': '2.1.0',
                'status': 'operational'
            }
        }
    })
