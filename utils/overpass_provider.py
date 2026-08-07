import requests
import json
import math

class OverpassPOIProvider:
    """Fetches real Points of Interest (POIs) from OpenStreetMap via Overpass API."""

    def __init__(self):
        self.endpoint = "https://overpass-api.de/api/interpreter"

    def get_pois_around(self, lat: float, lon: float, radius: int = 500) -> dict:
        """Query OSM Overpass API for POIs (public transport, subways, shops, cafes, offices) around coordinates."""
        query = f"""
        [out:json][timeout:10];
        (
          node["railway"="station"](around:{radius},{lat},{lon});
          node["station"="subway"](around:{radius},{lat},{lon});
          node["highway"="bus_stop"](around:{radius},{lat},{lon});
          node["amenity"~"cafe|restaurant|bank|atm|pharmacy"](around:{radius},{lat},{lon});
          node["shop"~"supermarket|convenience|clothes"](around:{radius},{lat},{lon});
          node["office"](around:{radius},{lat},{lon});
        );
        out body;
        """
        try:
            resp = requests.post(self.endpoint, data={"data": query}, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                elements = data.get("elements", [])
                
                counts = {
                    "subways": 0,
                    "bus_stops": 0,
                    "competitors_shops": 0,
                    "cafes_restaurants": 0,
                    "offices": 0,
                    "total_pois": len(elements)
                }
                
                poi_details = []
                for el in elements:
                    tags = el.get("tags", {})
                    name = tags.get("name", "Без названия")
                    poi_type = "other"
                    
                    if tags.get("station") == "subway" or tags.get("railway") == "station":
                        counts["subways"] += 1
                        poi_type = "subway"
                    elif tags.get("highway") == "bus_stop":
                        counts["bus_stops"] += 1
                        poi_type = "bus_stop"
                    elif "shop" in tags:
                        counts["competitors_shops"] += 1
                        poi_type = "shop"
                    elif tags.get("amenity") in ["cafe", "restaurant"]:
                        counts["cafes_restaurants"] += 1
                        poi_type = "cafe"
                    elif "office" in tags:
                        counts["offices"] += 1
                        poi_type = "office"
                        
                    poi_details.append({
                        "id": el.get("id"),
                        "lat": el.get("lat"),
                        "lon": el.get("lon"),
                        "name": name,
                        "type": poi_type,
                        "tags": tags
                    })
                    
                # Calculate estimated foot traffic score based on POI density
                traffic_score = (counts["subways"] * 1500) + (counts["bus_stops"] * 400) + \
                                (counts["competitors_shops"] * 250) + (counts["cafes_restaurants"] * 200) + \
                                (counts["offices"] * 300)
                traffic_score = max(500, min(15000, traffic_score))

                return {
                    "status": "success",
                    "lat": lat,
                    "lon": lon,
                    "radius": radius,
                    "counts": counts,
                    "traffic_score": traffic_score,
                    "pois": poi_details[:30]
                }
        except Exception as e:
            print(f"[Overpass] Error querying OSM: {e}")

        # Fallback if OSM query fails or times out
        return {
            "status": "fallback",
            "lat": lat,
            "lon": lon,
            "radius": radius,
            "counts": {
                "subways": 1,
                "bus_stops": 4,
                "competitors_shops": 8,
                "cafes_restaurants": 5,
                "offices": 3,
                "total_pois": 21
            },
            "traffic_score": 5200,
            "pois": []
        }

if __name__ == "__main__":
    provider = OverpassPOIProvider()
    # Test with Moscow Kremlin / Tverskaya coordinates
    res = provider.get_pois_around(55.7558, 37.6173, radius=500)
    print("Overpass OSM Test Result for Moscow Center:")
    print("Status:", res["status"])
    print("POI Counts:", res["counts"])
    print("Estimated Traffic Score:", res["traffic_score"])
