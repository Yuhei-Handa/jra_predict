import pypdfium2 as pdf
from glob import glob

def main():
    # 同ディレクトリにあるPDFファイルを取得
    pdf_files = glob('*.pdf')
    print(pdf_files)
    for pdf_file in pdf_files:
        # PDFファイルを開く
        doc = pdf.PdfDocument(pdf_file)
        # ページ数を取得
        for page in doc:
            textpage = page.get_textpage()
            text = textpage.get_text_range()
            print(text)
            print('---------------------------')

if __name__ == '__main__':
    main()