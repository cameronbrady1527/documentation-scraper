
import time
import json
import datetime
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from firecrawl import FirecrawlApp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("firecrawl.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("firecrawl-extractor")

class MarkdownExtractor:
    def __init__(
        self,
        api_key: str,
        output_base_dir: str = "../src/storage/scraped_docs",
        check_interval: int = 10
    ):
        """
        Initialize the markdown extractir with the Firecrawl SDK.
        
        Args:
            api_key: Your Firecrawl API key
            output_base_dir: Base directory for storing crawl results
            check_interval: How often to check crawl status (unit: seconds)
        """
        self.api_key = api_key
        self.output_base_dir = output_base_dir
        self.check_interval = check_interval

        # Initialize Firecrawl SDK
        self.firecrawl = FirecrawlApp(api_key=self.api_key)

        # Create base output directory
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

    def _generate_session_dir(self) -> Path:
        """Generate a unique session directory based on current date and time (in UTC)."""
        
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S") 
        session_dir = self.output_base_dir / f"crawl_{timestamp}"
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir
    
    def crawl_and_extract(
            self,
            base_url: str,
            included_paths: List[str] = None,
            max_pages: int = 5
    ) -> Tuple[Path, List[Path]]:
        """
        Crawl a URL with specified paths and extract markdown content.
        
        Args:
            base_url: The base URL to crawl
            included_paths: List of paths to include in the crawl (regex patterns)
            max_pages: Ceiling number of pages to crawl

        Returns:
            Tuple of (session_directory, list_of_saved_files)
        """
        # Create session directory
        session_dir = self._generate_session_dir()

        # Save crawl configurations
        config= {
            "base_url": base_url,
            "included_paths": included_paths,
            "max_pages": max_pages,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        with open(session_dir / "config.json", "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Starting crawl for {base_url}")

        try:
            # Prepare crawl parameters
            params = {
                'limit': max_pages,
                'scrapeOptions': {'formats': ['markdown', 'html']}
            }

            # Add included paths if specified
            if included_paths and len(included_paths) > 0:
                params['includePaths'] = included_paths

            # Start crawl using the SDK
            crawl_status = self.firecrawl.crawl_url(base_url, params=params)

            # Get crawl ID
            crawl_id = crawl_status.get('id')
            if not crawl_id:
                raise ValueError("Failed to get crawl ID from Firecrawl")
            
            logger.info(f"Crawl started with ID: {crawl_id}")

            # Save crawl ID
            with open(session_dir / "crawl_id.txt", "w") as f:
                f.write(crawl_id)

            # Wait for crawl to complete
            completed_status = self._wait_for_completion(crawl_id)

            # Save completed status
            with open(session_dir / "status.json", "w") as f:
                json.dump(completed_status, f, indent=2)

            if completed_status.get('status') == 'failed':
                error_msg = f"Crawl failed: {completed_status.get('error', 'Unknown error')}"
                logger.error(error_msg)
                with open(session_dir / "ERROR.txt", "w") as f:
                    f.write(error_msg)
                return session_dir, []
            
            # Get crawl results
            pages = self.firecrawl.get_crawl_pages(crawl_id)

            # Save raw pages for reference
            with open(session_dir / "pages.json", "w") as f:
                json.dump(pages, f, indent=2)

            # Extract and save markdown content
            saved_files = self._save_markdown_content(pages, session_dir)

            # Create index file
            if saved_files:
                self._create_index(saved_files, session_dir)

            logger.info(f"Crawl and extraction completed. {len(saved_files)} files saved.")
            return session_dir, saved_files

        except Exception as e:
            logger.error(f"Error during crawl: {str(e)}")
            with open(session_dir / "ERROR.txt", "w") as f:
                f.write(f"Error during crawl: {str(e)}")
            raise

    def _wait_for_completion(self, crawl_id: str) -> Dict[str, Any]:
        """Wait for a crawl to complete and return the final status."""
        max_retries = 3
        retry_count = 0

        while True:
            try:
                status = self.firecrawl.get(crawl_id)
                current_status = status.get('status')
                pages_crawled = status.get('pagesCrawled', 0)

                logger.info(f"Crawl status: {current_status}, Pages crawled: {pages_crawled}")

                if current_status in ['completed', 'failed']:
                    return status
                
                time.sleep(self.check_interval)
                retry_count = 0 # Reset retry count on successful request

            except Exception as e:
                retry_count += 1
                if retry_count > max_retries:
                    logger.error(f"Failed to check status after {max_retries} retries: {str(e)}")
                    raise
                logger.warning(f"Error checking status (retry {retry_count}/{max_retries}): {str(e)}")
                time.sleep(self.check_interval)

    def _save_markdown_content(self, pages: List[Dict[str, Any]], session_dir: Path) -> List[Path]:
        """
        Extract markdown content from crawled pages and save to files.

        Args:
            pages: List of page data from Firecrawl
            session_dir: Session directory to save files

        Returns:
            List of saved file paths
        """
        markdown_dir = session_dir / "markdown"
        markdown_dir.mkdir(exist_ok=True)

        saved_files=[]

        for page in pages:
            try:
                url = page.get('url', '')
                title = page.get('title', 'Untitled')

                # Check if markdown content is available
                formats = page.get('formats', {})

                if 'markdown' in formats and formats['markdown']:
                    markdown_content = formats['markdown']
                else:
                    logger.warning(f"No markdown content available for {url}")
                    continue

                # Create filename from URL
                path_part = url.split("://", 1)[-1]
                if '/' in path_part:
                    path_part = path_part.split('/', 1)[-1]

                # Create valid filename
                filename = path_part.replace("/", "_").replace("?", "_").replace("&", "_")
                if not filename:
                    filename = "index"
                if not filename.endswith('.md'):
                    filename += ".md"

                filepath = markdown_dir / filename

                # Add title and metadata
                full_content = f"# {title}\n\nSource URL: {url}\n\n---\n\n{markdown_content}"

                # Save to file
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(full_content)

                logger.info(f"Saved: {filepath}")
                saved_files.append(filepath)

            except Exception as e:
                logger.error(f"Error processing page {page.get('url', 'unknown')}: {str(e)}")

        return saved_files
    
    def _create_index(self, files: List[Path], session_dir: Path) -> Path:
        """Create an index file with links to all saved markdown files."""
        index_path = session_dir / "index.md"

        try:
            with open(index_path, "w", encoding="utf-8") as f:
                timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"# Crawl Results - {timestamp}\n\n")

                # Add crawl information if available
                config_path = session_dir / "config.json"
                if config_path.exists():
                    try:
                        with open(config_path, "r") as config_file:
                            config = json.load(config_file)
                            f.write(f"**Included Paths:**\n\n")
                            for path in config.get('included_paths', []) or []:
                                f.write(f"- `{path}`\n")
                            f.write("\n")
                    except Exception as e:
                        logger.warning(f"Failed to read config: {str(e)}")

                # List all files
                f.write("## Documents\n\n")

                for file_path in sorted(files):
                    relative_path = file_path.relative_to(session_dir)

                    # Try to extract title from the file
                    title = file_path.name
                    try:
                        with open(file_path, "r", encoding="utf-8") as doc_file:
                            first_line = doc_file.readline().strip()
                            if first_line.startswith("# "):
                                title = first_line[2:]
                    except Exception as e:
                        logger.warning(f"Failed to read title from {file_path}: {str(e)}")

                    f.write(f"- [{title}]({relative_path})\n")

            logger.info(f"Created index at: {index_path}")
            return index_path
        
        except Exception as e:
            logger.eror(f"Failed to create index: {str(e)}")
            raise


def main():
    parser = argparse.ArgumentParser(description="Extract markdown from websites using Firecrawl SDK")
    parser.add_argument("--api-key", required=True, help="Your Firecrawl API key")
    parser.add_argument("--url", required=True, help="URL to crawl")
    parser.add_argument("--paths", nargs="+", help="Paths to include in the crawl (regex patters)")
    parser.add_argument("--output-dir", default="crawled_docs", help="Base directory for output")
    parser.add_argument("--max-pages", type=int,default=100, help="Maximum pages to crawl")

    args = parser.parse_args()

    try:
        extractor = MarkdownExtractor(
            api_key=args.api_key,
            output_base_dir=args.output_dir
        )

        session_dir, saved_files = extractor.crawl_and_extract(
            base_url=args.url,
            included_paths=args.paths,
            max_pages=args.max_pages
        )

        if saved_files:
            print(f"\nSuccess! Extracted {len(saved_files)} markdown files to {session_dir}")
            print(f"See {session_dir}/index.md for a list of all files")
        else:
            print(f"\nNo markdown files were extracted. Check {session_dir} for error details.")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("See firecrawl.log for detailed error information")


if __name__ == "__main__":
    main()
