#!/usr/bin/env python3
"""
Quick test script to check if the backend is working properly
"""

import requests
import json

def test_backend():
    base_url = "http://localhost:5000"
    
    print("🔍 Testing backend health...")
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Backend is running")
            print(f"   Google OAuth configured: {health_data.get('google_oauth_configured', False)}")
            print(f"   Gemini configured: {health_data.get('gemini_configured', False)}")
            print(f"   Encryption configured: {health_data.get('encryption_configured', False)}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False
    
    try:
        # Test session functionality
        print("\n🔍 Testing session functionality...")
        session = requests.Session()
        response = session.get(f"{base_url}/debug/auth-test")
        if response.status_code == 200:
            auth_data = response.json()
            print("✅ Session functionality working")
            print(f"   Session works: {auth_data.get('session_works', False)}")
        else:
            print(f"❌ Session test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing session: {e}")
    
    try:
        # Test auth status endpoint
        print("\n🔍 Testing auth status endpoint...")
        session = requests.Session()
        response = session.get(f"{base_url}/api/user/status")
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Auth status endpoint working")
            print(f"   Authenticated: {status_data.get('authenticated', False)}")
        else:
            print(f"❌ Auth status test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing auth status: {e}")
    
    print("\n🔍 Testing Google OAuth initiation...")
    try:
        session = requests.Session()
        response = session.get(f"{base_url}/auth/google")
        if response.status_code == 200:
            auth_data = response.json()
            if 'auth_url' in auth_data:
                print("✅ Google OAuth initiation working")
                print(f"   Auth URL generated: {len(auth_data['auth_url']) > 0}")
            else:
                print("❌ No auth_url in response")
        else:
            print(f"❌ Google OAuth test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing Google OAuth: {e}")
    
    print("\n✅ Backend testing complete!")

if __name__ == "__main__":
    test_backend()
