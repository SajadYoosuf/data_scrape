import pdfplumber

def inspect_pdf(file_path, num_pages=10):
    with pdfplumber.open(file_path) as pdf:
        print(f"Total Pages: {len(pdf.pages)}")
        for i in range(min(num_pages, len(pdf.pages))):
            page = pdf.pages[i]
            text = page.extract_text()
            print(f"--- Page {i+1} ---")
            print(text[:1000]) # Print first 1000 characters
            print("\n")

if __name__ == "__main__":
    # inspect_pdf("KL_1987_ST_REP.pdf")
    # Check pages in the middle/end for detailed results
    with pdfplumber.open("KL_1987_ST_REP.pdf") as pdf:
        total = len(pdf.pages)
        print(f"Total Pages: {total}")
        # Look at pages 20, 50, 100, 150, etc.
        for i in [20, 50, 100, 150, 200, 250]:
            if i < total:
                page = pdf.pages[i]
                text = page.extract_text()
                print(f"--- Page {i+1} ---")
                print(text[:1000] if text else "No text found")
                print("\n")
