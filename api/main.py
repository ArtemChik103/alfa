from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import os
import json

from models.location_analyzer import LocationAnalyzer
from models.demand_forecaster import DemandForecaster
from models.client_segmenter import ClientSegmenter
from utils.overpass_provider import OverpassPOIProvider
from utils.macro_provider import MacroDataProvider

app = FastAPI(
    title="Альфа-Аналитика B2B API",
    description="Высокоточный B2B API с поддержкой DaData API, OpenStreetMap POI и макроэкономики ЦБ РФ",
    version="2.0.0"
)

location_analyzer = LocationAnalyzer()
demand_forecaster = DemandForecaster()
client_segmenter = ClientSegmenter()
overpass_provider = OverpassPOIProvider()
macro_provider = MacroDataProvider()

class LocationRequest(BaseModel):
    pedestrian_traffic: float = Field(..., description="Пешеходный трафик (чел/день)", ge=0)
    avg_purchase_value: float = Field(..., description="Средний чек (руб.)", ge=0)
    district: str = Field("central", description="Район города")

class LocationCoordsRequest(BaseModel):
    lat: float = Field(55.7558, description="Широта локации")
    lon: float = Field(37.6173, description="Долгота локации")
    avg_purchase_value: float = Field(2500.0, description="Предполагаемый средний чек")

class DemandRequest(BaseModel):
    category: str = Field("electronics", description="Категория товаров")
    region: str = Field("Moscow", description="Регион")
    periods: int = Field(6, description="Количество месяцев для прогноза", ge=1, le=24)

class ClientRequest(BaseModel):
    recency: int = Field(30, description="Давность последней покупки (дней)", ge=1)
    frequency: int = Field(5, description="Частота покупок (в месяц)", ge=1)
    monetary: float = Field(1500000.0, description="Средний оборот (руб.)", ge=0)
    company_size: int = Field(10, description="Размер штата сотрудников")

class InnRequest(BaseModel):
    inn_or_query: str = Field(..., description="ИНН организации (например, 7707083893 для Альфа-Банка) или название")

@app.get("/", tags=["Health Check"])
async def health_check():
    """Проверка работоспособности API и поставщиков данных"""
    cbr = macro_provider.get_cbr_rates()
    return {
        "status": "healthy",
        "service": "Альфа-Аналитика B2B API v2.0",
        "dadata_integration": "active",
        "osm_overpass_integration": "active",
        "cbr_macro_context": cbr
    }

@app.post("/analyze-location", tags=["Геоаналитика"])
async def analyze_location(req: LocationRequest):
    """Оценка потенциала и выручки точки по трафику и району"""
    return location_analyzer.predict(
        pedestrian_traffic=req.pedestrian_traffic,
        avg_purchase_value=req.avg_purchase_value,
        district=req.district
    )

@app.post("/analyze-location-coords", tags=["Геоаналитика"])
async def analyze_location_coords(req: LocationCoordsRequest):
    """Оценка потенциала локации с использованием реальных POI из OpenStreetMap"""
    osm_data = overpass_provider.get_pois_around(req.lat, req.lon, radius=500)
    traffic = osm_data["traffic_score"]
    
    analysis = location_analyzer.predict(
        pedestrian_traffic=traffic,
        avg_purchase_value=req.avg_purchase_value,
        district="central"
    )
    
    analysis["osm_real_data"] = osm_data
    return analysis

@app.post("/forecast-demand", tags=["Прогнозирование спроса"])
async def forecast_demand(req: DemandRequest):
    """Прогноз спроса с учетом макропоказателей ЦБ РФ и производственного календаря"""
    return demand_forecaster.forecast(
        category=req.category,
        region=req.region,
        months_ahead=req.periods
    )

@app.post("/segment-client", tags=["Сегментация B2B"])
async def segment_client(req: ClientRequest):
    """Сегментация клиента по RFM метрикам"""
    return client_segmenter.segment_by_metrics(
        recency=req.recency,
        frequency=req.frequency,
        monetary=req.monetary,
        company_size=req.company_size
    )

@app.post("/segment-client-inn", tags=["Сегментация B2B"])
async def segment_client_inn(req: InnRequest):
    """Автоматическая обогащенная сегментация по ИНН компании через DaData API"""
    return client_segmenter.segment_by_inn(req.inn_or_query)