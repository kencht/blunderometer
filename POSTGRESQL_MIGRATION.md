# PostgreSQL Migration Guide

## 🎯 Problem Solved: Persistent Storage on Render.com

Your Chess Blunder Tracker was losing all data on container restarts because it used SQLite files stored in `/tmp` (ephemeral storage). Now it uses **PostgreSQL with 1GB persistent storage** on Render.com's free tier!

## ✅ Benefits of PostgreSQL Migration

- **✅ 1GB Persistent Storage** - Data survives container restarts
- **✅ Multi-user Support** - All users share one database with proper isolation
- **✅ Better Performance** - PostgreSQL handles concurrent users better than SQLite
- **✅ Free on Render.com** - 30-day free PostgreSQL database (upgradeable to paid to keep data)
- **✅ Automatic Backups** - Daily snapshots (paid plans only)

## 🚀 Setup Instructions

### Step 1: Create PostgreSQL Database on Render.com

1. **Log into Render.com Dashboard**
2. **Click "New" → "PostgreSQL"**
3. **Choose "Free" plan** (1GB storage, 30-day limit)
4. **Name your database**: `blunderometer-db`
5. **Click "Create Database"**

### Step 2: Get Database Connection URL

After creating the database:
1. **Go to your database in Render Dashboard**
2. **Copy the "Internal Database URL"** (starts with `postgresql://`)
3. **This URL looks like**: `postgresql://username:password@hostname:port/database`

### Step 3: Configure Your Web Service

1. **Go to your Web Service in Render Dashboard**
2. **Go to "Environment" tab**
3. **Add Environment Variable**:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the PostgreSQL connection URL from Step 2
4. **Save Changes**

### Step 4: Deploy with PostgreSQL

Your application will now automatically:
- ✅ Detect `DATABASE_URL` environment variable
- ✅ Use PostgreSQL instead of SQLite
- ✅ Create tables automatically on first run
- ✅ Persist data across container restarts

## 📊 Migration from Existing SQLite Data

If you have existing SQLite data locally, run the migration script:

```bash
# Set your PostgreSQL URL (get from Render.com dashboard)
export DATABASE_URL="postgresql://username:password@hostname:port/database"

# Run migration script
python migrate_to_postgresql.py
```

This script will:
- ✅ Find all SQLite databases in `data/` folder
- ✅ Copy games and moves to PostgreSQL
- ✅ Preserve all analysis data
- ✅ Handle username-based data isolation

## 🏗️ Database Schema

The PostgreSQL version includes optimizations:

### Games Table
- Added string length constraints for PostgreSQL compatibility
- Composite unique constraint on `(lichess_id, username)` for multi-user support
- Indexes on `username` and `played_at` for performance

### Moves Table
- String length constraints for PostgreSQL
- Indexes on `game_lichess_id`, `played_at`, and `is_blunder` for fast queries

## 🔧 Local Development

For local development, you can still use SQLite:
- **No `DATABASE_URL`** → Uses SQLite files in `data/` folder
- **With `DATABASE_URL`** → Uses PostgreSQL

```bash
# Local development (SQLite)
python app.py

# Test with PostgreSQL locally
export DATABASE_URL="postgresql://localhost/blunderometer_dev"
python app.py
```

## 📈 Monitoring Usage

**Free PostgreSQL Limits:**
- **Storage**: 1GB (more than enough for chess data)
- **Duration**: 30 days (then needs upgrade to paid)
- **Connections**: 100 concurrent

**Upgrade Path:**
- **Basic Plan**: $6/month for persistent database
- **Keeps all your data** when upgrading from free

## 🎯 What Changed

### Before (SQLite + `/tmp`)
- ❌ Data lost on every container restart
- ❌ Separate database file per user
- ❌ No persistence in cloud
- ❌ Users lose all progress

### After (PostgreSQL)
- ✅ Data persists across restarts
- ✅ Single database with user isolation
- ✅ 1GB persistent storage
- ✅ Users keep all their progress

## 🚨 Important Notes

1. **30-Day Limit**: Free PostgreSQL expires after 30 days
2. **Upgrade Before Expiry**: Upgrade to paid plan to keep data
3. **Data Isolation**: Each username gets their own data scope
4. **Performance**: Much better for multiple concurrent users

## 🏁 Deployment Checklist

- [ ] Create PostgreSQL database on Render.com
- [ ] Copy DATABASE_URL to web service environment
- [ ] Deploy application
- [ ] Test with sample username
- [ ] Verify data persists after restart
- [ ] (Optional) Migrate existing SQLite data

Your Chess Blunder Tracker now has **persistent, reliable storage** that won't lose data! 🎉
