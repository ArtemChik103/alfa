import requests
import json
from datetime import datetime, timedelta

class MacroDataProvider:
    """Fetches real-time Central Bank of Russia (CBR) rates & Russian production calendar holidays."""
    
    def __init__(self):
        self.cbr_url = "https://www.cbr-xml-daily.ru/daily_json.js"

    def get_cbr_rates(self) -> dict:
        """Fetch real-time exchange rates (USD/RUB, CNY/RUB) from CBR API."""
        try:
            resp = requests.get(self.cbr_url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                valute = data.get("Valute", {})
                usd_rate = valute.get("USD", {}).get("Value", 90.5)
                cny_rate = valute.get("CNY", {}).get("Value", 12.5)
                return {
                    "status": "success",
                    "usd_rub": round(usd_rate, 2),
                    "cny_rub": round(cny_rate, 2),
                    "key_rate_cbr": 16.0, # CBR key rate
                    "date": data.get("Date", "")
                }
        except Exception as e:
            print(f"[CBR API] Error fetching rates: {e}")
            
        return {
            "status": "fallback",
            "usd_rub": 92.5,
            "cny_rub": 12.8,
            "key_rate_cbr": 16.0,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

    def get_russian_holidays(self, year: int = 2026) -> list:
        """Returns major Russian official public holidays for time series modeling."""
        holidays_ru = [
            f"{year}-01-01", f"{year}-01-02", f"{year}-01-03", f"{year}-01-04", f"{year}-01-05",
            f"{year}-01-06", f"{year}-01-07", f"{year}-01-08", # New Year & Christmas
            f"{year}-02-23", # Defender of the Fatherland Day
            f"{year}-03-08", # International Women's Day
            f"{year}-05-01", # Spring and Labor Day
            f"{year}-05-09", # Victory Day
            f"{year}-06-12", # Russia Day
            f"{year}-11-04"  # Unity Day
        ]
        return holidays_ru

if __name__ == "__main__":
    provider = MacroDataProvider()
    rates = provider.get_cbr_rates()
    print("CBR API Test Result:")
    print("USD/RUB:", rates["usd_rub"])
    print("CNY/RUB:", rates["cny_rub"])
    print("Key Rate:", rates["key_rate_cbr"])
    print("Holidays 2026 count:", len(provider.get_russian_holidays(2026)))
