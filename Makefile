.PHONY: help install run stop dev clean

help:
	@echo "🌾 Farming Life - Comandos disponibles"
	@echo ""
	@echo "  make run       - Ejecuta Backend + Frontend (recomendado)"
	@echo "  make dev       - Igual a 'run' con output detallado"
	@echo "  make stop      - Detiene todos los servidores"
	@echo "  make install   - Instala dependencias"
	@echo "  make clean     - Limpia archivos temporales"
	@echo ""
	@echo "Uso:"
	@echo "  make run"

run:
	@python run.py

dev:
	@python run.py

install:
	@echo "📦 Instalando dependencias..."
	@python -m venv env
	@./env/bin/pip install -r requirements.txt
	@./env/bin/pip install -r backend/requirements.txt 2>/dev/null || true
	@echo "✅ Instalación completa"

stop:
	@echo "🛑 Deteniendo servidores..."
	@pkill -f "python.*app.py" || true
	@pkill -f "http.server" || true
	@echo "✅ Servidores detenidos"

clean:
	@echo "🧹 Limpiando..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@rm -f /tmp/backend.log /tmp/frontend.log
	@echo "✅ Limpieza completa"
