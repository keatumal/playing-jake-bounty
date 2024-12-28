import json
import os
import random
import argparse
from pathlib import Path
from typing import Optional, Dict, List, Tuple

#BLOG_POSTS_DIR = 'data/blog_posts_md'
BLOG_POSTS_DIR = 'data/blog_posts_txt'
PROMPTS_DIR = 'data/blog_posts_prompts'
OUTPUT_DIR = 'data/training_datasets'

SYSTEM_PROMPT = """You are an AI trained to write blog posts in the exact style of the author of "BLOG OF JAKE" (www.blogofjake.com). Your goal is to perfectly replicate the author's writing style, tone, and formatting conventions."""

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Create training and test datasets for fine-tuning'
    )
    parser.add_argument(
        '--train-size',
        type=int,
        required=True,
        help='Number of examples for training dataset'
    )
    parser.add_argument(
        '--test-size',
        type=int,
        required=True,
        help='Number of examples for test dataset'
    )
    return parser.parse_args()

def validate_json_line(line: str) -> bool:
    """Validate that the line can be parsed back as valid JSON"""
    try:
        parsed = json.loads(line)
        assert "messages" in parsed
        assert len(parsed["messages"]) == 3
        assert all("role" in msg and "content" in msg for msg in parsed["messages"])
        return True
    except (json.JSONDecodeError, AssertionError) as e:
        print(f"JSON validation failed: {e}")
        return False

def read_file(file_path: str) -> Optional[str]:
    """Read content from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def get_matching_files() -> List[Tuple[str, str]]:
    """Get matching article and prompt files"""
    article_files = Path(BLOG_POSTS_DIR).glob('*.txt')
    matching_pairs = []
    
    for article_path in article_files:
        prompt_path = Path(PROMPTS_DIR) / f"{article_path.stem}.txt"
        if prompt_path.exists():
            matching_pairs.append((str(article_path), str(prompt_path)))
        else:
            print(f"Warning: No matching prompt found for {article_path.name}")
    
    return matching_pairs

def create_training_example(article_path: str, prompt_path: str) -> Optional[Dict]:
    """Create a single training example from article and prompt files"""
    # Read article content
    article_content = read_file(article_path)
    if not article_content:
        return None
    
    # Read prompt content
    prompt_content = read_file(prompt_path)
    if not prompt_content:
        return None
    
    # Format user prompt
    if not prompt_content.strip().endswith('.'):
        prompt_content = prompt_content.strip() + '.'
    #prompt_content = f"{prompt_content} Please format the output as Markdown."
    
    # Create the training example
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": prompt_content
        },
        {
            "role": "assistant",
            "content": article_content
        }
    ]
    
    return {"messages": messages}

def write_jsonl(examples: List[Dict], output_file: str) -> int:
    """Write examples to JSONL file and return number of successful writes"""
    success_count = 0
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in examples:
            json_line = json.dumps(example, ensure_ascii=False)
            if validate_json_line(json_line):
                f.write(json_line + '\n')
                success_count += 1
            else:
                print("Skipping invalid example")
    
    return success_count

def main():
    args = parse_args()
    required_examples = args.train_size + args.test_size
    
    # Get all matching files
    file_pairs = get_matching_files()
    total_pairs = len(file_pairs)
    
    if total_pairs < required_examples:
        print(f"Error: Not enough examples. Have {total_pairs}, need {required_examples}")
        return
    
    print(f"Found {total_pairs} matching article-prompt pairs")
    
    # Create all training examples
    print("\nCreating examples...")
    examples = []
    for i, (article_path, prompt_path) in enumerate(file_pairs, 1):
        print(f"[{i}/{total_pairs}] Processing {Path(article_path).name}...")
        
        example = create_training_example(article_path, prompt_path)
        if example:
            examples.append(example)
    
    if len(examples) < required_examples:
        print(f"Error: Only created {len(examples)} valid examples, need {required_examples}")
        return
    
    # Randomly shuffle and split examples
    random.shuffle(examples)
    train_examples = examples[:args.train_size]
    test_examples = examples[args.train_size:args.train_size + args.test_size]
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Write training dataset
    train_file = os.path.join(OUTPUT_DIR, 'train.jsonl')
    print(f"\nWriting training dataset ({args.train_size} examples)...")
    train_success = write_jsonl(train_examples, train_file)
    
    # Write test dataset
    test_file = os.path.join(OUTPUT_DIR, 'test.jsonl')
    print(f"\nWriting test dataset ({args.test_size} examples)...")
    test_success = write_jsonl(test_examples, test_file)
    
    print(f"\nDone! Created:")
    print(f"- Training dataset: {train_success} examples in {train_file}")
    print(f"- Test dataset: {test_success} examples in {test_file}")

if __name__ == '__main__':
    main()