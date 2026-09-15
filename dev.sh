#!/bin/bash
# 🌾 Farming Life - Inicia Backend + Frontend
# Uso: ./dev.sh

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🌾 Farming Life - Iniciando Backend + Frontend"
echo "================================================"
echo ""

# Activar venv
if [ ! -d "env" ]; then
    echo "❌ Virtual environment no encontrado"
    echo "   Ejecuta: python -m venv env"
    exit 1
fi

source env/bin/activate

# Matar procesos anteriores si existen
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "http.server" 2>/dev/null || true
sleep 1

# Iniciar Backend
echo "📡 Iniciando Backend (Flask) en puerto 5000..."
python backend/app.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   ✅ Backend PID: $BACKEND_PID"

# Iniciar Frontend
echo "🌐 Iniciando Frontend (HTTP Server) en puerto 8000..."
(cd frontend && python -m http.server 8000 > /tmp/frontend.log 2>&1 &)
FRONTEND_PID=$!
echo "   ✅ Frontend PID: $FRONTEND_PID"

echo ""
echo "================================================"
echo "✅ SERVIDORES CORRIENDO"
echo "================================================"
echo ""
echo "🌍 Frontend:  http://localhost:8000"
echo "📡 Backend:   http://localhost:5000/api"
echo ""
echo "📋 Ver logs:"
echo "   Backend:  tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo ""
echo "🛑 Detener: Ctrl+C (o: kill $BACKEND_PID $FRONTEND_PID)"
echo ""

# Esperar a entrada del usuario
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '✅ Detenido'" EXIT INT TERM

wait
