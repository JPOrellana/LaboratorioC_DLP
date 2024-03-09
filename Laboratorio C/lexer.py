import re

class Lexer:
    def __init__(self):
        self.TOKENS = {
            "SEPARATOR": re.compile(r'[{}\[\]();,]'),
            "OPERATOR": re.compile(r'[=+\-*/.?/#|^><:]'),
            "WHITESPACE": re.compile(r'\s+'),
            "NUMBER": re.compile(r'\d+(\.\d+)?'),
            "PLUS": re.compile(r'\+'),
            "MINUS": re.compile(r'-'),
            "TIMES": re.compile(r'\*'),
            "DIVIDE": re.compile(r'/'),
            "LPAREN": re.compile(r'\('),
            "RPAREN": re.compile(r'\)'),
            "KEYWORD": re.compile(r'\b(let|return|rule)\b'), # Recognize 'let', 'return', and 'rule' as keywords
            "IDENTIFIER": re.compile(r'[a-zA-Z_]\w*'),
            "LITERAL": re.compile(r"'([^']*)'|\"([^\"]*)\""),
            "EOF": re.compile(r'<<EOF>>'),
        }
        self.variables = {}

    def tokenize(self, input_text):
        tokens = []
        position = 0
        input_text = re.sub(r'\(\*.*?\*\)', '', input_text, flags=re.DOTALL)

        while position < len(input_text):
            current_text = input_text[position:]

            match = re.match(r'\s+', current_text)
            if match:
                position += match.end()
                continue

            matched = False
            for token_type, regex in self.TOKENS.items():
                match = regex.match(current_text)
                if match:
                    value = match.group()
                    tokens.append((token_type, value, position))
                    position += match.end()
                    matched = True
                    break

            if not matched:
                print(f"Unknown token at position {position}")
                position += 1

        return tokens

def realizar_sustituciones(identificador_values):
    sustituidos = identificador_values.copy()

    def reemplazar(match):
        target_identificador = match.group(0)
        if target_identificador in sustituidos:
            # Directamente retornamos el valor asociado sin modificarlo
            return sustituidos[target_identificador]
        return target_identificador

    for identificador, valor in list(identificador_values.items()):
        for target_identificador, target_valor in sustituidos.items():
            pattern = r'\b' + re.escape(target_identificador) + r'\b'
            sustituido = re.sub(pattern, reemplazar, valor)
            if sustituido != valor:
                sustituidos[identificador] = sustituido
                valor = sustituido

    return sustituidos


def sustituir_y_construir_rule(input_text, sustituidos):
    # Buscar la definición de 'rule tokens'
    rule_pattern = re.compile(r'rule\s+tokens\s*=(.*?)(?=\n\S|\Z)', re.DOTALL)
    match = rule_pattern.search(input_text)
    if not match:
        return "No se encontró la definición de 'rule tokens'."

    rule_body = match.group(1).strip()
    # Eliminar contenido dentro de {} y (* *)
    rule_body = re.sub(r'\{.*?\}', '', rule_body)
    rule_body = re.sub(r'\(\*.*?\*\)', '', rule_body)
    # Dividir el cuerpo de la regla en partes basadas en '|'
    partes_rule = rule_body.split('|')

    partes_sustituidas = []
    for parte in partes_rule:
        parte = parte.strip()
        # Sustituir los identificadores en la parte con los valores de 'sustituidos'
        for identificador, valor in sustituidos.items():
            parte = re.sub(r'\b' + re.escape(identificador) + r'\b', lambda m: valor, parte)
        if parte:  # Asegurar que la parte no esté vacía después de la limpieza
            partes_sustituidas.append(parte)

    # Reconstruir la regla con las partes sustituidas
    rule_sustituida = '|'.join(partes_sustituidas)
    # Limpiar para que coincida con el formato deseado
    rule_sustituida = rule_sustituida.replace("  ", " ").replace('\n', '').replace("||", "|").strip('|')

    return f"tokens: {rule_sustituida}"



def convertir_rangos(input_text):
    # Primero, eliminar comentarios
    texto_sin_comentarios = re.sub(r'\(\*.*?\*\)', '', input_text, flags=re.DOTALL)

    def expandir_rango(match):
        inicio, fin = match.groups()
        # Generar el rango expandido entre los dos caracteres sin añadir paréntesis adicionales aquí
        rango_expandido = '|'.join(chr(c) for c in range(ord(inicio), ord(fin) + 1))
        return rango_expandido

    def procesar_definicion(linea):
        if not linea.strip().startswith('let'):
            return None  # Esto omite líneas que no empiezan con 'let'
        # Convertir rangos; esta operación no añade paréntesis adicionales por sí misma
        valores_convertidos = re.sub(r"'(.)'-'(.)'", expandir_rango, linea)
        # Cambiar corchetes por paréntesis solo una vez, después de expandir todos los rangos
        valores_convertidos = valores_convertidos.replace('[', '(').replace(']', ')')
        return valores_convertidos

    # Aplicar transformaciones solo a las líneas 'let' y omitir sección 'rule'
    lineas_procesadas = filter(None, (procesar_definicion(linea) for linea in texto_sin_comentarios.splitlines()))
    texto_final = '\n'.join(lineas_procesadas)

    # Omitir cualquier línea que empiece con 'rule' en el resultado final
    texto_final_sin_rule = '\n'.join(linea for linea in texto_final.splitlines() if not linea.startswith('rule'))

    return texto_final_sin_rule



def aplicar_sustituciones_con_rangos_expandidos(input_text):
    # Primero, eliminamos los comentarios y la sección 'rule'
    texto_sin_comentarios_ni_rule = re.sub(r'\(\*.*?\*\)', '', input_text, flags=re.DOTALL)
    texto_sin_comentarios_ni_rule = re.sub(r'rule\s+tokens\s*=.*', '', texto_sin_comentarios_ni_rule, flags=re.DOTALL)

    # Luego, aplicamos la expansión de rangos
    texto_con_rangos_expandidos = convertir_rangos(texto_sin_comentarios_ni_rule)

    # Ahora, extraemos solo las definiciones 'let'
    definiciones_let = re.findall(r"let\s+(\w+)\s*=\s*(.*)", texto_con_rangos_expandidos)

    # Convertimos las definiciones en un diccionario para facilitar la sustitución
    sustituciones = {nombre: valor for nombre, valor in definiciones_let}

    # Función para sustituir los identificadores por sus valores en el texto
    def sustituir_identificador_por_valor(match):
        identificador = match.group(1)  # Capturamos el nombre del identificador
        return sustituciones.get(identificador, identificador)  # Sustituimos por su valor, si existe

    # Finalmente, aplicamos las sustituciones a cada definición 'let'
    resultado = '\n'.join([
        f"let {nombre} = {re.sub(r'\b(\w+)\b', sustituir_identificador_por_valor, valor)}"
        for nombre, valor in definiciones_let
    ])

    return resultado










