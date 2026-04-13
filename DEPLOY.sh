#!/bin/bash
# ═══════════════════════════════════════════════
# SALON APP - ONE SHOT DEPLOY SCRIPT
# Run this from WSL: bash /tmp/salon_final/DEPLOY.sh
# ═══════════════════════════════════════════════
set -e

BENCH="$HOME/frappe-bench"
SITE="salon.localhost"
APP="$BENCH/apps/salon_app"

echo "======================================"
echo " SALON APP DEPLOY"
echo "======================================"

# 1. Copy files
echo "[1/6] Copying app files..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp -rf "$SCRIPT_DIR/salon_app/"* "$APP/salon_app/"
cp -f "$SCRIPT_DIR/setup.py" "$APP/setup.py" 2>/dev/null || true
cp -f "$SCRIPT_DIR/requirements.txt" "$APP/requirements.txt" 2>/dev/null || true
echo "    Done"

# 2. Install Python package
echo "[2/6] Installing Python package..."
cd "$BENCH"
./env/bin/pip install -e "apps/salon_app" -q
echo "    Done"

# 3. Migrate
echo "[3/6] Running migrate..."
bench --site "$SITE" migrate 2>&1 | grep -E "Updating|Migrating|Error|error" || true
echo "    Done"

# 4. Load sample data
echo "[4/6] Loading sample data..."
bench --site "$SITE" execute salon_app.install.after_install 2>&1 | tail -5
echo "    Done"

# 5. Clear cache
echo "[5/6] Clearing cache..."
bench --site "$SITE" clear-cache
echo "    Done"

# 6. Restart
echo "[6/6] Restarting bench..."
bench restart 2>&1 | tail -3 || supervisorctl restart all 2>/dev/null || true
echo "    Done"

echo ""
echo "======================================"
echo " DEPLOY COMPLETE!"
echo "======================================"
echo " Salon Dashboard:  http://$SITE:8000/salon-dashboard"
echo " Men Portal:       http://$SITE:8000/men"
echo " Women Portal:     http://$SITE:8000/women"
echo " Unisex Portal:    http://$SITE:8000/unisex"
echo "======================================"
