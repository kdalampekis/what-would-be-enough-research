"""Build paper/report.md into paper/build/report.html and report.pdf (headless Chrome), and report the page
on which "References" starts (the sprint limit is 8 pages before references and appendices).

    .venv/bin/python paper/build_report.py            # needs: pip install markdown ; Google Chrome
The HTML can be opened in Google Docs (File > Open > Upload) to move the content into the official template.
"""

from __future__ import annotations

import base64
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CSS = """
@page { size: Letter; margin: 1in; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10.5pt; line-height: 1.32; color: #111; }
h1 { font-size: 17pt; text-align: center; margin: 0 0 6pt; }
h2 { font-size: 12.5pt; margin: 13pt 0 4pt; }
h3 { font-size: 11pt; margin: 9pt 0 3pt; }
p { margin: 0 0 6pt; text-align: justify; }
ul, ol { margin: 0 0 6pt 18pt; padding: 0; }
li { margin-bottom: 2pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 8pt; font-size: 8.6pt; }
th, td { border: 0.5pt solid #999; padding: 2pt 4pt; text-align: left; vertical-align: top; }
/* Appendix tables with 7 or more columns: a table wider than the page makes Chrome shrink every page, so these get
   equal-width columns that cannot overflow, and smaller type. */
h2.pagebreak ~ table:has(th:nth-child(7)) { table-layout: fixed; font-size: 7pt; }
h2.pagebreak ~ table:has(th:nth-child(7)) :is(th, td) { padding: 1.5pt 2.5pt; overflow-wrap: break-word; }
th { background: #eee; }
img { max-width: 74%; display: block; margin: 4pt auto; }
code { font-size: 9pt; }
pre { font-size: 7.6pt; line-height: 1.2; white-space: pre-wrap; background: #f6f6f6; padding: 5pt; border: 0.5pt solid #ccc; }
pre code { font-size: 7.6pt; }
.footnote { font-size: 8.5pt; }
h2.pagebreak { page-break-before: always; }
h2, h3 { break-after: avoid; page-break-after: avoid; }
"""


def main() -> int:
    src = (HERE / "report.md").read_text()
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S)
    html = markdown.markdown(src, extensions=["tables", "footnotes", "sane_lists", "fenced_code"])
    html = html.replace("<h2>References</h2>", '<h2 class="pagebreak">References</h2>')
    page_src = f"<!doctype html><html><head><meta charset='utf-8'><title>report</title><style>{CSS}</style></head><body>{html}</body></html>"
    # figures are embedded, so the HTML file is self-contained
    html = re.sub(r'src="([^"]+\.png)"', lambda m: 'src="data:image/png;base64,'
                  + base64.b64encode((HERE / m.group(1)).read_bytes()).decode() + '"', html)
    out = HERE / "build"
    out.mkdir(exist_ok=True)
    page = f"<!doctype html><html><head><meta charset='utf-8'><title>report</title><style>{CSS}</style></head><body>{html}</body></html>"
    (out / "report.html").write_text(page)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out / 'report.pdf'}", (out / "report.html").as_uri()],
                   check=True, capture_output=True, timeout=120)
    # Word file for the Google Docs template: text and tables via the system converter. It cannot carry images, so
    # each figure becomes a visible placeholder naming the file to insert.
    n = iter(range(1, 99))
    doc_html = re.sub(r'<img alt="[^"]*" src="\.\./figures/([^"]+)"\s*/?>',
                      lambda m: f"<b>[INSERT FIGURE {next(n)} HERE: figures/{m.group(1)}]</b>", page_src)
    (out / "_for_docx.html").write_text(doc_html)
    pandoc = shutil.which("pandoc")
    if pandoc:  # preferred: figures embedded, styles taken from the official template (paper/template/)
        ref = HERE / "template" / "apart_template.docx"
        md = re.sub(r"<!--.*?-->", "", (HERE / "report.md").read_text(), flags=re.S)
        (out / "_for_docx.md").write_text(md)
        cmd = [pandoc, str(out / "_for_docx.md"), "-f", "markdown-implicit_figures", "-o", str(out / "report.docx"),
               "--resource-path", f"{HERE}:{HERE.parent}"] + (["--reference-doc", str(ref)] if ref.exists() else [])
        subprocess.run(cmd, check=True, capture_output=True, timeout=300)
    else:  # fallback: text and tables only; figures become visible placeholders
        subprocess.run(["textutil", "-convert", "docx", str(out / "_for_docx.html"), "-output", str(out / "report.docx")],
                       check=False, capture_output=True, timeout=120)
    words = len(re.findall(r"\w+", src.split("## References")[0]))
    pdf = (out / "report.pdf").read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page[^s]", pdf))
    # main text ends where References starts (forced onto a new page): count pages of a main-only build
    main_html = page.split('<h2 class="pagebreak">References</h2>')[0] + "</body></html>"
    (out / "_main.html").write_text(main_html)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out / '_main.pdf'}", (out / "_main.html").as_uri()],
                   check=True, capture_output=True, timeout=120)
    main_pages = len(re.findall(rb"/Type\s*/Page[^s]", (out / "_main.pdf").read_bytes()))
    print(f"main text: {words} words, {main_pages} pages (limit 8); whole PDF: {pages} pages; "
          f"placeholders left: {src.count('⟦')}")
    return 0 if main_pages <= 8 else 1


if __name__ == "__main__":
    sys.exit(main())
