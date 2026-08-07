import os
import requests

DADATA_API_KEY = os.getenv("DADATA_API_KEY", "225939c9f990c2e2e9e7483e29a066e3ea06e8a9")
DADATA_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"

class DaDataClient:
    """Client for DaData.ru API to enrich B2B client data by INN or company name."""
    
    def __init__(self, api_key: str = DADATA_API_KEY):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Token {self.api_key}"
        }

    def get_company_by_inn(self, query: str) -> dict:
        """Fetch company details from DaData by INN or name."""
        payload = {"query": query.strip()}
        try:
            resp = requests.post(DADATA_URL, json=payload, headers=self.headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                suggestions = data.get("suggestions", [])
                if suggestions:
                    party = suggestions[0]
                    p_data = party.get("data", {})
                    
                    finance = p_data.get("finance", {}) or {}
                    revenue = finance.get("revenue") or 0
                    profit = finance.get("net_income") or 0
                    
                    employee_count = p_data.get("employee_count") or 1
                    
                    okved = p_data.get("okved") or ""
                    okved_type = p_data.get("okved_type") or ""
                    
                    state = p_data.get("state", {})
                    registration_date = state.get("registration_date")
                    company_age_years = 3.0
                    if registration_date:
                        import time
                        reg_ts = int(registration_date) / 1000.0
                        now_ts = time.time()
                        company_age_years = round((now_ts - reg_ts) / (365.25 * 86400), 1)

                    return {
                        "status": "success",
                        "inn": p_data.get("inn", query),
                        "kpp": p_data.get("kpp", ""),
                        "ogrn": p_data.get("ogrn", ""),
                        "name": party.get("value", ""),
                        "short_name": p_data.get("name", {}).get("short_with_opf", ""),
                        "address": p_data.get("address", {}).get("value", ""),
                        "okved": okved,
                        "okved_type": okved_type,
                        "employee_count": employee_count,
                        "revenue": revenue,
                        "profit": profit,
                        "company_age_years": company_age_years,
                        "management_name": p_data.get("management", {}).get("name", ""),
                        "raw": party
                    }
        except Exception as e:
            print(f"[DaData] Error fetching INN {query}: {e}")
            
        return {
            "status": "not_found",
            "inn": query,
            "name": f"Компания (ИНН {query})",
            "okved": "47.11",
            "employee_count": 5,
            "revenue": 10000000,
            "profit": 1000000,
            "company_age_years": 3.0
        }

if __name__ == "__main__":
    client = DaDataClient()
    # Test with Alfa-Bank INN 7707083893
    res = client.get_company_by_inn("7707083893")
    print("DaData Test Result:")
    print("Status:", res["status"])
    print("Name:", res["name"])
    print("Address:", res["address"])
    print("OKVED:", res["okved"])
    print("Employees:", res["employee_count"])
    print("Age:", res["company_age_years"])
