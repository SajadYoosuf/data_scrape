import json
import os
from collections import defaultdict

output_dir = "output"
years = [1957, 1960, 1965, 1967, 1970, 1977, 1980, 1982, 1987, 1991, 1996, 2001, 2006, 2011, 2016, 2021]

def analyze_gender_data():
    # Build a dictionary of known names -> gender from older elections
    known_gender = {}
    na_candidates = []
    
    for year in years:
        filepath = os.path.join(output_dir, f"winners_{year}.json")
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for const in data:
            for cand in const.get("all_candidates", []):
                name = cand["name"].strip().upper()
                sex = cand.get("sex", "N/A").upper()
                
                if sex in ["M", "F"]:
                    # Keep track of known genders
                    if name not in known_gender:
                        known_gender[name] = sex
                elif sex == "N/A" or sex == "":
                    na_candidates.append((year, const["constituency_name"], name))
                    
    print(f"Total known names from history: {len(known_gender)}")
    print(f"Total candidates with N/A gender: {len(na_candidates)}")
    
    # How many of the N/A candidates can we resolve using history?
    resolved_from_history = 0
    for y, c, name in na_candidates:
        if name in known_gender:
            resolved_from_history += 1
            
    print(f"Can resolve {resolved_from_history} from historical names.")
    
    # Show a sample of unresolved names to look for patterns
    print("\nSample of unresolved names:")
    unresolved = [name for y, c, name in na_candidates if name not in known_gender]
    for name in unresolved[:20]:
        print(f" - {name}")

if __name__ == "__main__":
    analyze_gender_data()
