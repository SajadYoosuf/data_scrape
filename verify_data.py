"""Final comprehensive verification of all election data files."""
import json
import os

output_dir = "output"
years = [1957, 1960, 1965, 1967, 1970, 1977, 1980, 1982, 1987, 1991, 1996, 2001, 2006, 2011, 2016, 2021]

# Expected constituency counts by year
expected = {
    1957: 113, 1960: 114, 1965: 133, 1967: 133, 1970: 133,
    1977: 140, 1980: 140, 1982: 140, 1987: 140, 1991: 140,
    1996: 140, 2001: 140, 2006: 140, 2011: 140, 2016: 140, 2021: 140
}

print("=" * 80)
print(f"{'Year':<6} {'Constituencies':<16} {'Expected':<10} {'Status':<10} {'Candidates':<12} {'Sample Winner'}")
print("=" * 80)

for year in years:
    filepath = os.path.join(output_dir, f"winners_{year}.json")
    if not os.path.exists(filepath):
        print(f"{year:<6} {'FILE MISSING':<16}")
        continue
    
    data = json.load(open(filepath, encoding='utf-8'))
    count = len(data)
    exp = expected.get(year, '?')
    
    # Check if data is properly structured (list of dicts with 'all_candidates')
    if isinstance(data, list) and len(data) > 0 and 'all_candidates' in data[0]:
        total_cands = sum(len(r['all_candidates']) for r in data)
        winner = data[0].get('winners', [{}])
        winner_name = winner[0]['name'] if winner else 'N/A'
        status = 'OK' if count == exp else f'MISMATCH'
        print(f"{year:<6} {count:<16} {exp:<10} {status:<10} {total_cands:<12} {winner_name}")
    else:
        print(f"{year:<6} {count:<16} {exp:<10} {'BAD FORMAT':<10}")

print("=" * 80)
print("\nDetailed check for each year...")
for year in years:
    filepath = os.path.join(output_dir, f"winners_{year}.json")
    if not os.path.exists(filepath):
        continue
    data = json.load(open(filepath, encoding='utf-8'))
    if not isinstance(data, list) or len(data) == 0 or 'all_candidates' not in data[0]:
        print(f"\n{year}: BAD FORMAT - not a list of constituency objects")
        continue
    
    issues = []
    for r in data:
        cid = r.get('constituency_id', '?')
        cname = r.get('constituency_name', '?')
        cands = r.get('all_candidates', [])
        winners = r.get('winners', [])
        
        if len(cands) == 0:
            issues.append(f"  Constituency {cid} ({cname}): No candidates")
        if len(winners) == 0:
            issues.append(f"  Constituency {cid} ({cname}): No winner identified")
        # Check votes are positive integers
        for c in cands:
            if not isinstance(c.get('votes'), int) or c['votes'] < 0:
                issues.append(f"  Constituency {cid} ({cname}): Bad votes for {c.get('name')}")
                break
    
    if issues:
        print(f"\n{year}: {len(issues)} issue(s):")
        for iss in issues[:5]:
            print(iss)
        if len(issues) > 5:
            print(f"  ... and {len(issues) - 5} more")
    else:
        print(f"{year}: All OK")
