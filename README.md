# 🔍 PhotoHunt OSINT

[![PyPI Version](https://img.shields.io/pypi/v/photohunt-osint)](https://pypi.org/project/photohunt-osint/)
[![Python Versions](https://img.shields.io/pypi/pyversions/photohunt-osint)](https://pypi.org/project/photohunt-osint/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**PhotoHunt OSINT** - современная библиотека для поиска лиц по открытым источникам. Идеально подходит для:
- Журналистских расследований 🕵️♂️
- Кибербезопасности 🔒 
- Социальных исследований 📊
- Поиска родственников 👪

## 🌟 Возможности
- 🚀 Асинхронный поиск
- 🔎 Поддержка 6 баз
- 🎭 Фильтрация полученных данных
- 📁 Экспорт в HTML/JSON/CSV/XLSX/TXT/XML
- 🌍 Локализация (RU/EN)

## 🗃️ Базы данных
| Название           | Кол-во лиц         | Точность | Период сбора данных         |
|----------------|---------------|----------|-----------------------------|
| `vk_wall`      | 1.11B         | 68.79%   | 2019-11 → 2020-11<br>2022-12 → 2023-01 |
| `vkok_avatar`  | 280.78M       | VK:37.90%<br>OK:40.19% | VK:2018-12 → 2019-06<br>OK:2019-06 → 2020-03 |
| `vkokn_avatar` | 312.96M       | VK:48.37%<br>OK:45.13% | VK:2022-09 → 2024-11*<br>OK:2022-09 → 2022-10 |
| `tt_avatar`    | 125.44M       | 10.52%   | 2021-03 → 2021-09           |
| `ch_avatar`    | 13.07M        | 8.94%    | 2021-05 → 2022-01           |
| `sb_photo`     | 55.74M        | 12.46%   | 2022-05 → 2022-08           |

<small>*Данные актуальны на 08.02.2025</small>

## 📦 Установка
```bash
pip install photohunt-osint
```

## 🔎 Принцип работы
1. **Загрузка фото** (локальные файлы/URL)
2. **Детекция лиц** с выделением характерных признаков
3. **Сравнение** с выбранной базой данных
4. **Ранжирование** результатов по точности совпадения

## 📌 Рекомендации
1. Используйте изображения с **четкой видимостью лиц**
2. Поддерживаемые форматы: JPEG, PNG
3. Размер изображения не более 25MB

## 🚀 Примеры использования

### Через класс PhotoHunt
```python
from photohunt import PhotoHunt
import asyncio

async def main(client):
    
    # Загрузка изображения
    upload_results = await client.upload_batch(["group_photo.jpg"])
        
    detect_results = []
    
    # Поиск по всем лицам на фото
    for result in upload_results:
        
        if not result.get("boundings"): continue
        
        red = await client.detect(
            query="vk_wall",
            filename=result["url"],
            boundings=result["boundings"],
            results=50
        )
            
        detect_results.extend(res)
        

    # Экспорт в Excel
    for i, detect_result in enumerate(detect_results, 1):
        
        client.export(results, {"xlsx": "report{i}.xlsx"})

if __name__ == "__main__":
    client = PhotoHunt()
    try:
        
        asyncio.run(main(client))
        
    finally:
        
        client.close()
```

### Через CLI
```bash
# Поиск по локальному изображению
photohunt -s photo.jpg -db vk_wall -r 150

# Пакетная обработка с фильтрами
photohunt -s "photos/*.jpg" \
  -db vkokn_avatar \
  -fl "age>=18" "city=Санкт-Петербург" \
  -o result \
  -f json
```

## 📊 Обработка результатов
### Структура данных
```python
{
    "profile": "https://vk.com/id1",
    "face": "https://i.search4faces.com/faces/vk01/.../example.jpg",
    "source": "https://sun9-33.userapi.com/.../example.jpg",
    "score": 60.72,
    "age": 40,
    "first_name": "Павел",
    "last_name": "Дуров",
    "maiden_name": "",
    "city": "Санкт-Петербург",
    "country": "Россия",
    "born": "10.10.1984",
    "bio": ""
}
```

### Методы анализа
```python
# Фильтрация результатов
high_confidence = [p for p in results if p['score'] > 75]

# Статистика по городам
from collections import Counter
cities = Counter(p["city"] for p in results)

# Экспорт контактов
contacts = [{'name': p["first_name"] +" " + p["last_name"], 'url': p["profile"]} for p in results]
```

## 📜 Лицензия
MIT License - подробности в файле [LICENSE](LICENSE)

---

## 👥 Контакты
- Email: whispjuxy@gmail.com
- KeyBase: [@lastobserver](https://keybase.io/lastobserver)

## 💖 Поддержать проект
Развитие инструмента поддерживается сообществом. Вы можете помочь: 

- **TON**: `UQCl6nBbfXaHz2Z4ka9QcTiPIEzVGY1Bwn9eDlBAgOUwKJp1`  
- **Bitcoin**: `1JnzRzZEXcKoT9echwfRrwGbWxLyLPo9Si`  
- **USDT TON**: `UQCl6nBbfXaHz2Z4ka9QcTiPIEzVGY1Bwn9eDlBAgOUwKJp1`