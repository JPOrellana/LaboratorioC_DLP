from lexer import Lexer, realizar_sustituciones, sustituir_y_construir_rule, convertir_rangos, aplicar_sustituciones_con_rangos_expandidos
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
                texto_con_rangos = convertir_rangos(input_text)
                print("\n===================================================")
                print("|                 Let con rangos                  |")
                print("===================================================")
                print(texto_con_rangos)


                texto_procesado = aplicar_sustituciones_con_rangos_expandidos(input_text)
                print("\n===================================================")
                print("|       Realizando sustituciones con rangos       |")
                print("===================================================")
                print(texto_procesado)


        except FileNotFoundError:
            print("==========================================================================")
            print(f"               ⚠  El archivo {file_path} no se encontró ⚠               ")
            print("==========================================================================")
    else:
        print("==========================================================================")
        print("|                  ⚠  No ingresó dirección del .yal ⚠                    |")
        print("| Para ejecutar deberá ingresar la ruta del .yal de la siguiente manera: |")
        print("|        ... Laboratorio C>python lexical_analyzer.py 'slr-1.yal'        |")
        print("==========================================================================")

if __name__ == "__main__":
    main()



                