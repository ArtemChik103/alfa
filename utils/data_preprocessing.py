import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from utils.compatibility_utils import ensure_numeric_target

def load_and_preprocess_locations_data(file_path):
    """Загрузка и предобработка данных для геоаналитики"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # Извлечение ключевых признаков
    df['pedestrian_traffic'] = df['pedestrian_traffic'].apply(lambda x: x['weekday_avg'])
    df['avg_purchase_value'] = df['commercial_metrics'].apply(lambda x: x['avg_purchase_value'])
    df['district_encoded'] = pd.Categorical(df['district']).codes
    
    # Целевая переменная - потенциал локации (средние ежемесячные продажи)
    df['location_potential'] = df['historical_activity'].apply(lambda x: x['avg_monthly_spending'])
    
    # Признаки для модели
    features = ['pedestrian_traffic', 'avg_purchase_value', 'district_encoded']
    X = df[features]
    y = df['location_potential']
    
    return X, y, features

def load_and_preprocess_demand_data(file_path):
    """Загрузка и предобработка данных для прогноза спроса"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Распаковка данных по категориям
    records = []
    for item in data:
        for category, cat_data in item['category_data'].items():
            record = {
                'region': item['region_id'],
                'period': item['period'],
                'category': category,
                'transaction_count': cat_data['transaction_count'],
                'total_volume': cat_data['total_volume'],
                'avg_transaction': cat_data['avg_transaction'],
                'growth_trend': cat_data['growth_trend'],
                'economic_index': item['external_factors']['economic_index']
            }
            records.append(record)
    
    df = pd.DataFrame(records)
    
    # Преобразование периода в datetime
    df['period_date'] = pd.to_datetime(df['period'] + '-01')
    
    # Признаки для модели
    features = ['transaction_count', 'avg_transaction', 'growth_trend', 'economic_index']
    X = df[features]
    y = df['total_volume']
    
    return X, y, features, df

def load_and_preprocess_segmentation_data(file_path):
    """Загрузка и предобработка данных для сегментации клиентов"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # Извлечение RFM-метрик
    df['recency'] = df['rfm_metrics'].apply(lambda x: x['recency'])
    df['frequency'] = df['rfm_metrics'].apply(lambda x: x['frequency'])
    df['monetary'] = df['rfm_metrics'].apply(lambda x: x['monetary'])
    
    # Кодирование размера компании
    df['company_size_encoded'] = pd.Categorical(
        df['company_profile'].apply(lambda x: x['size'])
    ).codes
    
    # Целевая переменная - сегмент
    df['segment_encoded'] = pd.Categorical(df['segment']).codes
    
    # Признаки для модели
    features = ['recency', 'frequency', 'monetary', 'company_size_encoded']
    X = df[features]
    y = ensure_numeric_target(df['segment_encoded'])
    
    # Сохраняем mapping для обратного преобразования
    segment_mapping = {i: seg for i, seg in enumerate(df['segment'].astype('category').cat.categories)}
    
    return X, y, features, segment_mapping