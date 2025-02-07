import argparse
import asyncio
import logging
import re
import os
import sys
import time
from typing import Any, Union
from tqdm import tqdm
from .photohunt import PhotoHunt

RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
WHITE = "\033[37m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"

RESET = "\033[0m"

def check_python_version():
    # Получаем текущую версию Python
    current_version = sys.version_info

    # Проверяем, что версия Python не ниже 3.6
    if current_version < (3, 6):
        print(RED + "⚠ Python должен быть версии 3.6 или выше" + RESET)
        sys.exit(1)
        
def print_dict(d):
    items = list(d.items())
    for i, (key, value) in enumerate(items):
        if i == len(items) - 1:
            print(f"{WHITE}└  {RESET}{key}: {value}\n")
        else:
            print(f"{WHITE}├  {RESET}{key}: {value}")

def print_banner():
    banner = r"""
   ▄███████▄    ▄█    █▄     ▄██████▄      ███      ▄██████▄          ▄█    █▄    ███    █▄  ███▄▄▄▄       ███     
  ███    ███   ███    ███   ███    ███ ▀█████████▄ ███    ███        ███    ███   ███    ███ ███▀▀▀██▄ ▀█████████▄ 
  ███    ███   ███    ███   ███    ███    ▀███▀▀██ ███    ███        ███    ███   ███    ███ ███   ███    ▀███▀▀██ 
  ███    ███  ▄███▄▄▄▄███▄▄ ███    ███     ███   ▀ ███    ███       ▄███▄▄▄▄███▄▄ ███    ███ ███   ███     ███   ▀ 
▀█████████▀  ▀▀███▀▀▀▀███▀  ███    ███     ███     ███    ███      ▀▀███▀▀▀▀███▀  ███    ███ ███   ███     ███     
  ███          ███    ███   ███    ███     ███     ███    ███        ███    ███   ███    ███ ███   ███     ███     
  ███          ███    ███   ███    ███     ███     ███    ███        ███    ███   ███    ███ ███   ███     ███     
 ▄████▀        ███    █▀     ▀██████▀     ▄████▀    ▀██████▀         ███    █▀    ████████▀   ▀█   █▀     ▄████▀   
                                                                                                                   
                                                                                                                                                                                                                                                                                                                                                                                                                   PhotoHunt Version — 1.0"""
                                                                             
    print(RED + banner + RESET)
    

def init_argparse() -> argparse.ArgumentParser:
    
    parser = argparse.ArgumentParser(
        description="PhotoHunt — поиск ВКонтакте по базам Search4Faces",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-s", "--sources",
        nargs="+",
        required=True,
        help=""" Пути к изображениям или URL для поиска. Поддерживает:
├ Локальные файлы: /path/to/image.jpg
├ URL: http://example.com/photo.jpg
└ Шаблоны: images/*.jpg\n
"""
    )

    parser.add_argument(
        "-o", "--output",
        default="report",
        help="Имя выходного файла (по умолчанию: report)\n"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["html", "json", "csv", "xlsx", "xml", "console", "txt"],
        default="html",
        help=""" Формат выходных данных:
├ html — Интерактивный отчет (по умолчанию)
├ json — Данные в JSON-формате
├ csv  — Таблица в формате CSV
├ xlsx — Файл Excel
├ xml  —  XML-документ
├ console  —  Вывод в консоль
└ txt  — Текстовый отчет\n
"""
    )

    parser.add_argument(
        "-db", "--database",
        choices=["vk_wall", "tt_avatar", "ch_avatar", "vkok_avatar", "vkokn_avatar", "sb_photo"],
        default="vk_wall",
        help=""" База данных для поиска:
├ vk_wall      — ВКонтакте посты и аватарки (самая новая)
├ tt_avatar    — ТикТок аватарки
├ ch_avatar    — Клуб Хауса аватарки
├ vkok_avatar  — ВКонтакте и Одноклассники
├ vkokn_avatar — Обновленная база ВКонтакте и Одноклассники
└ sb_photo     — Фото знаменитостей\n
"""
    )

    parser.add_argument(
        "-r", "--results",
        type=int,
        choices=[50, 100, 150, 200, 300, 500],
        default=100,
        help=""" Количество результатов:
├ 50
├ 100 (по умолчанию)
├ 150
├ 200
├ 300 
└ 500\n
"""
    )

    parser.add_argument(
        "-l", "--lang",
        choices=["ru", "en"],
        default="ru",
        help=""" Язык результатов:
├ ru (по умолчанию)
└ en\n
"""
    )

    # Фильтры
    parser.add_argument(
        "-fl", "--filters",
        nargs="+",
        default=[],
        help=""" Фильтры результатов в формате: поле=значение
 Примеры:
 ├ -fl country=Россия
 └ -fl "score>50" "age<=30"
 Поддерживаемые операторы: =, !=, >, <, >=, <=\n
"""
    )

    # Настройки отладки
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        help=""" Уровень детализации логов:
├ -v — info
└ -vv — debug\n
"""
    )

    return parser

def parse_filters(raw_filters: list[str]) -> list[dict[str, Any]]:
    """
    Парсинг фильтров из командной строки в структурированный формат
    
    :param raw_filters: Список фильтров в формате "поле[оператор]=значение"
    :return: Список словарей с условиями фильтрации
    
    Поддерживаемые операторы:
    =   - равно
    !=  - не равно
    >   - больше
    <   - меньше
    >=  - больше или равно
    <=  - меньше или равно
    
    Примеры:
    "age>25"         → {'age': {'gt': 25}}
    "country=Россия" → {'country': 'Россия'}
    "score<=75.5"    → {'score': {'lte': 75.5}}
    """
    filters = []
    operator_map = {
        '=': 'eq',
        '!=': 'neq',
        '>': 'gt',
        '<': 'lt',
        '>=': 'gte',
        '<=': 'lte'
    }
    
    pattern = r"(.+?)(>=|<=|!=|=|>|<)(.+)"
    
    for f in raw_filters:
        try:
            match = re.match(pattern, f)
            if not match:
                logging.error(f"Некорректный формат фильтра: {f}")
                return []
            
            field, op, value = match.groups()
            operator_key = operator_map[op]
            
            # Определение типа значения
            if value.startswith('"') and value.endswith('"'):
                parsed_value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                parsed_value = value[1:-1]
            else:
                try:
                    parsed_value = int(value)
                except ValueError:
                    try:
                        parsed_value = float(value)
                    except ValueError:
                        parsed_value = value

            # Формирование условия
            if operator_key == 'eq':
                filters.append({field: parsed_value})
            else:
                filters.append({field: {operator_key: parsed_value}})
                
        except Exception as e:
            logging.warning(f"Ошибка парсинга фильтра '{f}': {str(e)}")
            continue
            
    return filters

async def main():
    print_banner()
    check_python_version()
    parser = init_argparse()
    bar_format= "{l_bar}{bar}| {n_fmt}/{total_fmt}"
    args = parser.parse_args()

    # Настройка логирования
    log_level = logging.WARNING
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Инициализация клиента
    client = PhotoHunt()
    
    try:
        # Загрузка изображений с прогресс-баром
        with tqdm(args.sources, desc=GREEN + "Загрузка изображений" + RESET, bar_format=bar_format, colour="GREEN") as pbar:
            upload_results = await client.upload_batch(list(pbar))

        print(BLUE + "\n⚙️ Изображения были успешно найдены. Всего изображений было загружено: ", len(args.sources), "\n" + RESET)
        detect_results = []
        with tqdm(upload_results, desc=GREEN + "Поиск лиц" + RESET, bar_format=bar_format, colour="GREEN") as pbar:
            for result in pbar:
                
                if not result.get("url") or not result.get("boundings"):
                    
                    pbar.write(YELLOW + " ⚠ На изображение не было найдено лицо или произошла иная ошибка" + RESET)
                    
                    continue
                    
                res = await client.detect(
                    query=args.database,
                    filename=result["url"],
                    boundings=result["boundings"],
                    results=args.results,
                    lang=args.lang,
                    filters=parse_filters(args.filters)
                )
                detect_results.extend(res)
        
        persons = sum([len(r) for r in detect_results])
        if persons:
            print(BLUE + "\n⚙️ Лица были успешно найдены. Всего лиц: ", persons, "\n" + RESET)
        else:
            print(BLUE + "\n⚙️ К сожалению не было найдено схожих лиц или на изображении отсутствуют лица\n" + RESET)

            return
            
        with tqdm(detect_results, desc=GREEN + "Генерация отчета" + RESET, bar_format=bar_format, colour="GREEN") as pbar:
            names = []
            
            for i, detect_result in enumerate(pbar, 1):
                
                if not args.format == "console":
                    name = args.output + f"_{i}.{args.format}"
                    pbar.set_description(GREEN + "Генерируется: " + RESET + MAGENTA + name + RESET)
                    names.append(name)
                    client.export(detect_result, {args.format: name})
                    pbar.update()
                else:    
                    for person in detect_result:
                        
                        pbar.write(MAGENTA + "🔎 Найден человек: " + RESET)
                        print_dict(person)
                        
                        time.sleep(0.01)
                        pbar.update()
                        
            pbar.set_description(GREEN + "Отчет бы успешно сгенерирован" + RESET)
                
                
            
            if len(names):
          
                print(BLUE + "\n⚙️ Всего отчетов сгенерировано: ", i, RESET)
                print_dict(dict(zip([(os.getcwd() + args.output.rsplit("/", maxsplit=1)[0]) * len(names) if "/" in args.output else os.getcwd() * len(names)], names)))
                
    except Exception as e:
        logging.error(RED + "\nПроизошла неизвестная ошибка: " + str(e) + RESET + "\n")            
    finally:
        print(BLUE + "⚙️ Скрипт завершает свою работу" + RESET)
        
        await client.close()
        
if __name__ == "__main__":
    asyncio.run(main())