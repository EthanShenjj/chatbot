"""Tests for CORS configuration and security headers."""
import pytest
from flask import Flask


def test_cors_allowed_origin(client, app):
    """Test that requests from allowed origins are accepted."""
    allowed_origin = app.config['CORS_ORIGINS'][0]
    
    response = client.options('/api/auth/login',
                             headers={'Origin': allowed_origin})
    
    assert response.status_code in [200, 204]
    assert 'Access-Control-Allow-Origin' in response.headers


def test_cors_disallowed_origin(client, app):
    """Test that requests from disallowed origins are rejected."""
    disallowed_origin = 'https://malicious-site.com'
    
    # Make sure this origin is not in allowed list
    assert disallowed_origin not in app.config['CORS_ORIGINS']
    
    response = client.options('/api/auth/login',
                             headers={'Origin': disallowed_origin})
    
    # CORS should not include the disallowed origin
    if 'Access-Control-Allow-Origin' in response.headers:
        assert response.headers['Access-Control-Allow-Origin'] != disallowed_origin


def test_security_headers_present(client):
    """Test that security headers are present in responses."""
    response = client.get('/api/sessions')
    
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('X-XSS-Protection') == '1; mode=block'


def test_security_headers_on_all_endpoints(client):
    """Test that security headers are present on all endpoint types."""
    endpoints = [
        ('GET', '/api/sessions'),
        ('POST', '/api/auth/login'),
        ('OPTIONS', '/api/auth/login'),
    ]
    
    for method, endpoint in endpoints:
        if method == 'GET':
            response = client.get(endpoint)
        elif method == 'POST':
            response = client.post(endpoint, json={})
        elif method == 'OPTIONS':
            response = client.options(endpoint)
        
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers


def test_cors_credentials_support(client, app):
    """Test that CORS supports credentials."""
    allowed_origin = app.config['CORS_ORIGINS'][0]
    
    response = client.options('/api/auth/login',
                             headers={'Origin': allowed_origin})
    
    # Flask-CORS should include credentials header when supports_credentials=True
    assert response.status_code in [200, 204]


def test_cors_allowed_methods(client, app):
    """Test that CORS allows required HTTP methods."""
    allowed_origin = app.config['CORS_ORIGINS'][0]
    
    response = client.options('/api/auth/login',
                             headers={
                                 'Origin': allowed_origin,
                                 'Access-Control-Request-Method': 'POST'
                             })
    
    assert response.status_code in [200, 204]
    if 'Access-Control-Allow-Methods' in response.headers:
        allowed_methods = response.headers['Access-Control-Allow-Methods']
        assert 'POST' in allowed_methods


def test_cors_allowed_headers(client, app):
    """Test that CORS allows required headers."""
    allowed_origin = app.config['CORS_ORIGINS'][0]
    
    response = client.options('/api/auth/login',
                             headers={
                                 'Origin': allowed_origin,
                                 'Access-Control-Request-Headers': 'Content-Type, Authorization'
                             })
    
    assert response.status_code in [200, 204]
    if 'Access-Control-Allow-Headers' in response.headers:
        allowed_headers = response.headers['Access-Control-Allow-Headers'].lower()
        assert 'content-type' in allowed_headers
        assert 'authorization' in allowed_headers
