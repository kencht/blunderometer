# 🚀 Deploy Chess Blunder Tracker with Persistent PostgreSQL Storage

## ✅ Problem Solved!

Your Chess Blunder Tracker now uses **PostgreSQL with 1GB persistent storage** instead of ephemeral SQLite files. **No more data loss on container restarts!**

## 🎯 Quick Start Deployment

### 1. Create PostgreSQL Database

1. **Go to [Render.com Dashboard](https://dashboard.render.com/)**
2. **Click "New" → "PostgreSQL"**
3. **Select "Free" plan** (1GB storage)
4. **Name**: `blunderometer-db`
5. **Click "Create Database"**
6. **Copy the "Internal Database URL"** (starts with `postgresql://`)

### 2. Update Web Service Environment

1. **Go to your existing Web Service in Render**
2. **Environment tab → Add Environment Variable**:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the PostgreSQL URL from step 1
3. **Save Changes**

### 3. Deploy

Your next deployment will automatically:
- ✅ Use PostgreSQL instead of SQLite
- ✅ Create database tables automatically  
- ✅ Persist all data across restarts
- ✅ Support multiple users concurrently

## 📊 Migrate Existing Data (Optional)

If you have existing SQLite data locally:

```bash
# Set your PostgreSQL connection (from Render dashboard)
export DATABASE_URL="postgresql://username:password@hostname:port/database"

# Run migration
python migrate_to_postgresql.py
```

## 🧪 Test Your Setup

```bash
# Test locally (uses SQLite)
python test_postgresql.py

# Test with PostgreSQL (set DATABASE_URL first)
export DATABASE_URL="your_postgresql_url"
python test_postgresql.py
```

## 📈 What You Get

### Storage Upgrade
- **Before**: SQLite in `/tmp` (ephemeral, lost on restart)
- **After**: PostgreSQL (1GB persistent, survives restarts)

### Multi-User Support
- **Before**: Separate SQLite file per user
- **After**: Single PostgreSQL database with user isolation

### Performance
- **Before**: SQLite file locking issues with concurrent users
- **After**: PostgreSQL handles multiple users efficiently

### Data Safety
- **Before**: All data lost on every container restart
- **After**: Data persists indefinitely (30 days free, upgrade to keep)

## 🎮 How It Works

### Database Detection
```python
# Automatically detects PostgreSQL vs SQLite
if os.getenv('DATABASE_URL'):
    # Use PostgreSQL (cloud deployment)
    print("Using PostgreSQL for persistent storage")
else:
    # Use SQLite (local development)
    print("Using SQLite for local development")
```

### User Data Isolation
```sql
-- Each user's data is isolated by username
SELECT * FROM games WHERE username = 'your_username';
SELECT * FROM moves WHERE game_lichess_id IN (
    SELECT lichess_id FROM games WHERE username = 'your_username'
);
```

### Schema Optimizations
- String length constraints for PostgreSQL compatibility
- Composite unique constraints for multi-user data
- Indexes for fast queries on large datasets

## 🔧 Local Development

You can still develop locally with SQLite:

```bash
# Local development (no DATABASE_URL)
python app.py
# Uses SQLite files in data/ folder

# Test PostgreSQL locally
export DATABASE_URL="postgresql://localhost/chess_dev"
python app.py
# Uses PostgreSQL
```

## 💰 Cost Breakdown

### Free Tier (Perfect for Starting)
- **PostgreSQL**: Free for 30 days (1GB storage)
- **Web Service**: Free (512MB RAM, sleeps after 15min idle)
- **Total**: $0/month

### Production Tier (When You're Ready)
- **PostgreSQL Basic**: $6/month (persistent, 256MB RAM, daily backups)
- **Web Service Starter**: $7/month (512MB RAM, always on)
- **Total**: $13/month for persistent, always-on service

## 🚨 Important Notes

1. **30-Day Limit**: Free PostgreSQL expires after 30 days
2. **Upgrade Path**: Upgrade before expiry to keep all data
3. **Data Safety**: PostgreSQL data persists across deployments
4. **Concurrent Users**: Much better performance than SQLite

## 🏁 Deployment Checklist

- [ ] Create PostgreSQL database on Render
- [ ] Copy DATABASE_URL to web service environment
- [ ] Deploy application (automatic table creation)
- [ ] Test with your Lichess username
- [ ] Verify data persists after manual restart
- [ ] (Optional) Migrate existing SQLite data
- [ ] Set up upgrade reminder before 30-day limit

## 🎉 Success!

Your Chess Blunder Tracker now has:
- ✅ **Persistent storage** that survives restarts
- ✅ **1GB database** space (thousands of games)
- ✅ **Multi-user support** without conflicts
- ✅ **Professional-grade** PostgreSQL reliability
- ✅ **Free hosting** to get started

**No more lost analysis data!** Your users can now track their chess improvement over time without worrying about data loss. 🚀♟️
