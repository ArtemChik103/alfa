import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from folium import Map, Marker, Circle
import folium
from streamlit_folium import folium_static
import json
import time
import os

# Настройка страницы
st.set_page_config(
    page_title="Альфа-Аналитика",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Загрузка стилей
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    :root {
        --primary-color: #EF4444; /* Red */
        --secondary-color: #3B82F6; /* Blue */
        --background-color: #111827; /* Dark Gray */
        --card-background-color: #1F2937; /* Lighter Gray */
        --text-color: #F9FAFB; /* Almost White */
        --subtle-text-color: #9CA3AF; /* Gray */
        --success-color: #10B981; /* Green */
        --warning-color: #F59E0B; /* Yellow */
        --font-family: 'Inter', sans-serif;
    }

    body {
        font-family: var(--font-family);
        color: var(--text-color);
        background-color: var(--background-color);
    }

    .stApp {
        background-color: var(--background-color);
    }

    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-color);
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .main-header span {
        color: var(--primary-color);
    }

    .subheader {
        font-size: 1.1rem;
        color: var(--subtle-text-color);
        text-align: center;
        margin-bottom: 3rem;
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: var(--card-background-color);
        border-right: 1px solid #374151;
    }
    
    .css-1d391kg .st-emotion-cache-16txtl3 {
        color: var(--text-color);
    }

    /* Metric Cards */
    .metric-card {
        background-color: var(--card-background-color);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #374151;
        margin: 0.5rem 0;
        text-align: center;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        border-color: var(--primary-color);
    }

    .metric-card h3 {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--subtle-text-color);
        margin-bottom: 0.5rem;
    }

    .metric-card p {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }

    /* Recommendation Box */
    .recommendation-box {
        background-color: var(--card-background-color);
        border-left: 4px solid var(--primary-color);
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .recommendation-box strong {
        color: var(--text-color);
    }

    /* Custom Boxes */
    .custom-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid;
    }
    .success-box {
        background-color: rgba(16, 185, 129, 0.1);
        border-color: var(--success-color);
        color: var(--success-color);
    }
    .warning-box {
        background-color: rgba(245, 158, 11, 0.1);
        border-color: var(--warning-color);
        color: var(--warning-color);
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton>button[kind="primary"] {
        background-color: var(--primary-color);
    }

    .stButton>button:hover {
        transform: scale(1.02);
    }

    /* Section Headers */
    h3 {
        font-weight: 600;
        color: var(--text-color);
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    h4 {
        font-weight: 600;
        color: var(--text-color);
        margin-top: 1rem;
    }

</style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown('<h1 class="main-header">🏦 Альфа-Аналитика для <span>бизнеса</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Прогнозируйте спрос, оптимизируйте локации, увеличивайте прибыль</p>', unsafe_allow_html=True)

# Боковая панель
with st.sidebar:
    st.markdown("### 🚀 Навигация")
    selected_page = st.radio(
        "Выберите сценарий:",
        ["🏠 Главная", "📍 Анализ локаций", "📈 Прогноз спроса", "👥 Сегментация клиентов"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ Настройки")
    api_base_url = st.text_input("URL API", "http://localhost:8000", key="api_url")
    
    st.markdown("---")
    st.markdown("### ℹ️ Информация")
    st.markdown("Это демо-версия MVP B2B-продукта Альфа-Банка")
    st.markdown("Все данные синтетические")

# Функция для проверки доступности API
def check_api_availability():
    try:
        response = requests.get(f"{api_base_url}/")
        return response.status_code == 200
    except:
        return False

# Главная страница
if selected_page == "🏠 Главная":
    st.markdown("""
    ### 🎯 Добро пожаловать в Альфа-Аналитику!
    
    Это демонстрационная платформа для B2B-продукта Альфа-Банка, основанная на монетизации данных и DS-экспертизы.
    
    #### 🚀 Доступные сценарии:
    
    **📍 Анализ локаций** - Определите лучшие места для открытия новых точек продаж на основе пешеходного трафика и демографических данных.
    
    **📈 Прогноз спроса** - Спрогнозируйте спрос на товарные категории в разных регионах с учетом экономических факторов.
    
    **👥 Сегментация клиентов** - Разделите ваших корпоративных клиентов на сегменты для персонализированных предложений.
    
    #### 💡 Как это работает:
    - Все данные являются синтетическими и сгенерированы для демонстрации
    - Модели обучены на реалистичных данных, имитирующих банковскую аналитику
    - Результаты носят рекомендательный характер
    
    **Начните с выбора сценария в боковой панели!**
    """)
    
    # Статус API
    st.markdown("### 🔌 Статус API")
    if check_api_availability():
        st.success("✅ API доступен и работает корректно")
    else:
        st.warning("⚠️ API недоступен. Проверьте URL в настройках или запустите бэкенд")

# Анализ локаций
elif selected_page == "📍 Анализ локаций":
    st.markdown("### 📍 Анализ потенциала локации")
    
    col1, col2 = st.columns([1, 1])
    
    # --- Translation Dictionaries ---
    districts_ru = {
        "central": "Центральный", "north": "Северный", "south": "Южный", 
        "east": "Восточный", "west": "Западный", "northeast": "Северо-Восточный", 
        "northwest": "Северо-Западный", "southeast": "Юго-Восточный", "southwest": "Юго-Западный"
    }
    districts_en = {v: k for k, v in districts_ru.items()}

    with col1:
        st.markdown("#### Параметры локации")
        
        pedestrian_traffic = st.slider(
            "Пешеходный трафик (чел/день)", 
            1000, 30000, 12500,
            help="Среднее количество пешеходов в будние дни"
        )
        
        avg_purchase_value = st.slider(
            "Средний чек (руб.)", 
            500, 3000, 1200,
            help="Средняя сумма покупки в районе"
        )
        
        district_ru = st.selectbox(
            "Район", 
            options=list(districts_ru.values()),
            index=0,
            help="Административный район города"
        )
        district = districts_en[district_ru]
        
        analyze_button = st.button("✨ Проанализировать локацию", type="primary", use_container_width=True)
    
    with col2:
        if analyze_button:
            with st.spinner("🔍 Анализируем потенциал локации..."):
                try:
                    response = requests.post(
                        f"{api_base_url}/analyze-location",
                        json={
                            "pedestrian_traffic": pedestrian_traffic,
                            "avg_purchase_value": avg_purchase_value,
                            "district": district
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()["analysis_result"]
                        
                        st.markdown("#### 📊 Результаты анализа")
                        
                        # Основные метрики
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        
                        with metric_col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>💰 Потенциал</h3>
                                <p style="color: var(--primary-color);">{result['potential_monthly_revenue']/1000000:.1f} млн ₽/мес</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with metric_col2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>⭐ Оценка</h3>
                                <p style="color: var(--success-color);">{result['recommendation_score']}%</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with metric_col3:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>🎯 Уверенность</h3>
                                <p style="color: var(--secondary-color);">{result['confidence']*100:.0f}%</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Рекомендации
                        st.markdown("#### 💡 Рекомендации")
                        for i, rec in enumerate(result['recommendations'], 1):
                            st.markdown(f"""
                            <div class="recommendation-box">
                                <strong>{i}. {rec}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Карта с маркером
                        st.markdown("#### 🗺️ Географическое положение")
                        
                        # --- Coordinates for districts ---
                        district_coords = {
                            "central": [55.7558, 37.6173],
                            "north": [55.8368, 37.5892],
                            "south": [55.6293, 37.6422],
                            "east": [55.7522, 37.7982],
                            "west": [55.7353, 37.4433],
                            "northeast": [55.8781, 37.6536],
                            "northwest": [55.8281, 37.4499],
                            "southeast": [55.6981, 37.7722],
                            "southwest": [55.6615, 37.5218]
                        }
                        coords = district_coords.get(district, [55.7558, 37.6173])

                        m = Map(location=coords, zoom_start=12, tiles='CartoDB dark_matter')
                        
                        # Определение цвета маркера в зависимости от оценки
                        if result['recommendation_score'] >= 80:
                            color = 'green'
                        elif result['recommendation_score'] >= 70:
                            color = 'blue'
                        else:
                            color = 'red'
                        
                        marker = Marker(
                            coords,
                            popup=f"""
                            <b>Потенциал локации</b><br>
                            Оценка: {result['recommendation_score']}%<br>
                            Прогноз: {result['potential_monthly_revenue']/1000000:.1f} млн ₽/мес
                            """,
                            icon=folium.Icon(color=color, icon='info-sign')
                        )
                        
                        # Круг радиуса влияния
                        circle = Circle(
                            coords,
                            radius=500,
                            color=color,
                            fill=True,
                            fill_opacity=0.2,
                            popup=f"Радиус влияния: 500м"
                        )
                        
                        marker.add_to(m)
                        circle.add_to(m)
                        folium_static(m)
                        
                    else:
                        st.error(f"❌ Ошибка API: {response.status_code}")
                        st.error(response.text)
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Не удалось подключиться к API. Проверьте URL в настройках.")
                except Exception as e:
                    st.error(f"❌ Произошла ошибка: {str(e)}")

# Прогноз спроса
elif selected_page == "📈 Прогноз спроса":
    st.markdown("### 📈 Прогноз спроса на товары")
    
    col1, col2 = st.columns([1, 1])
    
    # --- Translation Dictionaries ---
    categories_ru = {
        "electronics": "Электроника", "groceries": "Продукты", "clothing": "Одежда",
        "pharmacy": "Аптеки", "household": "Товары для дома", "beauty": "Красота", "sports": "Спорт"
    }
    categories_en = {v: k for k, v in categories_ru.items()}

    regions_ru = {
        "REG_MSK": "Москва", "REG_SPB": "Санкт-Петербург", "REG_NSK": "Новосибирск",
        "REG_EKB": "Екатеринбург", "REG_KZN": "Казань"
    }
    regions_en = {v: k for k, v in regions_ru.items()}

    with col1:
        st.markdown("#### Параметры прогноза")
        
        category_ru = st.selectbox(
            "Категория товаров", 
            options=list(categories_ru.values()),
            index=0,
            help="Выберите категорию для прогноза"
        )
        category = categories_en[category_ru]
        
        region_ru = st.selectbox(
            "Регион", 
            options=list(regions_ru.values()),
            index=0,
            help="Выберите регион для анализа"
        )
        region = regions_en[region_ru]
        
        economic_index = st.slider(
            "Экономический индекс", 
            80, 120, 100,
            help="100 = базовый уровень экономической активности"
        )
        
        periods = st.slider(
            "Горизонт прогноза (месяцев)", 
            1, 6, 3,
            help="Количество месяцев для прогноза"
        )
        
        forecast_button = st.button("🔮 Спрогнозировать спрос", type="primary", use_container_width=True)
    
    with col2:
        if forecast_button:
            with st.spinner("📊 Генерируем прогноз..."):
                try:
                    response = requests.post(
                        f"{api_base_url}/forecast-demand",
                        json={
                            "category": category,
                            "region": region,
                            "economic_index": economic_index,
                            "periods": periods
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()["forecast_result"]
                        
                        st.markdown(f"#### 📊 Прогноз на {result['forecast_period']} для категории '{result['category']}'")
                        
                        # Таблица с прогнозами
                        if result['forecasts']:
                            forecast_df = pd.DataFrame(result['forecasts'])
                            
                            st.markdown("##### 📋 Детальный прогноз")
                            display_df = forecast_df[['month_name', 'predicted_volume']].copy()
                            display_df['predicted_volume'] = display_df['predicted_volume'].apply(
                                lambda x: f"{x/1000000:.1f} млн ₽"
                            )
                            display_df.columns = ['Месяц', 'Прогнозируемый объем']
                            
                            st.dataframe(
                                display_df,
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # График прогноза
                            st.markdown("##### 📈 График динамики спроса")
                            
                            fig = go.Figure()
                            
                            # Основной прогноз
                            fig.add_trace(go.Scatter(
                                x=forecast_df['month_name'],
                                y=forecast_df['predicted_volume'],
                                mode='lines+markers',
                                name='Прогноз',
                                line=dict(color='var(--primary-color)', width=3),
                                marker=dict(size=10),
                                hovertemplate='<b>%{x}</b><br>Объем: %{y:,.0f} ₽<extra></extra>'
                            ))
                            
                            # Доверительные интервалы
                            fig.add_trace(go.Scatter(
                                x=forecast_df['month_name'] + forecast_df['month_name'][::-1],
                                y=forecast_df['upper_bound'].tolist() + forecast_df['lower_bound'].tolist()[::-1],
                                fill='toself',
                                fillcolor='rgba(239, 68, 68, 0.2)',
                                line=dict(color='rgba(255,255,255,0)'),
                                hoverinfo="skip",
                                name='Доверительный интервал'
                            ))
                            
                            fig.update_layout(
                                title=f"Прогноз спроса на {category} в регионе {region}",
                                xaxis_title="Месяц",
                                yaxis_title="Объем продаж (руб.)",
                                hovermode='x unified',
                                template='plotly_dark',
                                yaxis_tickformat=',',
                                height=400,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)'
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Рекомендации
                            if 'recommendations' in result and result['recommendations']:
                                st.markdown("#### 💡 Рекомендации по закупкам")
                                for i, rec in enumerate(result['recommendations'], 1):
                                    if 'рост' in rec.lower() or 'увелич' in rec.lower():
                                        box_class = "success-box"
                                    elif 'снижени' in rec.lower() or 'сократ' in rec.lower():
                                        box_class = "warning-box"
                                    else:
                                        box_class = "recommendation-box"
                                    
                                    st.markdown(f"""
                                    <div class="custom-box {box_class}">
                                        <strong>{i}. {rec}</strong>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Статистика по категории
                            if 'category_insights' in result:
                                insights = result['category_insights']
                                st.markdown("#### 📊 Статистика по категории")
                                
                                insight_col1, insight_col2, insight_col3 = st.columns(3)
                                
                                with insight_col1:
                                    st.metric("Средний объем", f"{insights.get('avg_volume', 0)/1000000:.1f} млн ₽")
                                
                                with insight_col2:
                                    st.metric("Темп роста", f"{insights.get('growth_rate', 0)*100:.1f}%")
                                
                                with insight_col3:
                                    st.metric("Волатильность", f"{insights.get('volatility', 0)*100:.1f}%")
                        
                    else:
                        st.error(f"❌ Ошибка API: {response.status_code}")
                        st.error(response.text)
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Не удалось подключиться к API. Проверьте URL в настройках.")
                except Exception as e:
                    st.error(f"❌ Произошла ошибка: {str(e)}")

# Сегментация клиентов
elif selected_page == "👥 Сегментация клиентов":
    st.markdown("### 👥 Сегментация B2B-клиентов")
    
    col1, col2 = st.columns([1, 1])
    
    # --- Translation Dictionaries ---
    company_sizes_ru = {
        "small": "Малая", "medium": "Средняя", 
        "large": "Крупная", "enterprise": "Корпорация"
    }
    company_sizes_en = {v: k for k, v in company_sizes_ru.items()}

    with col1:
        st.markdown("#### Данные клиента")
        
        recency = st.slider(
            "Давность последней покупки (дней)", 
            1, 90, 15,
            help="Сколько дней прошло с последней покупки"
        )
        
        frequency = st.slider(
            "Частота покупок (в месяц)", 
            1, 50, 12,
            help="Сколько покупок совершает клиент в среднем за месяц"
        )
        
        monetary = st.number_input(
            "Средний оборот (руб.)", 
            100000, 500000000, 5000000,
            step=100000,
            help="Средний ежемесячный оборот клиента"
        )
        
        company_size_ru = st.selectbox(
            "Размер компании", 
            options=list(company_sizes_ru.values()),
            index=1,
            help="Размер компании клиента"
        )
        company_size = company_sizes_en[company_size_ru]
        
        segment_button = st.button("🎯 Проанализировать клиента", type="primary", use_container_width=True)
    
    with col2:
        if segment_button:
            with st.spinner("🔍 Определяем сегмент клиента..."):
                try:
                    response = requests.post(
                        f"{api_base_url}/segment-client",
                        json={
                            "recency": recency,
                            "frequency": frequency,
                            "monetary": monetary,
                            "company_size": company_size
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()["segmentation_result"]
                        
                        st.markdown(f"#### 🏷️ Сегмент: {result['segment_name']}")
                        
                        # Цветовая индикация сегмента
                        segment_colors = {
                            "high_value_loyal": "#27ae60",
                            "medium_value_growing": "#2980b9", 
                            "low_value_potential": "#f39c12",
                            "at_risk": "#e74c3c",
                            "High-Value Loyal": "#27ae60",
                            "Growing Potential": "#2980b9",
                            "New Opportunity": "#f39c12",
                            "At Risk": "#e74c3c"
                        }
                        
                        color = segment_colors.get(result['segment_name'].lower(), "#7f8c8d")
                        
                        st.markdown(f"""
                        <div style='background-color: var(--card-background-color); padding: 20px; border-radius: 12px; border-left: 5px solid {color}; margin-bottom: 20px;'>
                            <h3 style='color: {color}; border-bottom: none; margin-top: 0;'>{result['segment_name']}</h3>
                            <p style='color: var(--text-color); font-size: 1.1rem;'>
                                {result['segment_description']}
                            </p>
                            <p style='color: var(--subtle-text-color);'>
                                <strong>Уверенность:</strong> {result['confidence']*100:.0f}%
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Рекомендуемые действия
                        st.markdown("#### 🎯 Рекомендуемые действия")
                        for i, action in enumerate(result['recommendations'], 1):
                            st.checkbox(f"{i}. {action}", value=True)
                        
                        # Ключевые метрики
                        if 'key_metrics' in result:
                            st.markdown("#### 📊 Ключевые метрики")
                            
                            metrics = result['key_metrics']
                            metric_col1, metric_col2 = st.columns(2)
                            
                            with metric_col1:
                                st.metric("Монетарный потенциал", f"{metrics['monetary_potential']/1000000:.1f} млн ₽")
                            
                            with metric_col2:
                                st.metric("Уровень лояльности", metrics['loyalty_level'].title())
                        
                        # RFM-анализ
                        st.markdown("#### 📈 RFM-анализ")
                        
                        rfm_data = pd.DataFrame({
                            'Метрика': ['Recency (R)', 'Frequency (F)', 'Monetary (M)'],
                            'Значение': [recency, frequency, monetary/1000000],
                            'Максимум': [90, 50, 500]
                        })
                        
                        # Нормализация для визуализации
                        rfm_data['Нормированное'] = rfm_data['Значение'] / rfm_data['Максимум']
                        
                        fig = px.bar(
                            rfm_data,
                            x='Метрика',
                            y='Нормированное',
                            title="RFM-профиль клиента",
                            color='Метрика',
                            color_discrete_map={
                                'Recency (R)': 'var(--primary-color)',
                                'Frequency (F)': 'var(--secondary-color)',
                                'Monetary (M)': 'var(--success-color)'
                            },
                            text=rfm_data['Значение'].apply(lambda x: f'{x:,.0f}')
                        )
                        
                        fig.update_layout(
                            yaxis_title="Нормированное значение",
                            template='plotly_dark',
                            height=350,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                        fig.update_traces(textposition='outside')
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                    else:
                        st.error(f"❌ Ошибка API: {response.status_code}")
                        st.error(response.text)
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Не удалось подключиться к API. Проверьте URL в настройках.")
                except Exception as e:
                    st.error(f"❌ Произошла ошибка: {str(e)}")

# Футер
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; font-size: 0.9rem;'>
    <p>🚀 MVP B2B-продукта Альфа-Банка | Все права защищены © 2025</p>
    <p>💡 Демонстрационная версия с синтетическими данными</p>
</div>
""", unsafe_allow_html=True)