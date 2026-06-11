import numpy as np
import sounddevice as sd
import wave
import scipy.io.wavfile as wavfile
from typing import List, Tuple
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from datetime import datetime

class AudioScramblerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Аудио Скремблер - Лабораторная работа №2")
        self.root.geometry("800x600")
        
        # Инициализация скремблера
        self.scrambler = AudioScrambler()
        
        # Переменные для хранения данных
        self.original_audio = None
        self.scrambled_audio = None
        self.descrambled_audio = None
        self.current_key = None
        self.is_recording = False
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Стили
        style = ttk.Style()
        style.theme_use('clam')
        
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка веса столбцов и строк
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Заголовок
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="🔐 Аудио Скремблер", 
                                font=('Arial', 18, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, 
                                   text="Система шифрования аудиосигнала методом временной перестановки",
                                   font=('Arial', 10))
        subtitle_label.pack()
        
        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').grid(row=1, column=0, 
                                                            sticky=(tk.W, tk.E), pady=10)
        
        # Панель параметров
        params_frame = ttk.LabelFrame(main_frame, text="Параметры", padding="10")
        params_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        params_frame.columnconfigure(1, weight=1)
        
        # Частота дискретизации
        ttk.Label(params_frame, text="Частота дискретизации (Гц):").grid(row=0, column=0, 
                                                                          sticky=tk.W, pady=5)
        self.sample_rate_var = tk.StringVar(value="44100")
        sample_rate_combo = ttk.Combobox(params_frame, textvariable=self.sample_rate_var,
                                         values=["8000", "16000", "22050", "44100", "48000"],
                                         state="readonly", width=15)
        sample_rate_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Длительность записи
        ttk.Label(params_frame, text="Длительность записи (сек):").grid(row=1, column=0, 
                                                                        sticky=tk.W, pady=5)
        self.duration_var = tk.StringVar(value="5.0")
        duration_spinbox = ttk.Spinbox(params_frame, from_=1.0, to=30.0, 
                                       textvariable=self.duration_var, width=15)
        duration_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Большой интервал T
        ttk.Label(params_frame, text="Большой интервал T (сек):").grid(row=2, column=0, 
                                                                       sticky=tk.W, pady=5)
        self.T_var = tk.StringVar(value="1.0")
        T_spinbox = ttk.Spinbox(params_frame, from_=0.5, to=10.0, increment=0.1,
                                textvariable=self.T_var, width=15)
        T_spinbox.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Малый интервал t
        ttk.Label(params_frame, text="Малый интервал t (сек):").grid(row=3, column=0, 
                                                                     sticky=tk.W, pady=5)
        self.t_var = tk.StringVar(value="0.1")
        t_spinbox = ttk.Spinbox(params_frame, from_=0.01, to=1.0, increment=0.01,
                                textvariable=self.t_var, width=15)
        t_spinbox.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Информация о сегментах
        self.segments_info = ttk.Label(params_frame, text="Количество сегментов: -")
        self.segments_info.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, pady=10)
        
        # Первая строка кнопок
        row1_frame = ttk.Frame(buttons_frame)
        row1_frame.grid(row=0, column=0, pady=5)
        
        self.record_btn = ttk.Button(row1_frame, text="🎤 Записать с микрофона", 
                                     command=self.record_audio_thread, width=25)
        self.record_btn.grid(row=0, column=0, padx=5)
        
        self.load_btn = ttk.Button(row1_frame, text="📂 Загрузить файл", 
                                   command=self.load_audio, width=20)
        self.load_btn.grid(row=0, column=1, padx=5)
        
        # Вторая строка кнопок
        row2_frame = ttk.Frame(buttons_frame)
        row2_frame.grid(row=1, column=0, pady=5)
        
        self.scramble_btn = ttk.Button(row2_frame, text="🔐 Зашифровать", 
                                       command=self.scramble_audio, width=20, state="disabled")
        self.scramble_btn.grid(row=0, column=0, padx=5)
        
        self.descramble_btn = ttk.Button(row2_frame, text="🔓 Расшифровать", 
                                         command=self.descramble_audio, width=20, state="disabled")
        self.descramble_btn.grid(row=0, column=1, padx=5)
        
        # Третья строка кнопок
        row3_frame = ttk.Frame(buttons_frame)
        row3_frame.grid(row=2, column=0, pady=5)
        
        self.save_original_btn = ttk.Button(row3_frame, text="💾 Сохранить оригинал", 
                                            command=lambda: self.save_audio(self.original_audio, "original"),
                                            width=20, state="disabled")
        self.save_original_btn.grid(row=0, column=0, padx=5)
        
        self.save_scrambled_btn = ttk.Button(row3_frame, text="💾 Сохранить зашифрованный", 
                                             command=lambda: self.save_audio(self.scrambled_audio, "scrambled"),
                                             width=20, state="disabled")
        self.save_scrambled_btn.grid(row=0, column=1, padx=5)
        
        self.save_descrambled_btn = ttk.Button(row3_frame, text="💾 Сохранить расшифрованный", 
                                               command=lambda: self.save_audio(self.descrambled_audio, "descrambled"),
                                               width=20, state="disabled")
        self.save_descrambled_btn.grid(row=0, column=2, padx=5)
        
        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').grid(row=4, column=0, 
                                                            sticky=(tk.W, tk.E), pady=10)
        
        # Информационная панель
        info_frame = ttk.LabelFrame(main_frame, text="Информация", padding="10")
        info_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_text = tk.Text(info_frame, height=10, width=70, wrap=tk.WORD)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Кнопка очистки лога
        clear_btn = ttk.Button(info_frame, text="Очистить лог", 
                               command=self.clear_log, width=15)
        clear_btn.grid(row=1, column=0, pady=5)
        
        # Статус бар
        self.status_bar = ttk.Label(self.root, text="Готов к работе", relief=tk.SUNKEN)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Обновление информации о сегментах
        self.update_segments_info()
        
        # Привязка событий
        self.T_var.trace('w', lambda *args: self.update_segments_info())
        self.t_var.trace('w', lambda *args: self.update_segments_info())
        
    def update_segments_info(self):
        try:
            T = float(self.T_var.get())
            t = float(self.t_var.get())
            if t > 0:
                n_segments = int(T / t)
                self.segments_info.config(text=f"Количество сегментов: {n_segments}")
        except:
            pass
            
    def log_message(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        
    def clear_log(self):
        """Очистка лога"""
        self.status_text.delete(1.0, tk.END)
        
    def update_status(self, message):
        """Обновление статус бара"""
        self.status_bar.config(text=message)
        
    def record_audio_thread(self):
        """Запись аудио в отдельном потоке"""
        threading.Thread(target=self.record_audio, daemon=True).start()
        
    def record_audio(self):
        """Запись аудио с микрофона"""
        try:
            self.record_btn.config(state="disabled")
            self.update_status("Запись аудио...")
            
            duration = float(self.duration_var.get())
            sample_rate = int(self.sample_rate_var.get())
            
            self.scrambler.sample_rate = sample_rate
            self.original_audio = self.scrambler.record_audio(duration=duration)
            
            self.log_message(f"✅ Аудио записано. Длительность: {duration} сек")
            self.update_status("Запись завершена")
            
            # Активируем кнопки
            self.scramble_btn.config(state="normal")
            self.save_original_btn.config(state="normal")
            
            # Сбрасываем предыдущие данные
            self.scrambled_audio = None
            self.descrambled_audio = None
            self.current_key = None
            self.scrambled_btn.config(state="disabled")
            self.descrambled_btn.config(state="disabled")
            self.save_scrambled_btn.config(state="disabled")
            self.save_descrambled_btn.config(state="disabled")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка записи: {e}")
            self.update_status("Ошибка записи")
        finally:
            self.record_btn.config(state="normal")
            
    def load_audio(self):
        """Загрузка аудио из файла"""
        try:
            filename = filedialog.askopenfilename(
                title="Выберите аудиофайл",
                filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
            )
            
            if filename:
                self.update_status("Загрузка аудио...")
                self.original_audio = self.scrambler.load_audio(filename)
                self.log_message(f"📂 Загружен файл: {os.path.basename(filename)}")
                self.update_status("Аудио загружено")
                
                # Активируем кнопки
                self.scramble_btn.config(state="normal")
                self.save_original_btn.config(state="normal")
                
                # Сбрасываем предыдущие данные
                self.scrambled_audio = None
                self.descrambled_audio = None
                self.current_key = None
                self.scrambled_btn.config(state="disabled")
                self.descrambled_btn.config(state="disabled")
                self.save_scrambled_btn.config(state="disabled")
                self.save_descrambled_btn.config(state="disabled")
                
        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки: {e}")
            self.update_status("Ошибка загрузки")
            
    def scramble_audio(self):
        """Шифрование аудио"""
        if self.original_audio is None:
            messagebox.showwarning("Предупреждение", "Сначала запишите или загрузите аудио")
            return
            
        try:
            self.update_status("Шифрование аудио...")
            T = float(self.T_var.get())
            t = float(self.t_var.get())
            
            self.scrambled_audio, self.current_key = self.scrambler.scramble(
                self.original_audio, T=T, t=t
            )
            
            self.log_message(f"🔐 Аудио зашифровано. Ключ: {self.current_key[:10]}...")
            self.update_status("Шифрование завершено")
            
            # Активируем кнопки
            self.descramble_btn.config(state="normal")
            self.save_scrambled_btn.config(state="normal")
            self.scrambled_btn.config(state="normal")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка шифрования: {e}")
            self.update_status("Ошибка шифрования")
            
    def descramble_audio(self):
        """Расшифровка аудио"""
        if self.scrambled_audio is None or self.current_key is None:
            messagebox.showwarning("Предупреждение", "Сначала зашифруйте аудио")
            return
            
        try:
            self.update_status("Расшифровка аудио...")
            T = float(self.T_var.get())
            t = float(self.t_var.get())
            
            self.descrambled_audio = self.scrambler.descramble(
                self.scrambled_audio, self.current_key, T=T, t=t
            )
            
            self.log_message(f"🔓 Аудио расшифровано")
            self.update_status("Расшифровка завершена")
            
            # Активируем кнопки
            self.save_descrambled_btn.config(state="normal")
            
        except Exception as e:
            self.log_message(f"❌ Ошибка расшифровки: {e}")
            self.update_status("Ошибка расшифровки")
            
    def save_audio(self, audio_data, prefix):
        """Сохранение аудио в файл"""
        if audio_data is None:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                title="Сохранить аудиофайл",
                defaultextension=".wav",
                filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
                initialfile=f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            )
            
            if filename:
                self.update_status("Сохранение аудио...")
                self.scrambler.save_audio(audio_data, filename)
                self.log_message(f"💾 Аудио сохранено: {os.path.basename(filename)}")
                self.update_status("Сохранение завершено")
                
        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения: {e}")
            self.update_status("Ошибка сохранения")


class AudioScrambler:
    def __init__(self, sample_rate: int = 44100):
        """
        Инициализация скремблера
        
        Args:
            sample_rate: Частота дискретизации (по умолчанию 44100 Гц)
        """
        self.sample_rate = sample_rate
        
    def record_audio(self, duration: float = 5.0) -> np.ndarray:
        """
        Запись аудио с микрофона
        
        Args:
            duration: Длительность записи в секундах
            
        Returns:
            Массив с аудиоданными
        """
        print(f"🎤 Запись началась... Говорите {duration} секунд")
        recording = sd.rec(int(duration * self.sample_rate), 
                          samplerate=self.sample_rate, 
                          channels=1, 
                          dtype=np.float32)
        sd.wait()
        print("✅ Запись завершена")
        return recording.flatten()
    
    def split_into_segments(self, audio: np.ndarray, T: float = 1.0, t: float = 0.1) -> List[np.ndarray]:
        """
        Разбиение аудиосигнала на сегменты
        
        Args:
            audio: Аудиосигнал
            T: Длительность большого интервала (сек)
            t: Длительность малого интервала (сек)
            
        Returns:
            Список сегментов аудио
        """
        segment_length = int(t * self.sample_rate)
        segments = []
        
        for i in range(0, len(audio), segment_length):
            segment = audio[i:i + segment_length]
            if len(segment) > 0:
                # Дополняем нулями, если сегмент короче
                if len(segment) < segment_length:
                    segment = np.pad(segment, (0, segment_length - len(segment)), 'constant')
                segments.append(segment)
        
        print(f"📊 Аудио разбито на {len(segments)} сегментов по {t*1000:.0f} мс")
        return segments
    
    def generate_key(self, n_segments: int) -> List[int]:
        """
        Генерация ключа перестановки
        
        Args:
            n_segments: Количество сегментов
            
        Returns:
            Список индексов перестановки (ключ)
        """
        key = list(range(n_segments))
        random.shuffle(key)
        return key
    
    def scramble(self, audio: np.ndarray, T: float = 1.0, t: float = 0.1, 
                 key: List[int] = None) -> Tuple[np.ndarray, List[int]]:
        """
        Перемешивание аудиосигнала (шифрование)
        
        Args:
            audio: Исходный аудиосигнал
            T: Длительность большого интервала
            t: Длительность малого интервала
            key: Ключ перестановки (если None, генерируется автоматически)
            
        Returns:
            Кортеж (зашифрованное аудио, ключ)
        """
        segments = self.split_into_segments(audio, T, t)
        n_segments = len(segments)
        
        if key is None:
            key = self.generate_key(n_segments)
        
        # Перемешиваем сегменты согласно ключу
        scrambled_segments = [segments[key[i]] for i in range(n_segments)]
        
        # Объединяем сегменты обратно
        scrambled_audio = np.concatenate(scrambled_segments)
        
        print(f"🔐 Аудио зашифровано с ключом: {key[:10]}{'...' if len(key) > 10 else ''}")
        return scrambled_audio, key
    
    def descramble(self, scrambled_audio: np.ndarray, key: List[int], 
                   T: float = 1.0, t: float = 0.1) -> np.ndarray:
        """
        Обратное преобразование (расшифровка)
        
        Args:
            scrambled_audio: Зашифрованное аудио
            key: Ключ перестановки
            T: Длительность большого интервала
            t: Длительность малого интервала
            
        Returns:
            Расшифрованное аудио
        """
        segment_length = int(t * self.sample_rate)
        n_segments = len(key)
        
        # Разбиваем зашифрованное аудио на сегменты
        segments = []
        for i in range(n_segments):
            start = i * segment_length
            end = start + segment_length
            segment = scrambled_audio[start:end]
            if len(segment) < segment_length:
                segment = np.pad(segment, (0, segment_length - len(segment)), 'constant')
            segments.append(segment)
        
        # Восстанавливаем исходный порядок
        # Создаем обратную перестановку
        inverse_key = [0] * n_segments
        for i, k in enumerate(key):
            inverse_key[k] = i
        
        # Применяем обратную перестановку
        original_segments = [segments[inverse_key[i]] for i in range(n_segments)]
        
        # Объединяем
        original_audio = np.concatenate(original_segments)
        
        print("🔓 Аудио расшифровано")
        return original_audio
    
    def save_audio(self, audio: np.ndarray, filename: str):
        """
        Сохранение аудио в WAV файл
        
        Args:
            audio: Аудиоданные
            filename: Имя файла
        """
        # Нормализуем до диапазона int16
        audio_normalized = audio / np.max(np.abs(audio))
        audio_int16 = (audio_normalized * 32767).astype(np.int16)
        
        wavfile.write(filename, self.sample_rate, audio_int16)
        print(f"💾 Аудио сохранено в файл: {filename}")
    
    def load_audio(self, filename: str) -> np.ndarray:
        """
        Загрузка аудио из WAV файла
        
        Args:
            filename: Имя файла
            
        Returns:
            Аудиоданные в формате float32
        """
        sample_rate, audio = wavfile.read(filename)
        self.sample_rate = sample_rate
        return audio.astype(np.float32)


def main():
    """Основная функция запуска GUI"""
    root = tk.Tk()
    app = AudioScramblerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\n📦 Убедитесь, что установлены необходимые библиотеки:")
        print("   pip install numpy sounddevice scipy")