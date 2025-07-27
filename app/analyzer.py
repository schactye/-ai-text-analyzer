import time
import re
from collections import Counter
from datetime import datetime
from typing import List, Dict, Optional
import logging

from app.models import (
    AnalysisResponse, SentimentResult, LanguageResult, 
    TextStatistics, KeywordResult, APIStats
)

logger = logging.getLogger(__name__)

class TextAnalyzer:
    """Основной класс для анализа текста"""
    
    def __init__(self):
        self.start_time = time.time()
        self.stats = {
            'total_requests': 0,
            'total_texts_analyzed': 0,
            'processing_times': [],
            'languages': Counter(),
        }
        
        # Словарь языков
        self.language_names = {
            'ru': 'Russian', 'en': 'English', 'es': 'Spanish', 'fr': 'French',
            'de': 'German', 'it': 'Italian', 'pt': 'Portuguese', 'nl': 'Dutch',
        }
        
        logger.info("TextAnalyzer инициализирован")
    
    def analyze(self, text: str, include_keywords: bool = True, max_keywords: int = 10) -> AnalysisResponse:
        """Основная функция анализа текста"""
        start_time = time.time()
        
        try:
            # Обновляем статистику
            self.stats['total_requests'] += 1
            self.stats['total_texts_analyzed'] += 1
            
            # Выполняем анализ
            sentiment = self._analyze_sentiment(text)
            language = self._detect_language(text)
            statistics = self._calculate_statistics(text)
            keywords = self._extract_keywords(text, max_keywords) if include_keywords else None
            
            # Обновляем статистику языков
            self.stats['languages'][language.language] += 1
            
            processing_time = (time.time() - start_time) * 1000
            self.stats['processing_times'].append(processing_time)
            
            return AnalysisResponse(
                sentiment=sentiment,
                language=language,
                statistics=statistics,
                keywords=keywords,
                processing_time_ms=processing_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Ошибка при анализе текста: {str(e)}")
            raise
    
    def _analyze_sentiment(self, text: str) -> SentimentResult:
        """Анализ тональности текста"""
        try:
            # Простой анализ по ключевым словам
            positive_words = ['хорошо', 'отлично', 'прекрасно', 'замечательно', 'супер', 'великолепно', 'доволен', 'рекомендую']
            negative_words = ['плохо', 'ужасно', 'отвратительно', 'кошмар', 'ужас', 'плохой', 'разочарован']
            
            text_lower = text.lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                label, polarity, confidence = "positive", 0.6, 0.7
            elif neg_count > pos_count:
                label, polarity, confidence = "negative", -0.6, 0.7
            else:
                label, polarity, confidence = "neutral", 0.0, 0.5
            
            return SentimentResult(
                label=label,
                confidence=confidence,
                polarity=polarity,
                subjectivity=0.5
            )
            
        except Exception as e:
            logger.warning(f"Ошибка анализа тональности: {e}")
            return SentimentResult(
                label="neutral",
                confidence=0.5,
                polarity=0.0,
                subjectivity=0.5
            )
    
    def _detect_language(self, text: str) -> LanguageResult:
        """Определение языка текста"""
        try:
            # Простое определение по символам
            if re.search(r'[а-яё]', text.lower()):
                return LanguageResult(language="ru", language_name="Russian", confidence=0.8)
            else:
                return LanguageResult(language="en", language_name="English", confidence=0.6)
                    
        except Exception as e:
            logger.warning(f"Ошибка определения языка: {e}")
            return LanguageResult(language="unknown", language_name="Unknown", confidence=0.1)
    
    def _calculate_statistics(self, text: str) -> TextStatistics:
        """Вычисление статистики текста"""
        try:
            # Базовые подсчеты
            char_count = len(text)
            words = re.findall(r'\b\w+\b', text)
            word_count = len(words)
            sentences = re.split(r'[.!?]+', text)
            sentence_count = len([s for s in sentences if s.strip()])
            paragraphs = text.split('\n\n')
            paragraph_count = len([p for p in paragraphs if p.strip()])
            
            # Средние значения
            avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # Простой индекс читабельности
            if word_count > 0 and sentence_count > 0:
                readability = 100 - (avg_word_length * 5 + avg_sentence_length * 2)
                readability = max(0, min(100, readability))
            else:
                readability = 50
            
            return TextStatistics(
                character_count=char_count,
                word_count=word_count,
                sentence_count=sentence_count,
                paragraph_count=max(1, paragraph_count),
                avg_word_length=round(avg_word_length, 2),
                avg_sentence_length=round(avg_sentence_length, 2),
                readability_score=round(readability, 1)
            )
            
        except Exception as e:
            logger.warning(f"Ошибка вычисления статистики: {e}")
            return TextStatistics(
                character_count=len(text),
                word_count=0,
                sentence_count=1,
                paragraph_count=1,
                avg_word_length=0,
                avg_sentence_length=0,
                readability_score=50
            )
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[KeywordResult]:
        """Извлечение ключевых слов"""
        try:
            # Простая версия: частотный анализ
            stop_words = {
                'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'это',
                'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are'
            }
            
            # Извлекаем слова
            words = re.findall(r'\b[а-яёa-z]{3,}\b', text.lower())
            
            # Фильтруем стоп-слова и считаем частоты
            word_freq = Counter([word for word in words if word not in stop_words])
            
            # Преобразуем в результат
            keywords = []
            total_words = sum(word_freq.values())
            
            for word, freq in word_freq.most_common(max_keywords):
                importance = freq / total_words if total_words > 0 else 0
                keywords.append(KeywordResult(
                    word=word,
                    frequency=freq,
                    importance=round(importance, 3)
                ))
            
            return keywords
            
        except Exception as e:
            logger.warning(f"Ошибка извлечения ключевых слов: {e}")
            return []
    
    def get_stats(self) -> APIStats:
        """Получение статистики использования API"""
        try:
            avg_time = sum(self.stats['processing_times']) / len(self.stats['processing_times']) if self.stats['processing_times'] else 0
            most_common_lang = self.stats['languages'].most_common(1)[0][0] if self.stats['languages'] else 'unknown'
            uptime = time.time() - self.start_time
            
            return APIStats(
                total_requests=self.stats['total_requests'],
                total_texts_analyzed=self.stats['total_texts_analyzed'],
                avg_processing_time_ms=round(avg_time, 2),
                most_common_language=most_common_lang,
                uptime_seconds=round(uptime, 2)
            )
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return APIStats(
                total_requests=0,
                total_texts_analyzed=0,
                avg_processing_time_ms=0,
                most_common_language='unknown',
                uptime_seconds=0
            )
