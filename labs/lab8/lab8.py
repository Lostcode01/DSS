#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Графический интерфейс для лабораторной работы №8
Шифрование методом гаммирования с LCG
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading

# Импортируем классы из основной программы (предполагается, что файл с ними называется lab8.py)
# Если основной код находится в этом же файле, раскомментируйте классы ниже.
# Для примера предположим, что классы уже определены в текущем модуле.
# В реальном проекте замените импорт на from lab8 import LinearCongruentialGenerator, GammaCipher

# ----------------------------------------------------------------------
# Классы из основной программы (скопированы для самодостаточности)
# ----------------------------------------------------------------------

class LinearCongruentialGenerator:
    """Линейный конгруэнтный генератор псевдослучайных чисел"""
    def __init__(self, a=5, b=7, m=4096, seed=4003):
        self.a = a
        self.b = b
        self.m = m
        self.seed = seed
        self.current = seed
        self.history = [seed]

    def next(self):
        self.current = (self.a * self.current + self.b) % self.m
        self.history.append(self.current)
        return self.current

    def reset(self):
        self.current = self.seed
        self.history = [self.seed]

    def generate_sequence(self, length):
        self.reset()
        return [self.next() for _ in range(length)]

    def get_period(self):
        self.reset()
        seen = {}
        count = 0
        while True:
            val = self.next()
            if val in seen:
                return count - seen[val]
            seen[val] = count
            count += 1
            if count > self.m * 2:
                return count


class GammaCipher:
    """Шифр гаммирования с использованием LCG"""
    def __init__(self, a=5, b=7, m=4096, seed=4003):
        self.generator = LinearCongruentialGenerator(a, b, m, seed)
        self.a = a
        self.b = b
        self.m = m
        self.seed = seed

    def text_to_bytes(self, text):
        return text.encode('utf-8')

    def bytes_to_text(self, byte_data):
        return byte_data.decode('utf-8')

    def generate_gamma(self, length):
        self.generator.reset()
        gamma = bytearray()
        for _ in range(length):
            value = self.generator.next()
            gamma.append(value & 0xFF)
        return bytes(gamma)

    def encrypt(self, plaintext):
        plaintext_bytes = self.text_to_bytes(plaintext)
        gamma = self.generate_gamma(len(plaintext_bytes))
        ciphertext_bytes = bytearray()
        for i in range(len(plaintext_bytes)):
            ciphertext_bytes.append(plaintext_bytes[i] ^ gamma[i])
        return {
            'plaintext': plaintext,
            'ciphertext_hex': ciphertext_bytes.hex().upper(),
            'ciphertext_bytes': bytes(ciphertext_bytes),
            'gamma_hex': gamma.hex().upper(),
            'gamma': gamma,
            'length': len(plaintext_bytes),
            'parameters': {
                'a': self.a,
                'b': self.b,
                'm': self.m,
                'seed': self.seed
            }
        }

    def decrypt(self, ciphertext_hex):
        ciphertext_bytes = bytes.fromhex(ciphertext_hex)
        gamma = self.generate_gamma(len(ciphertext_bytes))
        plaintext_bytes = bytearray()
        for i in range(len(ciphertext_bytes)):
            plaintext_bytes.append(ciphertext_bytes[i] ^ gamma[i])
        try:
            plaintext = self.bytes_to_text(bytes(plaintext_bytes))
        except UnicodeDecodeError:
            plaintext = f"[Binary data] {plaintext_bytes.hex().upper()}"
        return {
            'plaintext': plaintext,
            'ciphertext_hex': ciphertext_hex,
            'gamma_hex': gamma.hex().upper(),
            'gamma': gamma,
            'length': len(ciphertext_bytes),
            'parameters': {
                'a': self.a,
                'b': self.b,
                'm': self.m,
                'seed': self.seed
            }
        }


# ----------------------------------------------------------------------
# Графический интерфейс
# ----------------------------------------------------------------------

class GammaCipherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Гаммирование с LCG - Лабораторная работа №8")
        self.root.geometry("950x750")
        self.root.resizable(True, True)

        # Переменные для параметров генератора
        self.a_var = tk.StringVar(value="5")
        self.b_var = tk.StringVar(value="7")
        self.m_var = tk.StringVar(value="4096")
        self.seed_var = tk.StringVar(value="4003")
        self.period_var = tk.StringVar(value="")

        # Создаём экземпляр шифра (по умолчанию)
        self.cipher = GammaCipher()

        # Создаём интерфейс
        self.create_widgets()

        # Обновляем отображение периода при изменении параметров
        self.update_period()

    def create_widgets(self):
        # Основной фрейм с прокруткой
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ===== Параметры генератора =====
        param_frame = ttk.LabelFrame(main_frame, text="Параметры линейного конгруэнтного генератора", padding="5")
        param_frame.pack(fill=tk.X, pady=(0,10))

        ttk.Label(param_frame, text="a (множитель):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(param_frame, textvariable=self.a_var, width=10).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(param_frame, text="b (приращение):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(param_frame, textvariable=self.b_var, width=10).grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(param_frame, text="m (модуль):").grid(row=0, column=4, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(param_frame, textvariable=self.m_var, width=10).grid(row=0, column=5, padx=5, pady=2)

        ttk.Label(param_frame, text="Y0 (начальное):").grid(row=0, column=6, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(param_frame, textvariable=self.seed_var, width=10).grid(row=0, column=7, padx=5, pady=2)

        ttk.Button(param_frame, text="Применить параметры", command=self.apply_params).grid(row=0, column=8, padx=10, pady=2)

        ttk.Label(param_frame, text="Период генератора:").grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        ttk.Label(param_frame, textvariable=self.period_var, foreground="blue").grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=5, pady=2)

        # ===== Ввод текста =====
        text_frame = ttk.LabelFrame(main_frame, text="Ввод данных", padding="5")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0,10))

        ttk.Label(text_frame, text="Исходный текст (UTF-8):").pack(anchor=tk.W)
        self.text_input = scrolledtext.ScrolledText(text_frame, height=5, wrap=tk.WORD)
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=(0,5))

        ttk.Label(text_frame, text="Шифротекст (HEX):").pack(anchor=tk.W)
        self.hex_input = scrolledtext.ScrolledText(text_frame, height=3, wrap=tk.WORD)
        self.hex_input.pack(fill=tk.BOTH, expand=True)

        # ===== Кнопки действий =====
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0,10))

        ttk.Button(btn_frame, text="Зашифровать", command=self.encrypt_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Расшифровать", command=self.decrypt_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сохранить результат", command=self.save_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Загрузить HEX из файла", command=self.load_hex_file).pack(side=tk.LEFT, padx=5)

        # ===== Вывод результатов =====
        result_frame = ttk.LabelFrame(main_frame, text="Результаты", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True)

        # Разделитель
        paned = ttk.PanedWindow(result_frame, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Верхняя часть: шифротекст/открытый текст
        top_frame = ttk.Frame(paned)
        paned.add(top_frame, weight=1)

        ttk.Label(top_frame, text="Открытый текст:").pack(anchor=tk.W)
        self.plain_output = scrolledtext.ScrolledText(top_frame, height=4, wrap=tk.WORD)
        self.plain_output.pack(fill=tk.BOTH, expand=True, pady=(0,5))

        ttk.Label(top_frame, text="Шифротекст (HEX):").pack(anchor=tk.W)
        self.cipher_output = scrolledtext.ScrolledText(top_frame, height=3, wrap=tk.WORD)
        self.cipher_output.pack(fill=tk.BOTH, expand=True)

        # Нижняя часть: гамма и таблица
        bottom_frame = ttk.Frame(paned)
        paned.add(bottom_frame, weight=1)

        ttk.Label(bottom_frame, text="Гамма (HEX):").pack(anchor=tk.W)
        self.gamma_output = scrolledtext.ScrolledText(bottom_frame, height=2, wrap=tk.WORD)
        self.gamma_output.pack(fill=tk.BOTH, expand=True, pady=(0,5))

        ttk.Label(bottom_frame, text="Таблица гаммирования (первые 20 байт):").pack(anchor=tk.W)
        self.table_output = scrolledtext.ScrolledText(bottom_frame, height=8, wrap=tk.WORD, font=("Courier New", 9))
        self.table_output.pack(fill=tk.BOTH, expand=True)

    def apply_params(self):
        """Применить параметры генератора"""
        try:
            a = int(self.a_var.get())
            b = int(self.b_var.get())
            m = int(self.m_var.get())
            seed = int(self.seed_var.get())
            # Проверка на корректность
            if m <= 0:
                raise ValueError("Модуль m должен быть положительным")
            if seed < 0 or seed >= m:
                raise ValueError("Начальное значение должно быть в [0, m-1]")
            self.cipher = GammaCipher(a, b, m, seed)
            self.update_period()
            messagebox.showinfo("Успех", f"Параметры применены.\nПериод генератора: {self.period_var.get()}")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные параметры: {e}")

    def update_period(self):
        """Обновить отображение периода генератора"""
        try:
            a = int(self.a_var.get())
            b = int(self.b_var.get())
            m = int(self.m_var.get())
            seed = int(self.seed_var.get())
            temp_gen = LinearCongruentialGenerator(a, b, m, seed)
            period = temp_gen.get_period()
            self.period_var.set(str(period))
        except:
            self.period_var.set("ошибка")

    def encrypt_action(self):
        """Зашифровать текст из поля ввода"""
        plaintext = self.text_input.get("1.0", tk.END).strip()
        if not plaintext:
            messagebox.showwarning("Предупреждение", "Введите текст для шифрования")
            return
        try:
            result = self.cipher.encrypt(plaintext)
            # Вывод результатов
            self.plain_output.delete("1.0", tk.END)
            self.plain_output.insert("1.0", result['plaintext'])

            self.cipher_output.delete("1.0", tk.END)
            self.cipher_output.insert("1.0", result['ciphertext_hex'])

            self.gamma_output.delete("1.0", tk.END)
            self.gamma_output.insert("1.0", result['gamma_hex'])

            # Таблица гаммирования (первые 20 символов)
            self.show_gamma_table(result['gamma'], result['plaintext'].encode('utf-8'), result['ciphertext_bytes'])

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при шифровании: {e}")

    def decrypt_action(self):
        """Расшифровать HEX из поля шифротекста"""
        hex_str = self.hex_input.get("1.0", tk.END).strip().replace(" ", "").replace("\n", "")
        if not hex_str:
            # Попробуем взять из поля результата шифротекста
            hex_str = self.cipher_output.get("1.0", tk.END).strip().replace(" ", "").replace("\n", "")
        if not hex_str:
            messagebox.showwarning("Предупреждение", "Введите шифротекст в HEX формате")
            return
        try:
            # Проверка на чётное количество символов
            if len(hex_str) % 2 != 0:
                raise ValueError("HEX строка должна содержать чётное количество символов")
            result = self.cipher.decrypt(hex_str)

            self.plain_output.delete("1.0", tk.END)
            self.plain_output.insert("1.0", result['plaintext'])

            self.cipher_output.delete("1.0", tk.END)
            self.cipher_output.insert("1.0", result['ciphertext_hex'])

            self.gamma_output.delete("1.0", tk.END)
            self.gamma_output.insert("1.0", result['gamma_hex'])

            # Для таблицы нужно исходное сообщение (plaintext) и гамма
            # Получаем байты открытого текста
            plain_bytes = result['plaintext'].encode('utf-8')
            cipher_bytes = bytes.fromhex(result['ciphertext_hex'])
            self.show_gamma_table(result['gamma'], plain_bytes, cipher_bytes)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при расшифровании: {e}")

    def show_gamma_table(self, gamma, plaintext_bytes=None, ciphertext_bytes=None):
        """Отобразить таблицу гаммирования (первые 20 байт)"""
        if plaintext_bytes is None:
            plaintext_bytes = b''
        if ciphertext_bytes is None:
            ciphertext_bytes = b''

        max_show = 20
        length = min(len(gamma), max_show)

        lines = []
        header = f"{'№':2} | {'Символ':6} | {'Код(dec)':9} | {'Код(bin)':8} | {'Гамма':5} | {'Гамма(bin)':8} | {'Результат'}"
        lines.append(header)
        lines.append("-" * 70)

        for i in range(length):
            if i < len(plaintext_bytes):
                p_byte = plaintext_bytes[i]
                p_char = chr(p_byte) if 32 <= p_byte < 127 else '.'
                p_bin = format(p_byte, '08b')
            else:
                p_byte = 0
                p_char = '.'
                p_bin = '--------'

            g_byte = gamma[i]
            g_bin = format(g_byte, '08b')

            # Если есть ciphertext_bytes, используем его для результата
            if i < len(ciphertext_bytes):
                result = ciphertext_bytes[i]
            else:
                result = p_byte ^ g_byte

            r_char = chr(result) if 32 <= result < 127 else '.'
            r_bin = format(result, '08b')

            line = f"{i:2} | {p_char:6} | {p_byte:9} | {p_bin} | {g_byte:5} | {g_bin} | {r_char} ({result})"
            lines.append(line)

        if len(gamma) > max_show:
            lines.append(f"... и ещё {len(gamma)-max_show} символов")

        self.table_output.delete("1.0", tk.END)
        self.table_output.insert("1.0", "\n".join(lines))

    def clear_all(self):
        """Очистить все поля ввода и вывода"""
        self.text_input.delete("1.0", tk.END)
        self.hex_input.delete("1.0", tk.END)
        self.plain_output.delete("1.0", tk.END)
        self.cipher_output.delete("1.0", tk.END)
        self.gamma_output.delete("1.0", tk.END)
        self.table_output.delete("1.0", tk.END)

    def save_result(self):
        """Сохранить текущие результаты в текстовый файл"""
        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not filename:
            return
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== Результаты шифрования/расшифрования ===\n")
                f.write(f"Параметры генератора: a={self.cipher.a}, b={self.cipher.b}, m={self.cipher.m}, seed={self.cipher.seed}\n")
                f.write(f"Период: {self.period_var.get()}\n\n")
                f.write("Открытый текст:\n")
                f.write(self.plain_output.get("1.0", tk.END).strip() + "\n\n")
                f.write("Шифротекст (HEX):\n")
                f.write(self.cipher_output.get("1.0", tk.END).strip() + "\n\n")
                f.write("Гамма (HEX):\n")
                f.write(self.gamma_output.get("1.0", tk.END).strip() + "\n\n")
                f.write("Таблица гаммирования:\n")
                f.write(self.table_output.get("1.0", tk.END).strip() + "\n")
            messagebox.showinfo("Успех", f"Результаты сохранены в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def load_hex_file(self):
        """Загрузить HEX строку из файла"""
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("HEX files", "*.hex"), ("All files", "*.*")])
        if not filename:
            return
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = f.read().strip()
            # Удаляем пробелы и переводы строк
            data = ''.join(data.split())
            self.hex_input.delete("1.0", tk.END)
            self.hex_input.insert("1.0", data)
            messagebox.showinfo("Успех", f"HEX данные загружены из файла:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")


def main():
    root = tk.Tk()
    app = GammaCipherGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()