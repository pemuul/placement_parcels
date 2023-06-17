import json
import random

# Создадим список для хранения данных
data = []

# Зададим количество элементов в json файле
num_elements = 1000

# Устанавливаем диапазон для случайных значений
length_range = (20, 30)
width_range = (20, 30)
height_range = (10, 100)
mass_range = (5, 200)

# Генерируем данные
for i in range(num_elements):
    item = {
        "id": i + 1,
        "length": random.randint(*length_range),
        "width": random.randint(*width_range),
        "height": random.randint(*height_range),
        "mass": random.randint(*mass_range)
    }
    data.append(item)

# Записываем данные в json файл
with open('input_json.txt', 'w') as f:
    json.dump(data, f, indent=4)
