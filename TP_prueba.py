import re
import json
import mmh3
from collections import defaultdict

# Data dictionary structure
data_dict = {
    'TOKEN': [],
    'LEXEMAS': defaultdict(list)
}

# Predefined lexemes for tokens
predefined_lexemes = {
    'ARTICULO': ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas'],
    'SUSTANTIVO': ['Nietzsche', 'temas', 'libro', 'mundo', 'persona'],
    'VERBO': ['escribir', 'leer', 'ser', 'haber', 'ir', 'escribió', 'escriben'],
    'ADJETIVO': ['grande', 'pequeño', 'bueno', 'malo', 'nuevo', 'viejo'],
    'ADVERBIO': ['rápidamente', 'lentamente', 'bien', 'mal', 'cerca', 'lejos'],
    'OTROS': ['sobre', 'con', 'sin', 'en', 'por', 'para', 'y', 'o', 'a', 'de'],
    'ERROR_LX': []
}

# Function to initialize the data dictionary with predefined lexemes
def initialize_with_lexemes():
    for token, lexemes in predefined_lexemes.items():
        if token not in data_dict['TOKEN']:
            data_dict['TOKEN'].append(token)
        for lexeme in lexemes:
            if lexeme not in data_dict['LEXEMAS'][token]:
                data_dict['LEXEMAS'][token].append(lexeme)

# Function to load the existing data dictionary
def load_data_dict(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            loaded_dict = json.load(file)
            for token in loaded_dict['TOKEN']:
                if token not in data_dict['TOKEN']:
                    data_dict['TOKEN'].append(token)
                for lexeme in loaded_dict['LEXEMAS'][token]:
                    if lexeme not in data_dict['LEXEMAS'][token]:
                        data_dict['LEXEMAS'][token].append(lexeme)
            print("Data dictionary loaded successfully.")
            return True
    except FileNotFoundError:
        print("Data dictionary file not found.")
        return False
    except KeyError as e:
        print(f"KeyError: {e}")
        return False

# Function to prompt the user to assign a token
def prompt_for_token(lexeme):
    token_options = {
        1: 'ARTICULO',
        2: 'SUSTANTIVO',
        3: 'VERBO',
        4: 'ADJETIVO',
        5: 'ADVERBIO',
        6: 'OTROS',
        7: 'ERROR_LX'  # Adding ERROR_LX as an option
    }
    while True:
        print(f"Please assign a token to this lexeme: {lexeme}")
        for number, token in token_options.items():
            print(f"{number} - {token}")
        try:
            choice = int(input("Enter the number corresponding to your choice: "))
            if choice in token_options:
                return token_options[choice]
            else:
                print("Incorrect option, please enter a number between the allowed ones.")
        except ValueError:
            print("Invalid input, please enter a number.")

# Function to read and tokenize the input text
def tokenize_text(file_path, entry_number):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    lexemes = re.split(r'\s+|(?<!\d)[.,;:!?](?!\d)', text)
    output_tokens = []
    found_lexemes = set()
    new_lexemes = set()

    for index, lexeme in enumerate(lexemes):
        lexeme = lexeme.strip()
        if not lexeme:
            continue
        
        found_lexemes.add(lexeme)
        token_found = False
        
        for token in data_dict['TOKEN']:
            if lexeme in data_dict['LEXEMAS'][token]:
                output_tokens.append(f'TXT{entry_number}-{index + 1}: {token}')
                token_found = True
                break
        
        if not token_found:
            new_token = prompt_for_token(lexeme)
            if new_token == 'ERROR_LX':
                print(f"Lexeme '{lexeme}' identified as lexical error.")
            if new_token not in data_dict['TOKEN']:
                data_dict['TOKEN'].append(new_token)
            data_dict['LEXEMAS'][new_token].append(lexeme)
            output_tokens.append(f'TXT{entry_number}-{index + 1}: {new_token}')
            new_lexemes.add(lexeme)

    return output_tokens, found_lexemes, new_lexemes

# Function to save data dictionary to a JSON file
def save_data_dict(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data_dict, file, ensure_ascii=False, indent=4)
    print("Data dictionary saved successfully.")

# Function to generate the output file for the syntactic analyzer
def generate_output_file(file_path, output_tokens):
    with open(file_path, 'w', encoding='utf-8') as file:
        for token_info in output_tokens:
            file.write(f"{token_info}\n")
    print("Output file generated successfully.")

# Function to display statistical information
def display_statistics(found_lexemes, new_lexemes):
    total_lexemes = len(found_lexemes)
    unprocessed_lexemes = len(new_lexemes)
    processed_lexemes = total_lexemes - unprocessed_lexemes

    print("----------------------------------------------------")
    print(f"Total lexemes in current text: {total_lexemes}")
    print(f"Processed lexemes: {processed_lexemes} ({(processed_lexemes / total_lexemes) * 100:.2f}%)")
    print(f"Unprocessed lexemes: {unprocessed_lexemes} ({(unprocessed_lexemes / total_lexemes) * 100:.2f}%)")
    print("----------------------------------------------------")

    for token in data_dict['TOKEN']:
        print(f"{token}: {len(data_dict['LEXEMAS'][token])} lexemes")

# Main function to execute the tokenizer
def main():
    input_file = 'input.txt'  # Replace with the path to your input file
    data_dict_file = 'data_dict.json'
    output_file = 'output.txt'
    print("**----------------------------------------------------**")
    print("Inicio del programa")
    print("**----------------------------------------------------**")
    
    use_predefined_patterns = input("Do you want to use predefined lexemes? (yes/no): ").strip().lower() == 'yes'
    
    if use_predefined_patterns:
        initialize_with_lexemes()
        print("Initialized data dictionary with predefined lexemes.")
    
    if load_data_dict(data_dict_file):
        print("Loaded existing data dictionary.")
    else:
        print("No existing data dictionary found. Starting with a new one.")

    entry_number = 1  # This should be incremented for each new file processed

    output_tokens, found_lexemes, new_lexemes = tokenize_text(input_file, entry_number)
    save_data_dict(data_dict_file)
    generate_output_file(output_file, output_tokens)
    display_statistics(found_lexemes, new_lexemes)

if __name__ == "__main__":
    main()
