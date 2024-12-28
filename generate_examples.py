import os
import random
import time
import argparse
from pathlib import Path
from typing import Optional, List
from openai import OpenAI
from dotenv import load_dotenv

# Attempt 1
#FINE_TUNED_MODEL = 'ft:gpt-4o-mini-2024-07-18:aiguys:playing-jake:AjEl8h8G'
# Attempt 2
FINE_TUNED_MODEL = 'ft:gpt-4o-mini-2024-07-18:aiguys:playing-jake:AjGVKlp0'

PROMPTS_DIR = 'data/blog_posts_prompts'
OUTPUT_DIR = 'data/result_examples'
# Delay between API requests (seconds)
DEFAULT_DELAY = 2

SYSTEM_PROMPT = """You are an AI trained to write blog posts in the exact style of the author of "BLOG OF JAKE" (www.blogofjake.com). Your goal is to perfectly replicate the author's writing style, tone, and formatting conventions."""

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Generate articles using fine-tuned model'
    )
    parser.add_argument(
        '--count',
        type=int,
        required=True,
        help='Number of articles to generate'
    )
    parser.add_argument(
        '--delay',
        type=int,
        default=DEFAULT_DELAY,
        help=f'Delay between requests in seconds (default: {DEFAULT_DELAY})'
    )
    return parser.parse_args()

def get_random_prompts(count: int) -> List[tuple]:
    """Get random prompts from directory"""
    # Collect all prompts
    prompt_files = list(Path(PROMPTS_DIR).glob('*.txt'))
    
    if not prompt_files:
        raise ValueError(f"No prompts found in {PROMPTS_DIR}")
    
    # If requested more than available - adjust count
    if count > len(prompt_files):
        print(f"Warning: Found only {len(prompt_files)} prompts, requested {count}")
        print("Will use all available prompts")
        count = len(prompt_files)
    
    # Shuffle and take required number
    selected = random.sample(prompt_files, count)
    
    # Create unique output filename for each prompt
    return [(f, f"generated_{i+1}_{f.stem}.txt") for i, f in enumerate(selected)]

def read_prompt(file_path: Path) -> Optional[str]:
    """Read prompt from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def generate_article(prompt: str) -> Optional[str]:
    """Generate article using API"""
    try:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                #"content": f"{prompt} Please format the output as Markdown."
                "content": prompt
            }
        ]
        
        response = client.chat.completions.create(
            model=FINE_TUNED_MODEL,
            messages=messages,
            # temperature=0.7,
            # max_tokens=2000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"API error: {e}")
        return None

def save_article(content: str, output_path: Path) -> bool:
    """Save article to file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error saving to {output_path}: {e}")
        return False

def main():
    args = parse_args()
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        # Get random prompts
        prompts = get_random_prompts(args.count)
        print(f"\nSelected {len(prompts)} random prompts")
        
        success_count = 0
        for i, (prompt_file, output_name) in enumerate(prompts, 1):
            print(f"\n[{i}/{len(prompts)}] Processing {prompt_file.name}...")
            
            # Read prompt
            prompt_text = read_prompt(prompt_file)
            if not prompt_text:
                continue
            
            # Generate article
            content = generate_article(prompt_text)
            if not content:
                continue
            
            # Save result
            output_path = Path(OUTPUT_DIR) / output_name
            if save_article(content, output_path):
                success_count += 1
                print(f"Saved result to {output_name}")
            
            # Add delay between requests
            if i < len(prompts):
                time.sleep(args.delay)
        
        print(f"\nDone! Successfully generated {success_count} out of {len(prompts)} articles")
        print(f"Results are in: {OUTPUT_DIR}")
        
    except Exception as e:
        print(f"\nFatal error: {e}")
        exit(1)

if __name__ == '__main__':
    load_dotenv()
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    client = OpenAI()
    main()