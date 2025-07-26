#!/bin/bash

# Bermuda React Frontend Deployment Script

echo "🚀 Starting Bermuda React Frontend Deployment"
echo "=" * 50

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Make sure you're in the frontend-react directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Type check
echo "🔍 Running type check..."
npm run type-check
if [ $? -ne 0 ]; then
    echo "❌ Type check failed. Please fix TypeScript errors."
    exit 1
fi

# Lint check
echo "🧹 Running linter..."
npm run lint
if [ $? -ne 0 ]; then
    echo "❌ Linting failed. Please fix linting errors or run 'npm run lint:fix'."
    exit 1
fi

# Build for production
echo "🏗️ Building for production..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Build failed. Please check the errors above."
    exit 1
fi

echo "✅ Build completed successfully!"
echo "📁 Production files are in the 'dist' directory"

# Check if Firebase CLI is available
if command -v firebase &> /dev/null; then
    echo "🔥 Firebase CLI found. Would you like to deploy? (y/n)"
    read -r deploy_choice
    
    if [ "$deploy_choice" = "y" ] || [ "$deploy_choice" = "Y" ]; then
        echo "🚀 Deploying to Firebase Hosting..."
        firebase deploy --only hosting
        
        if [ $? -eq 0 ]; then
            echo "✅ Deployment successful!"
        else
            echo "❌ Deployment failed. Please check Firebase configuration."
        fi
    fi
else
    echo "💡 To deploy, install Firebase CLI: npm install -g firebase-tools"
fi

echo "🎉 All done!"