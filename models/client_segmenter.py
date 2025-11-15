import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

class ClientSegmenter:
    def __init__(self):
        self.kmeans_model = None
        self.classifier = None
        self.scaler = StandardScaler()
        self.pca = None
        self.segment_mapping = None
        self.feature_names = None
        self.original_feature_names = None
        
    def train(self, X, y, features, segment_mapping):
        """Обучение модели сегментации клиентов"""
        self.original_feature_names = features
        self.segment_mapping = segment_mapping
        
        # Стандартизация данных
        X_scaled = self.scaler.fit_transform(X)
        
        # Определение оптимального числа кластеров
        optimal_k = self._find_optimal_clusters(X_scaled)
        
        # Обучение KMeans
        self.kmeans_model = KMeans(
            n_clusters=optimal_k, 
            random_state=42,
            n_init=10
        )
        clusters = self.kmeans_model.fit_predict(X_scaled)
        
        # Обучение классификатора
        self.classifier = RandomForestClassifier(
            n_estimators=100, 
            random_state=42
        )
        self.classifier.fit(X_scaled, clusters)
        
        # PCA для визуализации
        self.pca = PCA(n_components=2)
        X_pca = self.pca.fit_transform(X_scaled)
        
        # Визуализация кластеров
        self._plot_clusters(X_pca, clusters)
        
        # Визуализация важности признаков
        self._plot_feature_importance(X_scaled, features)
        
        # Оценка качества
        self._evaluate_model(X_scaled, clusters)
        
        return True
    
    def _find_optimal_clusters(self, X_scaled):
        """Определение оптимального числа кластеров"""
        inertia = []
        silhouette_scores = []
        k_range = range(2, 8)  # k от 2 до 7
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_scaled)
            inertia.append(kmeans.inertia_)
            
            if k > 1:
                try:
                    score = silhouette_score(X_scaled, kmeans.labels_)
                    silhouette_scores.append(score)
                except:
                    silhouette_scores.append(0)
        
        # Выбор оптимального k по силуэтному коэффициенту
        if silhouette_scores:
            # Находим индекс максимального значения в silhouette_scores
            max_idx = np.argmax(silhouette_scores)
            # Оптимальное k = начальное значение (2) + индекс + 1 (т.к. k>1)
            optimal_k = 2 + max_idx + 1
        else:
            optimal_k = 4
        
        print(f"Оптимальное количество кластеров: {optimal_k}")
        
        # Визуализация
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        plt.plot(k_range, inertia, 'bo-')
        plt.xlabel('Количество кластеров')
        plt.ylabel('Inertia')
        plt.title('Метод локтя')
        plt.grid(True, alpha=0.3)
        
        if silhouette_scores:
            plt.subplot(1, 2, 2)
            # Создаем правильный диапазон для silhouette_scores
            k_silhouette = range(3, 3 + len(silhouette_scores))  # k от 3 до 3+len(scores)
            plt.plot(k_silhouette, silhouette_scores, 'ro-')
            plt.xlabel('Количество кластеров')
            plt.ylabel('Silhouette Score')
            plt.title('Silhouette Score')
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('clustering_evaluation.png')
        plt.close()
        
        return optimal_k
    
    def _plot_clusters(self, X_pca, clusters):
        """Визуализация кластеров с помощью PCA"""
        plt.figure(figsize=(10, 8))
        
        # Создание DataFrame для удобства
        pca_df = pd.DataFrame({
            'PC1': X_pca[:, 0],
            'PC2': X_pca[:, 1],
            'Cluster': clusters
        })
        
        # Построение графика
        sns.scatterplot(
            data=pca_df,
            x='PC1', y='PC2',
            hue='Cluster',
            palette='viridis',
            alpha=0.7,
            s=100
        )
        
        plt.title('Кластеризация B2B-клиентов (PCA)')
        plt.xlabel('PCA Component 1')
        plt.ylabel('PCA Component 2')
        plt.legend(title='Кластер')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('b2b_clusters_pca.png')
        plt.close()
    
    def _plot_feature_importance(self, X_scaled, feature_names):
        """Визуализация важности признаков"""
        if self.classifier is None:
            return
        
        feature_importance = self.classifier.feature_importances_
        
        # Убедимся, что количество признаков совпадает
        num_features = len(feature_importance)
        display_names = feature_names[:num_features] if len(feature_names) > num_features else feature_names
        
        # Если признаков меньше, чем важностей - дополним названиями
        if len(display_names) < num_features:
            display_names = display_names + [f'feature_{i}' for i in range(len(display_names), num_features)]
        
        plt.figure(figsize=(10, 6))
        # Исправляем FutureWarning для barplot
        sns.barplot(
            x=feature_importance,
            y=display_names,
            orient='h',  # Горизонтальный барплот
            palette='viridis'
        )
        plt.title('Важность признаков для сегментации клиентов')
        plt.xlabel('Важность')
        plt.tight_layout()
        plt.savefig('segmentation_feature_importance.png')
        plt.close()
    
    def _evaluate_model(self, X_scaled, clusters):
        """Оценка качества модели"""
        # Кросс-валидация
        from sklearn.model_selection import cross_val_score
        
        scores = cross_val_score(
            self.classifier, 
            X_scaled, 
            clusters, 
            cv=5, 
            scoring='accuracy'
        )
        
        print(f"Точность классификации: {scores.mean():.3f} ± {scores.std():.3f}")
        
        # Подробный отчет
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, clusters, test_size=0.2, random_state=42
        )
        y_pred = self.classifier.predict(X_test)
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
    
    def predict_segment(self, recency, frequency, monetary, company_size):
        """Прогноз сегмента клиента"""
        # Кодирование размера компании
        size_mapping = {'small': 0, 'medium': 1, 'large': 2, 'enterprise': 3}
        size_encoded = size_mapping.get(company_size.lower(), 1)
        
        # Подготовка данных
        features = np.array([[
            recency,
            frequency,
            monetary,
            size_encoded
        ]])
        
        # Стандартизация - используем уже обученный scaler
        if hasattr(self.scaler, 'scale_'):
            features_scaled = self.scaler.transform(features)
        else:
            # Если scaler не обучен, используем стандартные значения
            features_scaled = features.copy()
        
        # Предсказание
        segment_id = self.classifier.predict(features_scaled)[0]
        
        # Расчет уверенности
        probabilities = self.classifier.predict_proba(features_scaled)[0]
        confidence = float(np.max(probabilities))
        
        # Получение названия сегмента
        segment_name_en = self.segment_mapping.get(int(segment_id), "Unknown")

        # --- Translation of segment names ---
        segment_translation = {
            "high_value_loyal": "Лояльные с высокой ценностью",
            "medium_value_growing": "Растущие со средней ценностью",
            "low_value_potential": "Потенциальные с низкой ценностью",
            "at_risk": "В зоне риска",
            "High-Value Loyal": "Лояльные с высокой ценностью",
            "Growing Potential": "Растущий потенциал",
            "New Opportunity": "Новая возможность",
            "At Risk": "В зоне риска"
        }
        segment_name = segment_translation.get(segment_name_en, segment_name_en)
        
        # Генерация рекомендаций
        recommendations = self._generate_recommendations(segment_id, monetary)
        
        return {
            'segment_id': int(segment_id),
            'segment_name': segment_name,
            'segment_description': self._get_segment_description(segment_id),
            'recommendations': recommendations,
            'confidence': confidence,
            'key_metrics': {
                'monetary_potential': monetary,
                'loyalty_level': self._calculate_loyalty_level(recency, frequency)
            }
        }
    
    def _get_segment_description(self, segment_id):
        """Получение описания сегмента"""
        segment_id = int(segment_id)
        descriptions = {
            0: "Высокая ценность, высокая лояльность - стратегические партнеры",
            1: "Средняя ценность, растущий потенциал - перспективные клиенты", 
            2: "Низкая активность, риск оттока - требуют внимания",
            3: "Недавно присоединились, высокий потенциал - новые возможности"
        }
        return descriptions.get(segment_id, "Стандартный клиент")
    
    def _generate_recommendations(self, segment_id, monetary):
        """Генерация рекомендаций по сегменту"""
        segment_id = int(segment_id)
        
        recommendations = {
            0: [
                "Предложите премиальные услуги и персонального менеджера",
                "Разработайте эксклюзивные условия сотрудничества",
                "Предложите кросс-продажи смежных продуктов"
            ],
            1: [
                "Создайте программы лояльности для стимулирования роста",
                "Предложите обучающие материалы и кейсы успеха",
                "Рассмотрите возможность расширения ассортимента"
            ],
            2: [
                "Проведите опрос удовлетворенности клиентов",
                "Предложите специальные условия для возврата активности",
                "Проанализируйте причины снижения активности"
            ],
            3: [
                "Обеспечьте отличную поддержку на этапе адаптации",
                "Предложите пробные периоды для дополнительных услуг",
                "Создайте персонализированный план развития"
            ]
        }
        
        # Добавление финансовых рекомендаций
        if monetary > 50000000:
            recommendations[segment_id].append("Рассмотрите возможность включения в VIP-программу")
        
        return recommendations.get(segment_id, ["Стандартные условия обслуживания"])
    
    def _calculate_loyalty_level(self, recency, frequency):
        """Расчет уровня лояльности"""
        # Простая эвристика на основе RF-значений
        if recency < 7 and frequency > 10:
            return "высокий"
        elif recency < 30 and frequency > 5:
            return "средний"
        else:
            return "низкий"
    
    def save_models(self, base_path='models/saved_models/'):
        """Сохранение всех моделей"""
        os.makedirs(base_path, exist_ok=True)
        
        try:
            # Сохранение KMeans
            joblib.dump(self.kmeans_model, f"{base_path}kmeans_segmenter.pkl")
            
            # Сохранение классификатора
            joblib.dump(self.classifier, f"{base_path}rf_classifier.pkl")
            
            # Сохранение scaler и PCA
            joblib.dump(self.scaler, f"{base_path}scaler.pkl")
            joblib.dump(self.pca, f"{base_path}pca.pkl")
            
            # Сохранение mapping
            joblib.dump(self.segment_mapping, f"{base_path}segment_mapping.pkl")
            
            # Сохранение оригинальных названий признаков
            joblib.dump(self.original_feature_names, f"{base_path}feature_names.pkl")
            
            print("✅ Все модели сегментации успешно сохранены")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при сохранении моделей сегментации: {e}")
            return False
    
    @classmethod
    def load_models(cls, base_path='models/saved_models/'):
        """Загрузка всех моделей"""
        segmenter = cls()
        
        if not os.path.exists(base_path):
            print("❌ Папка с моделями не найдена. Требуется обучение.")
            return segmenter
        
        try:
            # Загрузка моделей
            segmenter.kmeans_model = joblib.load(f"{base_path}kmeans_segmenter.pkl")
            segmenter.classifier = joblib.load(f"{base_path}rf_classifier.pkl")
            segmenter.scaler = joblib.load(f"{base_path}scaler.pkl")
            segmenter.pca = joblib.load(f"{base_path}pca.pkl")
            segmenter.segment_mapping = joblib.load(f"{base_path}segment_mapping.pkl")
            
            # Загрузка оригинальных названий признаков
            if os.path.exists(f"{base_path}feature_names.pkl"):
                segmenter.original_feature_names = joblib.load(f"{base_path}feature_names.pkl")
            
            print("✅ Все модели сегментации успешно загружены")
            return segmenter
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке моделей сегментации: {e}")
            print("⚠️ Требуется повторное обучение модели сегментации")
            return segmenter