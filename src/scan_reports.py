"""Find state-level TB tables in supplied annual reports using embedded PDF text."""
from pathlib import Path
import re
from pypdf import PdfReader

REPORTS = Path(__file__).resolve().parents[1] / "data" / "raw"
OUT = Path(__file__).resolve().parents[1] / "results" / "report_table_candidates.txt"
PATTERN = re.compile(r"state.?wise|state/ut|state and union|treatment outcome|notified.*state|state.*notified", re.I)

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as out:
        for pdf in sorted(REPORTS.glob("*.pdf"), key=lambda item: item.stat().st_size):
            reader = PdfReader(str(pdf))
            print(f"Scanning {pdf.name}: {len(reader.pages)} pages", flush=True)
            for page_no, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                if PATTERN.search(text):
                    snippet = " ".join(text.split())[:1200]
                    out.write(f"\n\n### {pdf.name} | PDF page {page_no}\n{snippet}\n")
    print(f"Wrote candidates to {OUT}")

if __name__ == "__main__":
    main()
