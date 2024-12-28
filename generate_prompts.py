import os
import time
from pathlib import Path
from openai import OpenAI
from typing import Optional
from dotenv import load_dotenv

BLOG_POSTS_DIR = 'data/blog_posts_md'
OUTPUT_DIR = 'data/blog_posts_prompts'
# Delay between API calls (seconds)
DEFAULT_DELAY = 1

# Templates
SYSTEM_PROMPT = """You are an assistant that creates prompts for fine-tuning language models. Your task is to analyze blog posts written in Markdown format and generate concise, natural-sounding prompts. These prompts will be used to request blog posts on similar topics and in a similar style."""

USER_PROMPT_TEMPLATE = """Please read the following blog post written in Markdown format. After analyzing it, do the following:

- Identify the main topic and tone of the blog post.
- Create a concise and natural-sounding prompt that a user might use to request a blog post on the same topic and in a similar style.
- The prompt should be suitable for generating a full blog post, not just answering a question.

Examples of prompts you might generate:

- 'Write a blog post about <topic>'
- 'Create an article on <concept>'
- 'Explain <idea> in a blog format'

Here is the blog post content:

{ARTICLE_CONTENT}

Now, generate the prompt. Output just the prompt text without quotes and other decorations."""

def read_markdown_file(file_path: str) -> Optional[str]:
    """Read content from markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"  Error reading file {file_path}: {e}")
        return None

def generate_prompt(article_content: str, delay: int = DEFAULT_DELAY) -> Optional[str]:
    """Generate prompt using OpenAI API"""
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(ARTICLE_CONTENT=article_content)}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        time.sleep(delay)
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"  Error generating prompt: {e}")
        return None

def save_prompt(content: str, output_path: str) -> None:
    """Save generated prompt to file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"  Error saving prompt to {output_path}: {e}")

def main(delay: int = DEFAULT_DELAY):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    markdown_files = list(Path(BLOG_POSTS_DIR).glob('*.md'))
    total_files = len(markdown_files)
    
    print(f"Found {total_files} markdown files to process\n")
    
    for i, md_file in enumerate(markdown_files, 1):
        print(f"[{i}/{total_files}] Processing {md_file.name}...")
        
        # Check if output file already exists
        output_file = Path(OUTPUT_DIR) / f"{md_file.stem}.txt"
        if output_file.exists():
            print("  Skipping - prompt already generated")
            continue
        
        # Read markdown content
        content = read_markdown_file(md_file)
        if not content:
            continue
        
        # Generate prompt
        prompt = generate_prompt(content, delay)
        if not prompt:
            continue
        
        # Save result
        save_prompt(prompt, output_file)

        if i == 3:
            exit(0)
        
if __name__ == '__main__':
    load_dotenv()
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: Please set OPENAI_API_KEY environment variable!")
        exit(1)
    
    client = OpenAI()
    main()