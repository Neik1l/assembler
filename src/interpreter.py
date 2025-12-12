# src/interpreter.py

import sys
import json
import struct

# Размер памяти (64K ячеек по 4 байта — но в УВМ ячейка = 4 байта? Нет, в условии — просто "значение")
# Будем хранить как словарь: адрес → int (32-бит)
MEMORY_SIZE = 65536

def load_program(filepath):
    with open(filepath, "rb") as f:
        return f.read()

def decode_instruction(program, pc):
    if pc >= len(program):
        return None, pc

    # Читаем первый байт, чтобы определить opcode
    a = program[pc] & 0x7F  # младшие 7 бит

    if a == 57:  # LOAD
        if pc + 5 > len(program):
            raise ValueError("Недостаточно байт для LOAD")
        word = int.from_bytes(program[pc:pc+5], byteorder='little')
        operand = (word >> 7) & ((1 << 31) - 1)
        return ("LOAD", operand), pc + 5
    elif a == 102:  # READ
        return ("READ", None), pc + 1
    elif a == 112:  # WRITE
        if pc + 3 > len(program):
            raise ValueError("Недостаточно байт для WRITE")
        word = int.from_bytes(program[pc:pc+3], byteorder='little')
        addr = (word >> 7) & 0x1FFF  # 13 бит, но по спецификации адрес 12 бит (0–4095)
        return ("WRITE", addr), pc + 3
    elif a == 5:  # BSWAP
        return ("BSWAP", None), pc + 1
    else:
        raise ValueError(f"Неизвестный opcode A={a} at PC={pc}")

def run(program, start_addr=0, end_addr=255):
    memory = [0] * MEMORY_SIZE  # простой массив
    acc = 0
    pc = 0

    while pc < len(program):
        instr, new_pc = decode_instruction(program, pc)
        if instr is None:
            break
        opcode, operand = instr
        pc = new_pc

        if opcode == "LOAD":
            acc = operand
        elif opcode == "READ":
            addr = acc
            if not (0 <= addr < MEMORY_SIZE):
                raise ValueError(f"READ: адрес вне диапазона: {addr}")
            acc = memory[addr]
        elif opcode == "WRITE":
            addr = operand
            if not (0 <= addr < MEMORY_SIZE):
                raise ValueError(f"WRITE: адрес вне диапазона: {addr}")
            memory[addr] = acc
        elif opcode == "BSWAP":
            # bswap для 32-битного целого
            acc_bytes = acc.to_bytes(4, byteorder='little', signed=False)
            swapped = int.from_bytes(acc_bytes, byteorder='big', signed=False)
            acc = swapped

    # Дамп памяти
    dump = {str(i): memory[i] for i in range(start_addr, min(end_addr + 1, MEMORY_SIZE))}
    return dump

def main():
    if len(sys.argv) < 4:
        print("Usage: python interpreter.py <program.bin> <dump.json> <start_addr> <end_addr>")
        sys.exit(1)

    prog_file = sys.argv[1]
    dump_file = sys.argv[2]
    start = int(sys.argv[3])
    end = int(sys.argv[4])

    program = load_program(prog_file)
    memory_dump = run(program, start, end)

    with open(dump_file, "w", encoding="utf-8") as f:
        json.dump(memory_dump, f, indent=2)

    print(f"Выполнено. Дамп памяти сохранён в {dump_file}")

if __name__ == "__main__":
    main()