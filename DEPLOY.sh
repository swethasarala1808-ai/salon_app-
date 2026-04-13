#!/bin/bash
set -e

echo "=============================="
echo "  SALON APP COMPLETE DEPLOY"
echo "=============================="

BENCH_DIR="$HOME/frappe-bench"
APP_DIR="$BENCH_DIR/apps/salon_app"
SITE="salon.localhost"

# Step 1: Install salon_app if not installed
echo ""
echo "[1/7] Checking salon_app installation..."
cd $BENCH_DIR

INSTALLED=$(bench --site $SITE list-apps 2>/dev/null | grep -c "salon_app" || true)
if [ "$INSTALLED" -eq "0" ]; then
    echo "  Installing salon_app on $SITE..."
    bench --site $SITE install-app salon_app
    echo "  ✔ salon_app installed"
else
    echo "  ✔ salon_app already installed"
fi

# Step 2: Install Python package
echo ""
echo "[2/7] Installing Python package..."
./env/bin/pip install -e apps/salon_app --quiet
echo "  ✔ Python package installed"

# Step 3: Run migrate
echo ""
echo "[3/7] Running migrate..."
bench --site $SITE migrate
echo "  ✔ Migration complete"

# Step 4: Load sample data
echo ""
echo "[4/7] Loading sample data..."
bench --site $SITE execute salon_app.install.after_install || echo "  (Sample data may already exist)"

# Step 5: Clear all caches
echo ""
echo "[5/7] Clearing cache..."
bench --site $SITE clear-cache
bench clear-cache

# Step 6: Restart
echo ""
echo "[6/7] Restarting bench..."
bench restart || echo "  (If restart fails, run: bench start)"

echo ""
echo "=============================="
echo "  DEPLOY COMPLETE!"
echo "=============================="
echo ""
echo "Your sites:"
echo "  Salon Home:       http://salon.localhost:8001/"
echo "  Men Portal:       http://salon.localhost:8001/men"
echo "  Women Portal:     http://salon.localhost:8001/women"
echo "  Unisex Portal:    http://salon.localhost:8001/unisex"
echo "  Salon Dashboard:  http://salon.localhost:8001/salon-dashboard"
echo "  Beauty Dashboard: http://salon.localhost:8001/beauty-dashboard"
echo ""
echo "Next steps:"
echo "  1. Go to Frappe backend → Salon Type Settings"
echo "  2. Add Men, Women, Unisex settings (phone, UPI, address)"
echo "  3. Go to Salon Branch → Add your branches (Bengaluru, Chennai etc)"
echo "  4. Go to Salon Staff → Add staff with correct Salon Type"
echo "  5. Go to Salon Service → Add services with correct Salon Type"
echo ""
