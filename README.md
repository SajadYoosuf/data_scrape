# 🕵️ Kerala Election Data Scraper

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase)](https://supabase.com/)
[![PDF-Extraction](https://img.shields.io/badge/PDF_Extraction-FF0000?style=for-the-badge&logo=adobe)](https://github.com/jsvine/pdfplumber)

The data acquisition layer for the Kerala Election Comparison System. This module handles the ingestion of 70 years of raw electoral data from official PDF reports and web archives.

---

## 🛠️ Data Sources
*   **Official PDF Reports:** Historical Legislative Assembly (Assembly) and Lok Sabha (LS) state reports from the Election Commission.
*   **ODK Raw Data:** Digital archives in JSON format for recent election cycles.
*   **Web Scrapes:** Supplemental data for candidate demographics and gender verification.

## 🚀 Capabilities

*   **PDF Ingestion:** Extracting structured candidate results from complex, multi-page official PDF reports.
*   **Data Normalization:** Handling name variations and constituency delimitation changes across decades.
*   **Gender Identification:** Advanced script-based learning for candidate gender classification (EN/ML).
*   **Database Synchronization:** Automated upload scripts for pushing verified data to the Supabase PostgreSQL cluster.
*   **Data Verification:** Robust scripts to check vote totals, seat counts, and alliance mappings.

## 📂 Directory Structure

| File | Description |
| :--- | :--- |
| `scrape_elections.py` | Main logic for processing historical records |
| `scraper.py` | Core utility for PDF and web data extraction |
| `upload_to_supabase.py` | ETL pipeline for database synchronization |
| `verify_data.py` | Post-upload data integrity check suite |
| `learn_gender.py` | Machine-learning assisted gender classification |
| `supabase_schema.sql` | The source of truth for the database structure |

## 🏗️ Usage

### 1. Setup
```bash
pip install pdfplumber pandas psycopg2-binary python-dotenv
```


```

### 3. Pipeline Execution
```bash
# Initialize schema (if first time)
# psql -f supabase_schema.sql

# Run extraction
python scrape_elections.py

# Upload and verify
python upload_to_supabase.py
python verify_data.py
```

---

## 🔒 Data Privacy & Integrity
*   This module is used purely for historical research and academic data visualization.
*   All data is sourced from public domain records.
*   Verification scripts ensure that the total votes polled per constituency match the individual candidate aggregates within a 0.1% margin of error.

Developed for the Kerala Election Archive Initiative.