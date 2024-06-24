import re
import json
from collections import defaultdict

# Estructura del diccionario de datos
data_dict = {
    'POSICIONES': defaultdict(lambda: defaultdict(list)),
    'num_files_processed': 0,  # Número de archivos procesados
    'predefined_lexemes_used':
    False  # Si se han utilizado los lexemas predefinidos
}

# Lexemas predefinidos para los tokens
predefined_lexemes = {
    'ARTICULO': ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas'],
    'SUSTANTIVO': ['Nietzsche', 'temas', 'libro', 'mundo', 'persona'],
    'VERBO':
    ['escribir', 'leer', 'ser', 'haber', 'ir', 'escribió', 'escriben'],
    'ADJETIVO': ['grande', 'pequeño', 'bueno', 'malo', 'nuevo', 'viejo'],
    'ADVERBIO': ['rápidamente', 'lentamente', 'bien', 'mal', 'cerca', 'lejos'],
    'OTROS': ['sobre', 'con', 'sin', 'en', 'por', 'para', 'y', 'o', 'a', 'de'],
    'ERROR_LX': []
}


# Función para inicializar el diccionario de datos con lexemas predefinidos
def initialize_with_lexemes():
    for token, lexemes in predefined_lexemes.items():
        for lexeme in lexemes:
            data_dict['POSICIONES'][token][lexeme.lower()] = []
    data_dict['predefined_lexemes_used'] = True


# Función para cargar el diccionario de datos existente
def load_data_dict(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            loaded_dict = json.load(file)
            data_dict.update(loaded_dict)
            # Convertir la estructura del diccionario cargado a defaultdict
            data_dict['POSICIONES'] = defaultdict(
                lambda: defaultdict(list), {
                    token:
                    defaultdict(
                        list, {
                            lexeme.lower(): positions
                            for lexeme, positions in lexemes.items()
                        })
                    for token, lexemes in data_dict['POSICIONES'].items()
                })
            print("Diccionario de datos cargado exitosamente.")
            return True
    except FileNotFoundError:
        print("Archivo del diccionario de datos no encontrado.")
        return False
    except KeyError as e:
        print(f"Error de clave: {e}")
        return False


# Función para pedir al usuario que asigne un token
def prompt_for_token(lexeme):
    token_options = {
        1: 'ARTICULO',
        2: 'SUSTANTIVO',
        3: 'VERBO',
        4: 'ADJETIVO',
        5: 'ADVERBIO',
        6: 'OTROS',
        7: 'ERROR_LX'  # Añadir ERROR_LX como opción
    }
    while True:
        print(f"\nPor favor, asigne un token a este lexema: {lexeme}")
        for number, token in token_options.items():
            print(f"{number} - {token}")
        try:
            choice = int(
                input("Ingrese el número correspondiente a su elección: "))
            if choice in token_options:
                return token_options[choice]
            else:
                print("Opción incorrecta, por favor ingrese un número válido.")
        except ValueError:
            print("Entrada no válida, por favor ingrese un número.")


# Función para leer y tokenizar el texto de entrada
def tokenize_text(file_path, entry_number):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    lexemes = re.split(r'\s+|(?<!\d)[.,;:!?](?!\d)', text)
    found_lexemes = set()
    new_lexemes = set()

    posicion = 1

    for lexeme in lexemes:
        lexeme = lexeme.strip().lower()  # Convertir lexema a minúsculas
        if not lexeme:
            continue

        found_lexemes.add(lexeme)
        token_found = False

        for token in data_dict['POSICIONES']:
            if lexeme in data_dict['POSICIONES'][token]:
                data_dict['POSICIONES'][token][lexeme].append(
                    f'TXT{entry_number}-{posicion}')
                token_found = True
                break

        if not token_found:
            new_token = prompt_for_token(lexeme)
            if new_token == 'ERROR_LX':
                print(f"Lexema '{lexeme}' identificado como error léxico.")
            if new_token not in data_dict['POSICIONES']:
                data_dict['POSICIONES'][new_token] = defaultdict(list)
            data_dict['POSICIONES'][new_token][lexeme].append(
                f'TXT{entry_number}-{posicion}')
            new_lexemes.add(lexeme)

        posicion += 1

    return found_lexemes, new_lexemes


# Función para guardar el diccionario de datos en un archivo JSON
def save_data_dict(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data_dict, file, ensure_ascii=False, indent=4)
    print("Diccionario de datos guardado exitosamente.")


# Función para generar el archivo de salida para el analizador sintáctico
def generate_output_file(file_path, entry_number):
    output_data = {
        token: {
            lexeme: [
                pos for pos in positions
                if pos.startswith(f'TXT{entry_number}-')
            ]
            for lexeme, positions in lexemes.items() if any(
                pos.startswith(f'TXT{entry_number}-') for pos in positions)
        }
        for token, lexemes in data_dict['POSICIONES'].items()
    }
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(output_data, file, ensure_ascii=False, indent=4)
    print("Archivo de salida generado exitosamente.")


# Función para mostrar información estadística
def display_statistics(found_lexemes, new_lexemes, prev_lexemes_count,
                       new_lexemes_count):
    total_lexemes = len(found_lexemes)
    unprocessed_lexemes = len(new_lexemes)
    processed_lexemes = total_lexemes - unprocessed_lexemes

    print("\n----------------------------------------------------")
    print(f"Total de lexemas en el texto actual: {total_lexemes}")
    print(
        f"Lexemas procesados: {processed_lexemes} ({(processed_lexemes / total_lexemes) * 100:.2f}%)"
    )
    print(
        f"Lexemas no procesados: {unprocessed_lexemes} ({(unprocessed_lexemes / total_lexemes) * 100:.2f}%)"
    )
    print("----------------------------------------------------")

    for token in data_dict['POSICIONES']:
        print(f"\n{token}:")
        print(
            f"  Lexemas antes del procesamiento: {prev_lexemes_count[token]}")
        print(
            f"  Lexemas añadidos en este archivo: {new_lexemes_count[token]}")
        print(f"  Total de lexemas: {len(data_dict['POSICIONES'][token])}")


# Función principal para ejecutar el tokenizador
def main():
    data_dict_file = 'data_dict.json'

    if load_data_dict(data_dict_file):
        print("Diccionario de datos cargado exitosamente.")
    else:
        print(
            "No se encontró el diccionario de datos existente. Comenzando con uno nuevo."
        )

    if data_dict['num_files_processed'] == 0 and not data_dict[
            'predefined_lexemes_used']:
        use_predefined_patterns = input(
            "¿Desea usar lexemas predefinidos? (sí/no): ").strip().lower(
            ) == 'sí'
        if use_predefined_patterns:
            initialize_with_lexemes()
            print(
                "Diccionario de datos inicializado con lexemas predefinidos.")
    else:
        print(
            "Los lexemas predefinidos ya han sido utilizados o no es la primera iteración. Omitiendo inicialización."
        )

    input_file = input("Ingrese la ruta del archivo de entrada: ").strip(
    )  # Obtener la ruta del archivo de entrada del usuario
    entry_number = data_dict[
        'num_files_processed'] + 1  # Incrementar el número de entrada basado en los archivos procesados
    output_file = f'output{entry_number}.txt'  # Nombre del archivo de salida basado en el número de entrada

    # Contar la cantidad de lexemas antes del procesamiento
    prev_lexemes_count = {
        token: len(lexemes)
        for token, lexemes in data_dict['POSICIONES'].items()
    }

    found_lexemes, new_lexemes = tokenize_text(input_file, entry_number)

    # Contar la cantidad de lexemas después del procesamiento
    new_lexemes_count = {
        token: len(data_dict['POSICIONES'][token]) - prev_lexemes_count[token]
        for token in data_dict['POSICIONES']
    }

    save_data_dict(data_dict_file)
    generate_output_file(output_file, entry_number)
    display_statistics(found_lexemes, new_lexemes, prev_lexemes_count,
                       new_lexemes_count)

    data_dict[
        'num_files_processed'] = entry_number  # Actualizar el número de archivos procesados
    save_data_dict(
        data_dict_file)  # Guardar el diccionario de datos actualizado


if __name__ == "__main__":
    main()
import re
import json
from collections import defaultdict

# Estructura del diccionario de datos
data_dict = {
    'POSICIONES': defaultdict(lambda: defaultdict(list)),
    'num_files_processed': 0,  # Número de archivos procesados
    'predefined_lexemes_used':
    False  # Si se han utilizado los lexemas predefinidos
}

# Lexemas predefinidos para los tokens
predefined_lexemes = {
    'ARTICULO': ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas'],
    'SUSTANTIVO': ['Nietzsche', 'temas', 'libro', 'mundo', 'persona'],
    'VERBO':
    ['escribir', 'leer', 'ser', 'haber', 'ir', 'escribió', 'escriben'],
    'ADJETIVO': ['grande', 'pequeño', 'bueno', 'malo', 'nuevo', 'viejo'],
    'ADVERBIO': ['rápidamente', 'lentamente', 'bien', 'mal', 'cerca', 'lejos'],
    'OTROS': ['sobre', 'con', 'sin', 'en', 'por', 'para', 'y', 'o', 'a', 'de'],
    'ERROR_LX': []
}


# Función para inicializar el diccionario de datos con lexemas predefinidos
def initialize_with_lexemes():
    for token, lexemes in predefined_lexemes.items():
        for lexeme in lexemes:
            data_dict['POSICIONES'][token][lexeme.lower()] = []
    data_dict['predefined_lexemes_used'] = True


# Función para cargar el diccionario de datos existente
def load_data_dict(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            loaded_dict = json.load(file)
            data_dict.update(loaded_dict)
            # Convertir la estructura del diccionario cargado a defaultdict
            data_dict['POSICIONES'] = defaultdict(
                lambda: defaultdict(list), {
                    token:
                    defaultdict(
                        list, {
                            lexeme.lower(): positions
                            for lexeme, positions in lexemes.items()
                        })
                    for token, lexemes in data_dict['POSICIONES'].items()
                })
            print("Diccionario de datos cargado exitosamente.")
            return True
    except FileNotFoundError:
        print("Archivo del diccionario de datos no encontrado.")
        return False
    except KeyError as e:
        print(f"Error de clave: {e}")
        return False


# Función para pedir al usuario que asigne un token
def prompt_for_token(lexeme):
    token_options = {
        1: 'ARTICULO',
        2: 'SUSTANTIVO',
        3: 'VERBO',
        4: 'ADJETIVO',
        5: 'ADVERBIO',
        6: 'OTROS',
        7: 'ERROR_LX'  # Añadir ERROR_LX como opción
    }
    while True:
        print(f"\nPor favor, asigne un token a este lexema: {lexeme}")
        for number, token in token_options.items():
            print(f"{number} - {token}")
        try:
            choice = int(
                input("Ingrese el número correspondiente a su elección: "))
            if choice in token_options:
                return token_options[choice]
            else:
                print("Opción incorrecta, por favor ingrese un número válido.")
        except ValueError:
            print("Entrada no válida, por favor ingrese un número.")


# Función para leer y tokenizar el texto de entrada
def tokenize_text(file_path, entry_number):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    lexemes = re.split(r'\s+|(?<!\d)[.,;:!?](?!\d)', text)
    found_lexemes = set()
    new_lexemes = set()

    posicion = 1

    for lexeme in lexemes:
        lexeme = lexeme.strip().lower()  # Convertir lexema a minúsculas
        if not lexeme:
            continue

        found_lexemes.add(lexeme)
        token_found = False

        for token in data_dict['POSICIONES']:
            if lexeme in data_dict['POSICIONES'][token]:
                data_dict['POSICIONES'][token][lexeme].append(
                    f'TXT{entry_number}-{posicion}')
                token_found = True
                break

        if not token_found:
            new_token = prompt_for_token(lexeme)
            if new_token == 'ERROR_LX':
                print(f"Lexema '{lexeme}' identificado como error léxico.")
            if new_token not in data_dict['POSICIONES']:
                data_dict['POSICIONES'][new_token] = defaultdict(list)
            data_dict['POSICIONES'][new_token][lexeme].append(
                f'TXT{entry_number}-{posicion}')
            new_lexemes.add(lexeme)

        posicion += 1

    return found_lexemes, new_lexemes


# Función para guardar el diccionario de datos en un archivo JSON
def save_data_dict(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data_dict, file, ensure_ascii=False, indent=4)
    print("Diccionario de datos guardado exitosamente.")


# Función para generar el archivo de salida para el analizador sintáctico
def generate_output_file(file_path, entry_number):
    output_data = {
        token: {
            lexeme: [
                pos for pos in positions
                if pos.startswith(f'TXT{entry_number}-')
            ]
            for lexeme, positions in lexemes.items() if any(
                pos.startswith(f'TXT{entry_number}-') for pos in positions)
        }
        for token, lexemes in data_dict['POSICIONES'].items()
    }
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(output_data, file, ensure_ascii=False, indent=4)
    print("Archivo de salida generado exitosamente.")


# Función para mostrar información estadística
def display_statistics(found_lexemes, new_lexemes, prev_lexemes_count,
                       new_lexemes_count):
    total_lexemes = len(found_lexemes)
    unprocessed_lexemes = len(new_lexemes)
    processed_lexemes = total_lexemes - unprocessed_lexemes

    print("\n----------------------------------------------------")
    print(f"Total de lexemas en el texto actual: {total_lexemes}")
    print(
        f"Lexemas procesados: {processed_lexemes} ({(processed_lexemes / total_lexemes) * 100:.2f}%)"
    )
    print(
        f"Lexemas no procesados: {unprocessed_lexemes} ({(unprocessed_lexemes / total_lexemes) * 100:.2f}%)"
    )
    print("----------------------------------------------------")

    for token in data_dict['POSICIONES']:
        print(f"\n{token}:")
        print(
            f"  Lexemas antes del procesamiento: {prev_lexemes_count[token]}")
        print(
            f"  Lexemas añadidos en este archivo: {new_lexemes_count[token]}")
        print(f"  Total de lexemas: {len(data_dict['POSICIONES'][token])}")


# Función principal para ejecutar el tokenizador
def main():
    data_dict_file = 'data_dict.json'

    if load_data_dict(data_dict_file):
        print("Diccionario de datos cargado exitosamente.")
    else:
        print(
            "No se encontró el diccionario de datos existente. Comenzando con uno nuevo."
        )

    if data_dict['num_files_processed'] == 0 and not data_dict[
            'predefined_lexemes_used']:
        use_predefined_patterns = input(
            "¿Desea usar lexemas predefinidos? (sí/no): ").strip().lower(
            ) == 'sí'
        if use_predefined_patterns:
            initialize_with_lexemes()
            print(
                "Diccionario de datos inicializado con lexemas predefinidos.")
    else:
        print(
            "Los lexemas predefinidos ya han sido utilizados o no es la primera iteración. Omitiendo inicialización."
        )

    input_file = input("Ingrese la ruta del archivo de entrada: ").strip(
    )  # Obtener la ruta del archivo de entrada del usuario
    entry_number = data_dict[
        'num_files_processed'] + 1  # Incrementar el número de entrada basado en los archivos procesados
    output_file = f'output{entry_number}.txt'  # Nombre del archivo de salida basado en el número de entrada

    # Contar la cantidad de lexemas antes del procesamiento
    prev_lexemes_count = {
        token: len(lexemes)
        for token, lexemes in data_dict['POSICIONES'].items()
    }

    found_lexemes, new_lexemes = tokenize_text(input_file, entry_number)

    # Contar la cantidad de lexemas después del procesamiento
    new_lexemes_count = {
        token: len(data_dict['POSICIONES'][token]) - prev_lexemes_count[token]
        for token in data_dict['POSICIONES']
    }

    save_data_dict(data_dict_file)
    generate_output_file(output_file, entry_number)
    display_statistics(found_lexemes, new_lexemes, prev_lexemes_count,
                       new_lexemes_count)

    data_dict[
        'num_files_processed'] = entry_number  # Actualizar el número de archivos procesados
    save_data_dict(
        data_dict_file)  # Guardar el diccionario de datos actualizado


if __name__ == "__main__":
    main()
