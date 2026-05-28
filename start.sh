#!/bin/bash
echo ""
echo " ========================================"
echo "  SSH Consumables Inventory System 2026"
echo " ========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo " ERROR: Python3 not found. Install it first."
    exit 1
fi

# Install Flask if needed
python3 -c "import flask" 2>/dev/null || pip3 install flask --quiet

cd "$SCRIPT_DIR/backend"

# Init DB
python3 -c "import app; app.init_db()" 2>/dev/null

echo " Starting backend on http://localhost:5050 ..."
python3 app.py &
BACKEND_PID=$!

sleep 2

# Open browser
echo " Opening frontend..."
if command -v xdg-open &>/dev/null; then
    xdg-open "$SCRIPT_DIR/frontend/index.html"
elif command -v open &>/dev/null; then
    open "$SCRIPT_DIR/frontend/index.html"
fi

echo ""
echo " ========================================"
echo "  Running! Default logins:"
echo "  admin / admin123   (Administrator)"
echo "  sameh / sameh123   (Engineer)"
echo "  ahmed / ahmed123   (Technician)"
echo " ========================================"
echo ""
echo " Press CTRL+C to stop."

wait $BACKEND_PID
