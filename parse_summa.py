#!/usr/bin/env python3
"""
Final Script to parse Summa Theologica text into structured articles with proper section tracking.
"""

import re
import os
import sys

def parse_summa_text(input_file):
    """
    Parse the Summa Theologica text file line by line, maintaining internal state 
    to track sections, questions, and articles.
    """
    
    # Ensure output directories exist
    os.makedirs('I_Pars', exist_ok=True)
    os.makedirs('II_Pars', exist_ok=True)
    os.makedirs('III_Pars', exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Internal state tracking
    current_section = ""
    current_question = ""
    current_part = ""
    
    # Article parsing state
    current_article_header = None
    current_article_content = []
    in_article = False
    
    # Read through the file line by line
    for line in lines:
        # Skip empty lines at beginning of article
        if not line.strip() and not in_article:
            continue
            
        # Check for section headers (like "TREATISE ON PRUDENCE AND JUSTICE")
        section_match = re.match(r'^\s*(TREATISE ON .*)$', line, re.IGNORECASE)
        if section_match:
            current_section = section_match.group(1).strip()
            print(f"Found section: {current_section}")
            continue
            
        # Check for part headers (like "SECOND PART OF THE SECOND PART")
        part_match = re.match(r'^\s*(SECOND PART OF THE SECOND PART.*)$', line, re.IGNORECASE)
        if part_match:
            current_part = part_match.group(1).strip()
            print(f"Found part: {current_part}")
            continue
            
        # Check for question headers (like "QUESTION 1")
        question_match = re.match(r'^\s*(QUESTION\s+(\d+))$', line, re.IGNORECASE)
        if question_match:
            current_question = question_match.group(1).strip()
            print(f"Found question: {current_question}")
            continue
            
        # Check for article headers (like "FIRST ARTICLE [II-II, Q. 1, Art. 1]")
        article_match = re.match(r'^\s*([A-Z]+(?:-[A-Z]+)?) ARTICLE \[([^\]]+)\]$', line.strip())
        if article_match:
            ordinal = article_match.group(1)
            reference = article_match.group(2)
            
            # Save previous article if we were in one
            if in_article and current_article_header:
                save_article(current_article_header, current_article_content)
                
            # Start new article
            current_article_header = f"{ordinal} ARTICLE [{reference}]"
            current_article_content = []
            in_article = True
            
            print(f"Found article header: {current_article_header}")
            continue
            
        # If we're inside an article and haven't hit another article header, collect content
        if in_article:
            if line.strip() == '---' or line.startswith('______________________'):
                # Skip separator lines but keep collecting content  
                continue
            current_article_content.append(line)
            
    # Save the final article
    if in_article and current_article_header:
        save_article(current_article_header, current_article_content)

def save_article(header, content_lines):
    """
    Save an article to appropriate directory with proper naming.
    """
    
    # Extract reference information from header
    match = re.search(r'([A-Z]+(?:-[A-Z]+)?) ARTICLE \[(.*)\]', header)
    if not match:
        print(f"Warning: Could not parse header: {header}")
        return
        
    ordinal = match.group(1)
    reference = match.group(2)
    
    # Parse reference properly to get part, question, article
    # Look for pattern like "II-II, Q. 1, Art. 1"
    part = "II-II" if "II-II" in reference else ("I" if "I" in reference else ("III" if "III" in reference else "UNKNOWN"))
    question_match = re.search(r'Q\. (\d+)', reference)
    article_match = re.search(r'Art\. (\d+)', reference)
    
    question = question_match.group(1) if question_match and question_match.group(1).isdigit() else "0"
    article = article_match.group(1) if article_match and article_match.group(1).isdigit() else "0"
    
    # Determine which directory based on part
    if 'II-II' in reference:
        output_dir = 'II_Pars'
    elif 'I' in reference and not 'II' in reference:
        output_dir = 'I_Pars'
    elif 'III' in reference:
        output_dir = 'III_Pars'
    else:
        output_dir = 'II_Pars'
    
    # Create clean filename
    ref_clean = reference.replace('/', '_').replace(' ', '_')
    # Clean up malformed references 
    ref_clean = re.sub(r'Q,_(\d+)', r'Q.\1', ref_clean)
    ref_clean = re.sub(r'Q\._(\d+)', r'Q.\1', ref_clean)
    # Remove any problematic characters but retain valid ones
    ref_clean = re.sub(r'[^A-Za-z0-9_,.-]', '_', ref_clean)
    
    filename = f"Q{question}_A{article}_{ref_clean}.txt"
    
    # Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Write the file
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{header}\n\n")
        for line in content_lines:
            if line.strip():  # Only write non-empty lines
                f.write(line)
            
    print(f"Saved: {filename} to {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_summa.py <input_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} does not exist")
        sys.exit(1)
        
    print("Starting Summa Theologica parsing...")
    parse_summa_text(input_file)
    print("Parsing completed!")