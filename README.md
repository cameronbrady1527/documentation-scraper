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
uv pip install firecrawl python-dotenv pyyaml
```

## Usage

### Crawler Mode

The crawler systematically explores websites following specified path patterns:

```bash
python run_crawler.py --api-key YOUR_API_KEY --url https://docs.anthropic.com --paths "/claude/docs/.+" "/claude/reference/.+" --output-dir anthropic_docs --max-pages 5
```

### Scraper Mode

The scraper now loads its API key from a `.env` file at the root of the project and reads one or more URLs from the `providers.yaml` file (located at `../providers.yaml`). It then loops through all the URLs to scrape their content.

Ensure your `.env` file contains your API key as follows:
```bash
FIRECRAWL_API_KEY=your_api_key_here
```
And your `providers.yaml` file defines one or more providers and their corresponding URLs:
```yaml
providers:
  - name: anthropic
    root_urls:
      - "https://docs.anthropic.com/en/docs"
      - "https://docs.anthropic.com/en/api"
    ...
```
Run the scraper with:

```bash
python run_scraper.py --output-dir anthropic_docs --max-pages 5
```
> **Note:**  
> - The API key is now loaded from the `.env` file. Do not pass it as a command-line argument.  
> - The URL(s) to scrape are read from the `providers.yaml` file. The scraper loops over all URLs provided.  
> - The default output directory is `../src/storage/scraped_docs`, but you can override it with `--output-dir`.


### Arguments

#### Crawler Arguments
- `--api-key` (required): Your Firecrawl API key
- `--url` (required): The base URL to start the crawl
- `--paths` (optional): One or more regex patterns specifying which paths to include
- `--output-dir` (optional, default: `crawled_docs`): Base directory for output
- `--max-pages` (optional, default: `100`): Maximum pages to crawl

#### Scraper Arguments
**API Key**: Now loaded from the `.env` file (set `FIRECRAWL_API_KEY` in the file).
- **URLs**: Read from `providers.yaml` (located at `../providers.yaml`), allowing multiple URLs to be processed.
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
1. Loads the API key from the `.env` file
2. Reads one or more target URLs from `providers.yaml`
3. Creates a timestamped session directory for each scrape operation
4. Submits each URL for scraping and monitors progress until completion
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
- **Use the scraper** when targeting specific URLs or smaller documentation sets. The updated scraper now supports multiple URLs from `providers.yaml` and automatically loads your API key from the `.env` file.

## License

This project is open-source. Modify and distribute as needed.

## Contributions

Pull requests and feature suggestions are welcome!
