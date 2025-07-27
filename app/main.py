from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from app.analyzer import TextAnalyzer
from app.models import AnalysisRequest, AnalysisResponse

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальный анализатор
analyzer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global analyzer
    # Startup
    analyzer = TextAnalyzer()
    logger.info("🚀 AI Text Analyzer запущен!")
    logger.info("📝 Документация доступна по адресу: /docs")
    yield
    # Shutdown
    logger.info("🛑 AI Text Analyzer остановлен")

# Создание FastAPI приложения
app = FastAPI(
    title="AI Text Analyzer",
    description="Мощный инструмент для анализа текста с использованием NLP и машинного обучения",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def root():
    """Главная страница API"""
    return {
        "message": "🧠 AI Text Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "analyze_endpoint": "/analyze"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Проверка состояния сервиса"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AI Text Analyzer",
        "version": "1.0.0"
    }

@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_text(request: AnalysisRequest):
    """
    Анализ текста с использованием NLP
    
    - **text**: Текст для анализа (обязательный)
    - **include_keywords**: Включить извлечение ключевых слов (по умолчанию: true)
    - **max_keywords**: Максимальное количество ключевых слов (по умолчанию: 10)
    """
    global analyzer
    
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Текст не может быть пустым")
        
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Текст слишком длинный (макс. 10000 символов)")
        
        # Выполняем анализ
        result = analyzer.analyze(
            text=request.text,
            include_keywords=request.include_keywords,
            max_keywords=request.max_keywords
        )
        
        logger.info(f"Анализ выполнен для текста длиной {len(request.text)} символов")
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при анализе текста: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")

@app.post("/batch-analyze", tags=["Analysis"])
async def batch_analyze(texts: List[str], max_keywords: int = 5):
    """
    Пакетный анализ нескольких текстов
    """
    global analyzer
    
    try:
        if len(texts) > 100:
            raise HTTPException(status_code=400, detail="Максимум 100 текстов за раз")
        
        results = []
        for i, text in enumerate(texts):
            if len(text.strip()) > 0:
                result = analyzer.analyze(text, max_keywords=max_keywords)
                result.text_id = i
                results.append(result)
        
        return {"results": results, "processed_count": len(results)}
        
    except Exception as e:
        logger.error(f"Ошибка при пакетном анализе: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка пакетного анализа: {str(e)}")

@app.get("/stats", tags=["Statistics"])
async def get_stats():
    """Статистика использования API"""
    global analyzer
    return analyzer.get_stats()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
