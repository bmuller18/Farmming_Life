# 🌾 Farming Life - Guía Rápida

## Inicio rápido

### Opción 1: Script automático (RECOMENDADO)
```bash
./dev.sh
```

Esto inicia Backend + Frontend automáticamente.

---

### Opción 2: Usando Make
```bash
make run
```

---

### Opción 3: Manual en terminales separadas

**Terminal 1 - Backend:**
```bash
source env/bin/activate
python backend/app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
source ../env/bin/activate
python -m http.server 8000
```

---

## URLs

- **Frontend:** http://localhost:8000 🌍
- **Backend API:** http://localhost:5000/api 📡
- **Health Check:** http://localhost:5000/health

---

## Comandos útiles

```bash
# Ejecutar ambos servidores
./dev.sh
make run

# Detener servidores
Ctrl+C (en la terminal)
# o manualmente:
make stop

# Ver logs
tail -f /tmp/backend.log    # Backend
tail -f /tmp/frontend.log   # Frontend

# Limpiar archivos temporales
make clean
```

---

## Estructura del Proyecto

```
.
├── backend/
│   ├── app.py              # Flask API
│   ├── services/           # Business logic
│   ├── repositories/       # Database access
│   └── requirements.txt
│
├── frontend/
│   ├── index.html          # HTML principal
│   ├── style.css           # Estilos neumórficos
│   ├── script.js           # Lógica JavaScript
│   └── app.py              # Frontend Flet (antiguo)
│
├── dev.sh                  # Script para ejecutar ambos
├── Makefile                # Comandos cortos
├── run.py                  # Script Python alternativo
└── QUICKSTART.md           # Este archivo
```

---

## Características Implementadas

✅ **Backend (Flask REST API)**
- 🌾 Cultivos con ciclos de crecimiento
- 💰 Sistema de economía (compra/venta)
- 🏠 Múltiples casas y parcelas
- 📦 Inventario de cosechas
- ⏱️ Temporizadores de cultivos
- 🔀 Venta en lotes (batch selling)

✅ **Frontend (HTML/CSS/JavaScript)**
- 🎨 Diseño neumórfico moderno
- 📊 Dashboard en tiempo real
- 🌾 Vista de la granja con parcelas
- 🎒 Inventario con agrupación por tipo
- ⏳ Contadores de tiempo (hh:mm:ss)
- 💸 Venta con selector de cantidad

---

## Próximos Pasos

1. 🏡 **Properties Page** - Compra de casas
2. 🛒 **Market Page** - Sistema de mercado
3. ⭐ **Level System** - Experiencia y leveling
4. 🌱 **Más cultivos** - Ampliar catálogo

---

¡Disfruta el juego! 🚀
