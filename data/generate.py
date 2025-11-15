import pandas as pd
import numpy as np
import random
import json
from datetime import datetime, timedelta
import os

# Создаем директорию для сохранения данных
os.makedirs('synthetic_data', exist_ok=True)

def generate_locations_data(n_samples=1000):
    """Генератор синтетических данных для геоаналитики и оптимизации точек продаж"""
    locations = []
    
    moscow_districts = ['central', 'north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest']
    age_groups = ['18-25', '26-35', '36-45', '46-55', '56+']
    income_levels = ['high', 'medium', 'low']
    employment_types = ['office_workers', 'students', 'retail_workers', 'other']
    competitor_names = ['Magnit', 'Pyaterochka', 'Perekrestok', 'Lenta', 'Fix Price', 'Okey', 'Azbuka Vkusa', 'Other']
    
    for i in range(n_samples):
        # Генерируем координаты в пределах Москвы
        lat = 55.75 + random.uniform(-0.3, 0.3)
        lng = 37.62 + random.uniform(-0.3, 0.3)
        
        # Генерируем район с реалистичными характеристиками
        district = random.choice(moscow_districts)
        
        # Настраиваем параметры в зависимости от района
        if district == 'central':
            pedestrian_traffic = random.randint(15000, 25000)
            avg_income = 'high'
            store_density = random.randint(20, 40)
        elif district in ['northwest', 'southwest']:
            pedestrian_traffic = random.randint(8000, 15000)
            avg_income = 'medium'
            store_density = random.randint(10, 25)
        else:
            pedestrian_traffic = random.randint(3000, 10000)
            avg_income = 'low'
            store_density = random.randint(5, 15)
        
        # Генерируем демографический профиль
        age_distribution = {age: round(random.random(), 2) for age in age_groups}
        total = sum(age_distribution.values())
        age_distribution = {age: round(value/total, 2) for age, value in age_distribution.items()}
        
        income_distribution = {level: round(random.random(), 2) for level in income_levels}
        total = sum(income_distribution.values())
        income_distribution = {level: round(value/total, 2) for level, value in income_distribution.items()}
        
        # Генерируем конкурентов
        num_competitors = random.randint(0, 15)
        competitor_list = random.sample(competitor_names, min(num_competitors, len(competitor_names)))
        competitor_shares = [round(random.random(), 2) for _ in range(len(competitor_list))]
        total = sum(competitor_shares)
        if total > 0:
            competitor_shares = [round(share/total, 2) for share in competitor_shares]
        
        competitors = {
            "within_500m": random.randint(0, 8),
            "within_1km": random.randint(5, num_competitors + 5),
            "market_share": {comp: share for comp, share in zip(competitor_list, competitor_shares)},
            "store_density": store_density
        }
        
        # Генерируем историческую активность
        avg_monthly_spending = random.randint(5000000, 20000000)
        growth_rate = round(random.uniform(-0.1, 0.3), 2)
        seasonal_coeff = {
            "summer": round(random.uniform(0.8, 1.5), 2),
            "winter": round(random.uniform(0.6, 1.2), 2),
            "spring": round(random.uniform(0.9, 1.3), 2),
            "autumn": round(random.uniform(0.8, 1.2), 2)
        }
        
        location = {
            "location_id": f"LOC_{i+1:04d}",
            "coordinates": {"lat": round(lat, 6), "lng": round(lng, 6)},
            "district": district,
            "city": "Москва",
            "pedestrian_traffic": {
                "weekday_avg": pedestrian_traffic,
                "weekend_avg": int(pedestrian_traffic * 1.5),
                "peak_hours": sorted(random.sample(range(8, 22), 4))
            },
            "demographic_profile": {
                "age_groups": age_distribution,
                "income_level": income_distribution,
                "employment": {
                    "office_workers": round(random.uniform(0.3, 0.8), 2),
                    "students": round(random.uniform(0.05, 0.3), 2),
                    "retail_workers": round(random.uniform(0.05, 0.25), 2),
                    "other": 0.0  # Будет рассчитано как остаток
                }
            },
            "competitors": competitors,
            "historical_activity": {
                "avg_monthly_spending": avg_monthly_spending,
                "growth_rate": growth_rate,
                "seasonal_coefficient": seasonal_coeff
            },
            "commercial_metrics": {
                "avg_purchase_value": round(random.uniform(500, 1500), 2),
                "purchase_frequency": round(random.uniform(1.5, 3.5), 1),
                "popular_categories": random.sample(['groceries', 'electronics', 'clothing', 'pharmacy', 'household'], 3)
            }
        }
        
        # Корректируем долю "other" в employment
        total_employment = sum(location["demographic_profile"]["employment"].values())
        location["demographic_profile"]["employment"]["other"] = round(1.0 - total_employment, 2)
        
        locations.append(location)
    
    return pd.DataFrame(locations)

def generate_demand_forecast_data(n_samples=1000):
    """Генератор данных для прогноза спроса"""
    demand_data = []
    
    regions = ['moscow', 'st_petersburg', 'novosibirsk', 'ekaterinburg', 'kazan', 'rostov', 'krasnodar', 'vladivostok']
    categories = ['electronics', 'groceries', 'clothing', 'pharmacy', 'household', 'beauty', 'sports']
    
    for i in range(n_samples):
        region = random.choice(regions)
        period = f"2024-{random.randint(1, 12):02d}"
        
        # Генерируем данные по категориям
        category_data = {}
        for category in categories:
            # Базовые параметры зависят от категории
            if category == 'electronics':
                base_volume = random.randint(100000000, 300000000)
                growth_trend = round(random.uniform(0.05, 0.15), 2)
                avg_transaction = random.randint(3000, 5000)
            elif category == 'groceries':
                base_volume = random.randint(300000000, 600000000)
                growth_trend = round(random.uniform(0.02, 0.08), 2)
                avg_transaction = random.randint(800, 1500)
            elif category == 'clothing':
                base_volume = random.randint(200000000, 400000000)
                growth_trend = round(random.uniform(0.08, 0.18), 2)
                avg_transaction = random.randint(2500, 4500)
            else:
                base_volume = random.randint(50000000, 200000000)
                growth_trend = round(random.uniform(0.03, 0.12), 2)
                avg_transaction = random.randint(1000, 3000)
            
            # Сезонность зависит от категории и месяца
            month = int(period.split('-')[1])
            if category == 'electronics':
                seasonality = {
                    "q1": round(0.9 + 0.1 * random.random(), 2),
                    "q2": round(1.1 + 0.1 * random.random(), 2),
                    "q3": round(0.8 + 0.1 * random.random(), 2),
                    "q4": round(1.5 + 0.2 * random.random(), 2)
                }
            elif category == 'groceries':
                seasonality = {
                    "q1": round(1.2 + 0.1 * random.random(), 2),
                    "q2": round(0.9 + 0.1 * random.random(), 2),
                    "q3": round(0.8 + 0.1 * random.random(), 2),
                    "q4": round(1.4 + 0.1 * random.random(), 2)
                }
            else:
                seasonality = {
                    "q1": round(1.0 + 0.2 * random.random(), 2),
                    "q2": round(1.2 + 0.2 * random.random(), 2),
                    "q3": round(1.0 + 0.2 * random.random(), 2),
                    "q4": round(1.2 + 0.2 * random.random(), 2)
                }
            
            # Демографический спрос
            if category == 'electronics':
                demographic_demand = {
                    "18-25": round(0.3 + 0.1 * random.random(), 2),
                    "26-35": round(0.4 + 0.1 * random.random(), 2),
                    "36-45": round(0.2 + 0.1 * random.random(), 2),
                    "46+": round(0.1 + 0.1 * random.random(), 2)
                }
            elif category == 'groceries':
                demographic_demand = {
                    "18-25": round(0.1 + 0.1 * random.random(), 2),
                    "26-35": round(0.3 + 0.1 * random.random(), 2),
                    "36-45": round(0.4 + 0.1 * random.random(), 2),
                    "46+": round(0.2 + 0.1 * random.random(), 2)
                }
            else:
                demographic_demand = {
                    "18-25": round(0.25 + 0.15 * random.random(), 2),
                    "26-35": round(0.35 + 0.15 * random.random(), 2),
                    "36-45": round(0.25 + 0.15 * random.random(), 2),
                    "46+": round(0.15 + 0.15 * random.random(), 2)
                }
            
            # Нормализуем демографические доли
            total = sum(demographic_demand.values())
            demographic_demand = {k: round(v/total, 2) for k, v in demographic_demand.items()}
            
            category_data[category] = {
                "transaction_count": int(base_volume / avg_transaction * (1 + growth_trend)),
                "total_volume": base_volume,
                "avg_transaction": avg_transaction,
                "growth_trend": growth_trend,
                "seasonality": seasonality,
                "demographic_demand": demographic_demand
            }
        
        # Внешние факторы
        external_factors = {
            "economic_index": round(95 + 20 * random.random(), 1),
            "weather_impact": round(0.8 + 0.4 * random.random(), 2),
            "holiday_effect": round(1.0 + 0.5 * random.random(), 2),
            "competitor_activity": round(0.7 + 0.6 * random.random(), 2)
        }
        
        # Прогноз на 3 месяца
        forecast_3months = {}
        for category in categories[:3]:  # Прогноз только для первых 3 категорий
            base_volume = category_data[category]["total_volume"]
            growth = category_data[category]["growth_trend"]
            forecast_volume = int(base_volume * (1 + growth) * 1.1)  # +10% для прогноза
            forecast_3months[category] = {
                "volume": forecast_volume,
                "confidence": round(0.7 + 0.25 * random.random(), 2)
            }
        
        record = {
            "region_id": f"REG_{region.upper()}",
            "period": period,
            "category_data": category_data,
            "external_factors": external_factors,
            "forecast_3months": forecast_3months
        }
        
        demand_data.append(record)
    
    return pd.DataFrame(demand_data)

def generate_b2b_segmentation_data(n_samples=1000):
    """Генератор данных для RFM-сегментации B2B-клиентов"""
    b2b_data = []
    
    company_sizes = ['small', 'medium', 'large', 'enterprise']
    industries = ['retail', 'wholesale', 'manufacturing', 'logistics', 'it_services', 'food_service', 'pharmacy']
    categories = ['office_supplies', 'it_services', 'logistics', 'marketing', 'equipment', 'raw_materials']
    
    for i in range(n_samples):
        company_size = random.choice(company_sizes)
        industry = random.choice(industries)
        
        # Генерируем характеристики компании в зависимости от размера
        if company_size == 'small':
            annual_revenue = random.randint(50000000, 200000000)
            employee_count = random.randint(5, 50)
            years_in_business = random.randint(1, 10)
        elif company_size == 'medium':
            annual_revenue = random.randint(200000000, 1000000000)
            employee_count = random.randint(50, 250)
            years_in_business = random.randint(3, 15)
        elif company_size == 'large':
            annual_revenue = random.randint(1000000000, 5000000000)
            employee_count = random.randint(250, 1000)
            years_in_business = random.randint(5, 20)
        else:  # enterprise
            annual_revenue = random.randint(5000000000, 20000000000)
            employee_count = random.randint(1000, 10000)
            years_in_business = random.randint(10, 30)
        
        # RFM метрики (зависят от размера компании)
        if company_size == 'small':
            recency = random.randint(1, 30)
            frequency = random.randint(5, 20)
            monetary = random.randint(1000000, 10000000)
        elif company_size == 'medium':
            recency = random.randint(1, 15)
            frequency = random.randint(15, 50)
            monetary = random.randint(5000000, 50000000)
        elif company_size == 'large':
            recency = random.randint(1, 7)
            frequency = random.randint(30, 100)
            monetary = random.randint(20000000, 200000000)
        else:  # enterprise
            recency = random.randint(1, 3)
            frequency = random.randint(50, 200)
            monetary = random.randint(50000000, 500000000)
        
        # Поведенческие паттерны
        payment_methods = {
            "card": round(0.5 + 0.3 * random.random(), 2),
            "bank_transfer": round(0.3 + 0.3 * random.random(), 2),
            "cash": round(0.1 + 0.2 * random.random(), 2)
        }
        total = sum(payment_methods.values())
        payment_methods = {k: round(v/total, 2) for k, v in payment_methods.items()}
        
        peak_times = sorted(random.sample(['09:00-11:00', '11:00-13:00', '13:00-15:00', '15:00-17:00', '17:00-19:00'], 2))
        
        seasonal_patterns = {
            "high_season": random.sample(['december', 'june', 'september'], 1),
            "low_season": random.sample(['august', 'february', 'july'], 1)
        }
        
        # Предпочтения категорий
        category_preferences = {cat: round(random.random(), 2) for cat in categories}
        total = sum(category_preferences.values())
        category_preferences = {cat: round(v/total, 2) for cat, v in category_preferences.items()}
        
        # Индикаторы лояльности
        contract_duration = random.randint(6, 36)
        upsell_history = random.randint(0, 5)
        support_requests = random.randint(1, 20)
        nps_score = random.randint(30, 90)
        
        # Определяем сегмент на основе RFM
        if recency <= 7 and frequency >= 30 and monetary >= 50000000:
            segment = "high_value_loyal"
        elif recency <= 15 and frequency >= 15 and monetary >= 10000000:
            segment = "medium_value_growing"
        elif recency <= 30 and frequency >= 5 and monetary >= 1000000:
            segment = "low_value_potential"
        else:
            segment = "at_risk"
        
        # Прогнозируемая пожизненная ценность
        if segment == "high_value_loyal":
            plv = annual_revenue * 0.1 * random.uniform(3, 5)
        elif segment == "medium_value_growing":
            plv = annual_revenue * 0.1 * random.uniform(2, 3)
        elif segment == "low_value_potential":
            plv = annual_revenue * 0.1 * random.uniform(1, 2)
        else:
            plv = annual_revenue * 0.1 * random.uniform(0.5, 1)
        
        # Рекомендуемые действия
        if segment == "high_value_loyal":
            actions = ["offer_premium_services", "assign_personal_manager", "cross_sell_analytics"]
        elif segment == "medium_value_growing":
            actions = ["offer_growth_packages", "provide_success_stories", "suggest_integrations"]
        elif segment == "low_value_potential":
            actions = ["provide_training", "offer_trial_premium", "send_case_studies"]
        else:
            actions = ["conduct_satisfaction_survey", "offer_special_discount", "assign_account_manager"]
        
        record = {
            "client_id": f"B2B_{i+1:05d}",
            "company_profile": {
                "size": company_size,
                "industry": industry,
                "annual_revenue": annual_revenue,
                "employee_count": employee_count,
                "years_in_business": years_in_business
            },
            "rfm_metrics": {
                "recency": recency,
                "frequency": frequency,
                "monetary": monetary
            },
            "behavior_patterns": {
                "payment_methods": payment_methods,
                "peak_transaction_times": peak_times,
                "seasonal_patterns": seasonal_patterns,
                "category_preferences": category_preferences
            },
            "loyalty_indicators": {
                "contract_duration": contract_duration,
                "upsell_history": upsell_history,
                "support_requests": support_requests,
                "nps_score": nps_score
            },
            "segment": segment,
            "predicted_lifetime_value": int(plv),
            "recommended_actions": actions
        }
        
        b2b_data.append(record)
    
    return pd.DataFrame(b2b_data)

def generate_market_analysis_data(n_samples=500):
    """Генератор данных для анализа рынка и конкурентов"""
    market_data = []
    
    regions = ['moscow_metropolitan', 'st_petersburg', 'ural_region', 'siberia', 'south_russia', 'volga_region']
    market_segments = ['retail_fmCG', 'logistics', 'real_estate', 'food_service', 'pharmacy']
    
    for i in range(n_samples):
        region = random.choice(regions)
        segment = random.choice(market_segments)
        year = random.randint(2023, 2025)
        quarter = random.randint(1, 4)
        
        # Размер рынка и рост
        if segment == 'retail_fmCG':
            market_size = random.randint(300000000000, 600000000000)
            growth_rate = round(random.uniform(0.08, 0.15), 2)
            digital_penetration = round(random.uniform(0.3, 0.6), 2)
        elif segment == 'logistics':
            market_size = random.randint(150000000000, 300000000000)
            growth_rate = round(random.uniform(0.05, 0.12), 2)
            digital_penetration = round(random.uniform(0.2, 0.4), 2)
        elif segment == 'real_estate':
            market_size = random.randint(400000000000, 800000000000)
            growth_rate = round(random.uniform(0.03, 0.08), 2)
            digital_penetration = round(random.uniform(0.15, 0.35), 2)
        else:
            market_size = random.randint(100000000000, 250000000000)
            growth_rate = round(random.uniform(0.06, 0.14), 2)
            digital_penetration = round(random.uniform(0.25, 0.5), 2)
        
        # Анализ конкурентов
        num_competitors = random.randint(2, 8)
        competitor_ids = [f"COMP_{j+1:03d}" for j in range(num_competitors)]
        market_shares = [round(random.random(), 2) for _ in range(num_competitors)]
        total = sum(market_shares)
        market_shares = [round(share/total, 2) for share in market_shares]
        
        competitors = []
        for comp_id, share in zip(competitor_ids, market_shares):
            strengths = random.sample(['price', 'logistics', 'brand_recognition', 'product_range', 'customer_service', 'digital_experience'], 2)
            weaknesses = random.sample(['price', 'logistics', 'brand_recognition', 'product_range', 'customer_service', 'digital_experience'], 2)
            locations_count = random.randint(10, 200)
            
            competitors.append({
                "competitor_id": comp_id,
                "market_share": share,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "locations_count": locations_count
            })
        
        # Потребительские тренды
        consumer_trends = {
            "online_shopping": round(random.uniform(0.3, 0.7), 2),
            "mobile_payments": round(random.uniform(0.5, 0.9), 2),
            "personalization_demand": round(random.uniform(0.4, 0.8), 2),
            "sustainability_focus": round(random.uniform(0.2, 0.6), 2)
        }
        
        # Производительность локаций
        if region == 'moscow_metropolitan':
            high_performing = ['central', 'northwest', 'southwest']
            emerging = ['east', 'outer_moscow']
            declining = ['industrial_zones']
        elif region == 'st_petersburg':
            high_performing = ['central', 'admiralteysky', 'vasileostrovsky']
            emerging = ['kalininsky', 'krasnoselsky']
            declining = ['industrial_areas']
        else:
            high_performing = ['city_center', 'business_district']
            emerging = ['suburbs', 'new_developments']
            declining = ['remote_areas']
        
        record = {
            "analysis_id": f"ANALYSIS_{i+1:04d}",
            "market_segment": segment,
            "region": region,
            "time_period": f"{year}_q{quarter}",
            "market_size": {
                "total_volume": market_size,
                "growth_rate": growth_rate,
                "digital_penetration": digital_penetration
            },
            "competitor_analysis": competitors,
            "consumer_trends": consumer_trends,
            "location_performance": {
                "high_performing_districts": high_performing,
                "emerging_districts": emerging,
                "declining_areas": declining
            }
        }
        
        market_data.append(record)
    
    return pd.DataFrame(market_data)

def generate_metadata():
    """Генератор метаданных и словарей"""
    metadata = {
        "category_mappings": {
            "mcc_codes": {
                "5411": "grocery_stores",
                "5732": "electronics",
                "5651": "clothing",
                "5912": "pharmacy",
                "5812": "restaurants",
                "7997": "fitness",
                "5311": "department_stores",
                "5499": "convenience_stores",
                "5541": "gas_stations",
                "5814": "fast_food"
            },
            "industry_codes": {
                "47": "retail",
                "46": "wholesale",
                "62": "it_services",
                "49": "transportation",
                "68": "real_estate",
                "56": "food_service",
                "47.7": "specialized_retail",
                "47.9": "non_store_retail"
            }
        },
        "geographical_regions": {
            "moscow": {
                "districts": ["central", "north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"],
                "population_density": [15000, 8500, 7800, 6200, 9100, 5800, 7200, 4900, 6500],
                "avg_income_level": ["high", "medium-high", "medium", "medium-low", "high", "low", "medium-high", "low", "medium"]
            },
            "st_petersburg": {
                "districts": ["central", "admiralteysky", "vasileostrovsky", "petrogradsky", "krasnoselsky"],
                "population_density": [12000, 9500, 8700, 7800, 6500],
                "avg_income_level": ["high", "high", "medium-high", "medium", "low"]
            },
            "novosibirsk": {
                "districts": ["central", "leninsky", "oktyabrsky", "kalininsky", "sovetский"],
                "population_density": [10000, 8000, 7500, 6800, 6200],
                "avg_income_level": ["medium-high", "medium", "medium-low", "low", "medium"]
            }
        },
        "time_series_parameters": {
            "seasonality_factors": {
                "monthly": [0.95, 0.92, 1.05, 1.12, 1.15, 1.25, 0.95, 0.85, 1.05, 1.15, 1.25, 1.45],
                "weekly": [0.85, 1.15, 1.25, 1.20, 1.15, 0.95, 0.85],
                "daily": [0.6, 0.8, 1.1, 1.2, 1.1, 0.9, 0.7, 0.6, 0.7, 0.9, 1.2, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.6]
            },
            "trend_coefficients": {
                "electronics": 0.08,
                "groceries": 0.05,
                "clothing": 0.12,
                "pharmacy": 0.15,
                "household": 0.07,
                "beauty": 0.10,
                "sports": 0.09
            }
        },
        "api_endpoints": {
            "location_analysis": "/api/v1/location-analysis",
            "demand_forecast": "/api/v1/demand-forecast",
            "b2b_segmentation": "/api/v1/b2b-segmentation",
            "market_analysis": "/api/v1/market-analysis"
        },
        "pricing_tiers": {
            "basic": {
                "monthly_price": 100000,
                "max_requests": 1000,
                "features": ["location_analysis", "basic_forecasts"]
            },
            "professional": {
                "monthly_price": 350000,
                "max_requests": 5000,
                "features": ["all_basic", "advanced_forecasts", "b2b_segmentation"]
            },
            "enterprise": {
                "monthly_price": 1000000,
                "max_requests": "unlimited",
                "features": ["all_professional", "custom_models", "dedicated_support"]
            }
        }
    }
    
    return metadata

# Генерация и сохранение всех данных
print("Генерация синтетических данных для кейса Альфа-Банка...")
print("=" * 50)

# 1. Данные для оптимизации точек продаж
print("1. Генерация данных для геоаналитики (100000 записей)...")
locations_df = generate_locations_data(100000)
locations_df.to_json('synthetic_data/locations_data.json', orient='records', indent=2, force_ascii=False)
locations_df.head(2).to_csv('synthetic_data/locations_data_sample.csv', index=False)
print(f"✓ Сохранено: synthetic_data/locations_data.json ({len(locations_df)} записей)")

# 2. Данные для прогноза спроса
print("\n2. Генерация данных для прогноза спроса (100000 записей)...")
demand_df = generate_demand_forecast_data(100000)
demand_df.to_json('synthetic_data/demand_forecast_data.json', orient='records', indent=2, force_ascii=False)
demand_df.head(2).to_csv('synthetic_data/demand_forecast_data_sample.csv', index=False)
print(f"✓ Сохранено: synthetic_data/demand_forecast_data.json ({len(demand_df)} записей)")

# 3. Данные для RFM-сегментации B2B
print("\n3. Генерация данных для сегментации B2B-клиентов (100000 записей)...")
b2b_df = generate_b2b_segmentation_data(100000)
b2b_df.to_json('synthetic_data/b2b_segmentation_data.json', orient='records', indent=2, force_ascii=False)
b2b_df.head(2).to_csv('synthetic_data/b2b_segmentation_data_sample.csv', index=False)
print(f"✓ Сохранено: synthetic_data/b2b_segmentation_data.json ({len(b2b_df)} записей)")

# 4. Данные для анализа рынка
print("\n4. Генерация данных для анализа рынка (500 записей)...")
market_df = generate_market_analysis_data(500)
market_df.to_json('synthetic_data/market_analysis_data.json', orient='records', indent=2, force_ascii=False)
market_df.head(2).to_csv('synthetic_data/market_analysis_data_sample.csv', index=False)
print(f"✓ Сохранено: synthetic_data/market_analysis_data.json ({len(market_df)} записей)")

# 5. Метаданные
print("\n5. Генерация метаданных и словарей...")
metadata = generate_metadata()
with open('synthetic_data/metadata.json', 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
print("✓ Сохранено: synthetic_data/metadata.json")

# 6. Пример API-ответа
print("\n6. Генерация примера API-ответа...")
sample_api_response = {
    "request_id": "req_123456",
    "timestamp": datetime.now().isoformat(),
    "query_params": {
        "location": {"lat": 55.7558, "lng": 37.6173},
        "radius": 1000,
        "categories": ["groceries", "electronics"]
    },
    "results": {
        "location_analysis": locations_df.iloc[0].to_dict(),
        "demand_forecast": demand_df.iloc[0].to_dict(),
        "market_insights": market_df.iloc[0].to_dict(),
        "recommended_actions": [
            "Открыть магазин в данном районе",
            "Фокус на электронике и продуктах",
            "Целевая аудитория: 26-35 лет с высоким доходом"
        ]
    },
    "confidence_score": 0.85,
    "processing_time_ms": 125
}
with open('synthetic_data/sample_api_response.json', 'w', encoding='utf-8') as f:
    json.dump(sample_api_response, f, indent=2, ensure_ascii=False)
print("✓ Сохранено: synthetic_data/sample_api_response.json")

print("\n" + "=" * 50)
print("✅ Все данные успешно сгенерированы и сохранены в директорию 'synthetic_data/'")
print(f"📊 Всего записей сгенерировано: {len(locations_df) + len(demand_df) + len(b2b_df) + len(market_df)}")
print("📁 Файлы готовы для использования в ML-моделях и веб-приложении")
print("=" * 50)

# Выводим структуру сгенерированных данных
print("\nСтруктура сгенерированных данных:")

# Пример структуры locations_data
print("\n🔹 locations_data.json (пример первой записи):")
print(json.dumps(locations_df.iloc[0].to_dict(), indent=2, ensure_ascii=False)[:500] + "...")

# Пример структуры demand_forecast_data
print("\n🔹 demand_forecast_data.json (пример первой записи):")
print(json.dumps(demand_df.iloc[0].to_dict(), indent=2, ensure_ascii=False)[:500] + "...")

# Пример структуры b2b_segmentation_data
print("\n🔹 b2b_segmentation_data.json (пример первой записи):")
print(json.dumps(b2b_df.iloc[0].to_dict(), indent=2, ensure_ascii=False)[:500] + "...")

print("\n💡 Советы по использованию:")
print("1. Используйте locations_data.json для обучения моделей геоаналитики")
print("2. demand_forecast_data.json идеально подходит для LSTM/Prophet моделей")
print("3. b2b_segmentation_data.json можно использовать для RFM-анализа и кластеризации")
print("4. market_analysis_data.json поможет в создании рекомендательных систем")
print("5. metadata.json содержит словари для предобработки и feature engineering")