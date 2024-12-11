import re
import sys
import math
import toml
from typing import List, Dict


def parse_constants(lines: List[str]) -> Dict[str, float]:
    """Разбираем все константы и вычисляем их значения."""
    constants = {}

    for line in lines:
        # Пропускаем пустые строки и комментарии
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("set"):  # Set оператор
            match = re.match(r"set\s+([_a-zA-Z]+)\s*=\s*(.+)", line)
            if not match:
                raise SyntaxError(f"Некорректное объявление константы: {line}")
            name, value = match.groups()

            if value.startswith("![") and value.endswith("]"):  # Выражение для вычисления
                expression = value[2:-1].split()
                result = evaluate_expression(expression, constants)
                constants[name] = result
            else:  # Простое значение
                if is_float(value):
                    constants[name] = float(value)
                elif value.isdigit():
                    constants[name] = int(value)
                else:
                    raise ValueError(f"Некорректное значение константы: {value}")

        elif "=" in line:  # Вложенные массивы или другие слова
            key, value = map(str.strip, line.split("=", 1))
            if value.startswith("{") and value.endswith("}"):
                constants[key] = parse_array(value)
            else:
                constants[key] = value

    return constants


def parse_array(array_text: str) -> List[float]:
    """Парсинг массивов: { val. val. ... }"""
    array_text = array_text.strip("{}")
    values = [float(x) for x in array_text.split(".") if x.strip()]
    return values


def evaluate_expression(expression: List[str], constants: Dict[str, float]) -> float:
    """Вычисление постфиксной формы с поддержкой операций +, -, *, sqrt."""
    stack = []
    for token in expression:
        if token in constants:
            stack.append(constants[token])
        elif is_float(token):
            stack.append(float(token))
        elif token == "+":
            b, a = stack.pop(), stack.pop()
            stack.append(a + b)
        elif token == "-":
            b, a = stack.pop(), stack.pop()
            stack.append(a - b)
        elif token == "*":
            b, a = stack.pop(), stack.pop()
            stack.append(a * b)
        elif token == "sqrt":
            a = stack.pop()
            stack.append(math.sqrt(a))
        else:
            raise ValueError(f"Неизвестный токен в выражении: {token}")

    if len(stack) != 1:
        raise ValueError("Некорректное выражение")
    return stack.pop()


def is_float(value: str) -> bool:
    """Проверяем, является ли значение числом."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def main():
    if len(sys.argv) != 2:
        print("Использование: python tool.py <output_file.toml>")
        sys.exit(1)

    print("Скрипт начал свою работу")

    output_file = sys.argv[1]

    # Считываем входные данные из stdin
    print("Введите входной текст (Ctrl+D для завершения):")
    input_lines = sys.stdin.read().splitlines()

    try:
        # Парсим данные и вычисляем выражения
        constants = parse_constants(input_lines)

        # Исправляем массивы для TOML
        constants["graph"] = [x for x in constants.get("graph", []) if x != 0.0]
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

    # Преобразуем в формат TOML
    toml_data = toml.dumps(constants)

    # Записываем в файл
    with open(output_file, "w") as f:
        f.write(toml_data)

    print(f"Файл TOML успешно создан: {output_file}")


if __name__ == "__main__":
    main()
