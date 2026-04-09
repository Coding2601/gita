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
└── resources/                 # Static resources
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
