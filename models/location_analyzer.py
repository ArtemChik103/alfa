import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

class LocationAnalyzer:
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.scaler = StandardScaler()
        
    def train(self, X, y, features):
        """Обучение модели анализа локаций"""
        self.feature_names = features
        
        # Разделение данных
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Создание pipeline
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler()),
            ('regressor', RandomForestRegressor(
                n_estimators=100, 
                random_state=42,
                n_jobs=-1
            ))
        ])
        
        # Настройка гиперпараметров
        param_grid = {
            'regressor__n_estimators': [50, 100],
            'regressor__max_depth': [None, 10, 20]
        }
        
        grid_search = GridSearchCV(
            pipeline, param_grid, cv=3, scoring='r2', n_jobs=-1
        )
        grid_search.fit(X_train, y_train)
        
        self.model = grid_search.best_estimator_
        
        # Оценка качества
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Location Analyzer - MSE: {mse:.2f}, R²: {r2:.3f}")
        print(f"Лучшие параметры: {grid_search.best_params_}")
        
        # Визуализация важности признаков
        self._plot_feature_importance(X_test)
        
        return r2
    
    def _plot_feature_importance(self, X_sample):
        """Визуализация важности признаков"""
        feature_importance = self.model.named_steps['regressor'].feature_importances_
        
        plt.figure(figsize=(10, 6))
        sns.barplot(
            x=feature_importance, 
            y=self.feature_names,
            palette='viridis'
        )
        plt.title('Важность признаков для прогнозирования потенциала локации')
        plt.xlabel('Важность')
        plt.tight_layout()
        plt.savefig('location_feature_importance.png')
        plt.close()
    
    def predict(self, pedestrian_traffic, avg_purchase_value, district):
        """Прогноз потенциала локации"""
        # Кодирование района
        district_mapping = {
            'central': 0, 'north': 1, 'south': 2, 'east': 3, 'west': 4,
            'northeast': 5, 'northwest': 6, 'southeast': 7, 'southwest': 8
        }
        district_encoded = district_mapping.get(district.lower(), 0)
        
        # Подготовка данных
        features = pd.DataFrame([{
            'pedestrian_traffic': pedestrian_traffic,
            'avg_purchase_value': avg_purchase_value,
            'district_encoded': district_encoded
        }])
        
        # Прогноз
        prediction = self.model.predict(features)[0]
        
        # Расчет уверенности на основе разброса предсказаний деревьев
        individual_tree_predictions = np.array([
            tree.predict(features)[0] for tree in self.model.named_steps['regressor'].estimators_
        ])
        
        pred_std = np.std(individual_tree_predictions)
        
        # Используем коэффициент вариации для нормализации
        # Добавляем небольшое значение к prediction для избежания деления на ноль
        cv = pred_std / (prediction + 1e-6)
        
        # Преобразуем CV в уверенность (0-1). Чем ниже CV, тем выше уверенность.
        # Используем экспоненциальное затухание для более плавной оценки
        confidence = np.exp(-cv)

        # Генерация рекомендаций
        recommendations = self._generate_recommendations(prediction, district)
        
        return {
            'potential_monthly_revenue': float(prediction),
            'recommendation_score': self._calculate_score(prediction),
            'recommendations': recommendations,
            'confidence': float(confidence)
        }
    
    def _calculate_score(self, prediction):
        """Расчет рекомендательного скоринга на основе нормализации"""
        
        # Задаем минимальный и максимальный ожидаемый доход
        MIN_REVENUE = 2000000  # Минимальный порог для скоринга
        MAX_REVENUE = 25000000 # Максимальный порог (соответствует ~95 баллам)
        
        # Ограничиваем значение prediction в рамках заданных порогов
        clipped_prediction = np.clip(prediction, MIN_REVENUE, MAX_REVENUE)
        
        # Нормализуем значение от 0 до 1
        normalized_score = (clipped_prediction - MIN_REVENUE) / (MAX_REVENUE - MIN_REVENUE)
        
        # Преобразуем в шкалу от 50 до 95
        # Это дает более реалистичный диапазон оценок
        score = 50 + (normalized_score * 45)
        
        return int(score)
    
    def _generate_recommendations(self, prediction, district):
        """Генерация рекомендаций на основе прогноза"""
        recommendations = []
        
        if prediction > 15000000:
            recommendations.append("Отличная локация! Рекомендуем открыть магазин полного формата")
            recommendations.append("Высокий потенциал для премиального ассортимента")
        elif prediction > 10000000:
            recommendations.append("Хорошая локация. Рекомендуем оптимизировать ассортимент под целевую аудиторию")
        else:
            recommendations.append("Умеренный потенциал. Рассмотрите мини-формат или фокус на онлайн-продажах")
        
        if district.lower() in ['central', 'northwest', 'southwest']:
            recommendations.append("Высокая конкуренция в районе. Сфокусируйтесь на уникальных преимуществах")
        
        return recommendations
    
    def save_model(self, path='models/saved_models/location_analyzer.pkl'):
        """Сохранение модели"""
        joblib.dump(self.model, path)
        print(f"Модель анализа локаций сохранена в {path}")
    
    @classmethod
    def load_model(cls, path='models/saved_models/location_analyzer.pkl'):
        """Загрузка модели"""
        analyzer = cls()
        analyzer.model = joblib.load(path)
        return analyzer