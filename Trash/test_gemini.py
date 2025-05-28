import requests
import json

# Test the classifier endpoint
url = "http://localhost:5000/debug/test-classifier"

# Custom test
custom_test = {
    "subject": "Your package from Amazon has been delivered",
    "sender": "tracking@amazon.com",
    "snippet": "Your package was delivered to your front door at 2:30 PM today"
}

print("Testing Gemini Classifier...")
print("=" * 50)

try:
    response = requests.post(url, json=custom_test)
    
    if response.status_code == 200:
        result = response.json()
        print("\nClassifier Test Results:")
        print(json.dumps(result, indent=2))
    else:
        print(f"\nError: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"\nError testing classifier: {e}")
    print("\nMake sure the backend server is running on port 5000")
