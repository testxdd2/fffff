import requests
import json
import base64
import os
from datetime import datetime

BASE_URL = "https://bdescolar.mineduc.cl/opac/api/v2"
CLIENT_ID = "NgOpac"
CLIENT_SECRET = "kvFqFy1i0Y4eUJhM"

def test_obtener_token():
    """Paso 1: Obtener token de cliente."""
    print("=" * 60)
    print("  TEST 1: OBTENER TOKEN DE CLIENTE")
    print("=" * 60)
    
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        resp = requests.post(
            f"{BASE_URL}/token",
            headers=headers,
            data="grant_type=client_credentials",
            timeout=15
        )
        print(f"  URL:     POST {BASE_URL}/token")
        print(f"  Status:  {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("token", "")
            expires = data.get("expiresIn", 0)
            print(f"  Token:   {token}")
            print(f"  Expira:  {expires} segundos ({expires//3600}h)")
            print(f"  ✅ Token obtenido correctamente.\n")
            return token
        else:
            print(f"  ❌ Falló: {resp.text[:200]}\n")
            return None
    except Exception as e:
        print(f"  ❌ Excepción: {e}\n")
        return None

def test_consultar_register(token):
    """Paso 2: Consultar /register."""
    print("=" * 60)
    print("  TEST 2: CONSULTAR /register")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payloads = [
        ("Array vacío ([]) ---", "[]"),
        ("Objeto vacío ({}) ----", "{}"),
        ("Con RUN de prueba ---", '[{"value":"22547371","type":"IDENTIFICADOR_EXTERNO"}]'),
    ]
    
    resultados = []
    
    for desc, body in payloads:
        print(f"\n  Body: {desc}")
        try:
            resp = requests.post(
                f"{BASE_URL}/register",
                headers=headers,
                data=body,
                timeout=15
            )
            print(f"  Status: {resp.status_code}")
            
            body_text = resp.text[:300]
            if "FORBIDDEN_ACCESS" in body_text:
                print(f"  Body:   ... "FORBIDDEN_ACCESS" detectado")
            elif "Cannot deserialize" in body_text:
                print(f"  Body:   ... "Cannot deserialize" detectado")
            else:
                print(f"  Body:   {body_text}")
            
            resultados.append((desc, resp.status_code, "FORBIDDEN_ACCESS" in body_text))
            
        except Exception as e:
            print(f"  ❌ Excepción: {e}")
            resultados.append((desc, 0, False))
    
    print()
    return resultados

def test_estado(token):
    print("=" * 60)
    print("  TEST 3: /status público (referencia)")
    print("=" * 60)
    
    try:
        resp = requests.get(
            f"{BASE_URL}/status",
            timeout=15
        )
        print(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            version = data.get("metadataCheckStatus", {}).get("version", "N/A")
            print(f"  Versión Odilo: {version}")
            print(f"  Conexiones OK: {sum(1 for c in data.get('statusConnections', []) if c.get('status') == 'SUCCESS')}/{len(data.get('statusConnections', []))}")
            print(f"  ✅ /status sigue público.\n")
        else:
            print(f"  ⚠️ Ya no es público: {resp.status_code}\n")
    except Exception as e:
        print(f"  ❌ Excepción: {e}\n")

def main():
    print(f"\n  🚀 INICIANDO TEST DEL MONITOR DE /register")
    print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  🌐 {BASE_URL}/register\n")
    
    token = test_obtener_token()
    if not token:
        print("❌ No se pudo obtener token. Abortando.")
        exit(1)
    
    resultados = test_consultar_register(token)
    
    test_estado(token)
    
    # Resumen final
    print("=" * 60)
    print("  RESUMEN FINAL")
    print("=" * 60)
    
    todos_ok = True
    for desc, status, forb in resultados:
        estado = "✅" if forb else ("⚠️" if status == 409 else "❌")
        print(f"  {estado} {desc.split(' -')[0]}: HTTP {status} | FORBIDDEN_ACCESS={'SÍ' if forb else 'NO'}")
        if status != 409 and not forb:
            todos_ok = False
    
    print()
    if todos_ok:
        print("  ✅ ESTADO ACTUAL: /register responde 409 FORBIDDEN_ACCESS.")
        print("  ✅ El monitor funcionará correctamente.")
        print("  ✅ Cuando cambie a otro código, se detectará el cambio.\n")
    else:
        print("  ⚠️ ALGO CAMBIÓ: /register ya no responde como antes.")
        print("  ⚠️ Revisar manualmente el endpoint.\n")
    
    if os.environ.get("GITHUB_ACTIONS") == "true":
        with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as f:
            f.write(f"status_ok={'true' if todos_ok else 'false'}\n")
            f.write(f"http_status={resultados[0][1] if resultados else 'N/A'}\n")

if __name__ == "__main__":
    main()
