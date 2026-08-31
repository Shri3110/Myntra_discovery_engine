import os
import json
import re

def mock_hinglish_translate(text):
    """
    A mock translation function to simulate converting Hinglish internet slang
    to standard English for better AI processing.
    """
    dictionary = {
        r'\bplz\b': 'please',
        r'\bthx\b': 'thanks',
        r'\bkya hai\b': 'what is',
        r'\bsahi\b': 'good',
        r'\bbakar\b': 'bad',
        r'\bchahiye\b': 'want',
    }
    
    translated_text = text.lower()
    for pattern, replacement in dictionary.items():
        translated_text = re.sub(pattern, replacement, translated_text)
        
    return translated_text

def clean_text(text):
    """Removes special characters, URLs, and extra spaces."""
    if not text:
        return ""
    
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    # Remove weird characters but keep basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', '', text)
    # Reduce multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def process_data(input_dir, output_dir):
    """Reads raw JSON files, cleans them, and saves to an output directory."""
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' not found. Please run Phase 1 scrapers first.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    processed_count = 0
    seen_texts = set()
    for filename in os.listdir(input_dir):
        if filename.endswith(".json") and not filename.startswith("cleaned_"):
            filepath = os.path.join(input_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Skipping {filename}: Invalid JSON")
                    continue
                    
            cleaned_data = []
            
            for item in data:
                # Different scrapers have different text keys
                text = item.get('text') or item.get('title') or ""
                if not text or text in seen_texts:
                    continue
                seen_texts.add(text)
                    
                cleaned_text = clean_text(text)
                translated_text = mock_hinglish_translate(cleaned_text)
                
                # Keep only substantive comments
                if len(translated_text.split()) > 3: 
                    item['cleaned_text'] = translated_text
                    cleaned_data.append(item)
                    
            output_filename = f"cleaned_{filename}"
            output_filepath = os.path.join(output_dir, output_filename)
            
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2)
                
            print(f"Processed {filename}: {len(cleaned_data)} valid items saved.")
            processed_count += 1
            
    print(f"Data cleaning complete. Processed {processed_count} files.")

if __name__ == "__main__":
    raw_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'phase_1_ingestion', 'data'))
    cleaned_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data_cleaned'))
    
    print("Starting data cleaner...")
    process_data(raw_data_dir, cleaned_data_dir)
