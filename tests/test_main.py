import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Тест главной страницы"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "AI Text Analyzer API" in data["message"]
    assert "version" in data

def test_health_check():
    """Тест проверки здоровья сервиса"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_analyze_positive_text():
    """Тест анализа позитивного текста"""
    response = client.post(
        "/analyze",
        json={
            "text": "Это отличный продукт! Я очень доволен покупкой.",
            "include_keywords": True,
            "max_keywords": 5
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Проверяем структуру ответа
    assert "sentiment" in data
    assert "language" in data
    assert "statistics" in data
    assert "keywords" in data
    assert "processing_time_ms" in data
    
    # Проверяем анализ тональности
    assert data["sentiment"]["label"] in ["positive", "negative", "neutral"]
    assert 0 <= data["sentiment"]["confidence"] <= 1
