from langchain_community.document_loaders import WebBaseLoader

def scraper(url: str):
    if not url.startswith("http"):
        url = f"https://{url}"
    loader = WebBaseLoader(url)
    docs = loader.load()
    scraped  = "\n".join([doc.page_content for doc in docs])
    title = docs[0].metadata.get('title', None)
    return {'content': scraped, "title": title}


