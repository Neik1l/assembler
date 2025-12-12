# src/assembler.py (обновлённый)

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

            if opcode == "LOAD":
                if not (0 <= operand_val <= (1 << 31) - 1):
                    raise ValueError(f"LOAD operand out of range: {operand_val}")
            elif opcode == "WRITE":
                if not (0 <= operand_val <= 4095):
                    raise ValueError(f"WRITE address out of range: {operand_val}")

            instructions.append({"opcode": opcode, "operand": operand_val})
    return instructions

def encode_instruction(instr):
    opcode = instr["opcode"]
    operand = instr["operand"]
    a = OPCODE_MAP[opcode]

    if opcode == "LOAD":
        value = a | (operand << 7)
        return value.to_bytes(5, byteorder='little')
    elif opcode == "READ":
        return bytes([a])
    elif opcode == "WRITE":
        value = a | (operand << 7)
        return value.to_bytes(3, byteorder='little')
    elif opcode == "BSWAP":
        return bytes([a])
    else:
        raise ValueError(f"Неизвестная команда: {opcode}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python assembler.py <input.csv> <output.bin> [--test]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    test_mode = "--test" in sys.argv

    instructions = parse_source(input_path)

    binary = b""
    for instr in instructions:
        binary += encode_instruction(instr)

    with open(output_path, "wb") as f:
        f.write(binary)

    print(f"Успешно ассемблировано {len(instructions)} команд.")

    if test_mode:
        # Вывод в формате: 0xB9, 0x93, ...
        bytes_list = [f"0x{b:02X}" for b in binary]
        print(", ".join(bytes_list))

if __name__ == "__main__":
    main()