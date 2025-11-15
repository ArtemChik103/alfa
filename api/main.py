from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
import joblib
import numpy as np
import pandas as pd
import os
import json
from models.location_analyzer import LocationAnalyzer
from models.demand_forecaster import DemandForecaster
from models.client_segmenter import ClientSegmenter

app = FastAPI(
    title="Альфа-Аналитика API",
    description="B2B API для монетизации данных и DS-экспертизы Альфа-Банка",
    version="1.0.0"
)

# Глобальные переменные для моделей
location_analyzer = None
demand_forecaster = None
client_segmenter = None

def load_models():
    """Загрузка всех моделей при старте приложения"""
    global location_analyzer, demand_forecaster, client_segmenter
    
    print("🔍 Загрузка моделей...")
    
    try:
        # Загрузка модели анализа локаций
        location_analyzer = LocationAnalyzer.load_model()
        print("✅ Модель анализа локаций загружена")
        
        # Загрузка модели прогноза спроса
        demand_forecaster = DemandForecaster.load_models()
        print("✅ Модель прогноза спроса загружена")
        
        # Загрузка модели сегментации
        client_segmenter = ClientSegmenter.load_models()
        print("✅ Модель сегментации клиентов загружена")
        
        print("✨ Все модели успешно загружены")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке моделей: {e}")
        return False

# Схемы данных для валидации
class LocationRequest(BaseModel):
    pedestrian_traffic: float = Field(..., description="Пешеходный трафик (чел/день)", ge=0)
    avg_purchase_value: float = Field(..., description="Средний чек (руб.)", ge=0)
    district: str = Field(..., description="Район города", pattern="^(central|north|south|east|west|northeast|northwest|southeast|southwest)$")

class DemandRequest(BaseModel):
    category: str = Field(..., description="Категория товаров")
    region: str = Field(..., description="Регион")
    economic_index: float = Field(100.0, description="Экономический индекс", ge=0)
    periods: int = Field(3, description="Количество месяцев для прогноза", ge=1, le=12)

class ClientRequest(BaseModel):
    recency: int = Field(..., description="Давность последней покупки (дней)", ge=1)
    frequency: int = Field(..., description="Частота покупок (в месяц)", ge=1)
    monetary: float = Field(..., description="Средний оборот (руб.)", ge=0)
    company_size: str = Field(..., description="Размер компании", pattern="^(small|medium|large|enterprise)$")

@app.on_event("startup")
async def startup_event():
    """Загрузка моделей при старте приложения"""
    success = load_models()
    if not success:
        print("⚠️  Некоторые модели не загружены. Требуется обучение.")

@app.get("/", tags=["Health Check"])
async def health_check():
    """Проверка работоспособности API"""
    return {
        "status": "healthy",
        "service": "Альфа-Аналитика API",
        "version": "1.0.0",
        "models_loaded": {
            "location_analyzer": location_analyzer is not None,
            "demand_forecaster": demand_forecaster is not None,
            "client_segmenter": client_segmenter is not None
        },
        "timestamp": pd.Timestamp.now().isoformat()
    }

@app.post("/analyze-location", tags=["Геоаналитика"])
async def analyze_location(request: LocationRequest):
    """Анализ потенциала локации для новой точки продаж"""
    if location_analyzer is None:
        raise HTTPException(
            status_code=503, 
            detail="Сервис анализа локаций временно недоступен. Пожалуйста, попробуйте позже."
        )
    
    try:
        result = location_analyzer.predict(
            pedestrian_traffic=request.pedestrian_traffic,
            avg_purchase_value=request.avg_purchase_value,
            district=request.district
        )
        
        return {
            "request": request.dict(),
            "analysis_result": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/forecast-demand", tags=["Прогноз спроса"])
async def forecast_demand(request: DemandRequest):
    """Прогноз спроса на товарную категорию"""
    if demand_forecaster is None:
        raise HTTPException(
            status_code=503, 
            detail="Сервис прогноза спроса временно недоступен. Пожалуйста, попробуйте позже."
        )
    
    try:
        result = demand_forecaster.predict(
            category=request.category,
            region=request.region,
            economic_index=request.economic_index,
            periods=request.periods
        )
        
        return {
            "request": request.dict(),
            "forecast_result": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/segment-client", tags=["Сегментация клиентов"])
async def segment_client(request: ClientRequest):
    """Сегментация B2B-клиента"""
    if client_segmenter is None:
        raise HTTPException(
            status_code=503, 
            detail="Сервис сегментации клиентов временно недоступен. Пожалуйста, попробуйте позже."
        )
    
    try:
        result = client_segmenter.predict_segment(
            recency=request.recency,
            frequency=request.frequency,
            monetary=request.monetary,
            company_size=request.company_size
        )
        
        return {
            "request": request.dict(),
            "segmentation_result": result,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/models/status", tags=["Системная информация"])
async def models_status():
    """Получение статуса всех моделей"""
    return {
        "location_analyzer": {
            "loaded": location_analyzer is not None,
            "type": "RandomForestRegressor",
            "last_updated": pd.Timestamp.now().isoformat()
        },
        "demand_forecaster": {
            "loaded": demand_forecaster is not None,
            "type": "Prophet + RandomForest",
            "categories": list(demand_forecaster.prophet_models.keys()) if demand_forecaster else [],
            "last_updated": pd.Timestamp.now().isoformat()
        },
        "client_segmenter": {
            "loaded": client_segmenter is not None,
            "type": "KMeans + RandomForestClassifier",
            "segments": client_segmenter.segment_mapping.values() if client_segmenter and client_segmenter.segment_mapping else [],
            "last_updated": pd.Timestamp.now().isoformat()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)