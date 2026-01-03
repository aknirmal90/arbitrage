# CLAUDE.md - AI Assistant Guide for Arbitrage Project

## Project Overview

This is a **cryptocurrency arbitrage monitoring system** built with Django 1.11 that integrates with the Coinigy API to track cryptocurrency exchanges, markets, and ticker prices for potential arbitrage opportunities.

**Primary Function:** Automated synchronization of cryptocurrency market data from Coinigy API, with admin-based management of tracked exchanges and markets.

**Tech Stack:**
- **Framework:** Django 1.11.7 (Python web framework)
- **Task Queue:** Celery 3.1.25 with Redis broker
- **Database:** PostgreSQL (via psycopg2)
- **Web Server:** Gunicorn 19.7.1
- **API Integration:** Coinigy REST API and WebSocket

## Architecture

### High-Level Data Flow

```
┌─────────────────┐
│  Celery Beat    │──── Every minute ────┐
│   (Scheduler)   │                      │
└─────────────────┘                      │
                                         ▼
┌─────────────────┐              ┌──────────────┐
│  Coinigy API    │◄─────────────│ SyncTicker   │
│  (External)     │              │  Task        │
└─────────────────┘              └──────────────┘
        │                               │
        │ Ticker Data                   │ Save
        ▼                               ▼
┌─────────────────┐              ┌──────────────┐
│   PostgreSQL    │              │  Market      │
│   Database      │◄─────────────│  Models      │
└─────────────────┘              └──────────────┘
        │                               ▲
        │                               │
        ▼                               │
┌─────────────────┐                     │
│  Django Admin   │─────────────────────┘
│   Interface     │  Manage enabled markets
└─────────────────┘
```

### Application Structure

This project uses **Django's app-based architecture**:

1. **markets** - Core app for exchange/market/ticker tracking
2. **transactions** - Placeholder app (currently inactive)
3. **coinigy** - API client library (not a Django app)
4. **arbitrage** - Main Django project configuration

## Directory Structure

```
/home/user/arbitrage/
├── arbitrage/                    # Main Django project
│   ├── settings/
│   │   ├── settings_generic.py   # Django core settings
│   │   └── settings_celery.py    # Celery configuration
│   ├── celeryapp.py              # Celery app initialization
│   ├── urls.py                   # URL routing (only /admin/)
│   └── wsgi.py                   # WSGI entry point
├── markets/                      # Markets Django app
│   ├── models.py                 # Coin, Exchange, Market, Ticker models
│   ├── tasks.py                  # Celery tasks (SyncExchanges, SyncMarkets, SyncTicker)
│   ├── forms.py                  # ModelForms for validation
│   ├── admin.py                  # Django admin customization
│   └── migrations/               # Database migrations
├── transactions/                 # Empty app (no active models)
├── coinigy/                      # Coinigy API client
│   ├── base.py                   # REST API client
│   └── websocket.py              # WebSocket client (not integrated)
├── bin/                          # Scripts and utilities
│   ├── env_variables.py          # Environment variable loader
│   ├── start-celery.sh           # Celery worker startup
│   ├── start-webapp.sh           # Gunicorn startup
│   └── startup.sh                # Screen session orchestrator
├── manage.py                     # Django management script
├── gunicorn.conf.py              # Gunicorn configuration
├── requirements.txt              # Python dependencies (pip-compile output)
└── requirements.in               # Dependency source file
```

## Core Models

### Location: `/home/user/arbitrage/markets/models.py`

#### 1. Coin
```python
- name: CharField(10)
```
Simple model for cryptocurrency identifiers.

#### 2. Exchange
```python
- exch_balance_enabled: BooleanField
- exch_code: CharField(10)           # e.g., "BTRX", "GDAX"
- exch_fee: DecimalField(14, 6)
- exch_id: IntegerField              # Coinigy exchange ID
- exch_name: CharField(80)
- exch_trade_enabled: BooleanField
- exch_url: CharField(160)
- is_user_enabled: BooleanField      # IMPORTANT: Controls if exchange is tracked
```

**Key Behavior:** Only exchanges where `is_user_enabled=True` will have their markets tracked.

#### 3. Market
```python
- exchange: ForeignKey(Exchange)
- mkt_id: IntegerField               # Coinigy market ID
- mkt_name: CharField(20)            # e.g., "BTC/USD"
- exchmkt_id: IntegerField
- currency_one: CharField(10, null=True)
- currency_two: CharField(10, null=True)
- is_user_enabled: BooleanField      # IMPORTANT: Controls if market is tracked
```

**Unique Constraint:** (exchange, mkt_id)

**Key Behavior:** Only markets where BOTH `market.is_user_enabled=True` AND `market.exchange.is_user_enabled=True` will have ticker data synced.

#### 4. Ticker
```python
- market: ForeignKey(Market)
- last_trade: DecimalField(36, 18)   # High precision for crypto prices
- high_trade: DecimalField(36, 18)
- low_trade: DecimalField(36, 18)
- current_volume: DecimalField(36, 18)
- timestamp: DateTimeField
- ask: DecimalField(36, 18)
- bid: DecimalField(36, 18)
```

**Note:** Uses extremely high precision (36 digits, 18 decimal places) to handle cryptocurrency price ranges.

## Celery Tasks

### Location: `/home/user/arbitrage/markets/tasks.py`

### 1. SyncExchanges
**Purpose:** Sync all exchanges from Coinigy API
**Trigger:** Manual or periodic
**Endpoint:** `exchanges` (POST)
**Behavior:** Creates or updates Exchange records

### 2. SyncMarkets
**Purpose:** Sync all markets for all exchanges
**Trigger:** Manual or periodic
**Endpoint:** `markets` (POST)
**Behavior:**
- Fetches markets for each exchange
- Parses currency pairs from market names (e.g., "BTC/USD" → currency_one="BTC", currency_two="USD")
- 0.5 second delay between exchanges to avoid rate limiting

### 3. SyncTicker (SCHEDULED)
**Purpose:** Sync ticker data for enabled markets
**Trigger:** **Every minute** (Celery Beat crontab)
**Endpoint:** `ticker` (POST)
**Behavior:**
- Only processes markets where `market.is_user_enabled=True` AND `market.exchange.is_user_enabled=True`
- Creates Ticker records for each enabled market
- Uses TickerForm for validation

**IMPORTANT:** This is the only scheduled task and runs continuously every minute.

## Coinigy API Integration

### REST API Client: `/home/user/arbitrage/coinigy/base.py`

```python
Base URL: https://api.coinigy.com/api/v1/
Authentication:
  - Header: X-API-KEY (from COININGY_USERNAME env var)
  - Header: X-API-SECRET (from COININGY_APISECRET env var)
```

### WebSocket Client: `/home/user/arbitrage/coinigy/websocket.py`

```python
WebSocket URL: wss://sc-02.coinigy.com/socketcluster/
Status: Implemented but NOT integrated into main workflow
```

**Note:** WebSocket client exists for real-time data but is currently unused.

## Environment Variables

### Required

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/arbitrage

# Coinigy API Credentials
COININGY_USERNAME=your_api_key
COININGY_APISECRET=your_api_secret
```

### Optional

```bash
# Celery
CELERY_BROKER_URL=redis://127.0.0.1:6379/0  # Default
CELERYD_TASK_TIME_LIMIT=9000                # Default: 9000 seconds

# Server
SERVER_ENV=production  # Set to skip local variables loading
```

### Local Development Variables

For local development, create `/home/user/arbitrage/bin/local_variables.py`:

```python
env_vars = {
    'DATABASE_URL': 'postgresql://user:password@localhost:5432/arbitrage',
    'COININGY_USERNAME': 'your_api_key',
    'COININGY_APISECRET': 'your_api_secret',
}
```

**IMPORTANT:** This file is gitignored and only loaded in non-production environments.

## Development Workflow

### Initial Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create local variables file
# Create bin/local_variables.py with env_vars dictionary

# 3. Run migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Start services (uses GNU Screen)
./bin/startup.sh
```

### Service Management

**Using startup.sh (Recommended):**
```bash
./bin/startup.sh
```
Creates a Screen session with:
- Tab 1: Web server (Gunicorn on port 8080)
- Tab 2: Celery worker (with Beat scheduler)
- Tab 3: Redis server

**Manual service start:**
```bash
# Web server
./bin/start-webapp.sh

# Celery worker with Beat
./bin/start-celery.sh

# Redis (if not running)
redis-server
```

### Admin Interface

Access Django admin at `http://localhost:8080/admin/`

**Key Admin Tasks:**
1. Enable/disable exchanges via admin actions
2. Enable/disable markets via admin actions
3. Filter markets by exchange, currency_one, currency_two
4. View ticker history for markets

## Common Development Tasks

### Adding a New Field to a Model

```bash
# 1. Edit models.py
# 2. Create migration
python manage.py makemigrations markets

# 3. Apply migration
python manage.py migrate markets
```

### Running Celery Tasks Manually

```python
# Django shell
python manage.py shell

from markets.tasks import SyncExchanges, SyncMarkets, SyncTicker

# Run synchronously
SyncExchanges().run()
SyncMarkets().run()
SyncTicker().run()

# Run asynchronously
SyncExchanges.delay()
```

### Database Access

```bash
# Django shell
python manage.py shell

from markets.models import Exchange, Market, Ticker

# Query enabled markets
enabled_markets = Market.objects.filter(
    is_user_enabled=True,
    exchange__is_user_enabled=True
)

# Get recent tickers
recent_tickers = Ticker.objects.order_by('-timestamp')[:100]
```

### Updating Dependencies

```bash
# Edit requirements.in
# Then compile
pip-compile --output-file requirements.txt requirements.in

# Install
pip install -r requirements.txt
```

## Key Conventions & Patterns

### 1. User Enablement Pattern

**CRITICAL:** The system uses `is_user_enabled` flags to control what data is tracked:
- Exchange level: `exchange.is_user_enabled`
- Market level: `market.is_user_enabled`
- Ticker sync only processes markets where BOTH are True

**Use Case:** Reduce API calls and database size by only tracking relevant markets.

### 2. Form-Based Validation

All model data from API goes through Django ModelForms:
- `ExchangeForm` - validates Exchange data
- `MarketForm` - validates Market data
- `TickerForm` - validates Ticker data

**Location:** `/home/user/arbitrage/markets/forms.py`

### 3. Admin-Centric Interface

No public views or API endpoints exist. All management is through Django admin:
- Enable/disable exchanges and markets
- View historical ticker data
- Monitor synchronization status

### 4. Celery Task Naming

Tasks follow `Sync<Entity>` pattern:
- `SyncExchanges`
- `SyncMarkets`
- `SyncTicker`

### 5. Split Settings Architecture

Settings are split across multiple files:
- `settings_generic.py` - Django core settings
- `settings_celery.py` - Celery configuration
- `__init__.py` - Imports both

**Benefit:** Cleaner organization, easier to maintain separate concerns.

### 6. High-Precision Decimals

All price fields use `DecimalField(36, 18)`:
- 36 total digits
- 18 decimal places
- Handles both very small (0.000000001 BTC) and large values

## Important Files Reference

### Configuration
- `/home/user/arbitrage/arbitrage/settings/settings_generic.py` - Django settings
- `/home/user/arbitrage/arbitrage/settings/settings_celery.py` - Celery config
- `/home/user/arbitrage/gunicorn.conf.py` - Gunicorn server config
- `/home/user/arbitrage/bin/env_variables.py` - Environment loader

### Core Logic
- `/home/user/arbitrage/markets/models.py` - Database models
- `/home/user/arbitrage/markets/tasks.py` - Celery sync tasks
- `/home/user/arbitrage/markets/forms.py` - Validation forms
- `/home/user/arbitrage/markets/admin.py` - Admin interface

### API Integration
- `/home/user/arbitrage/coinigy/base.py` - REST API client
- `/home/user/arbitrage/coinigy/websocket.py` - WebSocket client (unused)

### Deployment
- `/home/user/arbitrage/bin/startup.sh` - Service orchestrator
- `/home/user/arbitrage/bin/start-webapp.sh` - Web server start
- `/home/user/arbitrage/bin/start-celery.sh` - Celery worker start

## Known Issues & Limitations

### Security Issues

1. **SECRET_KEY hardcoded** in `settings_generic.py:24`
   - Should be environment variable
   - Current value should NOT be used in production

2. **DEBUG=True hardcoded** in `settings_generic.py:27`
   - Should be environment-based
   - Dangerous in production

3. **ALLOWED_HOSTS empty** in `settings_generic.py:29`
   - Will cause errors in production
   - Must be configured before deployment

### Architectural Limitations

1. **No Tests:** Test files exist but are empty stubs
2. **No API Endpoints:** Only admin interface available
3. **No Public Views:** Everything is admin-only
4. **Transactions App Empty:** Created but unused
5. **WebSocket Not Integrated:** Client exists but not used
6. **Old Dependencies:** Django 1.11.7 is EOL (End of Life)

### Operational Considerations

1. **API Rate Limiting:** 0.5 second delay in SyncMarkets, may need adjustment
2. **High Data Volume:** Ticker syncs every minute for all enabled markets
3. **No Data Retention Policy:** Tickers accumulate indefinitely
4. **No Error Alerting:** Failed tasks only visible in logs

## Testing Guidelines

### Current State
No tests implemented. Test infrastructure exists but unused.

### Recommended Testing Approach

```python
# Example test structure (not yet implemented)
from django.test import TestCase
from markets.models import Exchange, Market, Ticker
from markets.tasks import SyncTicker

class MarketModelTestCase(TestCase):
    def setUp(self):
        self.exchange = Exchange.objects.create(
            exch_id=1,
            exch_code='TEST',
            exch_name='Test Exchange',
            is_user_enabled=True
        )

    def test_enabled_markets_filter(self):
        # Test that only enabled markets are returned
        pass
```

### Testing Celery Tasks

```python
# Use Celery's eager mode for synchronous testing
CELERY_ALWAYS_EAGER = True
```

## Git Workflow

### Branch Strategy
- Main branch: `main` (or master)
- Feature branches: Use descriptive names
- AI-generated branches: Must start with `claude/` and end with session ID

### Commit Messages
Follow conventional commit style based on repository history:
- Be concise and descriptive
- Focus on "why" rather than "what"
- Examples from repo:
  - "adding market and transactions app"
  - "some boilerplate code"
  - "delete local_vars"

### Before Committing

```bash
# Check status
git status

# View changes
git diff

# View recent commits for style guidance
git log --oneline -10
```

## Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check DATABASE_URL is set
echo $DATABASE_URL

# Test PostgreSQL connection
psql $DATABASE_URL
```

**2. Celery Tasks Not Running**
```bash
# Check Redis is running
redis-cli ping

# Check Celery worker logs
# Look in Screen tab 2 or celery logs
```

**3. Coinigy API Authentication Error**
```bash
# Verify credentials are set
echo $COININGY_USERNAME
echo $COININGY_APISECRET

# Test API manually
curl -X POST https://api.coinigy.com/api/v1/exchanges \
  -H "X-API-KEY: $COININGY_USERNAME" \
  -H "X-API-SECRET: $COININGY_APISECRET"
```

**4. Import Errors**
```bash
# Ensure you're in virtual environment
which python

# Reinstall dependencies
pip install -r requirements.txt
```

## Performance Considerations

### Database Queries
- Markets app uses `select_related()` and `prefetch_related()` where appropriate
- Admin list views may be slow with many records
- Consider adding database indexes for frequently filtered fields

### Celery Task Optimization
- `SyncTicker` processes markets sequentially (potential bottleneck)
- Consider using Celery group tasks for parallel processing
- Current task limit: 200 tasks per worker before restart

### Memory Management
- Gunicorn worker count: `(CPU cores * 2) + 1`
- Celery max tasks per child: 200 (prevents memory leaks)
- Connection pooling: 120 second max age

## Future Enhancement Ideas

Based on codebase structure, potential enhancements:

1. **API Endpoints:** Create REST API for accessing market data
2. **WebSocket Integration:** Use existing websocket.py for real-time updates
3. **Arbitrage Detection:** Add logic to identify arbitrage opportunities
4. **Transactions App:** Implement transaction tracking
5. **Data Retention:** Add cleanup tasks for old ticker data
6. **Monitoring:** Add health checks and alerting
7. **Tests:** Implement comprehensive test suite
8. **Upgrade Django:** Move to supported Django version (4.x or 5.x)

## Quick Reference Commands

```bash
# Development
python manage.py runserver              # Dev server (not used, use Gunicorn)
python manage.py shell                  # Django shell
python manage.py dbshell               # Database shell

# Database
python manage.py migrate               # Apply migrations
python manage.py makemigrations        # Create migrations
python manage.py showmigrations        # Show migration status

# Admin
python manage.py createsuperuser       # Create admin user
python manage.py changepassword USER   # Change user password

# Celery
celery -A arbitrage worker -l info     # Start worker
celery -A arbitrage beat -l info       # Start beat scheduler
celery -A arbitrage inspect active     # View active tasks

# Server
./bin/startup.sh                       # Start all services
screen -r                              # Attach to screen session
```

## Contact & Documentation

**Repository:** /home/user/arbitrage
**Django Version:** 1.11.7
**Python Version:** 3.x (check with `python --version`)
**Database:** PostgreSQL

**External Documentation:**
- Django 1.11: https://docs.djangoproject.com/en/1.11/
- Celery 3.1: https://docs.celeryproject.org/en/3.1/
- Coinigy API: https://coinigy.docs.apiary.io/

---

**Last Updated:** 2026-01-03
**AI Assistant:** This file is specifically for AI assistants working on this codebase. Keep it updated as the project evolves.
