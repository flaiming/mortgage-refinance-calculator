#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$REPO_DIR/.venv"
FRONTEND_DIR="$REPO_DIR/frontend"
SERVICE_NAME="hypo"
NGINX_CONF="$REPO_DIR/deploy/hypo.vojtechoram.cz.nginx.conf"

echo "==> Deploying from $REPO_DIR"

# Check .env
if [ ! -f "$REPO_DIR/.env" ]; then
    echo "WARNING: .env file not found at $REPO_DIR/.env"
    echo "The app may not work without ARAD_API_KEY."
fi

# Virtualenv
echo "==> Setting up virtualenv"
if [ ! -f "$VENV_DIR/bin/pip" ]; then
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$REPO_DIR/requirements.txt" -q
echo "    Done."

# Frontend build
echo "==> Building frontend"
cd "$FRONTEND_DIR"
npm ci --silent
npm run build
cd "$REPO_DIR"
echo "    Done."

# Systemd
echo "==> Setting up systemd service"
sudo cp -f "$REPO_DIR/deploy/hypo.service" /etc/systemd/system/hypo.service
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"
echo "    Done. Status:"
sudo systemctl status "$SERVICE_NAME" --no-pager -l || true

# Nginx
echo "==> Setting up nginx"
sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/hypo.vojtechoram.cz
sudo nginx -t
sudo systemctl reload nginx
echo "    Done."

# Certbot
echo ""
read -p "==> Set up HTTPS with certbot? [y/N] " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo certbot --nginx -d hypo.vojtechoram.cz
fi

echo "==> Deployment complete."
