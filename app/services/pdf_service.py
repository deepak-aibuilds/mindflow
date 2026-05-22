from langchain_community.document_loaders import PyPDFLoader
import tempfile, os
def extract_pdf(file_bytes: bytes) -> dict:
    with tempfile.NamedTemporaryFile(delete=False,suffix='.pdf') as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        loader = PyPDFLoader(tmp_path)
        pages = []
        for doc in loader.lazy_load():
            pages.append(doc.page_content)
        text = "\n".join(pages)
       
        return {
            'content': text
        }
    finally:
         os.unlink(tmp_path)
  