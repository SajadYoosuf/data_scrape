import json
import os
import re
from collections import defaultdict

output_dir = "output"
years = [1957, 1960, 1965, 1967, 1970, 1977, 1980, 1982, 1987, 1991, 1996, 2001, 2006, 2011, 2016, 2021]

def get_words(name):
    # Remove initials, dots, and non-alphabetic chars
    cleaned = re.sub(r'[^A-Z\s]', ' ', name.upper())
    # Keep words longer than 2 characters
    return [w for w in cleaned.split() if len(w) > 2]

def learn_and_apply_gender():
    male_words = defaultdict(int)
    female_words = defaultdict(int)
    known_exact = {}
    
    # 1. Learn from history
    for year in years:
        filepath = os.path.join(output_dir, f"winners_{year}.json")
        if not os.path.exists(filepath): continue
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for const in data:
            for cand in const.get("all_candidates", []):
                name = cand["name"].strip().upper()
                sex = cand.get("sex", "N/A").upper()
                
                if sex in ["M", "F"]:
                    known_exact[name] = sex
                    for w in get_words(name):
                        if sex == "M": male_words[w] += 1
                        else: female_words[w] += 1

    # 2. Build predictors
    # A word is a female predictor if it appears mostly in female names
    female_predictors = set()
    for w, f_count in female_words.items():
        m_count = male_words.get(w, 0)
        # If it appears significantly more in female names
        if f_count > 0 and (f_count / (f_count + m_count)) >= 0.8:
            female_predictors.add(w)
            
    # Add some common known female predictors manually just in case
    manual_female = {"KUMARI", "AMMA", "DEVI", "LAKSHMI", "SINDHU", "USHA", "GEETHA", 
                     "BINDHU", "LATHA", "REMA", "LEELA", "RADHA", "SARASWATHI", "SUJATHA", 
                     "BEENA", "MARY", "SHYLAJA", "SUDHA", "SHOBHA", "SREEMATHI", "AYSHA", 
                     "FATHIMA", "KHADEEJA", "MERCY", "ROSA", "ANIE", "JAMEELA", "SUHARA", 
                     "SAFIYA", "KAMALAM", "SMT", "SUNITHA", "HAFSA", "PRATHIBHA", "ASHA", 
                     "VEENA", "MINI", "SHEEBA", "REKHA", "CHANDRIKA", "VALSALA", "SARADA"}
    female_predictors.update(manual_female)

    # Remove generic words that might have slipped in
    generic_words = {"THE", "AND", "ADV", "DR", "PROF"}
    female_predictors.difference_update(generic_words)

    # 3. Apply to N/A datasets and rewrite files
    total_fixed = 0
    total_inferred_f = 0
    total_inferred_m = 0
    
    for year in years:
        filepath = os.path.join(output_dir, f"winners_{year}.json")
        if not os.path.exists(filepath): continue
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        modified = False
        for const in data:
            # Need to update both all_candidates, winners, runners_up
            for list_type in ["all_candidates", "winners", "runners_up"]:
                for cand in const.get(list_type, []):
                    sex = cand.get("sex", "N/A").upper()
                    if sex == "N/A" or sex == "":
                        name = cand["name"].strip().upper()
                        # Try exact match
                        if name in known_exact:
                            cand["sex"] = known_exact[name]
                        else:
                            # Try word predictors
                            words = get_words(name)
                            if any(w in female_predictors for w in words):
                                cand["sex"] = "F"
                                total_inferred_f += 1
                            else:
                                cand["sex"] = "M"  # Default to Male
                                total_inferred_m += 1
                        
                        modified = True
                        total_fixed += 1
                        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
    print(f"Total N/A records fixed: {total_fixed}")
    print(f"Inferred Female: {total_inferred_f}")
    print(f"Inferred Male: {total_inferred_m}")
    print(f"Sample learned female predictors: {list(female_predictors)[:20]}")

if __name__ == "__main__":
    learn_and_apply_gender()
