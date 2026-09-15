#!/usr/bin/env python3
"""
🌾 Farming Life - Backend + Frontend Starter
Ejecuta Flask Backend + HTTP Server Frontend en un único comando
"""

import subprocess
import sys
import os
import time
import signal
import atexit
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.resolve()
BACKEND_PORT = 5000
FRONTEND_PORT = 8000

processes = []

def cleanup():
    """Mata todos los procesos cuando se cierra"""
    print("\n🛑 Deteniendo servidores...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except:
            proc.kill()
    print("✅ Servidores detenidos")

def run_backend():
    """Inicia Flask backend"""
    os.chdir(PROJECT_DIR)
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'

    proc = subprocess.Popen(
        [sys.executable, 'backend/app.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append(proc)
    return proc

def run_frontend():
    """Inicia HTTP server para frontend"""
    frontend_dir = PROJECT_DIR / 'frontend'
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'

    proc = subprocess.Popen(
        [sys.executable, '-m', 'http.server', str(FRONTEND_PORT)],
        cwd=frontend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append(proc)
    return proc

def monitor_process(proc, name):
    """Monitorea y muestra output de un proceso"""
    for line in iter(proc.stdout.readline, ''):
        if line:
            print(f"[{name}] {line.rstrip()}")

def main():
    print("=" * 60)
    print("🌾 Farming Life - Iniciando Backend + Frontend")
    print("=" * 60)
    print()

    # Registrar cleanup
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    print("📡 Iniciando Backend (Flask)...")
    backend = run_backend()

    print("🌐 Iniciando Frontend (HTTP Server)...")
    frontend = run_frontend()

    time.sleep(2)

    print()
    print("=" * 60)
    print("✅ SERVIDORES CORRIENDO")
    print("=" * 60)
    print()
    print(f"🌍 Frontend: http://localhost:{FRONTEND_PORT}")
    print(f"📡 Backend:  http://localhost:{BACKEND_PORT}/api")
    print()
    print("🔍 Health check Backend:")
    print(f"   curl http://localhost:{BACKEND_PORT}/health")
    print()
    print("🛑 Para detener: Ctrl+C")
    print()
    print("-" * 60)
    print()

    # Monitorear Backend en thread separado
    import threading
    backend_thread = threading.Thread(
        target=monitor_process,
        args=(backend, "Backend"),
        daemon=True
    )
    backend_thread.start()

    frontend_thread = threading.Thread(
        target=monitor_process,
        args=(frontend, "Frontend"),
        daemon=True
    )
    frontend_thread.start()

    # Esperar a que terminen
    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
