#!/usr/bin/env python3
"""Spectrum Hub crawler: polite, robots.txt-aware collector for public ASD resource pages.
Usage: python crawler.py --sources sources.json --out resources.json --inject index.html"""
import argparse, datetime as dt, json, re, time
from collections import deque
from urllib import robotparser
from urllib.parse import urldefrag, urljoin, urlparse
import requests
from bs4 import BeautifulSoup

UA = "SpectrumHubBot/0.1 (research project; contact: spectrumhub.project@gmail.com)"
CATS = {  # needs, aligned with the themes in Larnyo et al. (2024)
    "signs": ["sign", "symptom", "early", "milestone", "characteristic"],
    "diagnosis": ["diagnos", "screening", "evaluation", "assessment"],
    "care": ["therap", "treatment", "intervention", "speech", "occupational", "medication"],
    "caregivers": ["caregiver", "parent", "famil", "respite", "sibling"],
    "mental": ["anxiety", "depress", "mental health", "sleep", "gastro", "co-occurring"],
    "tech": ["assistive", "technology", "wearable", "communication device", "aac", " app "],
    "advocacy": ["advocacy", "self-advocate", "stigma", "acceptance", "rights", "neurodiversity"],
    "daily": ["routine", "school", "employment", "transition", "sensory", "daily living", "covid"],
    "local": ["find a provider", "directory", "near you", "locator", "state resources", "clinic"],
}
AUD = {
    "adults": ["autistic adult", "adults with autism", "self-advocate", "adulthood"],
    "caregivers": ["parent", "caregiver", "famil"],
    "professionals": ["clinician", "provider", "professional", "educator", "researcher"],
}
_robots = {}


def norm(u):
    u, _ = urldefrag(u)
    p = urlparse(u)
    q = "&".join(x for x in p.query.split("&") if x and not x.startswith(("utm_", "fbclid")))
    return p._replace(query=q, path=p.path.rstrip("/") or "/").geturl()


def allowed(url):
    p = urlparse(url)
    base = f"{p.scheme}://{p.netloc}"
    if base not in _robots:
        rp = robotparser.RobotFileParser(base + "/robots.txt")
        try:
            rp.read()
        except Exception:
            rp = None  # cannot read robots.txt: be conservative and skip the site
        _robots[base] = rp
    rp = _robots[base]
    return bool(rp and rp.can_fetch(UA, url))


def extract(html):
    soup = BeautifulSoup(html, "html.parser")
    meta = lambda **k: (soup.find("meta", attrs=k) or {}).get("content", "")
    title = meta(property="og:title") or (soup.title.string if soup.title and soup.title.string else "")
    desc = meta(name="description") or meta(property="og:description")
    for t in soup(["script", "style", "nav", "footer", "header", "form"]):
        t.decompose()
    text = " ".join(x.get_text(" ", strip=True) for x in soup.select("h1,h2,h3,p,li"))[:4000]
    if not desc:
        desc = next((p.get_text(" ", strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) >= 80), "")
    return " ".join(title.split()), " ".join(desc.split())[:240], text, soup


def tags(table, text, title, floor, n):
    low, tl = text.lower(), title.lower()
    sc = {k: sum(low.count(w) for w in ws) + 3 * sum(tl.count(w) for w in ws) for k, ws in table.items()}
    return [k for k in sorted(sc, key=sc.get, reverse=True)[:n] if sc[k] >= floor]


def crawl(src, max_pages, delay):
    seen, out, q = set(), [], deque(src["seeds"])
    while q and len(out) < max_pages:
        url = norm(q.popleft())
        if url in seen or not any(url.startswith(a) for a in src["allow"]) or not allowed(url):
            continue
        seen.add(url)
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=15)
            time.sleep(delay)
        except requests.RequestException as e:
            print("  skip", url, e)
            continue
        if r.status_code != 200 or "html" not in r.headers.get("content-type", "") or len(r.content) > 2_000_000:
            continue
        title, desc, text, soup = extract(r.text)
        for a in soup.find_all("a", href=True):
            q.append(urljoin(url, a["href"]))
        if text.lower().count("autis") < 2 or not title:
            continue  # keep the crawl on topic
        out.append({
            "title": title, "url": url, "source": src["name"], "tier": src["tier"],
            "audience": sorted(set(src.get("audience", [])) | set(tags(AUD, text, title, 2, 3))) or ["adults", "caregivers"],
            "cats": tags(CATS, text, title, 3, 3) or src.get("cats", []),
            "summary": desc or text[:200], "checked": dt.date.today().isoformat(),
        })
        print("  +", title[:70])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default="sources.json")
    ap.add_argument("--out", default="resources.json")
    ap.add_argument("--inject", help="HTML file whose <script id=data> block is refreshed")
    ap.add_argument("--delay", type=float, default=1.5, help="seconds between requests")
    ap.add_argument("--max-pages", type=int, help="override per-source page limit")
    a = ap.parse_args()
    items, seen_t = [], set()
    for src in json.load(open(a.sources)):
        print(src["name"])
        for it in crawl(src, a.max_pages or src.get("max_pages", 20), a.delay):
            key = (it["source"], it["title"].lower())
            if key not in seen_t:
                seen_t.add(key)
                items.append(it)
    json.dump(items, open(a.out, "w"), indent=1, ensure_ascii=False)
    print(f"{len(items)} resources -> {a.out}")
    if a.inject:
        s = open(a.inject, encoding="utf-8").read()
        blob = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
        s = re.sub(r'(<script id="data" type="application/json">).*?(</script>)', lambda m: m.group(1) + blob + m.group(2), s, flags=re.S)
        open(a.inject, "w", encoding="utf-8").write(s)
        print("refreshed", a.inject)


if __name__ == "__main__":
    main()
