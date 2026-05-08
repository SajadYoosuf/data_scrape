"""
Scrape Kerala Assembly Election results (2011, 2016, 2021) from keralaassembly.org
Each constituency page has an HTML table with: Name, Party, Votes, Percentage
"""
import requests
import json
import re
import time
import os
from html.parser import HTMLParser

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# URL patterns per year
URLS = {
    2011: 'http://www.keralaassembly.org/election/assembly_poll.php?year=2011&no={no}',
    2016: 'http://www.keralaassembly.org/election/2016/assembly_poll.php?year=2016&no={no}',
    2021: 'http://www.keralaassembly.org/election/2021/assembly_poll.php?year=2021&no={no}',
}

class ResultsParser(HTMLParser):
    """Parse the HTML table from keralaassembly.org constituency pages."""
    
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.in_link = False
        self.current_row = []
        self.current_cell = ''
        self.rows = []
        self.table_count = 0
        self.constituency_name = ''
        self.electorate = 0
        self.votes_polled = 0
        self.nota_votes = 0
        self.in_header_area = True  # Before the candidate table
        self.header_text = ''
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'table':
            self.table_count += 1
            if self.table_count == 2:  # Second table is the results table
                self.in_table = True
        if self.in_table:
            if tag == 'tr':
                self.in_row = True
                self.current_row = []
            elif tag == 'td':
                self.in_cell = True
                self.current_cell = ''
            elif tag == 'a':
                self.in_link = True
        if tag == 'font' and attrs_dict.get('color') == '#009900':
            self.in_header_area = True
            
    def handle_endtag(self, tag):
        if tag == 'table' and self.in_table:
            self.in_table = False
        if self.in_table:
            if tag == 'tr' and self.in_row:
                self.in_row = False
                if self.current_row:
                    self.rows.append(self.current_row)
            elif tag == 'td' and self.in_cell:
                self.in_cell = False
                self.current_row.append(self.current_cell.strip())
            elif tag == 'a':
                self.in_link = False
                
    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data


def parse_constituency_html(html, const_no):
    """Parse the HTML of a single constituency page."""
    parser = ResultsParser()
    parser.feed(html)
    
    # Extract constituency name from the header
    # Pattern: "1. Manjeshwar"
    name_match = re.search(r'(\d+)\.\s+([A-Za-z\s\(\)]+)\s*<br>', html)
    const_name = name_match.group(2).strip() if name_match else f"Constituency {const_no}"
    
    # Extract electorate info
    electorate_match = re.search(r'Electorate:\s*([\d,]+)', html)
    electorate = int(electorate_match.group(1).replace(',', '')) if electorate_match else 0
    
    votes_polled_match = re.search(r'Votes Polled:\s*([\d,]+)', html)
    votes_polled = int(votes_polled_match.group(1).replace(',', '')) if votes_polled_match else 0
    
    nota_match = re.search(r'NOTA:\s*([\d,]+)', html)
    nota_votes = int(nota_match.group(1).replace(',', '')) if nota_match else 0
    
    # Parse candidate rows (skip header row)
    candidates = []
    for i, row in enumerate(parser.rows):
        if len(row) >= 4:
            name = row[0].strip()
            party = row[1].strip()
            
            # Skip header row
            if name == 'Name of the Candidate' or party == 'Party':
                continue
            # Skip total row
            if 'Total' in name or 'total' in name:
                continue
                
            try:
                votes = int(row[2].replace(',', '').strip())
            except (ValueError, IndexError):
                continue
            try:
                percentage = float(row[3].strip())
            except (ValueError, IndexError):
                percentage = 0.0
                
            candidates.append({
                "rank": len(candidates) + 1,
                "name": name,
                "sex": "N/A",
                "party": party,
                "votes": votes,
                "percentage": percentage
            })
    
    # Sort by votes descending and re-assign ranks
    candidates.sort(key=lambda x: x['votes'], reverse=True)
    for i, c in enumerate(candidates):
        c['rank'] = i + 1
    
    seats = 1
    winners = [c for c in candidates if c['rank'] <= seats]
    runners_up = [c for c in candidates if c['rank'] == seats + 1]
    
    return {
        "constituency_id": str(const_no),
        "constituency_name": const_name,
        "seats": seats,
        "electorate": electorate,
        "votes_polled": votes_polled,
        "nota_votes": nota_votes,
        "winners": winners,
        "runners_up": runners_up,
        "all_candidates": candidates
    }


def scrape_year(year, num_constituencies=140):
    """Scrape all constituencies for a given year."""
    url_template = URLS[year]
    results = []
    
    print(f"\n{'='*60}")
    print(f"Scraping Kerala Assembly Election {year}")
    print(f"{'='*60}")
    
    for no in range(1, num_constituencies + 1):
        url = url_template.format(no=no)
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                data = parse_constituency_html(r.text, no)
                results.append(data)
                num_cands = len(data['all_candidates'])
                winner = data['winners'][0]['name'] if data['winners'] else 'N/A'
                print(f"  [{no:3d}/140] {data['constituency_name']:<25s} | {num_cands} candidates | Winner: {winner}")
            else:
                print(f"  [{no:3d}/140] HTTP {r.status_code} - Skipped")
        except Exception as e:
            print(f"  [{no:3d}/140] Error: {e}")
        
        time.sleep(0.3)  # Be polite to the server
    
    return results


def main():
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    for year in [2011, 2016]:
        results = scrape_year(year)
        
        output_file = os.path.join(output_dir, f"winners_{year}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        print(f"\n[OK] Saved {len(results)} constituencies to {output_file}")
        print(f"  Total candidates: {sum(len(r['all_candidates']) for r in results)}")


if __name__ == "__main__":
    main()
