import pdfplumber
import json
import re
import os

def parse_detailed_results(pdf_path):
    all_data = []
    with pdfplumber.open(pdf_path) as pdf:
        start_page = 0
        # Find where DETAILED RESULTS starts
        for i in range(len(pdf.pages)):
            text = pdf.pages[i].extract_text()
            if text and "DETAILED RESULTS" in text:
                start_page = i
                break
        
        if start_page == 0:
            # Fallback: look for "Constituency" followed by a number and "1."
            for i in range(len(pdf.pages)):
                text = pdf.pages[i].extract_text()
                if text and "Constituency" in text and "1." in text:
                    start_page = i
                    break

        print(f"Parsing {pdf_path} starting from page {start_page + 1}")
        
        current_constituency = None
        candidates = []
        
        # Regex for constituency line: 
        # "Constituency 1 MANJESWAR"
        # "Constituency : 131. ARIYANAD"
        # "Constituency 105 MATTANUR NUMBER OF SEATS 1"
        const_regex = re.compile(r"Constituency\s*:?\s*(\d+)\.?\s+(.*?)(?:\s+NUMBER OF SEATS[:\s]+(\d+)|$)")
        # Regex for 2006/2011/2016 style: "1. MANJESWAR", "4. HOSDRUG (SC)", "24. CALICUT- I", "30. SULTAN'S BATTERY"
        const_regex_new = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s\(\)\-'\.IVX]+)$")
        
        # Regex for candidate line: "1. CHERKALAM ABDULLAH M MUL 33853 41.85%"
        # Sometimes there's a space or dot after the number
        cand_regex = re.compile(r"^(\d+)\.?\s+(.*?)\s+([MF])\s+(.*?)\s+(\d+)\s+([\d\.]+)%")
        # Regex for 2006 style: "1.V J THANKAPPAN M 71 GEN CPI(M) 50122 229 50351"
        # No.CANDIDATE NAME SEX AGE CATEGORY PARTY GENERAL POSTAL TOTAL
        cand_regex_2006 = re.compile(r"^(\d+)\.?\s*(.*?)\s+([MF])\s+\d+\s+\w+\s+(.*?)\s+(\d+)\s+(\d+)\s+(\d+)")
        # Fallback regex for candidate line without SEX
        cand_regex_no_sex = re.compile(r"^(\d+)\.?\s+(.*?)\s+(.*?)\s+(\d+)\s+([\d\.]+)%")

        for i in range(start_page, len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                
                # Check for constituency
                match_const = const_regex.search(line)
                match_const_new = const_regex_new.search(line)
                
                if (match_const or match_const_new) and "DATA - SUMMARY" not in line and "VALID VOTES POLLED" not in line:
                    # Save previous constituency data
                    if current_constituency and candidates:
                        seats = current_constituency['seats']
                        winners = [c for c in candidates if c['rank'] <= seats]
                        runners_up = [c for c in candidates if c['rank'] == seats + 1]
                        all_data.append({
                            "constituency_id": current_constituency['id'],
                            "constituency_name": current_constituency['name'],
                            "seats": seats,
                            "winners": winners,
                            "runners_up": runners_up,
                            "all_candidates": candidates
                        })
                    
                    if match_const:
                        cid = match_const.group(1)
                        cname = match_const.group(2).strip().rstrip('.')
                        seats = int(match_const.group(3)) if match_const.group(3) else 1
                    else:
                        cid = match_const_new.group(1)
                        cname = match_const_new.group(2).strip().rstrip('.')
                        seats = 1
                        
                    current_constituency = {"id": cid, "name": cname, "seats": seats}
                    candidates = []
                    continue
                
                # Check for candidate
                match = cand_regex.search(line)
                if match:
                    rank = int(match.group(1))
                    name = match.group(2).strip()
                    sex = match.group(3)
                    party = match.group(4).strip()
                    votes = int(match.group(5))
                    percentage = float(match.group(6))
                    candidates.append({
                        "rank": rank, "name": name, "sex": sex, "party": party, "votes": votes, "percentage": percentage
                    })
                elif cand_regex_2006.search(line):
                    match = cand_regex_2006.search(line)
                    rank = int(match.group(1))
                    name = match.group(2).strip()
                    sex = match.group(3)
                    party = match.group(4).strip()
                    votes = int(match.group(7)) # TOTAL is the 7th group
                    candidates.append({
                        "rank": rank, "name": name, "sex": sex, "party": party, "votes": votes, "percentage": 0.0 # Will calculate later
                    })
                else:
                    match = cand_regex_no_sex.search(line)
                    if match:
                        rank = int(match.group(1))
                        name = match.group(2).strip()
                        party = match.group(3).strip()
                        votes = int(match.group(4))
                        percentage = float(match.group(5))
                        candidates.append({
                            "rank": rank, "name": name, "sex": "N/A", "party": party, "votes": votes, "percentage": percentage
                        })
        
        # Calculate percentages for 2006-style data (where votes are extracted but percentage is 0)
        for cand in candidates:
            if cand['percentage'] == 0.0 and len(candidates) > 0:
                total_votes = sum(c['votes'] for c in candidates)
                if total_votes > 0:
                    cand['percentage'] = round((cand['votes'] / total_votes) * 100, 2)
        
        # Save last constituency
        if current_constituency and candidates:
            seats = current_constituency['seats']
            winners = [c for c in candidates if c['rank'] <= seats]
            runners_up = [c for c in candidates if c['rank'] == seats + 1]
            all_data.append({
                "constituency_id": current_constituency['id'],
                "constituency_name": current_constituency['name'],
                "seats": seats,
                "winners": winners,
                "runners_up": runners_up,
                "all_candidates": candidates
            })
            
    return all_data

if __name__ == "__main__":
    files = [
        "KL_2006_ST_REP.pdf",
        "KL_2001_ST_REP.pdf",
        "KL_1996_ST_REP.pdf",
        "KL_1991_ST_REP.pdf",
        "KL_1987_ST_REP.pdf",
        "KL_1982_ST_REP.pdf",
        "KL_1980_ST_REP.pdf",
        "KL_1977_ST_REP.pdf",
        "KL_1970_ST_REP.pdf",
        "KL_1967_ST_REP.pdf",
        "KL_1965_ST_REP.pdf",
        "KL_1960_ST_REP.pdf",
        "KL_1957_ST_REP.pdf"
    ]
    
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for f in files:
        if os.path.exists(f):
            print(f"Processing {f}...")
            try:
                data = parse_detailed_results(f)
                year = f.split('_')[1]
                output_file = os.path.join(output_dir, f"winners_{year}.json") # Overwrite existing winners_XXXX.json
                with open(output_file, 'w') as out:
                    json.dump(data, out, indent=4)
                print(f"Saved {len(data)} constituencies to {output_file}")
            except Exception as e:
                print(f"Error processing {f}: {e}")
