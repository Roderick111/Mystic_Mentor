#!/bin/bash

# Production Deployment Script for Esoteric Vectors
# Deploys from Docker Hub to mystical-mentor.beautiful-apps.com

set -e

# Configuration
SERVER_USER="root"
SERVER_IP="31.97.153.220"
DOMAIN="mystical-mentor.beautiful-apps.com"
DOCKER_IMAGE="daniel1mathias/esoteric-vectors:latest"
DEPLOY_DIR="/opt/esoteric-vectors"

echo "🚀 Starting production deployment to $DOMAIN"
echo "📦 Docker Image: $DOCKER_IMAGE"
echo "🖥️  Server: $SERVER_USER@$SERVER_IP"

# Step 1: Create deployment directory on server
echo "📁 Creating deployment directory..."
ssh $SERVER_USER@$SERVER_IP "mkdir -p $DEPLOY_DIR/{data,logs,ssl,nginx/logs}"

# Step 2: Copy necessary files to server
echo "📤 Copying deployment files..."

# Copy docker-compose production file
scp docker-compose.production.yml $SERVER_USER@$SERVER_IP:$DEPLOY_DIR/docker-compose.yml

# Copy nginx configuration
scp -r nginx/ $SERVER_USER@$SERVER_IP:$DEPLOY_DIR/

# Copy web files (frontend)
scp -r web/ $SERVER_USER@$SERVER_IP:$DEPLOY_DIR/

# Copy environment template
scp config/production.env.example $SERVER_USER@$SERVER_IP:$DEPLOY_DIR/.env.example

echo "✅ Files copied successfully"

# Step 3: Setup on server
echo "⚙️  Setting up server environment..."

ssh $SERVER_USER@$SERVER_IP << 'EOF'
cd /opt/esoteric-vectors

# Update system
apt-get update

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "🔧 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Set proper permissions
chown -R root:root /opt/esoteric-vectors
chmod -R 755 /opt/esoteric-vectors

echo "✅ Server setup complete"
EOF

# Step 4: Instructions for user
echo ""
echo "🎉 Deployment preparation complete!"
echo ""
echo "Next steps to complete deployment:"
echo "1. SSH to your server: ssh $SERVER_USER@$SERVER_IP"
echo "2. Go to deployment directory: cd $DEPLOY_DIR"
echo "3. Copy .env.example to .env and fill in your production values:"
echo "   cp .env.example .env"
echo "   nano .env"
echo "4. Add your SSL certificates to the ssl/ directory"
echo "5. Create frontend secrets: cp web/config/secrets.example.js web/config/secrets.js"
echo "6. Edit web/config/secrets.js with your production Auth0 credentials"
echo "7. Pull and start the application: docker-compose pull && docker-compose up -d"
echo ""
echo "Your Docker image is ready at: $DOCKER_IMAGE"
echo "Domain configured for: $DOMAIN"
echo ""
echo "🔗 After deployment, your app will be available at: https://$DOMAIN"

echo ""
echo "Would you like me to connect to the server now and help complete the setup? (y/n)" 