# Alembic Database Migrations Guide

## Overview

This document provides instructions for running and managing database migrations for the SIR (South African service-at-home) marketplace backend.

## Migration Files

### 1. `001_add_bidding_system.py`
**Phase**: 1-2 (Bidding System)
**Creates**:
- `provider_bids` table - Stores each provider's bid on a booking request
- `service_pricing_ranges` table - Stores recommended price ranges for cosmetic/trainer services

**Modifies**:
- `bookings` table - Adds columns: `bid_status`, `bid_expires_at`, `final_price`

**Tables Created**:
```sql
provider_bids (
  id INT PRIMARY KEY,
  booking_id INT FOREIGN KEY,
  provider_id INT FOREIGN KEY,
  bid_price VARCHAR,
  bid_message TEXT,
  status VARCHAR(20) DEFAULT 'PENDING',
  created_at DATETIME DEFAULT NOW(),
  updated_at DATETIME DEFAULT NOW()
)

service_pricing_ranges (
  id INT PRIMARY KEY,
  service_id INT FOREIGN KEY,
  min_price VARCHAR,
  max_price VARCHAR,
  description TEXT,
  category VARCHAR,
  created_at DATETIME DEFAULT NOW(),
  updated_at DATETIME DEFAULT NOW()
)
```

**Columns Added to bookings**:
- `bid_status` VARCHAR(20) - Tracks booking request status in bidding flow
  - OPEN_FOR_BIDS: Waiting for provider bids
  - BIDS_RECEIVED: At least one bid received
  - PROVIDER_SELECTED: Customer selected a provider
  - EXPIRED: Bidding period expired
- `bid_expires_at` DATETIME - When bid window closes
- `final_price` VARCHAR - Price selected by customer (from chosen bid)

### 2. `002_add_rating_system.py`
**Phase**: 4 (Rating & Completion System)
**Modifies**:
- `provider_profiles` table - Adds columns for rating aggregation

**Columns Added to provider_profiles**:
- `average_rating` VARCHAR DEFAULT '0.0' - Calculated average of all ratings (e.g., "4.5")
- `total_ratings` INT DEFAULT 0 - Total number of ratings received

---

## Prerequisites

### 1. Python Dependencies
Ensure all requirements are installed:
```bash
pip install -r requirements.txt
```

Key packages:
- `alembic==1.13.1` - Database migration tool
- `sqlalchemy==2.0.23` - ORM
- `psycopg2-binary==2.9.9` - PostgreSQL driver (async via asyncpg)
- `python-dotenv==1.0.0` - Environment variable loading

### 2. Database Setup
Ensure PostgreSQL is running and accessible:

```bash
# Create database (if not exists)
createdb sir_dev

# Verify connection
psql -U user -h localhost -d sir_dev -c "SELECT version();"
```

### 3. Environment Configuration
Verify `.env` or `app/core/config.py` contains correct database URL:
```python
database_url = "postgresql://user:password@localhost:5432/sir_dev"
```

The `alembic.ini` file will automatically use this URL via `env.py`.

---

## Running Migrations

### 1. Install Alembic (if not already done)
```bash
pip install alembic
```

### 2. Check Migration Status
```bash
cd /Users/taku/Documents/DEV/ser_be
alembic current          # Show current database version
alembic history          # Show all migrations
```

### 3. Apply All Pending Migrations (Forward)
```bash
cd /Users/taku/Documents/DEV/ser_be
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001_add_bidding_system, Add bidding, pricing ranges, and rating system
INFO  [alembic.runtime.migration] Running upgrade 001_add_bidding_system -> 002_add_rating_system, Add rating system columns to provider profiles
```

### 4. Apply Specific Migration
```bash
# Apply only first migration
alembic upgrade 001_add_bidding_system

# Apply only second migration (if first is already applied)
alembic upgrade 002_add_rating_system
```

### 5. Rollback Migrations (Reverse)
```bash
# Rollback all migrations
alembic downgrade base

# Rollback to specific version
alembic downgrade 001_add_bidding_system

# Rollback one migration
alembic downgrade -1
```

---

## What Gets Created/Modified

### Phase 1-2: Bidding System (001_add_bidding_system)

#### New Table: provider_bids
- Tracks each provider's bid on a booking request
- Status flow: PENDING → ACCEPTED/REJECTED/WITHDRAWN
- Indexed on: booking_id, provider_id, status

**Sample data after booking creation**:
```
id | booking_id | provider_id | bid_price | bid_message | status  | created_at
1  | 123        | 5           | "700.00"  | "45 min"    | PENDING | 2026-09-12 14:00:00
2  | 123        | 8           | "750.00"  | "30 min"    | PENDING | 2026-09-12 14:05:00
```

#### New Table: service_pricing_ranges
- Stores recommended price ranges for cosmetic/trainer services
- Examples: Haircut R200-R400, Massage 60min R300-R600

**Sample data**:
```
id | service_id | min_price | max_price | category     | description
1  | 3          | "200"     | "400"     | HAIRCUT      | "Haircut - basic to premium"
2  | 4          | "250"     | "600"     | HAIR_STYLE   | "Hair styling/braiding"
3  | 5          | "200"     | "500"     | MASSAGE_30M  | "30-minute massage"
```

#### Modified Table: bookings
New columns track the bidding lifecycle:

```
id  | customer_id | service_id | bid_status        | bid_expires_at      | final_price | provider_id
123 | 1           | 2          | OPEN_FOR_BIDS     | 2026-09-12 18:00:00 | NULL        | NULL
    ↓ (bids come in)
123 | 1           | 2          | BIDS_RECEIVED     | 2026-09-12 18:00:00 | NULL        | NULL
    ↓ (customer selects)
123 | 1           | 2          | PROVIDER_SELECTED | 2026-09-12 18:00:00 | "700.00"    | 5
```

### Phase 4: Rating System (002_add_rating_system)

#### Modified Table: provider_profiles
New columns for rating aggregation:

```
provider_id | average_rating | total_ratings
5           | "4.5"          | 42
8           | "4.8"          | 15
```

---

## Verification

After running migrations, verify the new tables and columns exist:

```sql
-- List all tables
\dt

-- Check provider_bids table
SELECT * FROM provider_bids LIMIT 5;
\d provider_bids

-- Check service_pricing_ranges table
SELECT * FROM service_pricing_ranges LIMIT 5;
\d service_pricing_ranges

-- Check bookings columns
\d bookings
-- Should show: bid_status, bid_expires_at, final_price

-- Check provider_profiles columns
\d provider_profiles
-- Should show: average_rating, total_ratings
```

---

## Troubleshooting

### Migration fails with "no such table"
**Cause**: Base tables (bookings, services, users, provider_profiles) don't exist yet.
**Solution**: 
1. Create base tables first (main application initialization)
2. Then run alembic migrations

### "sqlalchemy.url not found" error
**Cause**: alembic.ini doesn't have database URL configured
**Solution**:
```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://user:password@localhost:5432/sir_dev"

# Or edit alembic.ini directly
vim alembic.ini  # Set sqlalchemy.url
```

### "relation 'bookings' does not exist"
**Cause**: Trying to add columns to bookings table that hasn't been created
**Solution**: Ensure base application has created all tables first via FastAPI models or initial migration

### Async connection errors
**Cause**: Alembic uses sync connections, but app uses async (asyncpg)
**Solution**: This is expected. Alembic migrations run synchronously to set up schema. The app will use async connections at runtime.

---

## Testing the Migration

### Quick Test: Run Application
```bash
cd /Users/taku/Documents/DEV/ser_be
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs and test endpoints:
- Create a booking → verifies bid_status column works
- Place a bid → verifies provider_bids table works
- Create rating → verifies average_rating column works

### Database Inspection
```bash
# Connect to database
psql -U user -d sir_dev

# Check migration history
SELECT * FROM alembic_version;

# Verify new tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

# Verify new columns in bookings
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'bookings' AND column_name IN ('bid_status', 'bid_expires_at', 'final_price');
```

---

## Migration Best Practices

### Before Running in Production

1. **Backup Database**:
   ```bash
   pg_dump -U user sir_dev > backup_before_migration.sql
   ```

2. **Test on Development Database First**:
   ```bash
   # Create test DB
   createdb sir_dev_test
   
   # Run migrations
   alembic upgrade head
   
   # Verify
   psql -U user -d sir_dev_test -c "SELECT * FROM alembic_version;"
   ```

3. **Check Migration Time**:
   - Both migrations are lightweight (just DDL statements)
   - Expected time: < 1 second
   - No data loss or downtime required

4. **Verify Indexes**:
   Migration creates indexes on:
   - provider_bids: (booking_id, provider_id, status)
   - service_pricing_ranges: (service_id)
   - bookings: (bid_status)
   - provider_profiles: (average_rating)

### Rolling Back

To rollback if issues arise:
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to before all migrations
alembic downgrade base

# Restore from backup if needed
psql -U user sir_dev < backup_before_migration.sql
```

---

## Next Steps After Migration

1. **Update FastAPI Models** (already done in codebase):
   - ProviderBid model → provider_bids table ✅
   - ServicePricingRange model → service_pricing_ranges table ✅
   - Booking model with bid_status columns ✅
   - ProviderProfile model with rating columns ✅

2. **Populate Reference Data**:
   ```python
   # Recommended service pricing ranges
   INSERT INTO service_pricing_ranges (service_id, min_price, max_price, category)
   VALUES 
     (3, '200', '400', 'HAIRCUT'),
     (4, '250', '600', 'HAIR_STYLE'),
     (5, '150', '350', 'NAILS'),
     (6, '200', '500', 'LASHES'),
     (7, '250', '600', 'MAKEUP'),
     (8, '200', '400', 'MASSAGE_30M'),
     (8, '300', '600', 'MASSAGE_60M'),
     (8, '400', '800', 'MASSAGE_90M'),
     (9, '200', '400', 'TRAINING_30M'),
     (9, '300', '600', 'TRAINING_60M'),
     (9, '400', '800', 'TRAINING_90M');
   ```

3. **Run Application Tests**:
   ```bash
   pytest tests/
   ```

4. **Deploy Backend**:
   - Start FastAPI server
   - Test all 30 endpoints
   - Monitor logs for any issues

---

## Related Files

- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Migration environment setup
- `alembic/script.py.mako` - Migration file template
- `alembic/versions/001_add_bidding_system.py` - Bidding system migration
- `alembic/versions/002_add_rating_system.py` - Rating system migration
- `app/db/database.py` - Database connection setup
- `app/models/` - SQLAlchemy models (already updated)
- `app/core/config.py` - Database URL configuration

---

## Summary

✅ **2 migrations created** for phases 1-4 implementation
- Creates provider_bids, service_pricing_ranges tables
- Adds bid_status, bid_expires_at, final_price to bookings
- Adds average_rating, total_ratings to provider_profiles

✅ **All DDL statements** are backward-compatible with downgrade functions
✅ **All indexes** created for query performance
✅ **Ready for production** deployment

**Run command**: `alembic upgrade head`
