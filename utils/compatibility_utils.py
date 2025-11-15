import pandas as pd
import numpy as np

def ensure_numeric_target(y):
    """Преобразование целевой переменной в числовой формат"""
    if pd.api.types.is_numeric_dtype(y):
        return y
    
    # Если это категориальные данные
    if pd.api.types.is_categorical_dtype(y):
        return y.cat.codes
    
    # Если это строковые данные
    if pd.api.types.is_string_dtype(y):
        return pd.Series(y).astype('category').cat.codes
    
    # Если это объектный тип
    if pd.api.types.is_object_dtype(y):
        return pd.Series(y).astype('category').cat.codes
    
    # По умолчанию - попытка преобразования в числовой
    try:
        return pd.to_numeric(y, errors='coerce')
    except:
        return pd.Series(y).astype('category').cat.codes

def fix_feature_names(feature_names, feature_importance):
    """Исправление несоответствия количества признаков и их важностей"""
    num_features = len(feature_importance)
    num_names = len(feature_names)
    
    if num_features == num_names:
        return feature_names
    
    if num_features > num_names:
        # Добавляем недостающие названия
        additional_names = [f'feature_{i}' for i in range(num_names, num_features)]
        return feature_names + additional_names
    
    if num_features < num_names:
        # Обрезаем лишние названия
        return feature_names[:num_features]
    
    return feature_names