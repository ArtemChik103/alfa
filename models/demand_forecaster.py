import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import joblib
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import warnings

# Игнорируем FutureWarnings для чистоты вывода
warnings.filterwarnings('ignore', category=FutureWarning)

class DemandForecaster:
    def __init__(self):
        self.prophet_models = {}
        self.correction_models = {}
        self.category_stats = {}
        
    def train(self, X, y, features, df):
        """Обучение модели прогноза спроса"""
        # Обучение моделей для каждой категории
        for category in df['category'].unique():
            category_data = df[df['category'] == category].copy()
            
            if len(category_data) < 10:
                continue
            
            # Подготовка данных для Prophet
            prophet_df = category_data[['period_date', 'total_volume']].rename(
                columns={'period_date': 'ds', 'total_volume': 'y'}
            )
            
            # Добавление регрессоров
            prophet_df['economic_index'] = category_data['economic_index'].values
            
            # Инициализация Prophet
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                interval_width=0.95
            )
            
            model.add_regressor('economic_index')
            
            # Обучение модели
            model.fit(prophet_df)
            self.prophet_models[category] = model
            
            # Статистика по категории
            self.category_stats[category] = {
                'avg_volume': category_data['total_volume'].mean(),
                'growth_rate': category_data['growth_trend'].mean(),
                'volatility': category_data['total_volume'].std() / category_data['total_volume'].mean()
            }
            
            # Обучение модели корректировки (если данных достаточно)
            if len(category_data) >= 20:
                self._train_correction_model(category_data, category)
            
            # Визуализация
            self._plot_forecast(model, category_data, category)
        
        print(f"Обучено моделей Prophet для {len(self.prophet_models)} категорий")
        return True
    
    def _train_correction_model(self, data, category):
        """Обучение модели корректировки прогнозов Prophet"""
        # Создание признаков для корректировки
        features = []
        targets = []
        
        for i in range(len(data) - 3):
            window = data.iloc[i:i+3]
            future = data.iloc[i+3]
            
            feature = {
                'month': window['period_date'].dt.month.mean(),
                'growth_trend': window['growth_trend'].mean(),
                'economic_index': window['economic_index'].mean(),
                'volume_trend': window['total_volume'].pct_change().mean()
            }
            features.append(feature)
            targets.append(future['total_volume'])
        
        if len(features) < 10:
            return
        
        X_corr = pd.DataFrame(features)
        y_corr = np.array(targets)
        
        # Разделение данных
        X_train, X_test, y_train, y_test = train_test_split(
            X_corr, y_corr, test_size=0.2, random_state=42
        )
        
        # Обучение модели корректировки
        corr_model = RandomForestRegressor(n_estimators=50, random_state=42)
        corr_model.fit(X_train, y_train)
        
        # Оценка качества
        y_pred = corr_model.predict(X_test)
        mape = mean_absolute_percentage_error(y_test, y_pred)
        
        if mape < 0.3:  # Достаточно хороший показатель
            self.correction_models[category] = corr_model
            print(f"Модель корректировки для {category} обучена. MAPE: {mape:.3f}")
    
    def _plot_forecast(self, model, data, category):
        """Визуализация прогноза"""
        # Используем 'ME' вместо 'M' для избежания FutureWarning
        future = model.make_future_dataframe(periods=3, freq='ME')
        future['economic_index'] = data['economic_index'].mean()
        
        forecast = model.predict(future)
        
        plt.figure(figsize=(12, 6))
        model.plot(forecast)
        plt.scatter(data['period_date'], data['total_volume'], color='red', label='Фактические данные')
        plt.title(f'Прогноз спроса для категории: {category}')
        plt.xlabel('Дата')
        plt.ylabel('Объем продаж (руб.)')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'demand_forecast_{category}.png')
        plt.close()
    
    def predict(self, category, region, economic_index=100.0, periods=3):
        """Прогноз спроса на будущие периоды"""
        if category not in self.prophet_models:
            return self._get_default_forecast(category, periods)
        
        model = self.prophet_models[category]
        
        # Создание future dataframe
        last_date = pd.Timestamp.now()
        # Используем 'ME' вместо 'M' для избежания FutureWarning
        future_dates = pd.date_range(start=last_date, periods=periods+1, freq='ME')[1:]
        
        future_df = pd.DataFrame({'ds': future_dates})
        future_df['economic_index'] = economic_index
        
        # Прогноз Prophet
        forecast = model.predict(future_df)
        
        # Применение корректировки, если есть модель
        if category in self.correction_models:
            corrected_volumes = self._apply_correction(forecast, category)
            forecast['yhat'] = corrected_volumes
        
        # Форматирование результата
        result = {
            'category': category,
            'region': region,
            'forecast_period': f'{periods} месяцев',
            'forecasts': [],
            'category_insights': self.category_stats.get(category, {})
        }
        
        # --- Manual translation of month names ---
        month_map = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 5: "Май", 6: "Июнь",
            7: "Июль", 8: "Август", 9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }

        for i, row in forecast.iterrows():
            forecast_date = row['ds']
            month_name = f"{month_map[forecast_date.month]} {forecast_date.year}"
            
            result['forecasts'].append({
                'date': forecast_date.strftime('%Y-%m'),
                'month_name': month_name,
                'predicted_volume': float(row['yhat']),
                'lower_bound': float(row['yhat_lower']),
                'upper_bound': float(row['yhat_upper']),
                'confidence': 0.95
            })

        # Генерация рекомендаций
        result['recommendations'] = self._generate_demand_recommendations(result)
        
        return result
    
    def _apply_correction(self, forecast_df, category):
        """Применение корректировки к прогнозу"""
        corr_model = self.correction_models[category]
        corrected_volumes = []
        
        for i, row in forecast_df.iterrows():
            features = pd.DataFrame([{
                'month': row['ds'].month,
                'growth_trend': self.category_stats[category]['growth_rate'],
                'economic_index': row['economic_index'],
                'volume_trend': 0.05  # Средний тренд
            }])
            
            corrected_volume = corr_model.predict(features)[0]
            corrected_volumes.append(corrected_volume)
        
        return corrected_volumes
    
    def _get_default_forecast(self, category, periods):
        """Прогноз по умолчанию для новой категории"""
        base_volume = 50000000  # 50 млн руб.
        growth_rate = 0.10  # 10% рост
        
        forecasts = []
        current_volume = base_volume
        
        for i in range(periods):
            forecast_date = pd.Timestamp.now() + pd.DateOffset(months=i+1)
            current_volume *= (1 + growth_rate)
            
            forecasts.append({
                'date': forecast_date.strftime('%Y-%m'),
                'month_name': forecast_date.strftime('%B %Y'),
                'predicted_volume': current_volume,
                'lower_bound': current_volume * 0.85,
                'upper_bound': current_volume * 1.15,
                'confidence': 0.80
            })
        
        return {
            'category': category,
            'region': 'REG_UNKNOWN',
            'forecast_period': f'{periods} месяцев',
            'forecasts': forecasts,
            'category_insights': {
                'avg_volume': base_volume,
                'growth_rate': growth_rate,
                'volatility': 0.2
            },
            'recommendations': [
                "Недостаточно данных для точного прогноза. Используется прогноз по умолчанию.",
                "Рекомендуем собрать больше исторических данных для улучшения точности."
            ]
        }
    
    def _generate_demand_recommendations(self, forecast_result):
        """Генерация рекомендаций по прогнозу спроса"""
        recommendations = []
        forecasts = forecast_result['forecasts']
        
        if not forecasts:
            return recommendations
        
        # Анализ тренда
        volumes = [f['predicted_volume'] for f in forecasts]
        trend = (volumes[-1] - volumes[0]) / volumes[0]
        
        if trend > 0.15:
            recommendations.append("📈 Сильный рост спроса. Рекомендуем увеличить закупки на 15-20%")
        elif trend > 0.05:
            recommendations.append("📊 Умеренный рост спроса. Оптимизируйте запасы для избежания дефицита")
        elif trend < -0.05:
            recommendations.append("📉 Снижение спроса. Сократите закупки и рассмотрите акции для стимулирования продаж")
        
        # Анализ волатильности
        if len(volumes) > 1:
            volatility = np.std(volumes) / np.mean(volumes)
            if volatility > 0.3:
                recommendations.append("⚠️ Высокая волатильность спроса. Рекомендуем гибкую стратегию закупок")
        
        # Сезонные рекомендации
        months = [pd.to_datetime(f['date']).month for f in forecasts]
        if any(6 <= month <= 8 for month in months):
            recommendations.append("☀️ Сезонный всплеск летом. Увеличьте запасы сезонных товаров")
        if any(11 <= month <= 12 for month in months):
            recommendations.append("🎄 Предновогодний спрос. Подготовьте дополнительные запасы и персонал")
        
        return recommendations
    
    def save_models(self, base_path='models/saved_models/'):
        """Сохранение всех моделей"""
        import os
        os.makedirs(base_path, exist_ok=True)
        
        # Сохранение Prophet моделей
        for category, model in self.prophet_models.items():
            model_path = f"{base_path}prophet_{category.replace(' ', '_')}.pkl"
            with open(model_path, 'wb') as f:
                joblib.dump(model, f)
        
        # Сохранение моделей корректировки
        for category, model in self.correction_models.items():
            model_path = f"{base_path}correction_{category.replace(' ', '_')}.pkl"
            joblib.dump(model, model_path)
        
        # Сохранение статистики
        stats_path = f"{base_path}category_stats.pkl"
        joblib.dump(self.category_stats, stats_path)
        
        print(f"Сохранено {len(self.prophet_models)} Prophet моделей и {len(self.correction_models)} моделей корректировки")
    
    @classmethod
    def load_models(cls, base_path='models/saved_models/'):
        """Загрузка всех моделей"""
        forecaster = cls()
        
        import os
        if not os.path.exists(base_path):
            print("Папка с моделями не найдена. Требуется обучение.")
            return forecaster
        
        # Загрузка Prophet моделей
        for file in os.listdir(base_path):
            if file.startswith('prophet_') and file.endswith('.pkl'):
                category = file[8:-4].replace('_', ' ')
                model_path = os.path.join(base_path, file)
                with open(model_path, 'rb') as f:
                    forecaster.prophet_models[category] = joblib.load(f)
        
        # Загрузка моделей корректировки
        for file in os.listdir(base_path):
            if file.startswith('correction_') and file.endswith('.pkl'):
                category = file[11:-4].replace('_', ' ')
                model_path = os.path.join(base_path, file)
                forecaster.correction_models[category] = joblib.load(model_path)
        
        # Загрузка статистики
        stats_path = os.path.join(base_path, 'category_stats.pkl')
        if os.path.exists(stats_path):
            forecaster.category_stats = joblib.load(stats_path)
        
        print(f"Загружено {len(forecaster.prophet_models)} Prophet моделей и {len(forecaster.correction_models)} моделей корректировки")
        return forecaster