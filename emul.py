import os
import string
import zipfile
import tkinter as tk
from tkinter import scrolledtext
import os
import select
import sys


def add_folder(path, folder_name):
    return os.path.join(path, folder_name)


def remove_last_folder(path):
    return os.path.dirname(path)


class Emulator:
    def __init__(self, username, hostname, zip_path, log_path):
        """
        Конструктор класса Emulator. Инициализирует пользователя, ПК, путь к архиву файловой системы и файл лога.

        :param username: Имя пользователя
        :param hostname: Имя компьютера
        :param zip_path: Путь к архиву файловой системы (ZIP)
        :param log_path: Путь к файлу лога
        """
        self.username = username
        self.hostname = hostname
        self.current_directory = '/'  # Текущая директория (начинаем с корня '/')
        self.absolute_path = r"C:\Users\marka\Desktop\Konfig"
        self.zip_path = zip_path
        self.log_path = log_path
        self.file_system = {}  # Словарь для хранения распакованных файлов и папок
        self._load_file_system()  # Распаковываем архив в память

    def _log(self, command, output):
        """
        Метод для записи команды пользователя и вывода программы в лог-файл.

        :param command: Ввод пользователя
        :param output: Вывод программы
        """
        with open(self.log_path, 'a') as log_file:
            # Записываем ввод команды с текущим местоположением пользователя
            log_file.write(f"{self.username}@{self.hostname}:{self._get_prompt_directory()}$ {command}\n")
            # Записываем результат команды
            if output:
                log_file.write(f"{output}\n")

    def _get_prompt_directory(self):
        """Метод для получения текущей директории для отображения в prompt."""
        return self.current_directory if self.current_directory != '/' else '/'

    def _load_file_system(self):
        """
        Метод для распаковки ZIP архива в виртуальную файловую систему.
        """
        if zipfile.is_zipfile(self.zip_path):
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    # Удаляем начальные / для удобства работы с файлами
                    normalized_path = file.lstrip('/')
                    self.file_system[normalized_path] = zip_ref.read(file).decode('utf-8')  # Добавляем файлы и их содержимое в словарь
        else:
            print("Error: provided file is not a ZIP archive.")

    def ls(self, directory=None):
        """
        Команда 'ls' выводит список файлов и папок в указанной директории (или текущей, если аргумент не передан).
        """
        if directory:
            path = os.path.join(self.current_directory, directory).lstrip('/')
        else:
            path = self.current_directory.lstrip('/')

        output = []
        found_files = False
        for file in self.file_system:
            if file.startswith(path):
                relative_path = file[len(path):].strip('/')
                if '/' not in relative_path:
                    output.append(relative_path)
                    found_files = True

        if not found_files:
            output.append("Directory is empty.")

        # Печатаем и возвращаем результат команды
        response = '\n'.join(output)
        print(response)
        return response


    def cd(self, path):
        """
        Команда 'cd' позволяет перемещаться между директориями.

        :param path: Путь к новой директории
        """

        if path == "..":
            # Переход на уровень выше
            if self.current_directory != '/':
                self.current_directory = os.path.dirname(self.current_directory.rstrip('/')) + '/'
                self.absolute_path = remove_last_folder(self.absolute_path)
                print(f"Новый абсолютный путь: {self.absolute_path}")
        else:
            # Переход в указанную директорию
            new_directory = os.path.join(self.current_directory, path).lstrip('/')
            if any(f.startswith(new_directory) for f in self.file_system):
                self.current_directory = new_directory.rstrip('/') + '/'
                self.absolute_path = add_folder(self.absolute_path, path)
                print(f"Новый абсолютный путь: {self.absolute_path}")
            else:
                response = "Error: directory not found."
                print(response)
                return response
        return ""

    def cat(self, filename):
        """
        Команда 'cat' выводит содержимое файла по абсолютному пути.

        :param filename: Имя файла для чтения
        :return: Содержимое файла или сообщение об ошибке
        """
        file_path = os.path.join(self.absolute_path, filename)  # Абсолютный путь к файлу
        if os.path.exists(file_path): #and os.path.isfile(file_path):  # Проверяем, существует ли файл и является ли он файлом
            try:
                with open(file_path, 'r') as f:
                    return f.read()  # Возвращаем содержимое файла
            except Exception as e:
                return f"Ошибка при чтении файла: {e}"  # Возвращаем ошибку, если чтение не удалось
        else:
            return f"Файл '{filename}' не найден по пути: {file_path}"

    def echo(self, text):
        """Выводит текст."""
        return text

class EmulatorGUI:
    def __init__(self, emulator):
        self.emulator = emulator

        # Создаем главное окно
        self.window = tk.Tk()
        self.window.title("Linux Emulator")
        self.window.configure(bg="black")  # Темная тема

        # Создаем область вывода
        self.output_text = scrolledtext.ScrolledText(self.window, width=80, height=20, bg="black", fg="green",
                                                     state='disabled', font=("Consolas", 12))
        self.output_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # sticky nsew позволяет растягивать элемент

        # Область для отображения текущего хоста и директории (нередактируемая)
        self.host_display = tk.Label(self.window, text=f"current directory: {emulator.username}@{emulator.hostname}:{emulator._get_prompt_directory()}$",
                                     bg="black", fg="green", font=("Consolas", 12), anchor="w")
        self.host_display.grid(row=2, column=0, sticky='w', padx=10, pady=5)

        # Поле для ввода команд
        self.command_entry = tk.Entry(self.window, width=80, bg="black", fg="green", font=("Consolas", 12), insertbackground="green")
        self.command_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Привязываем событие нажатия Enter
        self.command_entry.bind('<Return>', self.run_command)

        # Настройка растягивания
        self.window.grid_rowconfigure(0, weight=1)  # Растягиваем область вывода по вертикали
        self.window.grid_rowconfigure(1, weight=0)  # Поле для ввода команды не должно сильно изменять размер
        self.window.grid_rowconfigure(2, weight=0)  # Строка хоста фиксирована по высоте
        self.window.grid_columnconfigure(0, weight=1)  # Растягиваем все элементы по горизонтали

        # Запуск основного цикла окна
        self.window.mainloop()

    def run_command(self, event):
        """Обработчик ввода команды и её выполнения."""
        command = self.command_entry.get()
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, f"{emulator.username}@{emulator.hostname}:{emulator._get_prompt_directory()}$ {command}\n")
        self.output_text.config(state='disabled')
        with open(emulator.log_path, 'a') as log_file:
            # Записываем ввод команды с текущим местоположением пользователя
            log_file.write(f"{emulator.username}@{emulator.hostname}:{emulator._get_prompt_directory()}$ {command}\n")
        self.command_entry.delete(0, tk.END)  # Очищаем поле ввода

        # Получаем результат команды из эмулятора
        output = self.execute_command(command)
        with open(emulator.log_path, 'a') as log_file:
            log_file.write(f"{output}\n")
        # Обновляем область вывода

        self.host_display.config(text=f"current directory: {emulator.username}@{emulator.hostname}:{emulator._get_prompt_directory()}$")
        self.host_display.update()
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, f"{output}\n")
        self.output_text.config(state='disabled')
        self.output_text.yview(tk.END)  # Прокрутка вниз

    def execute_command(self, command):
        """Метод для выполнения команд через эмулятор."""
        if command.startswith("ls"):
            args = command.split(" ")
            if len(args) == 2:
                return self.emulator.ls(args[1])
            else:
                return self.emulator.ls()
        elif command.startswith("cd "):
            return self.emulator.cd(command.split(" ")[1])
        elif command.startswith("cat"):
            return self.emulator.cat(command.split(" ")[1])
        elif command.startswith("echo"):
            args = command.split(" ")
            if len(args) >= 2:
                return self.emulator.echo(args[1])
            else:
                return self.emulator.echo()
        elif command == "exit":
            self.window.destroy()
            return "Exiting emulator..."
        else:
            return "Unknown command."


# Основной код
if __name__ == "__main__":
    username = "user1"
    hostname = "my_pc"
    zip_path = "zxc.zip"
    log_path = "emulator.log"
    absolute_path = r"C:\Users\marka\Desktop\Konfig"

    # Создаем объект эмулятора
    emulator = Emulator(username, hostname, zip_path, log_path)

    # Запускаем графический интерфейс
    gui = EmulatorGUI(emulator)
