import re
import json
import time
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

# Import the Firecrawl SDK
from firecrawl import FirecrawlApp

class FirecrawlMarkdownScraper:
    def __init__(
        self, 
        api_key: str,
        output_dir: str = "../src/storage/scraped_docs",
        formats: List[str] = ["markdown", "html"]
    ):
        """
        Initialize the scraper with your Firecrawl API key and configuration.
        
        Args:
            api_key: Your Firecrawl API key
            output_dir: Directory to save markdown files
            formats: Content formats to request from Firecrawl
        """
        self.app = FirecrawlApp(api_key=api_key)
        self.output_dir = Path(output_dir)
        self.formats = formats
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a session subdirectory with timestamp
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / f"scrape_{timestamp}"
        self.session_dir.mkdir(exist_ok=True)
        
    def clean_filename(self, url: str) -> str:
        """
        Generate a clean filename from a URL.
        
        Args:
            url: The page URL
            
        Returns:
            A sanitized filename
        """
        # Remove protocol and domain
        if '//' in url:
            url = url.split('//', 1)[1]
        if '/' in url:
            url = url.split('/', 1)[1]
            
        # Replace special characters
        filename = re.sub(r'[^a-zA-Z0-9]', '_', url)
        
        # Handle empty filenames or filenames that start with invalid chars
        if not filename or filename.startswith('_'):
            filename = f"page_{filename}"
            
        # Truncate if too long
        if len(filename) > 100:
            filename = filename[:100]
            
        return filename + ".md"
    
    def format_markdown(self, content: str) -> str:
        """
        Ensure markdown content is properly formatted.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Properly formatted markdown
        """
        # Add line breaks before headers
        for i in range(6, 0, -1):
            header_marker = '#' * i
            content = re.sub(r'([^\n])(' + header_marker + r'\s)', r'\1\n\n\2', content)
        
        # Add line breaks after paragraphs
        content = re.sub(r'(\.\s|\?\s|\!\s)([A-Z])', r'\1\n\n\2', content)
        
        # Format lists properly
        content = re.sub(r'([^\n])(\s*[-*]\s)', r'\1\n\n\2', content)
        
        # Ensure code blocks have proper spacing
        content = re.sub(r'([^\n])```', r'\1\n\n```', content)
        content = re.sub(r'```([^\n])', r'```\n\1', content)
        
        # Fix excessive newlines
        while '\n\n\n' in content:
            content = content.replace('\n\n\n', '\n\n')
            
        return content
    
    def scrape_url(self, url: str, max_pages: int = 100, wait_time: int = 10) -> Dict[str, Any]:
        """
        Scrape a URL using Firecrawl and wait for the result.
        
        Args:
            url: The URL to scrape
            max_pages: Maximum number of pages to scrape
            wait_time: Time to wait between status checks (seconds)
            
        Returns:
            The scrape result
        """
        print(f"Starting to scrape {url}...")
        
        # Configure scrape parameters
        params = {
            'formats': self.formats,
            # 'maxPages': max_pages
        }
        
        # Start the scrape
        scrape_id = self.app.scrape_url(url, params=params)
        
        # Save scrape ID and parameters
        config = {
            'url': url,
            'scrape_id': scrape_id,
            # 'max_pages': max_pages,
            'formats': self.formats,
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        
        with open(self.session_dir / "config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"Scrape started with ID: {scrape_id}")
        
        # Wait for the scrape to complete
        result = None
        while True:
            status = self.app.get_scrape_status(scrape_id)
            print(f"Status: {status.get('status')} - Pages scraped: {status.get('pageCount', 0)}")
            
            if status.get('status') == 'completed':
                result = self.app.get_scrape_result(scrape_id)
                break
            elif status.get('status') == 'failed':
                raise Exception(f"Scrape failed: {status.get('error', 'Unknown error')}")
                
            time.sleep(wait_time)
        
        return result
    
    def save_page_as_markdown(self, page: Dict[str, Any]) -> Path:
        """
        Save a scraped page as a markdown file.
        
        Args:
            page: The page data from Firecrawl
            
        Returns:
            Path to the saved file
        """
        url = page.get('url', '')
        title = page.get('title', 'Untitled Page')
        
        # Get markdown content if available, otherwise try to use the HTML content
        if 'markdown' in page:
            content = page['markdown']
        elif 'html' in page:
            print(f"Warning: No markdown available for {url}, using HTML content")
            content = f"HTML content was scraped but not converted to markdown.\n\n```html\n{page['html']}\n```"
        else:
            print(f"Warning: No content available for {url}")
            content = "No content was scraped for this page."
        
        # Format the content
        formatted_content = self.format_markdown(content)
        
        # Create a filename
        filename = self.clean_filename(url)
        filepath = self.session_dir / filename
        
        # Create the markdown document with metadata
        metadata = f"""# {title}

**URL:** {url}  
**Scraped:** {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}

---

"""
        
        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(metadata + formatted_content)
        
        print(f"Saved: {filepath}")
        return filepath
    
    def create_index(self, files: List[Path]) -> Path:
        """
        Create an index file with links to all scraped pages.
        
        Args:
            files: List of markdown file paths
            
        Returns:
            Path to the index file
        """
        index_path = self.session_dir / "index.md"
        
        # Read scrape configuration if available
        config = {}
        config_path = self.session_dir / "config.json"
        if config_path.exists():
            with open(config_path, "r") as f:
                config = json.load(f)
        
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(f"# Scrape Results\n\n")
            f.write(f"**Source URL:** {config.get('url', 'Unknown')}\n\n")
            f.write(f"**Scraped on:** {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Pages scraped:** {len(files)}\n\n")
            
            f.write("## Pages\n\n")
            
            for file_path in sorted(files):
                # Extract title from file
                title = file_path.stem
                try:
                    with open(file_path, "r", encoding="utf-8") as page_file:
                        first_line = page_file.readline().strip()
                        if first_line.startswith("# "):
                            title = first_line[2:]
                except Exception as e:
                    print(f"Warning: Could not read title from {file_path}: {e}")
                
                relative_path = file_path.name
                f.write(f"- [{title}]({relative_path})\n")
        
        print(f"Created index at: {index_path}")
        return index_path
        
    def run(self, url: str, max_pages: int = 100) -> List[Path]:
        """
        Run the complete scrape process.
        
        Args:
            url: URL to scrape
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of paths to saved markdown files
        """
        try:
            # Scrape the URL
            result = self.scrape_url(url, max_pages)
            
            # Save the raw result for reference
            with open(self.session_dir / "result.json", "w") as f:
                json.dump(result, f, indent=2)
            
            # Process pages and save as markdown
            saved_files = []
            pages = result.get('pages', [])
            
            print(f"Processing {len(pages)} pages from {url}...")
            for page in pages:
                try:
                    filepath = self.save_page_as_markdown(page)
                    saved_files.append(filepath)
                except Exception as e:
                    print(f"Error saving page {page.get('url', 'unknown')}: {e}")
            
            # Create an index file
            if saved_files:
                self.create_index(saved_files)
            
            print(f"\nScrape completed successfully for {url}!")
            print(f"Saved {len(saved_files)} pages to {self.session_dir}")
            
            return saved_files
            
        except Exception as e:
            print(f"Error during scrape of {url}: {e}")
            
            # Save error information
            with open(self.session_dir / "ERROR.txt", "w") as f:
                f.write(f"Error: {str(e)}\n")
                f.write(f"Time: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n")
                
            return []

def main():
    # Load environment variables from .env
    from dotenv import load_dotenv
    load_dotenv()
    
    # Retrieve API key from .env
    API_KEY = os.getenv("FIRECRAWL_API_KEY")
    if not API_KEY:
        raise ValueError("API Key not found. Please set it in the .env file.")
    
    parser = argparse.ArgumentParser(description="Scrape URLs and save pages as markdown files")
    parser.add_argument("--output-dir", default="../src/storage/scraped_docs", help="Directory to save markdown files")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum number of pages to scrape")
    
    args = parser.parse_args()
    
    # Hardcoded list of URLs to scrape
    urls = [
        "https://docs.anthropic.com/en/home",
        "https://docs.anthropic.com/en/api/getting-started",
        "https://docs.anthropic.com/en/prompt-library/library",
        "https://docs.anthropic.com/en/docs/about-claude/use-case-guides/overview"
    ]
    
    # Initialize the scraper with the API key and output directory
    scraper = FirecrawlMarkdownScraper(
        api_key=API_KEY,
        output_dir=args.output_dir
    )
    
    # Loop over each URL and run the scraper
    for url in urls:
        print(f"\n--- Scraping URL: {url} ---")
        scraper.run(url, args.max_pages)

if __name__ == "__main__":
    main()
