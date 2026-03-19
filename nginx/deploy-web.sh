#!/bin/bash
# Deploy CaseFlow as a web app on the Raspberry Pi
# Run this script ON the Pi from the CaseClaimAPI directory

set -e

echo "=== CaseFlow Web App Deployment ==="
echo ""

# 1. Install Nginx if not already installed
if ! command -v nginx &> /dev/null; then
    echo "[1/5] Installing Nginx..."
    sudo apt update
    sudo apt install -y nginx
else
    echo "[1/5] Nginx already installed"
fi

# 2. Copy frontend files to /var/www/caseflow
echo "[2/5] Deploying frontend files..."
sudo mkdir -p /var/www/caseflow
sudo rm -rf /var/www/caseflow/*

# Determine the frontend source directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASEFLOW_DIR="$SCRIPT_DIR/../../CaseFlow"

if [ ! -d "$CASEFLOW_DIR/src" ]; then
    echo "ERROR: Frontend source not found at $CASEFLOW_DIR/src"
    echo "Make sure the CaseFlow folder is next to CaseClaimAPI"
    exit 1
fi

# Copy the full structure so import paths work:
#   /var/www/caseflow/config.js
#   /var/www/caseflow/src/index.html
#   /var/www/caseflow/src/components/...
#   /var/www/caseflow/src/styles/...
#   /var/www/caseflow/src/utils/...
sudo cp "$CASEFLOW_DIR/config.js" /var/www/caseflow/
sudo cp -r "$CASEFLOW_DIR/src" /var/www/caseflow/

sudo chown -R www-data:www-data /var/www/caseflow

echo "  Frontend deployed to /var/www/caseflow/"

# 3. Install Nginx config
echo "[3/5] Configuring Nginx..."
sudo cp "$SCRIPT_DIR/caseflow.conf" /etc/nginx/sites-available/caseflow
sudo ln -sf /etc/nginx/sites-available/caseflow /etc/nginx/sites-enabled/caseflow
sudo rm -f /etc/nginx/sites-enabled/default

# 4. Test Nginx config
echo "[4/5] Testing Nginx configuration..."
sudo nginx -t

# 5. Restart Nginx
echo "[5/5] Restarting Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "CaseFlow is now available at:"
echo "  http://$(hostname -I | awk '{print $1}')"
echo ""
echo "Make sure Django/Daphne is running on port 8000:"
echo "  cd ~/Desktop/CaseClaimAPI"
echo "  pipenv run daphne -b 0.0.0.0 -p 8000 api.asgi:application"
echo ""
echo "Anyone on the campus network can now access CaseFlow in their browser!"
