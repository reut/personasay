# Database Setup Guide

## Overview

PersonaSay uses SQLite for local development to store:
- Persona conversation memories
- Session IDs for grouping conversations
- User messages and AI responses
- Timestamps and metadata

## Database Files

### `personasay_starter.db` (Committed to Repo)
- **Purpose**: Template database with initial schema
- **Location**: `backend/data/personasay_starter.db`
- **Git Status**: ✅ Tracked and committed
- **Size**: ~1 MB
- **Contains**: Empty tables with proper schema

### `personasay.db` (Local Only)
- **Purpose**: Active runtime database
- **Location**: `backend/data/personasay.db`
- **Git Status**: ❌ Ignored by `.gitignore`
- **Contains**: Your actual conversation data

## Setup Instructions

### For New Clones

When you clone the repository to a new location:

```bash
cd backend
python init_db.py
```

This will:
1. Copy `personasay_starter.db` → `personasay.db`
2. Give you a fresh database with the correct schema
3. Preserve any starter data if included

### Manual Setup

If you prefer to set up manually:

```bash
cd backend/data
cp personasay_starter.db personasay.db
```

### Automatic Setup

The application will automatically create `personasay.db` if it doesn't exist on first run.

## Resetting Your Database

To start fresh with a clean database:

```bash
cd backend
python init_db.py
# Answer 'y' when prompted to overwrite
```

Or manually:

```bash
cd backend/data
rm personasay.db
cp personasay_starter.db personasay.db
```

## Production Considerations

### For Production Deployments

SQLite is great for development but consider these alternatives for production:

1. **PostgreSQL** (Recommended)
   ```python
   # In .env
   DATABASE_URL=postgresql://user:password@host:5432/personasay
   ```

2. **MySQL/MariaDB**
   ```python
   # In .env
   DATABASE_URL=mysql://user:password@host:3306/personasay
   ```

3. **Cloud Databases**
   - AWS RDS
   - Google Cloud SQL
   - Azure Database
   - Supabase
   - PlanetScale

### Migration Steps

1. Update `DATABASE_URL` in `.env`
2. Install appropriate database driver:
   ```bash
   pip install psycopg2-binary  # PostgreSQL
   pip install pymysql          # MySQL
   ```
3. Run migrations (if using Alembic)
4. Restart the application

## Git Configuration

### What's Tracked

```gitignore
# Tracked
!backend/data/personasay_starter.db
backend/data/.gitkeep
```

### What's Ignored

```gitignore
# Ignored
*.db
*.sqlite
*.sqlite3
backend/data/*.db
data/personasay.db
*.db-journal

# Exception for starter
!backend/data/personasay_starter.db
```

## Updating the Starter Database

If you want to update the starter database with new schema or seed data:

```bash
# 1. Make changes to your local database
cd backend
python main.py  # Run migrations, add seed data, etc.

# 2. Copy to starter
cd data
cp personasay.db personasay_starter.db

# 3. Commit the changes
git add personasay_starter.db
git commit -m "Update starter database schema"
git push
```

## Troubleshooting

### Database Locked Error

```
sqlite3.OperationalError: database is locked
```

**Solution**: Close all connections to the database:
```bash
lsof backend/data/personasay.db  # Find processes
kill -9 <PID>                     # Kill the process
```

### Schema Mismatch

```
sqlite3.OperationalError: no such table: persona_memory
```

**Solution**: Reinitialize database:
```bash
cd backend
python init_db.py
```

### Permission Denied

```
PermissionError: [Errno 13] Permission denied: 'personasay.db'
```

**Solution**: Fix permissions:
```bash
chmod 644 backend/data/personasay.db
```

## Database Schema

Current tables:

### `persona_memory`
- `id` (INTEGER PRIMARY KEY)
- `persona_id` (TEXT)
- `session_id` (TEXT)
- `message_type` (TEXT) - "human" or "ai"
- `content` (TEXT)
- `timestamp` (DATETIME)
- `meta_data` (TEXT) - JSON string

## Backup and Recovery

### Backup

```bash
# Simple backup
cp backend/data/personasay.db backup/personasay_$(date +%Y%m%d).db

# With compression
tar -czf backup/personasay_$(date +%Y%m%d).tar.gz backend/data/personasay.db
```

### Restore

```bash
# From simple backup
cp backup/personasay_20260212.db backend/data/personasay.db

# From compressed backup
tar -xzf backup/personasay_20260212.tar.gz
```

## Best Practices

1. **Never commit `personasay.db`** - it contains user data
2. **Do commit `personasay_starter.db`** - it's the template
3. **Backup regularly** if data is important
4. **Use PostgreSQL** for production
5. **Test migrations** on starter database first
6. **Document schema changes** in this file

## Related Files

- `backend/init_db.py` - Database initialization script
- `backend/app/langchain_personas.py` - Database models and queries
- `.gitignore` - Database ignore rules
- `backend/.env` - Database configuration
