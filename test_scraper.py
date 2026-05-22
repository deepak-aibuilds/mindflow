import asyncio
from app.services.scraper_service import scrape_url

async def main():
    result = await scrape_url("https://yetigrowth.com")
    print(result[0].page_content)

asyncio.run(main())