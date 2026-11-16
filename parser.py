#!/usr/bin/env python3
"""Парсер системных процессов команды `ps aux`."""

import subprocess
from collections import Counter
from datetime import datetime


USER = 0
CPU = 2
MEM = 3
COMMAND = 10


def get_processes() -> list[str]:
    """Возвращает список строк с информацией о процессах."""
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().splitlines()[1:]


def parse_process(line: str) -> tuple[str, float, float, str]:
    """Разбирает одну строку вывода `ps aux`."""
    parts = line.split(None, COMMAND)
    user = parts[USER]
    cpu = float(parts[CPU].replace(",", "."))
    mem = float(parts[MEM].replace(",", "."))
    command = parts[COMMAND]
    return user, cpu, mem, command


def short_name(command: str) -> str:
    """Возвращает имя процесса (первые 20 символов команды)."""
    name = command.split()[0].split("/")[-1]
    return name[:20]


def build_report(processes: list[str]) -> str:
    """Формирует текстовый отчёт по процессам."""
    users = Counter()
    total_cpu = 0.0
    total_mem = 0.0
    max_cpu = (0.0, "")
    max_mem = (0.0, "")

    for line in processes:
        user, cpu, mem, command = parse_process(line)
        users[user] += 1
        total_cpu += cpu
        total_mem += mem

        name = short_name(command)
        if cpu > max_cpu[0]:
            max_cpu = (cpu, name)
        if mem > max_mem[0]:
            max_mem = (mem, name)

    user_list = "', '".join(users.keys())
    lines = [
        "Отчёт о состоянии системы:",
        f"Пользователи системы: '{user_list}'",
        f"Процессов запущено: {len(processes)}",
        "",
        "Пользовательских процессов:",
    ]
    for user, count in users.most_common():
        lines.append(f"{user}: {count}")

    lines += [
        "",
        f"Всего памяти используется: {total_mem:.1f}%",
        f"Всего CPU используется: {total_cpu:.1f}%",
        f"Больше всего памяти использует: ({max_mem[0]:.1f}%, {max_mem[1]})",
        f"Больше всего CPU использует: ({max_cpu[0]:.1f}%, {max_cpu[1]})",
    ]
    return "\n".join(lines)


def save_report(report: str) -> str:
    """Сохраняет отчёт в файл с именем по текущей дате и времени."""
    filename = datetime.now().strftime("%d-%m-%Y-%H:%M-scan.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    return filename


def main() -> None:
    processes = get_processes()
    report = build_report(processes)
    print(report)
    filename = save_report(report)
    print(f"\nОтчёт сохранён в файл: {filename}")


if __name__ == "__main__":
    main()
