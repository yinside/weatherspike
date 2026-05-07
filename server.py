import http.server
import json
import urllib.request
import urllib.parse
import ssl
import time
import random
import re
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

CITY_NAMES = {
    "beijing": "北京",
    "shanghai": "上海",
    "shenzhen": "深圳",
    "guangzhou": "广州",
    "wuhan": "武汉",
    "chengdu": "成都",
    "chongqing": "重庆",
    "qingdao": "青岛",
    "hong-kong": "香港",
    "taipei": "台北",
    "tokyo": "东京",
    "osaka": "大阪",
    "seoul": "首尔",
    "busan": "釜山",
    "singapore": "新加坡",
    "bangkok": "曼谷",
    "manila": "马尼拉",
    "jakarta": "雅加达",
    "ho-chi-minh": "胡志明",
    "hanoi": "河内",
    "kuala-lumpur": "吉隆坡",
    "delhi": "德里",
    "mumbai": "孟买",
    "lucknow": "勒克瑙",
    "bengaluru": "班加罗尔",
    "kolkata": "加尔各答",
    "chennai": "金奈",
    "hyderabad": "海得拉巴",
    "dhaka": "达卡",
    "karachi": "卡拉奇",
    "lahore": "拉合尔",
    "islamabad": "伊斯兰堡",
    "colombo": "科伦坡",
    "kathmandu": "加德满都",
    "yangon": "仰光",
    "sydney": "悉尼",
    "melbourne": "墨尔本",
    "brisbane": "布里斯班",
    "perth": "珀斯",
    "adelaide": "阿德莱德",
    "auckland": "奥克兰",
    "wellington": "惠灵顿",
    "christchurch": "基督城",
    "tel-aviv": "特拉维夫",
    "jerusalem": "耶路撒冷",
    "ankara": "安卡拉",
    "istanbul": "伊斯坦布尔",
    "dubai": "迪拜",
    "abu-dhabi": "阿布扎比",
    "doha": "多哈",
    "riyadh": "利雅得",
    "kuwait-city": "科威特城",
    "muscat": "马斯喀特",
    "tehran": "德黑兰",
    "baghdad": "巴格达",
    "moscow": "莫斯科",
    "saint-petersburg": "圣彼得堡",
    "london": "伦敦",
    "paris": "巴黎",
    "berlin": "柏林",
    "madrid": "马德里",
    "rome": "罗马",
    "milan": "米兰",
    "munich": "慕尼黑",
    "amsterdam": "阿姆斯特丹",
    "brussels": "布鲁塞尔",
    "vienna": "维也纳",
    "zurich": "苏黎世",
    "stockholm": "斯德哥尔摩",
    "oslo": "奥斯陆",
    "copenhagen": "哥本哈根",
    "helsinki": "赫尔辛基",
    "warsaw": "华沙",
    "prague": "布拉格",
    "budapest": "布达佩斯",
    "athens": "雅典",
    "lisbon": "里斯本",
    "dublin": "都柏林",
    "bucharest": "布加勒斯特",
    "sofia": "索非亚",
    "kiev": "基辅",
    "barcelona": "巴塞罗那",
    "frankfurt": "法兰克福",
    "hamburg": "汉堡",
    "geneva": "日内瓦",
    "naples": "那不勒斯",
    "turin": "都灵",
    "lyon": "里昂",
    "marseille": "马赛",
    "manchester": "曼彻斯特",
    "birmingham": "伯明翰",
    "edinburgh": "爱丁堡",
    "glasgow": "格拉斯哥",
    "nyc": "纽约",
    "new-york": "纽约",
    "los-angeles": "洛杉矶",
    "chicago": "芝加哥",
    "houston": "休斯顿",
    "miami": "迈阿密",
    "seattle": "西雅图",
    "boston": "波士顿",
    "denver": "丹佛",
    "phoenix": "凤凰城",
    "atlanta": "亚特兰大",
    "san-francisco": "旧金山",
    "washington-dc": "华盛顿",
    "dallas": "达拉斯",
    "philadelphia": "费城",
    "detroit": "底特律",
    "austin": "奥斯汀",
    "san-diego": "圣地亚哥",
    "portland": "波特兰",
    "las-vegas": "拉斯维加斯",
    "orlando": "奥兰多",
    "tampa": "坦帕",
    "minneapolis": "明尼阿波利斯",
    "charlotte": "夏洛特",
    "nashville": "纳什维尔",
    "toronto": "多伦多",
    "vancouver": "温哥华",
    "montreal": "蒙特利尔",
    "calgary": "卡尔加里",
    "ottawa": "渥太华",
    "edmonton": "埃德蒙顿",
    "mexico-city": "墨西哥城",
    "guadalajara": "瓜达拉哈拉",
    "monterrey": "蒙特雷",
    "sao-paulo": "圣保罗",
    "rio-de-janeiro": "里约热内卢",
    "buenos-aires": "布宜诺斯",
    "santiago": "圣地亚哥",
    "bogota": "波哥大",
    "lima": "利马",
    "caracas": "加拉加斯",
    "quito": "基多",
    "montevideo": "蒙得维的亚",
    "asuncion": "亚松森",
    "la-paz": "拉巴斯",
    "brasilia": "巴西利亚",
    "cairo": "开罗",
    "alexandria": "亚历山大",
    "cape-town": "开普敦",
    "johannesburg": "约翰内斯堡",
    "nairobi": "内罗毕",
    "lagos": "拉各斯",
    "addis-ababa": "亚的斯亚贝巴",
    "casablanca": "卡萨布兰卡",
    "tunis": "突尼斯",
    "algiers": "阿尔及尔",
    "accra": "阿克拉",
    "dakar": "达喀尔",
}

CITY_ORDER = [
    "beijing", "shanghai", "shenzhen", "guangzhou", "wuhan",
    "chengdu", "chongqing", "qingdao", "hong-kong", "taipei",
    "tokyo", "osaka", "seoul", "busan", "singapore",
    "bangkok", "manila", "jakarta", "ho-chi-minh", "hanoi", "kuala-lumpur",
    "delhi", "mumbai", "lucknow", "bengaluru", "kolkata", "chennai",
    "hyderabad", "dhaka", "karachi", "lahore", "islamabad",
    "colombo", "kathmandu", "yangon",
    "sydney", "melbourne", "brisbane", "perth", "adelaide",
    "auckland", "wellington", "christchurch",
    "tel-aviv", "jerusalem", "ankara", "istanbul",
    "dubai", "abu-dhabi", "doha", "riyadh", "kuwait-city", "muscat",
    "tehran", "baghdad",
    "moscow", "saint-petersburg",
    "london", "paris", "berlin", "madrid", "rome", "milan", "munich",
    "amsterdam", "brussels", "vienna", "zurich",
    "stockholm", "oslo", "copenhagen", "helsinki",
    "warsaw", "prague", "budapest", "athens", "lisbon", "dublin",
    "bucharest", "sofia", "kiev",
    "barcelona", "frankfurt", "hamburg", "geneva",
    "naples", "turin", "lyon", "marseille",
    "manchester", "birmingham", "edinburgh", "glasgow",
    "nyc", "los-angeles", "chicago", "houston", "miami",
    "seattle", "boston", "denver", "phoenix", "atlanta",
    "san-francisco", "washington-dc", "dallas", "philadelphia", "detroit",
    "austin", "san-diego", "portland", "las-vegas", "orlando", "tampa",
    "minneapolis", "charlotte", "nashville",
    "toronto", "vancouver", "montreal", "calgary", "ottawa", "edmonton",
    "mexico-city", "guadalajara", "monterrey",
    "sao-paulo", "rio-de-janeiro", "buenos-aires",
    "santiago", "bogota", "lima", "caracas", "quito",
    "montevideo", "asuncion", "la-paz", "brasilia",
    "cairo", "alexandria", "cape-town", "johannesburg",
    "nairobi", "lagos", "addis-ababa",
    "casablanca", "tunis", "algiers", "accra", "dakar",
]

ctx = ssl._create_unverified_context()
price_history = {}
is_real_data = False
discovered_cities = set()


def city_name(cid):
    return CITY_NAMES.get(cid) or cid


def extract_city_from_slug(slug):
    if not slug or not isinstance(slug, str):
        return None
    m = re.match(
        r"^highest-temperature-in-(.+?)-on-(january|february|march|april|may|june|july|august|september|october|november|december)-\d{1,2}-\d{4}$",
        slug, re.IGNORECASE
    )
    return m.group(1) if m else None


def fetch_json(url, timeout=5):
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
    ev = fetch_json(url, timeout=5)
    if ev and isinstance(ev, dict) and not ev.get("closed"):
        return ev, slug
    return None, slug


def process_markets(ev, ev_slug):
    mkts = []
    title = ev.get("title", "")
    date_match = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:\s*,?\s*\d{4})?",
        title, re.IGNORECASE
    )
    date_str = date_match.group(0) if date_match else ""
    for mk in (ev.get("markets") or []):
        if mk.get("closed"):
            continue
        q = mk.get("question", "") or ""
        outcomes = mk.get("outcomes", "[]")
        prices = mk.get("outcomePrices", "[]")
        if isinstance(outcomes, str):
            try: outcomes = json.loads(outcomes)
            except: outcomes = []
        if isinstance(prices, str):
            try: prices = json.loads(prices)
            except: prices = []
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
        mkts.append({
            "id": mk.get("slug", ""),
            "temperature": temp,
            "isFahrenheit": is_fahrenheit,
            "isBelow": is_below,
            "date": date_str,
            "question": q[:120],
            "yesPrice": yes_price,
            "slug": mk.get("slug", ""),
            "url": f"https://polymarket.com/zh/event/{ev_slug}",
            "volume": mk.get("volume", 0) or 0,
        })
    return mkts


def discover_and_fetch():
    global is_real_data, price_history, discovered_cities
    results = []

    # Strategy 1: try tag endpoints
    events = []
    for tag in ("weather", "temperature"):
        try:
            resp = fetch_json(f"https://gamma-api.polymarket.com/events?tag_slug={tag}&active=true&closed=false&limit=300", timeout=6)
            if isinstance(resp, list) and len(resp) > 0:
                events = resp
                break
        except:
            continue

    # Strategy 2: per-city fallback (limited time budget)
    if not events:
        today = datetime.utcnow()
        cities_to_try = list(CITY_NAMES.keys())[:30]
        deadline = time.time() + 25
        with ThreadPoolExecutor(max_workers=8) as executor:
            tasks = []
            for cid in cities_to_try:
                for offset in range(3):
                    dt = today + timedelta(days=offset)
                    tasks.append((cid, dt))
            futures = {executor.submit(fetch_city_event, cid, dt): (cid, dt) for cid, dt in tasks}
            for future in as_completed(futures, timeout=30):
                if time.time() > deadline:
                    break
                cid, dt = futures[future]
                try:
                    ev, slug = future.result()
                    if ev:
                        mkts = process_markets(ev, slug)
                        cname = city_name(cid)
                        for m in mkts:
                            m["city"] = cid
                            m["cityName"] = cname
                        results.extend(mkts)
                        discovered_cities.add(cid)
                except:
                    pass

        results.sort(key=lambda r: (
            CITY_ORDER.index(r["city"]) if r["city"] in CITY_ORDER else 999,
            r.get("temperature") or 0,
        ))
        _update_price_history(results)
        return results

    # strategy 1: process events
    for ev in events:
        if ev.get("closed"):
            continue
        ev_slug = ev.get("slug", "") or ""
        cid = extract_city_from_slug(ev_slug)
        if not cid:
            continue
        discovered_cities.add(cid)
        mkts = process_markets(ev, ev_slug)
        cname = city_name(cid)
        for m in mkts:
            m["city"] = cid
            m["cityName"] = cname
        results.extend(mkts)

    results.sort(key=lambda r: (
        CITY_ORDER.index(r["city"]) if r["city"] in CITY_ORDER else 999,
        r.get("temperature") or 0,
    ))
    if results:
        is_real_data = True

    # fallback to simulated if too few
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
                "isFahrenheit": False,
                "isBelow": False,
                "date": "",
                "question": "",
                "yesPrice": price_val,
                "slug": "",
                "url": "",
                "volume": 0,
            })

    _update_price_history(results)
    return results


def _update_price_history(results):
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
                "cities": sorted(discovered_cities),
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(result)
            return

        if parsed.path == "/api/cities":
            all_cities = []
            all_ids = set(discovered_cities) | set(CITY_NAMES.keys())
            for cid in sorted(all_ids):
                all_cities.append({"id": cid, "name": city_name(cid)})
            result = json.dumps({"cities": all_cities}).encode()
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

        if parsed.path.startswith("/api/positions"):
            qs = urllib.parse.parse_qs(parsed.query)
            user = qs.get("user", [""])[0]
            if not user:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"missing user param"}')
                return
            url = f"https://data-api.polymarket.com/positions?user={user}&limit=50&sortBy=TOKENS&sortDirection=DESC"
            data = fetch_json(url, timeout=10)
            if data is None:
                data = []
            for p in data:
                es = p.get("eventSlug", "") or ""
                if es.startswith("highest-temperature-in-"):
                    p["isTemperature"] = True
            result = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(result)
            return

        if parsed.path.startswith("/api/activity"):
            qs = urllib.parse.parse_qs(parsed.query)
            users_param = qs.get("users", [""])[0]
            limit = int(qs.get("limit", ["50"])[0])
            if not users_param:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"missing users param"}')
                return
            addresses = [a.strip() for a in users_param.split(",") if a.strip()]
            all_activities = []
            for addr in addresses:
                url = f"https://data-api.polymarket.com/activity?user={addr}&limit={limit}&sortBy=TIMESTAMP&sortDirection=DESC&type=TRADE"
                batch = fetch_json(url, timeout=10)
                if isinstance(batch, list):
                    for a in batch:
                        es = a.get("eventSlug", "") or ""
                        if es.startswith("highest-temperature-in-"):
                            a["isTemperature"] = True
                        a["_wallet"] = addr
                    all_activities.extend(batch)
            all_activities.sort(key=lambda a: a.get("timestamp", 0) or 0, reverse=True)
            result = json.dumps(all_activities[:100]).encode()
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
