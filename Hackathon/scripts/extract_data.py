import fitz
file_path = '../data/data2.pdf'
text1 = []
doc = fitz.open(file_path)
for page in doc:
    text1.append(page.get_text())
with open('../data/extracted_text.txt', 'w') as f:
    f.write("\n".join(text1))