#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import http.cookiejar

# Base URL
BASE_URL = "http://127.0.0.1:8000"

# Crear cookie jar para mantener cookies
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

print("=== PROBANDO LOGIN ===")
login_data = {
    "username": "lenin9073@gmail.com", 
    "password": "Miranda12*"
}

# Hacer login
login_request = urllib.request.Request(
    f"{BASE_URL}/api/users/login/",
    data=json.dumps(login_data).encode('utf-8'),
    headers={"Content-Type": "application/json"}
)

try:
    login_response = opener.open(login_request)
    login_text = login_response.read().decode('utf-8')
    print(f"Login Status Code: {login_response.status}")
    print(f"Login Response: {login_text}")
    
    # Mostrar cookies
    print("Cookies después del login:")
    for cookie in cookie_jar:
        print(f"  {cookie.name}: {cookie.value}")

    print("\n=== PROBANDO /me ===")
    # Probar /me
    me_request = urllib.request.Request(f"{BASE_URL}/api/users/me/")
    me_response = opener.open(me_request)
    me_text = me_response.read().decode('utf-8')
    print(f"/me Status Code: {me_response.status}")
    print(f"/me Response: {me_text}")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Error Response: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")