import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker processes - using sync workers for compatibility
workers = int(os.environ.get("WEB_CONCURRENCY", 2))
worker_class = "sync"

# Timeouts - increased for slow LLM API calls
timeout = 120  # 2 minutes (default is 30s)
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info")

# Process naming
proc_name = "gita-ai"

# Server mechanics
daemon = False
pidfile = None

# SSL (handled by reverse proxy)
forwarded_allow_ips = "*"
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
