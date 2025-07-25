from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class AnalysisRequest(BaseModel):
    """Модель запроса для анализа текста"""
    text: str = Field(..., description="Текст для анализа", min_length=1, max_length=10000)
    include_keywords: bool = Field(True, description="Включить извлечение ключевых слов")
    max_keywords: int = Field(10, description="Максимальное количество ключевых слов", ge=1, le=50)
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Это отличный продукт! Я очень доволен покупкой. Рекомендую всем!",
                "include_keywords": True,
                "max_keywords": 5
            }
        }

class SentimentResult(BaseModel):
    """Результат анализа тональности"""
    label: str = Field(..., description="Метка тональности: positive, negative, neutral")
    confidence: float = Field(..., description="Уверенность в предсказании (0-1)", ge=0, le=1)
    polarity: float = Field(..., description="Полярность (-1 до 1)", ge=-1, le=1)
    subjectivity: float = Field(..., description="Субъективность (0-1)", ge=0, le=1)

class KeywordResult(BaseModel):
    """Результат извлечения ключевых слов"""
    word: str = Field(..., description="Ключевое слово")
    frequency: int = Field(..., description="Частота встречаемости")
    importance: float = Field(..., description="Важность слова (0-1)", ge=0, le=1)

class TextStatistics(BaseModel):
    """Статистика текста"""
    character_count: int = Field(..., description="Количество символов")
    word_count: int = Field(..., description="Количество слов")
    sentence_count: int = Field(..., description="Количество предложений")
    paragraph_count: int = Field(..., description="Количество абзацев")
    avg_word_length: float = Field(..., description="Средняя длина слова")
    avg_sentence_length: float = Field(..., description="Среднее количество слов в предложении")
    readability_score: float = Field(..., description="Индекс читабельности (0-100)")

class LanguageResult(BaseModel):
    """Результат определения языка"""
    language: str = Field(..., description="Код языка (ISO 639-1)")
    language_name: str = Field(..., description="Название языка")
    confidence: float = Field(..., description="Уверенность в определении", ge=0, le=1)

class AnalysisResponse(BaseModel):
    """Полный ответ анализа текста"""
    text_id: Optional[int] = Field(None, description="ID текста (для пакетного анализа)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время анализа")
    
    # Основные результаты
    sentiment: SentimentResult = Field(..., description="Результат анализа тональности")
    language: LanguageResult = Field(..., description="Результат определения языка")
    statistics: TextStatistics = Field(..., description="Статистика текста")
    
    # Опциональные результаты
    keywords: Optional[List[KeywordResult]] = Field(None, description="Ключевые слова")
    
    # Дополнительная информация
    processing_time_ms: float = Field(..., description="Время обработки в миллисекундах")
    
    class Config:
        schema_extra = {
            "example": {
                "text_id": None,
                "timestamp": "2025-01-15T10:30:00",
                "sentiment": {
                    "label": "positive",
                    "confidence": 0.87,
                    "polarity": 0.6,
                    "subjectivity": 0.8
                },
                "language": {
                    "language": "ru",
                    "language_name": "Russian",
                    "confidence": 0.95
                },
                "statistics": {
                    "character_count": 65,
                    "word_count": 12,
                    "sentence_count": 3,
                    "paragraph_count": 1,
                    "avg_word_length": 4.2,
                    "avg_sentence_length": 4.0,
                    "readability_score": 75.5
                },
                "keywords": [
                    {"word": "отличный", "frequency": 1, "importance": 0.9},
                    {"word": "продукт", "frequency": 1, "importance": 0.8},
                    {"word": "доволен", "frequency": 1, "importance": 0.7}
                ],
                "processing_time_ms": 125.5
            }
        }

class BatchAnalysisResponse(BaseModel):
    """Ответ для пакетного анализа"""
    results: List[AnalysisResponse] = Field(..., description="Результаты анализа для каждого текста")
    processed_count: int = Field(..., description="Количество обработанных текстов")
    total_processing_time_ms: float = Field(..., description="Общее время обработки")

class APIStats(BaseModel):
    """Статистика использования API"""
    total_requests: int = Field(..., description="Общее количество запросов")
    total_texts_analyzed: int = Field(..., description="Общее количество проанализированных текстов")
    avg_processing_time_ms: float = Field(..., description="Среднее время обработки")
    most_common_language: str = Field(..., description="Наиболее частый язык")
    uptime_seconds: float = Field(..., description="Время работы сервиса в секундах")
