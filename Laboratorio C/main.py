from lexer import Lexer, realizar_sustituciones, sustituir_y_construir_rule, convertir_rangos
import re
import sys

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r') as file:
                input_text = file.read()
                lexer = Lexer()

                # Extraer definiciones de variables
                let_pattern = re.compile(r'let\s+([a-zA-Z_]\w*)\s*=\s*(.*)')
                identificador_values = dict(let_pattern.findall(input_text))

                # Realizar sustituciones
                sustituidos = realizar_sustituciones(identificador_values)

                print("===================================================")
                print("|            Scanner del Archivo .yal             |")
                print("|-------------------------------------------------|")
                print("|       En el siguiente apartado se mostrará      |")
                print("| cómo se evaluó cada elemento de nuestro archivo |")
                print("===================================================")

                tokens = lexer.tokenize(input_text)  # Tokenizar el texto original
                
                # Imprimir los tokens resultantes
                for token in tokens:
                    print(f"Token: {token[0]}, Value: {token[1]}")

                print("\n===================================================")
                print("|            Realizando Sustituciones             |")
                print("===================================================")
                for identificador, valor in sustituidos.items():
                    print(f"{identificador}: {valor}")
                rule_result = sustituir_y_construir_rule(input_text, sustituidos)
                print(rule_result)


                # Convertir rangos en las definiciones 'let' y mostrar el resultado
                print("\n===================================================")
                print("|            Let con rangos             |")
                print("===================================================")
                texto_con_rangos_convertidos = convertir_rangos(input_text)
                print(texto_con_rangos_convertidos)



        except FileNotFoundError:
            print(f"El archivo {file_path} no se encontró.")
    else:
        print("Por favor, especifica el path del archivo .yal como argumento.")

if __name__ == "__main__":
    main()
