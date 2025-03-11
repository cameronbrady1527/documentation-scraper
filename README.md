# Documentation Scraper

This project provides a Python script that utilizes the Firecrawl SDK to extract markdown-formatted documentation from specified websites. The extracted content is well-structured, organized into timestamped directories, and includes an index for easy navigation.

## Key Features

- **Uses the Firecrawl SDK**: Properly leverages SDK methods like `crawl_url`, `get_crawl_status`, and `get_crawl_pages`.
- **Session-based organization**: Creates a timestamped directory for each crawl session.
- **Direct markdown extraction**: Uses Firecrawl's built-in markdown format extraction.
- **Comprehensive error handling**: Includes retries and proper error logging.
- **Well-structured output**: Organizes content into markdown files with metadata.
- **Index generation**: Creates an `index.md` file linking to all extracted documents.

## Installation

To use this scraper, you must install the required dependencies:

```bash
uv pip install firecrawl
```

## Usage

Run the script with the following command:

```bash
python firecrawl_markdown.py --api-key YOUR_API_KEY --url https://docs.anthropic.com --paths "/claude/docs/.+" "/claude/reference/.+" --output-dir anthropic_docs
```

### Arguments:
- `--api-key` (required): Your Firecrawl API key.
- `--url` (required): The base URL to start the crawl.
- `--paths` (optional): One or more regex patterns specifying which paths to include in the crawl.
- `--output-dir` (optional, default: `crawled_docs`): The base directory where crawled content will be stored.
- `--max-pages` (optional, default: `100`): The maximum number of pages to crawl.

## How It Works

1. **Initialize Firecrawl SDK**: The script initializes the SDK with your API key.
2. **Create a session directory**: It generates a unique session directory based on the timestamp.
3. **Start the crawl**: The script sends a request to Firecrawl with the given URL and path patterns.
4. **Monitor progress**: It continuously checks the crawl status until completion.
5. **Extract markdown**: Once completed, the script retrieves and saves markdown content from Firecrawl.
6. **Save output**: Each extracted page is stored as a markdown file in the session directory.
7. **Generate an index**: An `index.md` file is created, linking to all extracted documents.

## Output Structure

Each crawl session is saved in a timestamped directory:

```
src/storage/scraped_docs/
    ├── crawl_YYYYMMDD_HHMMSS/
    │   ├── config.json          # Crawl configuration details
    │   ├── crawl_id.txt         # ID of the Firecrawl session
    │   ├── status.json          # Final status of the crawl
    │   ├── pages.json           # Raw JSON output from Firecrawl
    │   ├── markdown/
    │   │   ├── page1.md         # Extracted markdown document
    │   │   ├── page2.md         # Another markdown document
    │   ├── index.md             # Index of all extracted documents
```

## Error Handling

- If a crawl fails, an `ERROR.txt` file is saved in the session directory.
- Logs are stored in `firecrawl.log`.
- The script retries status checks if failures occur.

## Logging

The script logs all activities and errors in `firecrawl.log` to help debug issues.

## License

This project is open-source. Modify and distribute as needed.

## Contributions

Pull requests and feature suggestions are welcome!

