#!/bin/bash
# Deployment script for Blunderometer

set -e

echo "🚀 Blunderometer Deployment Script"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check git status
echo "📋 Checking git status..."
if ! git diff --quiet; then
    echo "⚠️  Warning: You have uncommitted changes. Please commit them first:"
    git status --short
    echo ""
    echo "Run: git add . && git commit -m 'Prepare for deployment'"
    exit 1
fi

# Check if remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ Error: No git remote 'origin' found. Please add your GitHub repository:"
    echo "git remote add origin https://github.com/kencht/blunderometer.git"
    exit 1
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin main

echo "✅ Code pushed to GitHub successfully!"
echo ""
echo "🔧 Next Steps for Render.com Deployment:"
echo "1. Go to https://render.com and sign in with GitHub"
echo "2. Click 'New +' > 'Web Service'"
echo "3. Connect your GitHub account and select 'blunderometer' repository"
echo "4. Configure the service:"
echo "   - Name: blunderometer"
echo "   - Environment: Python 3"
echo "   - Build Command: ./build.sh"
echo "   - Start Command: python app.py"
echo "   - Instance Type: Free"
echo ""
echo "5. Add Environment Variables:"
echo "   - FLASK_ENV=production"
echo "   - DATABASE_URL=(will be set automatically when you add PostgreSQL)"
echo ""
echo "6. Add PostgreSQL Database:"
echo "   - In Render dashboard, click 'New +' > 'PostgreSQL'"
echo "   - Name: blunderometer-db"
echo "   - Instance Type: Free"
echo "   - Copy the 'External Database URL'"
echo "   - Go back to your web service and add it as DATABASE_URL"
echo ""
echo "7. Deploy!"
echo "   - Click 'Create Web Service'"
echo "   - Wait for build and deployment to complete"
echo ""
echo "📊 After Deployment:"
echo "   - Visit your app at https://blunderometer.onrender.com"
echo "   - Run the migration script to transfer existing data"
echo "   - Test with your Lichess username"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT_GUIDE.md"
