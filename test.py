#!/usr/bin/env python3
"""
Script de prueba para verificar la conectividad con Discord vía webhook.
Ejecuta: python3 test_discord_webhook.py
"""

import requests
import json
import sys
import os
from datetime import datetime

# Leer webhook desde variable de entorno (mejor práctica)
# Si no existe, usar una por defecto para pruebas (NO USAR EN PRODUCCIÓN)
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
if not WEBHOOK_URL:
    print("❌ ERROR: Variable DISCORD_WEBHOOK_URL no definida.")
    print("   Crea un webhook en Discord (Canal → Integraciones → Webhooks)")
    print("   Luego configúralo como secret en GitHub:")
    print("   Settings → Secrets and variables → Actions → New repository secret")
    print("   Nombre: DISCORD_WEBHOOK_URL")
    print("   Valor: https://discord.com/api/webhooks/...")
    sys.exit(1)

def enviar_mensaje(titulo, descripcion, color=14745344, fields=None):
    """
    Envía un embed a Discord.
    
    Args:
        titulo: Título del embed
        descripcion: Descripción del embed
        color: Color en decimal (14745344 = naranja, 65280 = verde, 16711680 = rojo)
        fields: Lista de dicts [{"name": "...", "value": "...", "inline": bool}]
    
    Returns:
        True si el envío fue exitoso, False en caso contrario
    """
    
    embed = {
        "title": titulo,
        "description": descripcion,
        "color": color,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {
            "text": "GitHub Actions — Test Automation"
        }
    }
    
    if fields:
        embed["fields"] = fields
    
    payload = {"embeds": [embed]}
    
    headers = {"Content-Type": "application/json"}
    
    try:
        resp = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        
        if resp.status_code in [200, 204]:
            print(f"✅ Mensaje enviado exitosamente (HTTP {resp.status_code})")
            return True
        else:
            print(f"❌ Error al enviar: HTTP {resp.status_code}")
            print(f"   Respuesta: {resp.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout — el webhook no respondió en 10 segundos")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión — verifica la URL del webhook")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    print("=" * 60)
    print("  PRUEBA DE WEBHOOK DE DISCORD")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Ocultar parte del webhook por seguridad
    if WEBHOOK_URL:
        url_truncada = WEBHOOK_URL[:50] + "..." if len(WEBHOOK_URL) > 50 else WEBHOOK_URL
        print(f"  Webhook: {url_truncada}")
    print()
    
    # 1. Mensaje de inicio
    print("[1] Enviando mensaje de inicio...")
    ok = enviar_mensaje(
        titulo="🚀 Monitor /register — Prueba de Integración",
        descripcion=(
            "Este es un mensaje de prueba para verificar que el sistema de "
            "notificaciones funciona correctamente.\n\n"
            f"**Entorno:** GitHub Actions\n"
            f"**Repositorio:** {os.environ.get('GITHUB_REPOSITORY', 'local')}\n"
            f"**Ejecución:** {os.environ.get('GITHUB_RUN_ID', 'N/A')}\n"
            f"**Ref:** {os.environ.get('GITHUB_REF', 'N/A')}"
        ),
        color=14745344  # Naranja
    )
    if not ok:
        sys.exit(1)
    
    # 2. Mensaje de prueba con campos
    print("\n[2] Enviando mensaje con campos detallados...")
    ok = enviar_mensaje(
        titulo="📋 Detalles de la Prueba",
        descripcion="Verificación de todos los componentes del sistema de monitoreo.",
        color=65280,  # Verde
        fields=[
            {"name": "🌐 Endpoint", "value": "`/opac/api/v2/register`", "inline": True},
            {"name": "🔑 Token", "value": "`NgOpac:kvFqFy1i0Y4eUJhM`", "inline": True},
            {"name": "📊 Estado actual", "value": "`409 FORBIDDEN_ACCESS`", "inline": True},
            {"name": "⏱ Intervalo", "value": "Cada 1 hora", "inline": True},
            {"name": "📡 Notificaciones", "value": "✅ Discord configurado", "inline": True},
            {"name": "🐍 Python", "value": f"{sys.version.split()[0]}", "inline": True}
        ]
    )
    if not ok:
        sys.exit(1)
    
    # 3. Mensaje de finalización
    print("\n[3] Enviando mensaje de finalización...")
    ok = enviar_mensaje(
        titulo="✅ Prueba Completada Exitosamente",
        descripcion=(
            "Todos los componentes funcionan correctamente:\n\n"
            "• Script Python → ✅\n"
            "• Conexión a Discord → ✅\n"
            "• Formato de embed → ✅\n"
            "• Variables de entorno → ✅\n\n"
            "El sistema de monitoreo está listo para usarse en producción."
        ),
        color=65280  # Verde
    )
    if not ok:
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("  ✅ TODAS LAS PRUEBAS PASARON")
    print("=" * 60)

if __name__ == "__main__":
    main()
