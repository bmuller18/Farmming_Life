"""
SLO Monitoring - Objetivos de Nivel de Servicio
Rastrea disponibilidad, latencia, y confiabilidad de la API
"""
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict
from flask import g, request


class SLOMetrics:
    """Recopila métricas de SLO en tiempo real"""

    def __init__(self):
        self.start_time = datetime.now()
        self.requests_total = 0
        self.requests_successful = 0
        self.requests_failed = 0
        self.requests_rate_limited = 0
        self.response_times = []
        self.endpoint_metrics = defaultdict(lambda: {
            "count": 0,
            "errors": 0,
            "total_time": 0,
            "slowest": 0,
        })
        self.downtime_windows = []  # Períodos de outage

    def record_request(self, endpoint, status_code, duration_ms):
        """Registrar una request completada"""
        self.requests_total += 1
        self.response_times.append(duration_ms)

        # Registrar por endpoint
        self.endpoint_metrics[endpoint]["count"] += 1
        self.endpoint_metrics[endpoint]["total_time"] += duration_ms
        if duration_ms > self.endpoint_metrics[endpoint]["slowest"]:
            self.endpoint_metrics[endpoint]["slowest"] = duration_ms

        # Clasificar request
        if status_code < 400:
            self.requests_successful += 1
        elif status_code == 429:  # Rate limited
            self.requests_rate_limited += 1
        else:
            self.requests_failed += 1
            self.endpoint_metrics[endpoint]["errors"] += 1

    def record_downtime(self, reason, duration_seconds):
        """Registrar un período de downtime"""
        self.downtime_windows.append({
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "duration_seconds": duration_seconds
        })

    def get_uptime_percentage(self):
        """Porcentaje de disponibilidad"""
        if self.requests_total == 0:
            return 100.0
        return (self.requests_successful / self.requests_total) * 100

    def get_error_rate(self):
        """Porcentaje de errores"""
        if self.requests_total == 0:
            return 0.0
        return ((self.requests_failed + self.requests_rate_limited) / self.requests_total) * 100

    def get_p95_latency(self):
        """Latencia p95 (95avo percentil)"""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[idx] if idx < len(sorted_times) else 0

    def get_p99_latency(self):
        """Latencia p99 (99avo percentil)"""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        idx = int(len(sorted_times) * 0.99)
        return sorted_times[idx] if idx < len(sorted_times) else 0

    def get_avg_latency(self):
        """Latencia promedio"""
        if not self.response_times:
            return 0
        return sum(self.response_times) / len(self.response_times)

    def get_rate_limit_percentage(self):
        """Porcentaje de requests rate-limited"""
        if self.requests_total == 0:
            return 0.0
        return (self.requests_rate_limited / self.requests_total) * 100

    def get_uptime_duration(self):
        """Tiempo desde que se inició el monitoreo"""
        elapsed = datetime.now() - self.start_time
        days = elapsed.days
        hours = elapsed.seconds // 3600
        minutes = (elapsed.seconds % 3600) // 60
        return f"{days}d {hours}h {minutes}m"

    def get_dashboard(self):
        """Retornar dashboard completo de SLOs"""
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime": {
                "percentage": f"{self.get_uptime_percentage():.2f}%",
                "requests_successful": self.requests_successful,
                "requests_total": self.requests_total,
            },
            "latency": {
                "average_ms": f"{self.get_avg_latency():.0f}ms",
                "p95_ms": f"{self.get_p95_latency():.0f}ms",
                "p99_ms": f"{self.get_p99_latency():.0f}ms",
                "max_ms": f"{max(self.response_times) if self.response_times else 0}ms",
            },
            "errors": {
                "error_rate": f"{self.get_error_rate():.2f}%",
                "total_errors": self.requests_failed,
                "rate_limited": self.requests_rate_limited,
            },
            "slos": {
                "availability_target": "99.9% ✅" if self.get_uptime_percentage() >= 99.9 else "99.9% ❌",
                "latency_p95_target": "<200ms ✅" if self.get_p95_latency() < 200 else "<200ms ❌",
                "latency_p99_target": "<500ms ✅" if self.get_p99_latency() < 500 else "<500ms ❌",
                "error_rate_target": "<0.1% ✅" if self.get_error_rate() < 0.1 else "<0.1% ❌",
                "rate_limit_target": "<5% ✅" if self.get_rate_limit_percentage() < 5 else "<5% ❌",
            },
            "endpoints": dict(self.endpoint_metrics),
            "monitoring_duration": self.get_uptime_duration(),
            "downtime_incidents": len(self.downtime_windows),
        }


# Instancia global de métricas
metrics = SLOMetrics()


def init_slo_monitoring(app):
    """Inicializar middleware de monitoreo de SLOs"""

    @app.before_request
    def before_request():
        """Registrar inicio de request"""
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        """Registrar finalización y calcular métricas"""
        if hasattr(g, 'start_time'):
            duration_ms = (time.time() - g.start_time) * 1000
            endpoint = request.endpoint or "unknown"

            # Registrar métrica
            metrics.record_request(
                endpoint=endpoint,
                status_code=response.status_code,
                duration_ms=duration_ms
            )

            # Alertar si request es muy lento
            if duration_ms > 1000:
                print(f"⚠️  Slow request: {endpoint} - {duration_ms:.0f}ms")

        return response

    @app.route('/api/slo/dashboard')
    def slo_dashboard():
        """Endpoint público para ver dashboard de SLOs"""
        return metrics.get_dashboard()

    print("✅ SLO Monitoring inicializado")


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

"""
En app.py:

from backend.slo_monitoring import init_slo_monitoring

app = Flask(__name__)
init_slo_monitoring(app)

Acceder al dashboard:

GET http://localhost:5000/api/slo/dashboard

Respuesta:
{
  "timestamp": "2026-09-16T10:30:00.000000",
  "uptime": {
    "percentage": "99.95%",
    "requests_successful": 1995,
    "requests_total": 2000
  },
  "latency": {
    "average_ms": "45ms",
    "p95_ms": "120ms",
    "p99_ms": "350ms",
    "max_ms": "2100ms"
  },
  "errors": {
    "error_rate": "0.25%",
    "total_errors": 5,
    "rate_limited": 0
  },
  "slos": {
    "availability_target": "99.9% ✅",
    "latency_p95_target": "<200ms ✅",
    "latency_p99_target": "<500ms ✅",
    "error_rate_target": "<0.1% ❌",
    "rate_limit_target": "<5% ✅"
  }
}
"""
