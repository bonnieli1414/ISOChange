import os
import sys
import argparse
import pypdf
from reportlab.pdfgen import canvas

def stamp_pdf(pdf_path, stamp_path, output_path=None):
    """
    Stamps the electronic signature image onto Page 2 and Page 3 of the target PDF
    at the exact coordinates corresponding to the scaled Excel sheet layouts.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at '{pdf_path}'")
        return False
    if not os.path.exists(stamp_path):
        print(f"Error: Stamp image not found at '{stamp_path}'")
        return False
        
    if output_path is None:
        output_path = pdf_path
        
    temp_stamp_pdf = "temp_stamp.pdf"
    
    # 1. Create temporary PDF with signature stamps using A4 page size (595.32, 841.92 pt)
    c = canvas.Canvas(temp_stamp_pdf, pagesize=(595.32, 841.92))
    
    # Page 1: Empty (Page 1 already has its stamp)
    c.showPage()
    
    # Page 2: Stamp [加工] at x=426.7, y=145.96, w=127.97, h=107.86
    c.drawImage(stamp_path, x=426.7, y=145.96, width=127.97, height=107.86, mask='auto')
    c.showPage()
    
    # Page 3: Stamp [包裝] at x=440.02, y=146.22, w=145.78, h=122.89
    c.drawImage(stamp_path, x=440.02, y=146.22, width=145.78, height=122.89, mask='auto')
    c.showPage()
    
    c.save()
    
    # 2. Merge pages
    try:
        reader = pypdf.PdfReader(pdf_path)
        stamp_reader = pypdf.PdfReader(temp_stamp_pdf)
        writer = pypdf.PdfWriter()
        
        for idx in range(len(reader.pages)):
            orig_page = reader.pages[idx]
            stamp_page = stamp_reader.pages[idx]
            
            if idx > 0:  # Page 2 (idx=1) and Page 3 (idx=2)
                orig_page.merge_page(stamp_page)
                
            writer.add_page(orig_page)
            
        with open(output_path, "wb") as f:
            writer.write(f)
            
        print(f"Successfully stamped PDF: {output_path}")
        return True
    except Exception as e:
        print(f"Error during PDF processing: {e}")
        return False
    finally:
        if os.path.exists(temp_stamp_pdf):
            os.remove(temp_stamp_pdf)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stamp electronic signature onto ISO PDF pages.")
    parser.add_argument("--pdf", default=r"06. ISO\文管\temp\TW-EN-26-0183-01-001\new\x369cc17cx1a03e9bd4cexx36c3.pdf", help="Path to the PDF file.")
    parser.add_argument("--stamp", default=r"06. ISO\文管\temp\TW-EN-26-0183-01-001\電子印章20260828.png", help="Path to the stamp image.")
    parser.add_argument("--output", help="Path to save the stamped PDF (overwrites input if not specified).")
    
    args = parser.parse_args()
    
    # Resolve relative paths based on current repository root
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_fullpath = os.path.join(base_dir, args.pdf) if not os.path.isabs(args.pdf) else args.pdf
    stamp_fullpath = os.path.join(base_dir, args.stamp) if not os.path.isabs(args.stamp) else args.stamp
    output_fullpath = args.output
    if output_fullpath and not os.path.isabs(output_fullpath):
        output_fullpath = os.path.join(base_dir, args.output)
        
    stamp_pdf(pdf_fullpath, stamp_fullpath, output_fullpath)
