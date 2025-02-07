import csv
import json
import xml.etree.ElementTree as ET
from openpyxl import Workbook
from jinja2 import Template

from .html_template import html_template

def generate_html(data, output_file):
    """Генерация HTML отчета с фильтрацией"""
    
    template = Template(html_template)
    rendered = template.render(
        people=data,
        total=len(data),
        data=json.dumps(data, ensure_ascii=False, default=str)
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(rendered)

def generate_xml(data, output_file):
    """Генерация XML отчета"""
    root = ET.Element('People')
    for person in data:
        person_elem = ET.SubElement(root, 'Person')
        for key, value in person.items():
            field = ET.SubElement(person_elem, key)
            field.text = str(value)
    
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

def generate_csv(data, output_file):
    """Генерация CSV отчета"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def generate_txt(data, output_file):
    """Генерация текстового отчета"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for person in data:
            for key, value in person.items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            f.write("\n")

def generate_json(data, output_file):
    """Генерация JSON отчета"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_xlsx(data, output_file):
    """Генерация XLSX отчета"""
    wb = Workbook()
    ws = wb.active
    ws.title = "PhotoHunt Report"
    
    headers = list(data[0].keys())
    ws.append(headers)
    
    for person in data:
        ws.append([str(person[key]) for key in headers])
    
    for column in ws.columns:
        max_length = 0
        column = [cell for cell in column]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column[0].column_letter].width = adjusted_width
    
    wb.save(output_file)

def generate_reports(data, formats):
    """
    Генерация отчетов в указанных форматах
    
    :param data: Список словарей с данными
    :param formats: Словарь с путями для сохранения в формате:
                   {'html': 'path.html', 'xml': 'path.xml', ...}
    """
    
    supported_formats = {"txt": generate_txt, "csv": generate_csv, "json": generate_json, "xlsx": generate_xlsx, "html": generate_html, "xml": generate_xml}
    for format, path in formats.items():
        supported_formats.get(format, lambda *args: print("[ ! ] Выбран не поддерживаемый формат"))(data, path)