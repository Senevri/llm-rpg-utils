from ast import parse
from importlib.resources.readers import remove_duplicates
from multiprocessing import process
import os
import sys
import json
import psutil
import asyncio
import requests
from xml.etree import ElementTree

__location__ = os.path.dirname(os.path.abspath(__file__))
__output__ = os.path.join(__location__, "output")

# Append parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


def combine_markdown_files(directory, output_file):
    with open(output_file, "w", encoding="UTF-8") as outfile:
        for filename in os.listdir(directory):
            if filename.endswith(".md"):
                filepath = os.path.join(directory, filename)
                with open(filepath, "r", encoding="UTF-8") as infile:
                    outfile.write(infile.read())
                    outfile.write("\n\n")  # Add a double newline between files


def process_files(directory, process_func):
    # Iterate through all markdown files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            filepath = os.path.join(directory, filename)

            with open(filepath, "r", encoding="UTF-8") as file:
                content = file.read()
            content = process_func(content)
            if content:
                with open(filepath, "w", encoding="UTF-8") as file:
                    file.write(content)


def remove_footers(directory, footer_locator):
    def remove_footer(content):
        footer_start = content.find(footer_locator)
        if footer_start != -1:
            footer_end = -1
            # Remove the footer section from the file
            content = content.replace(content[footer_start:footer_end], "")
        return content

    process_files(directory, remove_footer)


def remove_duplicate_links(directory):
    # Dictionary to store the links section content
    links_section_content = None

    def remove_duplicate_links(content):
        nonlocal links_section_content
        # Find the links section
        links_start = 0
        if links_start != -1:
            links_end = content.find("\n\n", links_start)
            if links_end == -1:
                links_end = len(content)

            current_links_section = content[links_start:links_end]

            if links_section_content is None:
                # Store the first encountered links section
                links_section_content = current_links_section
            else:
                # Remove the duplicate links section from the current file
                content = content.replace(current_links_section, "")

    process_files(directory, remove_duplicate_links)


async def crawl_parallel(urls: List[str], max_concurrent: int = 3):
    print("\n=== Parallel Crawling with Browser Reuse + Memory Check ===")

    # We'll keep track of peak memory usage across all tasks
    peak_memory = 0
    process = psutil.Process(os.getpid())

    def parse_html(html: str):
        # Parse the HTML content here
        # get content between <loc> and </loc>
        links = []

        while "<loc>" in html:
            start = html.find("<loc>") + len("<loc>")
            end = html.find("</loc>")
            url = html[start:end]
            html = html[end + len("</loc>") :]
            links.append(url)
        return links

    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss  # in bytes
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(
            f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB"
        )

    def save_results(url, content: str):
        # Save the content to a file, get filename from title,
        # add index if filename already exists
        folder = "crawl_results"
        if not os.path.exists(folder):
            os.mkdir(folder)
        base_filename = url.split("/")[-1] + ".md"
        # filename = f"crawl_result.md"
        index = 1
        filename = base_filename
        if os.path.exists(os.path.join(folder, filename)):
            return
        # while os.path.exists(os.path.join(folder, filename)):
        #     filename = f"{base_filename}_{index}.md"
        #     index += 1
        save_path = os.path.join(folder, filename)
        print(f"Saving content to {save_path}")
        with open(save_path, "w", encoding="UTF-8") as file:
            file.write(content)
            # json.dump(file, content)

    # Minimal browser config
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,  # corrected from 'verbos=False'
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # We'll chunk the URLs in batches of 'max_concurrent'
        success_count = 0
        fail_count = 0
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i : i + max_concurrent]
            tasks = []

            for j, url in enumerate(batch):
                # Unique session_id per concurrent sub-task
                session_id = f"parallel_session_{i + j}"
                task = crawler.arun(url=url, config=crawl_config, session_id=session_id)
                tasks.append(task)

            # Check memory usage prior to launching tasks
            log_memory(prefix=f"Before batch {i//max_concurrent + 1}: ")

            # Gather results
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check memory usage after tasks complete
            log_memory(prefix=f"After batch {i//max_concurrent + 1}: ")

            # Evaluate results
            for url, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"Error crawling {url}: {result}")
                    fail_count += 1
                elif result.success:
                    success_count += 1
                    # print(result)
                    save_results(url, result.markdown)
                else:
                    fail_count += 1

        print(f"\nSummary:")
        print(f"  - Successfully crawled: {success_count}")
        print(f"  - Failed: {fail_count}")

    finally:
        print("\nClosing crawler...")
        await crawler.close()
        # Final memory log
        log_memory(prefix="Final: ")
        print(f"\nPeak memory usage (MB): {peak_memory // (1024 * 1024)}")


def get_docs_urls(sitemap_url: str) -> List[str]:
    """
    Fetches all URLs from the Pydantic AI documentation.
    Uses the sitemap (https://ai.pydantic.dev/sitemap.xml) to get these URLs.

    Returns:
        List[str]: List of URLs
    """

    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()

        # Parse the XML
        root = ElementTree.fromstring(response.content)

        # Extract all URLs from the sitemap
        # The namespace is usually defined in the root element
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [loc.text for loc in root.findall(".//ns:loc", namespace)]

        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []


async def main():
    urls = get_docs_urls("https://fate-srd.com/sitemap-0.xml")
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_parallel(urls, max_concurrent=4)
    else:
        print("No URLs found to crawl")


if __name__ == "__main__":
    # asyncio.run(main())
    # remove_duplicate_links("crawl_results")
    # footer_locator = "[![Fate SRD Logo](https://fate-srd.com/_next/static/media/logo.efc58322.svg)]"
    # footer_locator = "## Where to Buy"
    # remove_footers("crawl_results", footer_locator)
    combine_markdown_files("crawl_results", "crawl_results.md")
