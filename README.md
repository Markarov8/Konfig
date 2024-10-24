# Konfig
# EmulatorShell

EmulatorShell — это графическая оболочка, работающая с архивом `zip`. Эмулятор поддерживает команды для навигации, просмотра содержимого и работы с архивом.

## Постановка задачи
Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу
эмулятора как можно более похожей на сеанс shell в UNIX-подобной ОС.
Эмулятор должен запускаться из реальной командной строки, а файл с
виртуальной файловой системой не нужно распаковывать у пользователя.
Эмулятор принимает образ виртуальной файловой системы в виде файла формата
zip. Эмулятор должен работать в режиме GUI.
Ключами командной строки задаются:
• Путь к архиву виртуальной файловой системы.
• Путь к лог-файлу.
Лог-файл имеет формат csv и содержит все действия во время последнего
сеанса работы с эмулятором. Для каждого действия указаны дата и время.
Необходимо поддержать в эмуляторе команды ls, cd и exit, а также
следующие команды:
1. cat.
2. echo
Все функции эмулятора должны быть покрыты тестами, а для каждой из
поддерживаемых команд необходимо написать 3 теста.

## Установка и запуск

### Требования:
- Python 3.x
- Библиотеки: `zipfile`, `os`, `tkinter`, `scrolledtext`

### Запуск:
1. Убедитесь, что у вас есть zip-архив с именем `zxc.zip` в текущей директории или измените путь к файлу в коде.
2. Запустите скрипт через командную строку:
```bash
python emul.py --zip_path zxc.zip --log_path emulator.txt
```

### Описание команд
-  Команда ls выводит список файлов и директорий в текущей директории внутри архива.

Пример: 
```bash
> ls
ExForDel.txt
ExForDel1.txt
```

- Команда cd изменяет текущую директорию.
   - cd <путь> - Переходил по указанному пути
   - cd / - Переходит в корневую директорию.
   - cd .. - Переходит на уровень выше.

Пример:
```bash
> cd zxc
> ls
root
```

- Команда cat выводит содержимое указанного файла в выбранной директории

- Пример:

```bash
> cat ExForDel.txt
HAHAHHAHAHAHA
```

- Команда echo выводит текст введённый после команды echo

Пример:

```bash
> echo Hello hell
Hello hell
```

- Команда exit завершает работу оболочки. Каждая выполненная команда записывается в файл emulator.txt. Формат лога:

```txt
user1@my_pc:/$ ls
zxc
user1@my_pc:/$ cd zxc
```

## Пример использования
```bash
>user1@my_pc:/$ cd zxc

>user1@my_pc:zxc/$ cd root

>user1@my_pc:zxc/root/$ ls

Test1
Test2
Test3
>user1@my_pc:zxc/root/$ cd Test1

>user1@my_pc:zxc/root/Test1/$ cat ExForDel.txt
HAHHAHAHAHHAHAHA
>user1@my_pc:zxc/root/Test1/$ exit
Exiting emulator...

```

## Скриншот работы
![https://imgur.com/a/Nc7JU29]
