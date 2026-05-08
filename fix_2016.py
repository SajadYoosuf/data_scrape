import json
import requests
from scrape_web import parse_constituency_html

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
r = requests.get('http://www.keralaassembly.org/election/2016/assembly_poll.php?year=2016&no=67', headers=headers)
data = parse_constituency_html(r.text, 67)
num_cands = len(data['all_candidates'])
print(f"Parsed: {data['constituency_name']} - {num_cands} candidates")

# Load existing data and insert
results = json.load(open('output/winners_2016.json', encoding='utf-8'))
results.append(data)
results.sort(key=lambda x: int(x['constituency_id']))

with open('output/winners_2016.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"Updated winners_2016.json: now {len(results)} constituencies")
