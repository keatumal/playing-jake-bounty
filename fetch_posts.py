import os
import time
import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urlparse

# Constants
POST_URLS_FILE = 'data/post_urls.txt'
OUTPUT_DIR = 'data/blog_posts_md'
# Default delay between requests in seconds
DEFAULT_DELAY = 2
# Default number of retries for failed requests
MAX_RETRIES = 10

def get_urls_from_file():
    """Read URLs from file, skipping empty lines"""
    with open(POST_URLS_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def get_page_content(url, delay=DEFAULT_DELAY, max_retries=MAX_RETRIES):
    """
    Get HTML content of the page with retries and delay
    
    Args:
        url: Target URL
        delay: Delay between requests in seconds
        max_retries: Maximum number of retry attempts
    """
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"  Retry attempt {attempt + 1}/{max_retries}")
            
            response = requests.get(url)
            response.raise_for_status()
            
            # Only delay after successful request
            time.sleep(delay)
            return response.text
            
        except requests.RequestException as e:
            if attempt == max_retries - 1:  # Last attempt
                print(f"  Failed to fetch page after {max_retries} attempts: {e}")
                return None
            time.sleep(delay)  # Delay before retry

def extract_article_content(html):
    """Extract article title and content"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Get H1
    h1 = soup.find('h1', class_='post-title')
    if h1:
        title = h1.text.strip()
        print('  Title:', title)
    else:
        print('  WARN: Title not found')
        return None, None
    
    # Get main content
    content_div = soup.find('div', class_='available-content')
    if not content_div:
        print("  WARN: Content block not found")
        return None, None
    
    # Remove subscription widget
    subscribe_widget = content_div.find('div', class_='subscribe-widget')
    if subscribe_widget:
        subscribe_widget.decompose()
    
    return title, str(content_div)

def html_to_markdown(html_content, title):
    """Convert HTML to Markdown"""
    converter = html2text.HTML2Text()
    converter.body_width = 0  # Disable line wrapping
    
    # Format markdown with title
    markdown = f"# {title}\n\n"
    markdown += converter.handle(html_content)
    return markdown

def get_slug_from_url(url):
    """Get slug from URL"""
    path = urlparse(url).path
    return path.strip('/').split('/')[-1]

def save_markdown(content, slug):
    """Save markdown to file"""
    output_file = os.path.join(OUTPUT_DIR, f"{slug}.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

def file_exists(slug):
    """Check if markdown file already exists"""
    return os.path.exists(os.path.join(OUTPUT_DIR, f"{slug}.md"))

def main(delay=DEFAULT_DELAY, max_retries=MAX_RETRIES):
    # Get list of URLs
    urls = get_urls_from_file()
    print(f"Found {len(urls)} URLs to process\n")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for url_num, url in enumerate(urls):
        print(f"[{url_num+1}/{len(urls)}] {url}...")
        
        # Skip if file already exists
        slug = get_slug_from_url(url)
        if file_exists(slug):
            print("  Skipping - already processed")
            continue
        
        # Get page content
        html = get_page_content(url, delay, max_retries)
        if not html:
            print()
            continue
        
        # Extract article content
        title, content = extract_article_content(html)
        if not content:
            continue
        
        # Convert to markdown
        markdown = html_to_markdown(content, title)
        
        # Save result
        save_markdown(markdown, slug)

if __name__ == '__main__':
    main()