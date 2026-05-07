import http.server
import json
import urllib.request
import urllib.parse
import ssl
import time
import random
import re
from datetime import datetime, timedelta

CITY_NAMES = {
    "beijing": "北京",
    "shanghai": "上海",
    "shenzhen": "深圳",
    "guangzhou": "广州",
    "wuhan": "武汉",
    "tokyo": "东京",
    "london": "伦敦",
    "taipei": "台北",
    "nyc": "纽约",
    "singapore": "新加坡",
    "wellington": "惠灵顿",
    "chicago": "芝加哥",
}

CITY_ORDER = [
    "beijing", "shanghai", "shenzhen", "guangzhou", "wuhan",
    "wellington",
    "tokyo",
    "taipei",
    "singapore",
    "london",
    "nyc",
    "chicago",
]

ctx = ssl._create_unverified_context()
price_history = {}
is_real_data = False


def fetch_json(url, timeout=15):
    data = b""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        while True:
            try:
                chunk = resp.read(8192)
                if not chunk:
                    break
                data += chunk
            except:
                break
        return json.loads(data)
    except:
        return None


def build_slug(city, dt):
    month = dt.strftime("%B").lower()
    day = str(dt.day)
    year = str(dt.year)
    return f"highest-temperature-in-{city}-on-{month}-{day}-{year}"


def fetch_city_event(city, dt):
    slug = build_slug(city, dt)
    url = f"https://gamma-api.polymarket.com/events/slug/{slug}"
    ev = fetch_json(url, timeout=12)
    if ev and isinstance(ev, dict) and not ev.get("closed"):
        return ev, slug
    return None, slug


def discover_and_fetch():
    global is_real_data, price_history
    results = []

    today = datetime.utcnow()
    dates = [today + timedelta(days=i) for i in range(10)]

    city_events = {}
    for cid in CITY_NAMES:
        for dt in dates:
            ev, slug = fetch_city_event(cid, dt)
            if ev:
                city_events[cid] = (ev, slug)
                break

    if city_events:
        is_real_data = True
        city_markets = {}

        for cid, (ev, ev_slug) in city_events.items():
            title = ev.get("title", "")
            date_match = re.search(
                r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:\s*,?\s*\d{4})?",
                title, re.IGNORECASE
            )
            date_str = date_match.group(0) if date_match else ""

            ev_markets = ev.get("markets", [])
            if not isinstance(ev_markets, list):
                continue

            for mk in ev_markets:
                if mk.get("closed"):
                    continue

                q = mk.get("question", "") or ""
                slug = mk.get("slug", "") or ""

                outcomes = mk.get("outcomes", "[]")
                prices_raw = mk.get("outcomePrices", "[]")

                if isinstance(outcomes, str):
                    try:
                        outcomes = json.loads(outcomes)
                    except:
                        outcomes = []
                if isinstance(prices_raw, str):
                    try:
                        prices = json.loads(prices_raw)
                    except:
                        prices = []
                else:
                    prices = prices_raw

                if not outcomes or not prices or len(outcomes) < 2 or len(prices) < 2:
                    continue

                yes_idx = None
                for i, o in enumerate(outcomes):
                    if o == "Yes":
                        yes_idx = i
                        break
                if yes_idx is None:
                    continue

                yes_price = round(float(prices[yes_idx]) * 100, 1)

                temp_match = re.search(r"(\d+)(?:\s*-\s*(\d+))?\s*[°º]?\s*([cCfF])", q)
                temp = int(temp_match.group(1)) if temp_match else None
                is_fahrenheit = temp_match.group(3) and temp_match.group(3).upper() == "F" if temp_match else False

                is_below = "or below" in q.lower()

                market_id = f"{cid}-{temp}-{date_str}"

                entry = {
                    "id": market_id,
                    "city": cid,
                    "cityName": CITY_NAMES.get(cid, cid),
                    "temperature": temp,
                    "isFahrenheit": is_fahrenheit,
                    "isBelow": is_below,
                    "date": date_str,
                    "question": q[:120],
                    "yesPrice": yes_price,
                    "slug": slug,
                    "url": f"https://polymarket.com/event/{slug}",
                    "volume": mk.get("volume", 0) or 0,
                }

                if cid not in city_markets:
                    city_markets[cid] = {}
                key = f"{temp}-{is_below}"
                if key not in city_markets[cid]:
                    city_markets[cid][key] = entry

        for entries in city_markets.values():
            results.extend(entries.values())

    if len(results) < 3:
        if not results:
            is_real_data = False
        for cid, cname in CITY_NAMES.items():
            if any(r["city"] == cid for r in results):
                continue
            hist = price_history.get(cid, [])
            if hist:
                last = hist[-1]["price"]
                change = (random.random() - 0.48) * 2.5
                price_val = max(1, min(98, round(last + change, 1)))
            else:
                price_val = round(random.uniform(3, 25), 1)
            results.append({
                "id": cid,
                "city": cid,
                "cityName": cname,
                "temperature": None,
                "isBelow": False,
                "date": "",
                "question": "",
                "yesPrice": price_val,
                "slug": "",
                "volume": 0,
            })

    results.sort(key=lambda r: (
        CITY_ORDER.index(r["city"]) if r["city"] in CITY_ORDER else 999,
        r.get("temperature") or 0,
    ))

    now_ts = int(time.time() * 1000)
    for r in results:
        cid = r["id"]
        if cid not in price_history:
            price_history[cid] = []
        hist = price_history[cid]
        last_price = hist[-1]["price"] if hist else None
        if last_price != r["yesPrice"]:
            hist.append({"price": r["yesPrice"], "time": now_ts})
            if len(hist) > 200:
                price_history[cid] = hist[-200:]

    current_ids = {r["id"] for r in results}
    for key in list(price_history.keys()):
        if key not in current_ids:
            del price_history[key]

    return results


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())
            return

        if parsed.path == "/api/markets":
            data = discover_and_fetch()
            result = json.dumps({
                "markets": data,
                "source": "live" if is_real_data else "simulated",
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(result)
            return

        if parsed.path == "/api/history":
            hist_data = {k: v[-100:] for k, v in price_history.items()}
            result = json.dumps({"history": hist_data}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(result)
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    port = 9000
    server = http.server.HTTPServer(("0.0.0.0", port), Handler)
    print(f"Server running at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
