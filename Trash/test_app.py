import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app, classifier, CATEGORIES

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_session():
    """Mock Flask session"""
    with patch('app.session') as mock_session:
        mock_session.__getitem__ = Mock()
        mock_session.__setitem__ = Mock()
        mock_session.__contains__ = Mock()
        yield mock_session

class TestEmailClassifier:
    """Test the EmailClassifier class"""
    
    def test_classifier_initialization(self):
        """Test that classifier initializes correctly"""
        assert classifier is not None
        assert hasattr(classifier, 'model')
    
    def test_classify_email_valid_input(self):
        """Test email classification with valid input"""
        with patch.object(classifier.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Work"
            mock_generate.return_value = mock_response
            
            result = classifier.classify_email(
                "Team Meeting Tomorrow",
                "manager@company.com",
                "Please join us for the weekly team meeting..."
            )
            
            assert result == "Work"
            assert result in CATEGORIES    
    def test_classify_email_invalid_response(self):
        """Test email classification with invalid AI response"""
        with patch.object(classifier.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "InvalidCategory"
            mock_generate.return_value = mock_response
            
            result = classifier.classify_email(
                "Test Subject",
                "test@example.com",
                "Test content"
            )
            
            assert result == "Notifications"  # Default category
    
    def test_classify_email_exception(self):
        """Test email classification when AI throws exception"""
        with patch.object(classifier.model, 'generate_content') as mock_generate:
            mock_generate.side_effect = Exception("AI Error")
            
            result = classifier.classify_email(
                "Test Subject",
                "test@example.com",
                "Test content"
            )
            
            assert result == "Notifications"  # Default category

class TestAPI:
    """Test API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_user_status_not_authenticated(self, client):
        """Test user status when not authenticated"""
        response = client.get('/api/user/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['authenticated'] == False
    
    def test_google_auth_endpoint(self, client):
        """Test Google auth endpoint"""
        with patch('app.Flow.from_client_config') as mock_flow:
            mock_flow_instance = Mock()
            mock_flow_instance.authorization_url.return_value = (
                'https://accounts.google.com/oauth2/auth?test=1', 'state123'
            )
            mock_flow.return_value = mock_flow_instance
            
            response = client.get('/auth/google')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'auth_url' in data
    
    def test_classify_emails_not_authenticated(self, client):
        """Test classify emails when not authenticated"""
        response = client.post('/api/emails/classify')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Not authenticated'

if __name__ == '__main__':
    pytest.main([__file__])
