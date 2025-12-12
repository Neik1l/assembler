# src/assembler.py

import sys
import csv
import os

OPCODE_MAP = {
    "LOAD": 57,
    "READ": 102,
    "WRITE": 112,
    "BSWAP": 5
}

def parse_source(filepath):
    instructions = []
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            opcode = row["opcode"].strip().upper()
            if opcode not in OPCODE_MAP:
                raise ValueError(f"Неизвестная команда: {opcode}")
            operand = row.get("operand", "").strip()
            operand_val = int(operand) if operand else None

            # Валидация операндов
            if opcode == "LOAD":
                if not (0 <= operand_val <= (1 << 31) - 1):
                    raise ValueError(f"LOAD operand out of range: {operand_val}")
            elif opcode == "WRITE":
                if not (0 <= operand_val <= 4095):  # 12 бит (7–19 = 13 бит, но 0–4095 = 12 бит)
                    raise ValueError(f"WRITE address out of range: {operand_val}")

            instructions.append({"opcode": opcode, "operand": operand_val})
    return instructions

def print_intermediate(instructions):
    for instr in instructions:
        opcode_name = instr["opcode"]
        operand = instr["operand"]
        a = OPCODE_MAP[opcode_name]
        if operand is not None:
            print(f"A={a}, B={operand}")
        else:
            print(f"A={a}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python assembler.py <input.csv> <output.bin> [--test]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    test_mode = "--test" in sys.argv

    if not os.path.exists(input_path):
        print(f"Файл не найден: {input_path}")
        sys.exit(1)

    instructions = parse_source(input_path)

    if test_mode:
        print_intermediate(instructions)

    # На этом этапе не записываем бинарник — только промежуточное представление
    # Сохраняем инструкции как внутреннюю структуру (для Этапа 2 будем использовать её)

    # Сохраняем во временный файл или передаём дальше (в данном случае просто подтверждаем)
    print(f"Успешно обработано {len(instructions)} команд.")

if __name__ == "__main__":
    main()