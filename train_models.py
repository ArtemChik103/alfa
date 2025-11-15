import os
import json
import pandas as pd
import numpy as np
from utils.data_preprocessing import (
    load_and_preprocess_locations_data,
    load_and_preprocess_demand_data,
    load_and_preprocess_segmentation_data
)
from models.location_analyzer import LocationAnalyzer
from models.demand_forecaster import DemandForecaster
from models.client_segmenter import ClientSegmenter
import time
import traceback

def create_directories():
    """Создание необходимых директорий"""
    directories = [
        'models/saved_models',
        'data/synthetic',
        'reports'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Директория создана: {directory}")

def train_location_model():
    """Обучение модели анализа локаций"""
    print("\n🚀 Обучение модели анализа локаций...")
    
    try:
        # Загрузка и предобработка данных
        X, y, features = load_and_preprocess_locations_data(
            'data/synthetic/locations_data.json'
        )
        
        print(f"Загружено {len(X)} записей для обучения")
        print(f"Признаки: {features}")
        
        # Обучение модели
        analyzer = LocationAnalyzer()
        r2 = analyzer.train(X, y, features)
        
        # Сохранение модели
        analyzer.save_model()
        
        print(f"✅ Модель анализа локаций обучена. R² = {r2:.3f}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при обучении модели анализа локаций: {e}")
        print(f"Подробности ошибки: {traceback.format_exc()}")
        return False

def train_demand_model():
    """Обучение модели прогноза спроса"""
    print("\n🚀 Обучение модели прогноза спроса...")
    
    try:
        # Загрузка и предобработка данных
        X, y, features, df = load_and_preprocess_demand_data(
            'data/synthetic/demand_forecast_data.json'
        )
        
        print(f"Загружено {len(df)} записей для обучения")
        print(f"Уникальные категории: {df['category'].unique()}")
        
        # Обучение модели
        forecaster = DemandForecaster()
        success = forecaster.train(X, y, features, df)
        
        if success:
            # Сохранение моделей
            forecaster.save_models()
            print("✅ Модель прогноза спроса обучена и сохранена")
            return True
        else:
            print("❌ Не удалось обучить модель прогноза спроса")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при обучении модели прогноза спроса: {e}")
        print(f"Подробности ошибки: {traceback.format_exc()}")
        return False

def train_segmentation_model():
    """Обучение модели сегментации клиентов"""
    print("\n🚀 Обучение модели сегментации клиентов...")
    
    try:
        # Загрузка и предобработка данных
        X, y, features, segment_mapping = load_and_preprocess_segmentation_data(
            'data/synthetic/b2b_segmentation_data.json'
        )
        
        print(f"Загружено {len(X)} записей для обучения")
        print(f"Уникальных сегментов: {len(segment_mapping)}")
        print(f"Сегменты: {list(segment_mapping.values())}")
        
        # Преобразование целевой переменной в числовой формат
        if not pd.api.types.is_numeric_dtype(y):
            print("⚠️ Целевая переменная не числовая. Преобразуем в числовой формат...")
            y = pd.Series(y).astype('category').cat.codes
        
        # Обучение модели
        segmenter = ClientSegmenter()
        success = segmenter.train(X, y, features, segment_mapping)
        
        if success:
            # Сохранение моделей
            if segmenter.save_models():
                print("✅ Модель сегментации клиентов обучена и сохранена")
                return True
            else:
                print("❌ Не удалось сохранить модель сегментации клиентов")
                return False
        else:
            print("❌ Не удалось обучить модель сегментации клиентов")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при обучении модели сегментации клиентов: {e}")
        print(f"Подробности ошибки: {traceback.format_exc()}")
        return False

def generate_sample_predictions():
    """Генерация примеров предсказаний для демонстрации"""
    print("\n📊 Генерация примеров предсказаний...")
    
    try:
        # 1. Пример для анализа локации
        location_analyzer = LocationAnalyzer.load_model()
        location_pred = location_analyzer.predict(
            pedestrian_traffic=12500,
            avg_purchase_value=1200,
            district='central'
        )
        
        print("✅ Пример для анализа локации сгенерирован")
        
        # 2. Пример для прогноза спроса
        demand_forecaster = DemandForecaster.load_models()
        demand_pred = demand_forecaster.predict(
            category='electronics',
            region='REG_MSK',
            economic_index=105.0
        )
        
        print("✅ Пример для прогноза спроса сгенерирован")
        
        # 3. Пример для сегментации клиента
        client_segmenter = ClientSegmenter.load_models()
        if hasattr(client_segmenter, 'classifier') and client_segmenter.classifier is not None:
            segment_pred = client_segmenter.predict_segment(
                recency=15,
                frequency=12,
                monetary=5000000,
                company_size='medium'
            )
            print("✅ Пример для сегментации клиента сгенерирован")
        else:
            print("⚠️ Модель сегментации не загружена, пропускаем пример")
            segment_pred = {
                'segment_id': 1,
                'segment_name': 'medium_value_growing',
                'segment_description': 'Средняя ценность, растущий потенциал',
                'recommendations': ['Стандартные рекомендации'],
                'confidence': 0.8,
                'key_metrics': {'monetary_potential': 5000000, 'loyalty_level': 'средний'}
            }
        
        # Сохранение примеров
        samples = {
            'location_analysis': location_pred,
            'demand_forecast': demand_pred,
            'client_segmentation': segment_pred
        }
        
        os.makedirs('reports', exist_ok=True)
        with open('reports/sample_predictions.json', 'w', encoding='utf-8') as f:
            json.dump(samples, f, indent=2, ensure_ascii=False)
        
        print("✅ Примеры предсказаний сгенерированы и сохранены в reports/sample_predictions.json")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при генерации примеров предсказаний: {e}")
        print(f"Подробности ошибки: {traceback.format_exc()}")
        return False

def main():
    """Основная функция обучения всех моделей"""
    start_time = time.time()
    
    print("🎯 НАЧАЛО ОБУЧЕНИЯ МОДЕЛЕЙ ДЛЯ MVP АЛЬФА-БАНКА")
    print("=" * 60)
    
    # Создание директорий
    create_directories()
    
    # Проверка наличия данных
    data_files = [
        'data/synthetic/locations_data.json',
        'data/synthetic/demand_forecast_data.json', 
        'data/synthetic/b2b_segmentation_data.json'
    ]
    
    missing_files = [f for f in data_files if not os.path.exists(f)]
    
    if missing_files:
        print("❌ ОТСУТСТВУЮТ НЕОБХОДИМЫЕ ФАЙЛЫ С ДАННЫМИ:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nПожалуйста, сгенерируйте синтетические данные сначала")
        return
    
    print("✅ Все необходимые файлы с данными присутствуют")
    
    # Обучение моделей
    success_count = 0
    
    if train_location_model():
        success_count += 1
    
    if train_demand_model():
        success_count += 1
    
    if train_segmentation_model():
        success_count += 1
    
    # Генерация примеров
    if success_count > 0:
        generate_sample_predictions()
    
    # Итоги
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "=" * 60)
    print(f"🏁 ОБУЧЕНИЕ ЗАВЕРШЕНО")
    print(f"✅ Успешно обучено моделей: {success_count}/3")
    print(f"⏱️  Общее время обучения: {total_time:.2f} секунд")
    print("=" * 60)
    
    if success_count == 3:
        print("\n🎉 ВСЕ МОДЕЛИ УСПЕШНО ОБУЧЕНЫ!")
        print("Теперь вы можете запустить API и веб-интерфейс:")
        print("1. API: uvicorn api.main:app --reload --port 8000")
        print("2. Веб-интерфейс: streamlit run web/app.py --server.port 8501")
    else:
        print(f"\n⚠️  НЕКОТОРЫЕ МОДЕЛИ НЕ ОБУЧЕНЫ ({3-success_count})")
        print("Проверьте логи ошибок выше и повторите обучение")
        print("Для повторного обучения выполните: python train_models.py")

if __name__ == "__main__":
    main()