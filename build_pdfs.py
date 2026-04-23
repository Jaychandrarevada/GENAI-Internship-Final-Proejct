from md2pdf.core import md2pdf
import os

files_to_convert = [
    ("HLD.md", "HLD.pdf"),
    ("LLD.md", "LLD.pdf"),
    ("Technical_Documentation.md", "Technical_Documentation.pdf")
]

for md_file, pdf_file in files_to_convert:
    print(f"Converting {md_file} to {pdf_file}...")
    try:
        md2pdf(pdf_file,
            md_content=open(md_file, "r", encoding="utf-8").read(),
            md_file_path=None,
            css_file_path=None,
            base_url=None)
        print(f"Successfully created {pdf_file}")
    except Exception as e:
        print(f"Error converting {md_file}: {e}")
