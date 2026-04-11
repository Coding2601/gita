# Gita AI

AI-powered Bhagavad Gita companion with semantic search and conversational chat capabilities.

## Overview

Gita AI is a Django-based web application that brings the timeless wisdom of the Bhagavad Gita to modern users through artificial intelligence. The platform combines semantic search technology with large language models to help users explore verses, find relevant teachings, and engage in meaningful spiritual conversations.

## Features

- **Semantic Search**: Find relevant verses based on meaning, not just keywords
- **AI Chat**: Converse with an AI assistant trained on Gita's teachings via `/agent/chat`
- **Rate Limiting**: Token bucket algorithm protects API endpoints using Upstash Redis
- **User Authentication**: Secure JWT-based authentication system
- **Singleton Pattern**: Process-wide Redis client for efficient resource management

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **AI/ML**: Cerebras LLM, BAAI/bge-small-en-v1.5 embeddings
- **Database**: SQLite (development), Upstash Redis (rate limiting)
- **Redis Client**: `upstash-redis` via singleton pattern
- **Middleware**: Custom auth, caching, and token bucket rate limiting

## Rate Limiting Architecture

The application implements a **Token Bucket** rate limiting strategy on the `/agent/chat` endpoint:

| Limit | Default | Description |
|-------|---------|-------------|
| Local (per-user) | 10 req/min | Per authenticated user or IP address |
| Global | 20 req/min | Across all users combined |
| Burst | 15 req | Short-term capacity above sustained rate |
| Interval | 60 seconds | Token refill period |

**Redis Key Structure:**
- `ratelimit:local:user_{id}` - Per-user buckets
- `ratelimit:local:ip:{ip}` - Anonymous user buckets
- `ratelimit:global:all` - Global bucket

**Architecture:**
- `RedisCache` singleton (`singleton.Redis`) manages one Upstash Redis client instance
- `TokenBucketRateLimiter` implements the algorithm
- `RateLimitMiddleware` applies limits to `/agent/chat` only
- Graceful degradation: allows requests if Redis is unavailable

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your UPSTASH_REDIS_REST_URL, CEREBRAS_API_KEY, etc.

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

## Build Script

The `build.sh` script automates deployment setup:

```bash
#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

**Usage:**
```bash
bash build.sh
```

**What it does:**
- Installs Python dependencies from `requirements.txt`
- Collects Django static files (`collectstatic --noinput`)
- Applies database migrations

## Deployment

### Gunicorn Configuration

The `gunicorn.conf.py` file configures the production WSGI server with settings optimized for AI workloads:

```python
# Key settings
timeout = 120          # 2 min (increased from 30s default for slow LLM calls)
workers = 2            # Configurable via WEB_CONCURRENCY env var
bind = "0.0.0.0:8000"  # Port configurable via PORT env var
```

**Why increased timeout?** The `/agent/chat/` endpoint calls the Cerebras LLM API, which can take 30-60+ seconds to generate responses. Without the increased timeout, Gunicorn kills workers mid-request causing **502 errors**.

**Run with Gunicorn:**
```bash
gunicorn gita.wsgi:application --config gunicorn.conf.py
```

**Or with environment variables:**
```bash
PORT=8000 WEB_CONCURRENCY=2 gunicorn gita.wsgi:application --config gunicorn.conf.py
```

### Production Checklist

- [ ] Run `build.sh` to collect static files and migrate database
- [ ] Set `DEBUG=False` in environment
- [ ] Configure `STATIC_ROOT` for static file serving
- [ ] Set `ALLOWED_HOSTS` with your domain
- [ ] Configure `CSRF_TRUSTED_ORIGINS` with your frontend URL
- [ ] Use Gunicorn with the provided config (not `runserver`)

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `UPSTASH_REDIS_REST_URL` | Yes | - | Upstash Redis REST API URL |
| `UPSTASH_REDIS_REST_TOKEN` | Yes | - | Upstash Redis authentication token |
| `CEREBRAS_API_KEY` | Yes | - | LLM API key for chat functionality |
| `RATE_LIMIT_LOCAL` | No | 10 | Per-user request limit per interval |
| `RATE_LIMIT_GLOBAL` | No | 20 | Global request limit per interval |
| `RATE_LIMIT_INTERVAL` | No | 60 | Token refill interval in seconds |
| `RATE_LIMIT_BURST` | No | 15 | Burst capacity above sustained rate |
| `SECRET_KEY` | Yes | - | Django secret key |
| `DEBUG` | No | False | Django debug mode |
| `PORT` | No | 8000 | Server port (Gunicorn) |
| `WEB_CONCURRENCY` | No | 2 | Number of Gunicorn workers |
| `LOG_LEVEL` | No | info | Gunicorn log level (debug/info/warning/error) |

## API Endpoints

| Endpoint | Method | Description | Rate Limited |
|----------|--------|-------------|--------------|
| `/agent/search/` | POST | Semantic search across Gita verses | No |
| `/agent/chat/` | POST | AI conversation with context | Yes |

### Rate Limit Response (HTTP 429)

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please wait before retrying.",
  "limit_type": "local",
  "retry_after": 6,
  "limit": 10,
  "window": 60
}
```

**Headers:**
- `Retry-After`: Seconds until next request allowed
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Timestamp when limit resets

## Project Structure

```
gita/
├── agent/
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── rate_limit.py      # Token bucket rate limiting
│   ├── urls.py
│   └── views.py
├── singleton/
│   └── Redis.py               # Process-wide Redis singleton
├── user/                      # Authentication & user management
├── manager/                   # Admin utilities
├── gita/                      # Core Django settings & middleware
├── resources/                 # Static resources
├── build.sh                   # Deployment build script
└── gunicorn.conf.py           # Gunicorn WSGI server config
```

## Middleware Stack

```python
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "user.middlewares.authmiddleware.AuthMiddleware",
    "agent.middleware.rate_limit.RateLimitMiddleware",  # Rate limiting
    "gita.middlewares.cachemiddleware.CacheMiddleware",
    # ... Django defaults
]
```

## Dependencies

```
Django==4.2.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
upstash-redis>=1.0.0
```

## License

This project is open source.
