"""
Kerala Election Data Scraper
============================
Sources:
  1. keralaassembly.org  – winners + full results per constituency (1982–2021)
  2. ODK / Zenodo        – 2026 candidate registry CSV
  3. ODK GitHub          – Assembly constituency extent CSV (name ↔ AC number map)
  4. ODK API             – 2026 full results JSON
"""

import argparse
import json
import time
import logging
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

ELECTION_YEARS = [1982, 1987, 1991, 1996, 2001, 2006, 2011, 2016, 2021]

ODK_RESULTS_2026_URL = "https://api.opendatakerala.org/api/kla2026/results/all.json"
ODK_CONSTITUENCY_CSV = "https://raw.githubusercontent.com/opendatakerala/KLA2026/main/data/Assembly_Constituency_Extent.csv"

BASE_KA = "http://www.keralaassembly.org/election/2021"
REQUEST_DELAY = 1.0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# HTTP helpers
# ──────────────────────────────────────────────
def fetch(url: str, retries: int = 3, is_json: bool = False):
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30, verify=False)
            r.raise_for_status()
            return r.json() if is_json else r.text
        except Exception as exc:
            log.warning("Attempt %d/%d failed for %s: %s", attempt, retries, url, exc)
            time.sleep(REQUEST_DELAY * attempt)
    return None

def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", s).strip()

def save_json(data, path: Path):
    count = len(data) if isinstance(data, list) else 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info("✓ Saved → %-55s  (%d records)", str(path), count)


# ──────────────────────────────────────────────
# Winners Scraper Logic
# ──────────────────────────────────────────────
def parse_text_results(html_content: str, year: int) -> list[dict]:
    """Parse winners from messy historical HTML/text blocks."""
    # Convert line-breaks to real newlines
    c = re.sub(r"<(br|p|tr|div|pre|nobr)[^>]*>", "\n", html_content, flags=re.I)
    c = re.sub(r"<[^>]+>", "", c)
    c = c.replace("&nbsp;", " ")
    
    rows = []
    lines = c.split("\n")
    for line in lines:
        line = line.strip()
        if not line or len(line) < 15: continue
        
        # Pattern 1: With AC No. (e.g., "1  MANJESWARAM  ...")
        m_with_no = re.match(r"^(\d+)\s+(.*)", line)
        if m_with_no:
            ac_no = int(m_with_no.group(1))
            rest = m_with_no.group(2).strip()
        else:
            # Pattern 2: No AC No. (e.g., "MANJESWARAM  ...")
            ac_no = None
            rest = line
            
        parts = re.split(r"\s{2,}", rest)
        if len(parts) < 2: continue
        
        # If parts[0] is clearly a column header, skip
        if parts[0].lower() in ["constituency", "no.", "winner", "candidate"]: continue
        
        constituency = parts[0].strip()
        name_part = parts[1].strip()
        party = parts[2].strip() if len(parts) > 2 else ""
        margin = parts[3].strip() if len(parts) > 3 else ""
        
        # Handle salutations
        if name_part.upper() in ["MR", "MS", "DR"] and len(parts) > 2:
            name = name_part + " " + parts[2].strip()
            party = parts[3].strip() if len(parts) > 3 else ""
            margin = parts[4].strip() if len(parts) > 4 else ""
        else:
            name = name_part

        rows.append({
            "year": year,
            "ac_number": ac_no,
            "Constituency": constituency,
            "Winner": name,
            "Party": party,
            "Margin": margin
        })
    return rows


def scrape_winners(year: int) -> list[dict]:
    if year == 2026:
        raw = fetch(ODK_RESULTS_2026_URL, is_json=True)
        if not raw: return []
        results = raw.get("data", [])
        winners = []
        for res in results:
            meta = res.get("constituency", {})
            cands = res.get("candidates", [])
            if cands:
                def v(c): return int(str(c.get("votes", 0)).replace(",", ""))
                sorted_cands = sorted(cands, key=v, reverse=True)
                w, ru = sorted_cands[0], (sorted_cands[1] if len(sorted_cands) > 1 else {})
                winners.append({
                    "year": 2026,
                    "ac_number": int(meta.get("constituency_Number", 0)),
                    "Constituency": meta.get("constituency_Name"),
                    "Winner": w.get("name"), "Party": w.get("party"),
                    "Front": w.get("alliance"), "Margin": v(w) - v(ru)
                })
        return winners

    if year <= 2001:
        yy = str(year)[2:]
        if year == 2001: yy = "01"
        url = f"http://www.keralaassembly.org/winner{yy}.html"
    else:
        url = f"{BASE_KA}/winners_margins.php?year={year}"

    log.info("[%d] Fetching from %s …", year, url)
    html = fetch(url)
    if not html: return []

    if year <= 2001:
        log.info("[%d] Using text parser …", year)
        return parse_text_results(html, year)

    # Table Parsing for 2006+
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        trs = table.find_all("tr")
        for i, tr in enumerate(trs[:10]):
            text = tr.get_text().lower()
            if "constituency" in text and ("winner" in text or "candidate" in text):
                headers = [clean(c.get_text()) for c in tr.find_all(["th", "td"])]
                rows = []
                for data_tr in trs[i+1:]:
                    cells = data_tr.find_all("td")
                    if len(cells) < 2: continue
                    row = {"year": year}
                    for j, h in enumerate(headers):
                        val = clean(cells[j].get_text()) if j < len(cells) else ""
                        nh = h
                        if "constituency" in h.lower(): nh = "Constituency"
                        elif "winner" in h.lower() or "candidate" in h.lower(): nh = "Winner"
                        elif "party" in h.lower(): nh = "Party"
                        elif "margin" in h.lower(): nh = "Margin"
                        elif "front" in h.lower(): nh = "Front"
                        row[nh] = val
                    link = data_tr.find("a")
                    if link and "href" in link.attrs:
                        m = re.search(r"no=(\d+)", link["href"])
                        if m: row["ac_number"] = int(m.group(1))
                    if row.get("Constituency"): rows.append(row)
                log.info("[%d] Scraped %d winners", year, len(rows))
                return rows
    return []


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true")
    args = p.parse_args()

    years = ELECTION_YEARS + [2026] if args.all else [2026, 2021, 2016]
    
    # Mapping
    try:
        csv_data = fetch(ODK_CONSTITUENCY_CSV)
        if csv_data:
            from io import StringIO
            df = pd.read_csv(StringIO(csv_data))
            mapping = df[["Constituency", "Sl. No. of Constituency"]].drop_duplicates().rename(columns={"Constituency": "name_en", "Sl. No. of Constituency": "ac_number"}).to_dict(orient="records")
            save_json(mapping, OUTPUT_DIR / "constituencies.json")
    except: pass
    
    for y in years:
        res = scrape_winners(y)
        if res: save_json(res, OUTPUT_DIR / f"winners_{y}.json")
        time.sleep(REQUEST_DELAY)
