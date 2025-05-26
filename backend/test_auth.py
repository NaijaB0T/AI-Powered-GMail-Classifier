#!/usr/bin/env python3
"""
Quick test script to verify OAuth authentication is working
Run this after starting your backend server
"""

import requests
import json

# Backend URL
BASE_URL = "http://localhost:5000"

# Test endpoints
endpoints = [
    ("/api/user/status", "GET", "Check authentication status"),
]

print("=== Gmail Classifier Authentication Test ===\n")

# Create a session to maintain cookies
session = requests.Session()

# Test 1: Check initial auth status
print("1. Checking initial authentication status...")
try:
    response = session.get(f"{BASE_URL}/api/user/status")
    data = response.json()
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {json.dumps(data, indent=2)}")
    print(f"   Authenticated: {'✅ Yes' if data.get('authenticated') else '❌ No'}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n2. Getting Google OAuth URL...")
try:
    response = session.get(f"{BASE_URL}/auth/google")
    data = response.json()
    if 'auth_url' in data:
        print(f"   ✅ OAuth URL received")
        print(f"   URL: {data['auth_url'][:80]}...")
    else:
        print(f"   ❌ No auth URL received: {data}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n3. Session Cookie Info:")
if session.cookies:
    for cookie in session.cookies:
        print(f"   Cookie: {cookie.name} = {cookie.value[:20]}...")
else:
    print("   No cookies set")

print("\n" + "="*50)
print("Next steps:")
print("1. If not authenticated, visit the OAuth URL in your browser")
print("2. Complete the Google sign-in process")
print("3. Check if you're redirected to the dashboard successfully")
print("4. Run this script again to verify authentication persisted")
