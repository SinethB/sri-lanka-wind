"""Build climatology.json: average daily rainfall (mm) per district for each calendar month.

Run once on your own machine (needs internet), then commit climatology.json next to index.html:
    python build_climatology.py
Data: Open-Meteo historical archive (ERA5 reanalysis), 2011-2025.
"""
import json, time, urllib.request, urllib.error

DISTRICTS = {
    "Ampara": (7.30, 81.67), "Anuradhapura": (8.34, 80.41), "Badulla": (6.99, 81.06),
    "Batticaloa": (7.71, 81.70), "Colombo": (6.93, 79.86), "Galle": (6.05, 80.22),
    "Gampaha": (7.09, 80.00), "Hambantota": (6.12, 81.12), "Jaffna": (9.66, 80.01),
    "Kalutara": (6.58, 79.96), "Kandy": (7.29, 80.63), "Kegalle": (7.25, 80.35),
    "Kilinochchi": (9.39, 80.40), "Kurunegala": (7.49, 80.37), "Mannar": (8.98, 79.91),
    "Matale": (7.47, 80.62), "Matara": (5.95, 80.55), "Monaragala": (6.87, 81.35),
    "Mullaitivu": (9.27, 80.81), "Nuwara Eliya": (6.97, 80.77), "Polonnaruwa": (7.94, 81.00),
    "Puttalam": (8.03, 79.84), "Ratnapura": (6.68, 80.40), "Trincomalee": (8.57, 81.23),
    "Vavuniya": (8.75, 80.50),
}
START, END = "2011-01-01", "2025-12-31"

def fetch(lat, lon):
    url = ("https://archive-api.open-meteo.com/v1/archive?latitude=%s&longitude=%s"
           "&start_date=%s&end_date=%s&daily=precipitation_sum&timezone=Asia%%2FColombo"
           % (lat, lon, START, END))
    for attempt in range(6):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)["daily"]
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            print("  rate limited, waiting 65 s...")
            time.sleep(65)
    raise RuntimeError("gave up after repeated rate limits")

out = {}
for name, (lat, lon) in DISTRICTS.items():
    print(name)
    d = fetch(lat, lon)
    tot, cnt = [0.0] * 12, [0] * 12
    for day, mm in zip(d["time"], d["precipitation_sum"]):
        if mm is None:
            continue
        m = int(day[5:7]) - 1
        tot[m] += mm
        cnt[m] += 1
    out[name] = [round(t / c, 2) if c else 0 for t, c in zip(tot, cnt)]
    time.sleep(3)

with open("climatology.json", "w") as f:
    json.dump({"period": "2011-2025", "source": "Open-Meteo archive (ERA5)", "districts": out}, f)
print("wrote climatology.json")
