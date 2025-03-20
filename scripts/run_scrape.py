import os
import datetime
from firecrawl import FirecrawlApp
from pathlib import Path
from dotenv import load_dotenv
from typing import List

class FirecrawlMarkdownScraper:

    MAX_PAGES = 25

    def __init__(
            self,
            api_key: str
    ):
        """
        Initialize the scraper with your Firecrawl API key and configuration.
        
        Args:
            api_key: Your Firecrawl API key       
        """
        self.app = FirecrawlApp(api_key=api_key)
        self.output_dir = Path("../src/storage/scraped_docs")
        self.formats = ["markdown", "html"]

    def run(self, url: str):
        # create a markdown file in "../src/storage/scraped_docs"
            # file example: scrape_20250312_043242
        directory = self.output_dir
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()[:-6].replace(':', '.')
        filename = Path(f"anthropic-api-{url[34:]}.md")
        # filename = Path(f"{timestamp}.md")
        filepath = directory / filename

        # Create the directory if it doesn't exist
        directory.mkdir(parents=True, exist_ok=True)

        
        # begin scraping and save in `scrape_status`
        scrape_status = self.app.scrape_url(url)
            # INTRODUCE ERROR HANDLING! IF SCRAPE IS UNSUCCESSFUL, SHOULD WRITE AN ERROR MESSAGE TO THE CONSOLE AND THE FILE? OR DELETE THE FILE?


        # save markdown content from `scrape_status['markdown']`
        scraped_markdown = scrape_status['markdown']

        # write markdown content to the file that we created at the beginning of the method
            # SHOULD WE REFORMAT THE MARKDOWN TO LOOK BETTER?
        filepath.write_text(scraped_markdown, encoding="utf-8")

        if scraped_markdown:
            print(f"\n--- Scraped URL: {url} ---")

def main():
    # Load environment variables from .env
    from dotenv import load_dotenv
    load_dotenv()
    
    # Retrieve API key from .env
    API_KEY = os.getenv("FIRECRAWL_API_KEY")
    if not API_KEY:
        raise ValueError("API Key not found. Please set it in the .env file.")
    
    # Hardcoded list of URLs to scrape
    urls = [
        "https://docs.anthropic.com/en/api/claude-on-amazon-bedrock",
        "https://docs.anthropic.com/en/api/claude-on-vertex-ai",
        "https://docs.anthropic.com/en/api/client-sdks",
        "https://docs.anthropic.com/en/api/complete",
        "https://docs.anthropic.com/en/api/errors",
        "https://docs.anthropic.com/en/api/getting-help",
        "https://docs.anthropic.com/en/api/getting-started",
        "https://docs.anthropic.com/en/api/ip-addresses",
        "https://docs.anthropic.com/en/api/messages",
        "https://docs.anthropic.com/en/api/messages-count-tokens",
        "https://docs.anthropic.com/en/api/messages-examples",
        "https://docs.anthropic.com/en/api/messages-streaming",
        "https://docs.anthropic.com/en/api/migrating-from-text-completions-to-messages",
        "https://docs.anthropic.com/en/api/models",
        "https://docs.anthropic.com/en/api/models-list",
        "https://docs.anthropic.com/en/api/openai-sdk",
        "https://docs.anthropic.com/en/api/prompt-validation",
        "https://docs.anthropic.com/en/api/rate-limits",
        "https://docs.anthropic.com/en/api/streaming",
        "https://docs.anthropic.com/en/api/supported-regions",
        "https://docs.anthropic.com/en/api/versioning",
    ]

    # Initialize a scraper
    scraper = FirecrawlMarkdownScraper(api_key=API_KEY)

    # Loop over each URL and run the scraper
    for url in urls:
        print(f"\n--- Scraping URL: {url} ---")
        scraper.run(url)

if __name__ == '__main__':
    main()