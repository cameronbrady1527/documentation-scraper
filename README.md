# Firecrawl Documentation Scraper

A powerful Python toolkit for extracting and organizing documentation from websites using the Firecrawl SDK. This project provides both crawling and scraping capabilities to generate well-structured markdown content from web documentation.

## About

Firecrawl Documentation Scraper is a specialized tool that combines website crawling and content extraction to help developers collect, organize, and utilize documentation from various sources. It leverages the Firecrawl SDK to handle the complex work of web navigation while delivering clean, formatted markdown output ready for immediate use.

## Key Features

- **Dual Functionality**: Includes both a crawler and a scraper to handle different documentation extraction needs
- **Firecrawl SDK Integration**: Properly leverages SDK methods for efficient web content extraction
- **Session-based Organization**: Creates timestamped directories for each operation
- **Direct Markdown Extraction**: Uses Firecrawl's built-in format conversion capabilities
- **Comprehensive Error Handling**: Includes retries and proper error logging
- **Well-structured Output**: Organizes content into markdown files with consistent metadata
- **Index Generation**: Creates navigable indexes linking to all extracted documents

## Installation

To use this toolkit, install the required dependencies:

```bash
uv pip install firecrawl
```

## Usage

### Crawler Mode

The crawler systematically explores websites following specified path patterns:

```bash
python run_crawler.py --api-key YOUR_API_KEY --url https://docs.anthropic.com --paths "/claude/docs/.+" "/claude/reference/.+" --output-dir anthropic_docs --max-pages 100
```

### Scraper Mode

The scraper targets specific URLs and extracts their content:

```bash
python run_scraper.py --api-key YOUR_API_KEY --url https://docs.anthropic.com --output-dir anthropic_docs --max-pages 5
```

### Arguments

#### Crawler Arguments
- `--api-key` (required): Your Firecrawl API key
- `--url` (required): The base URL to start the crawl
- `--paths` (optional): One or more regex patterns specifying which paths to include
- `--output-dir` (optional, default: `crawled_docs`): Base directory for output
- `--max-pages` (optional, default: `100`): Maximum pages to crawl

#### Scraper Arguments
- `--api-key` (required): Your Firecrawl API key
- `--url` (required): URL to scrape
- `--output-dir` (optional, default: `../src/storage/scraped_docs`): Directory for output
- `--max-pages` (optional, default: `5`): Maximum pages to scrape

## How It Works

### Crawler Process
1. Initializes the Firecrawl SDK with your API key
2. Creates a unique timestamped session directory
3. Sends a crawl request with specified URL and path patterns
4. Monitors crawl progress until completion
5. Retrieves and saves markdown content from all crawled pages
6. Generates an index of all extracted documents

### Scraper Process
1. Initializes the Firecrawl SDK with your API key
2. Creates a timestamped session directory
3. Submits the target URL for scraping
4. Monitors progress until completion
5. Processes each page and formats content as markdown
6. Creates an index linking to all scraped content

## Output Structure

Each operation creates a similarly structured output:

```
output_directory/
    ├── crawl_YYYYMMDD_HHMMSS/ (or scrape_YYYYMMDD_HHMMSS/)
    │   ├── config.json          # Configuration details
    │   ├── status.json/result.json # Operation results
    │   ├── markdown/            # Directory for crawler output
    │   │   ├── page1.md         # Extracted markdown document
    │   │   ├── page2.md         # Another markdown document
    │   ├── page1.md             # Direct scraper output
    │   ├── page2.md             # Another scraped document
    │   ├── index.md             # Index of all documents
```

## Advanced Features

### Content Formatting
Both tools apply formatting rules to ensure proper markdown structure:
- Proper header spacing
- Consistent paragraph breaks
- Normalized list formatting
- Clean code block presentation

### Error Recovery
- Automatic retries for transient failures
- Detailed error logging
- Session preservation even after failures

## Logging

- Crawler: Activities and errors logged to `firecrawl.log`
- Scraper: Status updates printed to console and errors saved to `ERROR.txt`

## Choosing Between Crawler and Scraper

- **Use the crawler** when you need to extract documentation from multiple pages following specific patterns
- **Use the scraper** when targeting specific URLs or smaller documentation sets

## License

This project is open-source. Modify and distribute as needed.

## Contributions

Pull requests and feature suggestions are welcome!
