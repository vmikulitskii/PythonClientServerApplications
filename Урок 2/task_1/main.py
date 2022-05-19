"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений или другого инструмента извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Пример того, что должно получиться:

Изготовитель системы,Название ОС,Код продукта,Тип системы

1,LENOVO,Windows 7,00971-OEM-1982661-00231,x64-based

2,ACER,Windows 10,00971-OEM-1982661-00231,x64-based

3,DELL,Windows 8.1,00971-OEM-1982661-00231,x86-based

Обязательно проверьте, что у вас получается примерно то же самое.

ПРОШУ ВАС НЕ УДАЛЯТЬ СЛУЖЕБНЫЕ ФАЙЛЫ TXT И ИТОГОВЫЙ ФАЙЛ CSV!!!
"""
import csv
import re


def get_data():
    parameters = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    main_data = []
    for i in range(1, 4):
        with open(f'info_{i}.txt', 'r', encoding='utf-8') as f_n:
            datas = f_n.readlines()

        result = []
        for parameter in parameters:
            for data in datas:
                if parameter in data:
                    result.append(data.split(':')[1].replace('\n', ''))

        result = [i] + [el[re.search(r'\s\w', el).regs[0][0] + 1:] for el in result]
        main_data.append(result)
    main_data.insert(0, parameters)
    return main_data


def write_to_csv(csv_file):
    with open(csv_file, 'w', encoding='utf-8') as f_n:
        f_n_writer = csv.writer(f_n)
        f_n_writer.writerows(get_data())


"""Проверяем"""
write_to_csv('report.csv')

with open('report.csv', 'r', encoding='utf-8') as f_n:
    data = csv.reader(f_n)
    print(list(data))
