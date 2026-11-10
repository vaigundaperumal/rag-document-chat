import pymupdf

def extract_text(file_path):
    
    document = pymupdf.open(file_path)
    
    pages = []
    
    for pagenumber,page in enumerate(document.pages()):
        
        text = page.get_text()
        
        pages.append({
            "page_number": pagenumber + 1,
            "content": text
        })
    
    document.close()
    
    return pages