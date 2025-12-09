from PyPDF2 import PdfReader
pdf="RWA - FastOracle.pdf"
r=PdfReader(pdf)
print("pages", len(r.pages))
with open("RWA-FastOracle.txt","w",encoding="utf-8") as f:
    f.write(f"pages: {len(r.pages)}\n")
    for i,p in enumerate(r.pages):
        t=p.extract_text()
        f.write(f"\n--- Page {i+1} ---\n")
        f.write((t if t else "[页面无提取文本或为图片]")+"\n")
print("done")
