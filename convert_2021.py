import json
import os

def convert_odk_to_standard(odk_path, output_path):
    with open(odk_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    results = []
    for entry in raw_data['data']:
        const_info = entry['constituency']
        candidates = entry['candidates']
        
        # Sort candidates by votes to assign rank
        candidates.sort(key=lambda x: x['votes'], reverse=True)
        
        processed_candidates = []
        for i, cand in enumerate(candidates):
            processed_candidates.append({
                "rank": i + 1,
                "name": cand['name'],
                "sex": "N/A", # ODK doesn't have SEX directly in this view
                "party": cand['party'] if cand['party'] else ("Independent" if cand['name'] != "NOTA" else "NOTA"),
                "votes": cand['votes'],
                "percentage": 0.0 # Will calculate
            })
            
        total_votes = sum(c['votes'] for c in processed_candidates)
        if total_votes > 0:
            for cand in processed_candidates:
                cand['percentage'] = round((cand['votes'] / total_votes) * 100, 2)
        
        seats = 1
        winners = [c for c in processed_candidates if c['rank'] <= seats]
        runners_up = [c for c in processed_candidates if c['rank'] == seats + 1]
        
        results.append({
            "constituency_id": const_info['constituency_Number'],
            "constituency_name": const_info['constituency_Name'],
            "seats": seats,
            "winners": winners,
            "runners_up": runners_up,
            "all_candidates": processed_candidates
        })
        
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    print(f"Saved {len(results)} constituencies for 2021.")

if __name__ == "__main__":
    convert_odk_to_standard('odk_raw.json', 'output/winners_2021.json')
