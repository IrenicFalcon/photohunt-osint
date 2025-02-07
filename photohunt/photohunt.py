import httpx
import asyncio
import re
import logging
import json
import aiofiles
from typing import Any, Optional
from urllib.parse import urlparse

from .generate_reports import generate_reports

logger = logging.getLogger(__name__)

class PhotoHunt:
    """Асинхронный клиент для работы с Search4Faces"""

    QUERY_MAP = {
        "vk_wall": "vk01",
        "tt_avatar": "tt00",
        "ch_avatar": "ch00",
        "vkok_avatar": "vkok",
        "vkokn_avatar": "vkokn",
        "sb_photo": "sb00"
    }

    def __init__(self, concurrency: int = 10):
        """
        :param concurrency: Максимальное количество одновременных соединений
        """
        self.concurrency = concurrency
        self.client = httpx.AsyncClient()

    async def upload_batch(self, sources: list[str]) -> list[dict[str, Any]]:
        """
        Пакетная загрузка изображений

        :param sources: Список путей к файлам или URL-адресов
        :return: Список результатов загрузки
        """
        tasks = [self._upload_single(source) for source in sources]
        return await asyncio.gather(*tasks)

    async def _upload_single(self, source: str) -> dict[str, Any]:
        """
        Обработка одного файла

        :param source: Путь к файлу или URL-адрес
        :return: Результат загрузки в формате JSON
        """
        bytes_data = await self.get_image_bytes(source)
        
        response = await self.client.post(
            "https://search4faces.com/assets/php/upload.php",
            content=bytes_data,
            timeout=30.0
        )
        
        try:
            
            if response.status_code:
                
                return response.json()
                
            else:
                
                print("error")
                
        except json.JSONDecodeError:
            
            return {"url": "", "boundings": [], "scale": 0.0}

    async def detect(
        self,
        query: str,
        filename: str,
        boundings: list[list[float]],
        lang: str = "ru",
        results: int = 50,
        filters: list[dict[str, Any]] = []
    ) -> list[list[dict[str, Any]]]:
        """
        Поиск лиц для нескольких наборов координат

        :param query: Тип поиска (ключ из QUERY_MAP)
        :param filename: Имя файла с сервера
        :param boundings: Список наборов координат лиц
        :param lang: Язык результатов
        :param results: Максимальное количество результатов
        :param filters: Список фильтров
        :return: Список результатов для каждого набора координат
        """
        
        processed_query = self.QUERY_MAP.get(query)
        if not processed_query:
            raise ValueError("Недопустимый параметр запроса")
       
        datas = []
        for bbox in boundings:
            payload = {
                "query": processed_query,
                "lang": lang,
                "results": results,
                "filename": filename,
                "boundings": bbox
            }
            
            response = await self.client.post(
                "https://search4faces.com/assets/php/detect.php",
                json=payload,
                timeout=60.0
            )
            datas.append(self._process_detect_response(response.json(), filters))
            
        return datas
    
    @staticmethod
    def export(data: list[dict], formats: dict):
        """
        Генерация отчетов в указанных форматах
    
        :param data: Список словарей с данными
        :param formats: Словарь с путями для сохранения в формате:
                   {'html': 'path.html', 'xml': 'path.xml', ...}
        """
        
        return generate_reports(data, formats)
        
    async def get_image_bytes(self, source: str) -> bytes:
        """
        Получение изображения из источника

        :param source: Путь к файлу или URL-адрес
        :return: Байты изображения
        """
        if self._is_valid_url(source):
            return await self._download_from_url(source)
        return await self._read_from_file(source)

    def _is_valid_url(self, url: str) -> bool:
        """Проверка валидности URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    async def _download_from_url(self, url: str) -> bytes:
        response = await self.client.get(url, timeout=30.0)
        
        response.raise_for_status()
        
        return response.content

    async def _read_from_file(self, file_path: str) -> bytes:
        async with aiofiles.open(file_path, 'rb') as f:
            
            return await f.read()

    def _process_detect_response(
        self, 
        raw_data: dict[str, Any], 
        filters: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Обработка и фильтрация результатов поиска

        :param raw_data: Сырые данные от сервера
        :param filters: Список фильтров
        :return: Отфильтрованные результаты
        """        
        return [
            self._parse_face(face)
            for face in raw_data.get("faces", [])
            if self._apply_filters(self._parse_face(face), filters)
        ]

    def _parse_face(self, raw_face: list) -> dict[str, Any]:
        """
        Преобразование данных о лице

        :param raw_face: Сырые данные лица
        :return: Структурированные данные
        """
        return {
            "profile": raw_face[1],
            "face": raw_face[2],
            "source": raw_face[9] or "",
            "score": self._parse_score(raw_face[10]),
            "age": self._parse_age(raw_face[12]),
            "first_name": raw_face[13] or "",
            "last_name": raw_face[14] or "",
            "maiden_name": raw_face[15] or "",
            "city": raw_face[16] or "",
            "country": raw_face[17] or "",
            "born": raw_face[18] or "",
            "bio": raw_face[19] or ""
        }

    def _apply_filters(self, face: dict[str, Any], filters: list[dict[str, Any]]) -> bool:
        """
        Применение фильтров к данным

        :param face: Данные о лице
        :param filters: Список фильтров
        :return: Результат проверки фильтров
        """
        for filter_dict in filters:
            for field, condition in filter_dict.items():
                if not self._check_condition(face.get(field), condition):
                    return False
        return True

    def _check_condition(self, value: Any, condition: Any) -> bool:
        """
        Проверка условия фильтра

        :param value: Значение для проверки
        :param condition: Условие фильтра
        :return: Результат проверки
        """
        try:
            if isinstance(condition, dict):
                return self._check_operator_condition(value, condition)
            if isinstance(condition, str):
                return condition.lower() in str(value).lower()
            if isinstance(condition, (int, float)):
                return value == condition
            return False
        except Exception:
            return False

    def _check_operator_condition(self, value: Any, condition: dict[str, Any]) -> bool:
        result = True
        if 'eq' in condition:
            result &= value == condition['eq']
        if 'gt' in condition:
            result &= value > condition['gt']
        if 'lt' in condition:
            result &= value < condition['lt']
        return result

    def _parse_score(self, score: Any) -> float:
        try:
            return max(0.0, min(100.0, float(score)))
        except (ValueError, TypeError):
            return 0.0

    def _parse_age(self, age: Any) -> Optional[int]:
        try:
            return int(age) if int(age) > 0 else None
        except (ValueError, TypeError):
            return None

    async def close(self):
        """Закрытие соединений"""
        await self.client.aclose()