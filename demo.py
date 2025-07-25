#!/usr/bin/env python3
"""
Демонстрационный скрипт для AI Text Analyzer
Показывает основные возможности API
"""

import requests
import json
import time
from typing import List, Dict

# Конфигурация
API_BASE_URL = "http://localhost:8000"
DEMO_TEXTS = [
    {
        "text": "Это отличный продукт! Я очень доволен покупкой. Рекомендую всем!",
        "description": "Позитивный отзыв на русском"
    },
    {
        "text": "This is a terrible product. I'm very disappointed with the quality.",
        "description": "Негативный отзыв на английском"
    },
    {
        "text": "Сегодня обычный день. Ничего особенного не происходит. Погода нормальная.",
        "description": "Нейтральный текст"
    },
    {
        "text": "Machine learning and artificial intelligence are transforming our world. These 
technologies enable computers to learn from data and make intelligent decisions.",
        "description": "Технический текст"
    },
    {
        "text": "🎉 Супер новость! Наша команда выиграла хакатон! 🏆 Мы разработали потрясающий 
AI-проект за 48 часов. Спасибо всем участникам! 💪✨",
        "description": "Текст с эмодзи и сленгом"
    }
]

def print_header(title: str):
    """Печать заголовка"""
    print(f"\n{'='*60}")
    print(f"🧠 {title}")
    print(f"{'='*60}")

def print_analysis_result(result: Dict, description: str):
    """Красивый вывод результата анализа"""
    print(f"\n📝 {description}")
    print(f"Текст: {result.get('text', 'N/A')[:100]}...")
    print("-" * 50)
    
    # Тональность
    sentiment = result.get('sentiment', {})
    sentiment_emoji = {
        'positive': '😊',
        'negative': '😞',
        'neutral': '😐'
    }
    print(f"😊 Тональность: {sentiment_emoji.get(sentiment.get('label', 'neutral'), '😐')} "
          f"{sentiment.get('label', 'unknown')} (уверенность: {sentiment.get('confidence', 0):.2f})")
    
    # Язык
    language = result.get('language', {})
    print(f"🌍 Язык: {language.get('language_name', 'Unknown')} "
          f"({language.get('language', 'unknown')}) - {language.get('confidence', 0):.2f}")
    
    # Статистика
    stats = result.get('statistics', {})
    print(f"📊 Статистика: {stats.get('word_count', 0)} слов, "
          f"{stats.get('sentence_count', 0)} предложений, "
          f"читабельность: {stats.get('readability_score', 0):.1f}/100")
    
    # Ключевые слова
    keywords = result.get('keywords', [])
    if keywords:
        top_keywords = [kw['word'] for kw in keywords[:5]]
        print(f"🔑 Ключевые слова: {', '.join(top_keywords)}")
    
    print(f"⚡ Время обработки: {result.get('processing_time_ms', 0):.1f}ms")

def check_api_health() -> bool:
    """Проверка доступности API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def analyze_single_text(text: str, description: str):
    """Анализ одного текста"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json={
                "text": text,
                "include_keywords": True,
                "max_keywords": 5
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            result['text'] = text  # Добавляем текст для отображения
            print_analysis_result(result, description)
        else:
            print(f"❌ Ошибка анализа: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка соединения: {e}")

def batch_analyze_demo():
    """Демонстрация пакетного анализа"""
    print_header("Пакетный анализ текстов")
    
    texts = [item["text"] for item in DEMO_TEXTS[:3]]
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/batch-analyze",
            json=texts,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Обработано {result['processed_count']} текстов")
            
            for i, analysis in enumerate(result['results']):
                print(f"\n📄 Текст {i+1}:")
                print(f"   Тональность: {analysis['sentiment']['label']}")
                print(f"   Язык: {analysis['language']['language_name']}")
                print(f"   Время: {analysis['processing_time_ms']:.1f}ms")
        else:
            print(f"❌ Ошибка пакетного анализа: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка соединения: {e}")

def show_api_stats():
    """Показать статистику API"""
    print_header("Статистика использования API")
    
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"📈 Всего запросов: {stats['total_requests']}")
            print(f"📝 Текстов проанализировано: {stats['total_texts_analyzed']}")
            print(f"⚡ Среднее время обработки: {stats['avg_processing_time_ms']:.1f}ms")
            print(f"🌍 Популярный язык: {stats['most_common_language']}")
            print(f"🕐 Время работы: {stats['uptime_seconds']:.1f}s")
        else:
            print(f"❌ Ошибка получения статистики: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка соединения: {e}")

def performance_test():
    """Тест производительности"""
    print_header("Тест производительности")
    
    test_text = "Это тестовый текст для проверки производительности анализатора."
    num_requests = 10
    
    print(f"🚀 Выполняем {num_requests} запросов...")
    
    times = []
    for i in range(num_requests):
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                json={"text": f"{test_text} Запрос #{i+1}", "include_keywords": False},
                timeout=10
            )
            
            if response.status_code == 200:
                request_time = (time.time() - start_time) * 1000
                times.append(request_time)
                print(f"   Запрос {i+1}: {request_time:.1f}ms")
            else:
                print(f"   Запрос {i+1}: Ошибка {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   Запрос {i+1}: Ошибка соединения")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📊 Результаты:")
        print(f"   Успешных запросов: {len(times)}/{num_requests}")
        print(f"   Среднее время: {avg_time:.1f}ms")
        print(f"   Минимальное время: {min_time:.1f}ms")
        print(f"   Максимальное время: {max_time:.1f}ms")
        print(f"   Пропускная способность: ~{1000/avg_time*60:.0f} запросов/минуту")

def main():
    """Главная функция демонстрации"""
    print_header("AI Text Analyzer - Демонстрация возможностей")
    
    # Проверяем доступность API
    print("🔍 Проверяем доступность API...")
    if not check_api_health():
        print("❌ API недоступно! Убедитесь, что сервер запущен на http://localhost:8000")
        print("💡 Запустите сервер командой: uvicorn app.main:app --reload")
        return
    
    print("✅ API доступно!")
    
    # Демонстрация анализа различных текстов
    print_header("Анализ различных типов текстов")
    
    for item in DEMO_TEXTS:
        analyze_single_text(item["text"], item["description"])
        time.sleep(0.5)  # Небольшая пауза между запросами
    
    # Пакетный анализ
    batch_analyze_demo()
    
    # Тест производительности
    performance_test()
    
    # Статистика
    show_api_stats()
    
    print_header("Демонстрация завершена!")
    print("🎉 Спасибо за внимание к AI Text Analyzer!")
    print("📖 Документация: http://localhost:8000/docs")
    print("🔗 GitHub: https://github.com/schactye/ai-text-analyzer")

if __name__
