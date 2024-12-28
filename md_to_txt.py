import re
from pathlib import Path
from markdown2 import Markdown
import html2text

# Configuration constants
INPUT_DIR = "data/blog_posts_md"
OUTPUT_DIR = "data/blog_posts_txt"
URL_PLACEHOLDER = "[URL]"


def convert_urls_to_placeholder(text):
    """
    Replace all URLs with a placeholder
    """
    url_pattern = r'<(http[s]?://[^\s<>]+)>|(?<![\[<])(http[s]?://[^\s<>]+)(?![\]>])'
    return re.sub(url_pattern, URL_PLACEHOLDER, text)

def markdown_to_text(content):
    """
    Convert markdown to plain text using markdown2 and html2text
    """
    # Convert markdown to HTML
    markdown = Markdown()
    html = markdown.convert(content)
    
    # Configure html2text
    converter = html2text.HTML2Text()
    converter.ignore_links = True
    converter.ignore_images = True
    converter.ignore_emphasis = True
    converter.body_width = 0  # Don't wrap lines
    converter.unicode_snob = True  # Use Unicode characters
    
    # Convert HTML to text
    text = converter.handle(html)
    
    # Replace URLs with placeholder
    text = convert_urls_to_placeholder(text)
    
    # Clean up any remaining markdown-style formatting
    text = re.sub(r'[\*_]{1,2}([^\*_]+)[\*_]{1,2}', r'\1', text)
    
    return text.strip()

def process_markdown_files():
    """
    Process all .md files in the specified directory
    """
    input_path = Path(INPUT_DIR)
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    
    for md_file in input_path.glob('*.md'):
        try:
            # Read markdown file
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert content
            text_content = markdown_to_text(content)
            
            # Create new file with the same name but .txt extension
            output_file = output_path / md_file.name.replace('.md', '.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
                
            print(f"Processed file: {md_file.name}")
            
        except Exception as e:
            print(f"Error processing {md_file.name}: {str(e)}")

if __name__ == "__main__":
    process_markdown_files()