'''
Для запуска данного скрипта нужен файл input_json.txt
Чтобы наполнить или создать фалй input_json.txt, нужно запустить скрипт create_random_cargos.py, он наполнит фалй рандоомными данными

Для визуализации схемы расположения нужно задать print_schem = True
На самой схеме, в углу будут написаны id груза
'#' '|' '_' '=' -  обозначины заданные отступы и границы отступов
'*' - заданы сами товары

Разбор ответа
{
    "id": 894, - пришедюший уникальный id ИЗНАЧАЛЬНО
    "length": 21, - пришедьшая длинна грузза ИЗНАЧАЛЬНО
    "width": 20, - пришедьшая ширина грузза ИЗНАЧАЛЬНО
    "height": 78, - пришедьшая высота грузза ИЗНАЧАЛЬНО
    "mass": 191, - пришедьшая масса грузза ИЗНАЧАЛЬНО
    "fit": "placed", - в каком состоянии товар ("denied" - не подошёл по габаритам, "fit" - подошёл по размерам, но влез, "placed" - вошёл в погрузку)
    "turn": false, - был ли повёрнут для размещения на 90 градусов
    "cords_x": 5, - в см, где размещён сам товар от дальней стенки в длинну кузова
    "cords_y": 65 - в см, где размещён сам товар от слева на право 
},

'''


import json
import copy


safe_distance_len = 5 # отступ от краёв см
truck_length = 500 # длинна кузова
truck_width = 250 # ширина кузова
truck_height = 200 # высота кузова
truck_mass = 10000 # максимальная вместимость по весу

round_up = False # отпбрасываем десятичные значения

print_schem = True # создать файл со схемой расположения груза


# груз 
class Cargo:
    def __init__(self, id, length, width, height, mass):
        if round_up:
            length = int(length)
            width = int(width)
        else:
            length = self.ceil_round(length)
            width = self.ceil_round(width)

        self.id = id
        self.length_origin = length
        self.width_origin = width
        self.height_origin = height
        self.mass = mass

        self.length = length + safe_distance_len * 2
        self.width = width + safe_distance_len * 2
        self.height = height + safe_distance_len
        self.ident = mass / (self.length * self.width)

        self.x = 0 # в длинну, с дальней части кузова
        self.y = 0 # в ширину, слева

        self.position = 0
        self.turn = False

        self.fit = 'unknown'

    def __str__(self) -> str:
        return str([self.id, self.length_origin, self.width_origin, self.length, self.width, self.x, self.y])
    
    @staticmethod
    def ceil_round(flot_inp):
        return_value = int(flot_inp)
        if flot_inp % 1 > 0:
            return_value += 1
        return return_value

    
    def revers_l_w(self):
        length = self.length 
        self.length = self.width
        self.width = length

        length_origin = self.length_origin 
        self.length_origin = self.width_origin
        self.width_origin = length_origin

        self.turn = self.turn == False

    def data_to_dict(self):
        return {
            'id' : self.id,
            'length' : self.length_origin,
            'width' : self.width_origin,
            'height' : self.height_origin,
            'mass' : self.mass,
            'fit' : self.fit,
            'turn' : self.turn,
            'cords_x' : self.x,
            'cords_y' : self.y,
        }
    

class Truck:
    def __init__(self, length, width, height, mass):
        self.length = length
        self.width = width
        self.height = height
        self.mass = mass

        self.filled_length_body = 0
        self.filled_width_body = 0
        self.filled_mass_body = 0
        self.max_length_cargo = 0


''' Получаем входящие данные в JSON из файла '''
def get_input_data_from_file():
    with open('input_json.txt') as json_file:
        data = json.load(json_file)

    return data


''' Отсееваем товары, которые совсем не подходят по размеру и массе '''
def mark_big_cargos(cargo_list, truck):
    for cargo_i in range(len(cargo_list)):
        cargo = cargo_list[cargo_i]
        if (cargo.height <= truck.height) and (cargo.mass <= truck.mass):
            #return_cargo_list.append(cargo)
            cargo_list[cargo_i].fit = 'fit'
        else:
            cargo_list[cargo_i].fit = 'denied'


def get_params_from_json(json_params):
    return (
        json_params['id'],
        json_params['length'],
        json_params['width'],
        json_params['height'],
        json_params['mass']
    )


def make_placement(cargos_list_p, truck_p):
    cargos_list = list(cargos_list_p)
    truck = copy.deepcopy(truck_p) 

    ''' Отсееваем товары, которые совсем не подходят по размеру и массе '''
    mark_big_cargos(cargos_list, truck)

    ''' Прописываем позицию в каждом элементе, это поможет нам его искать в будущем '''
    for cargo_i in range(len(cargos_list)):
        cargos_list[cargo_i].position = cargo_i


    ''' Оставляем только те, которые влазят в грузовик '''
    main_cargos_list= [cargos for cargos in cargos_list if cargos.fit == 'fit']
    main_cargos_list.sort(key=lambda x: -x.ident)

    layout_matrix_scheme = [[' ' for ii in range(truck.width)] for i in range(truck.length)]

    while True:
        for cargo_i in range(len(main_cargos_list)):
            cargo = main_cargos_list[cargo_i]
            
            # поворачиваем груз, чтобы он был боком, те cамым больше влезло
            if cargo.width > cargo.length:
                cargo.revers_l_w()

            # если блок так не влазит в ширену, то поворачиваем его
            if cargo.length + truck.filled_length_body > truck.length:
                cargo.revers_l_w()

            # если груз влез, записываем
            if (cargo.width + truck.filled_width_body <= truck.width) and (cargo.length + truck.filled_length_body <= truck.length) and (cargo.mass + truck.filled_mass_body <= truck.mass):
                # сдвигаем груз вниз, если там свободно, чтобы больше влезло
                filled_length_body_minus = 0
                if truck.filled_length_body > 0:
                    while layout_matrix_scheme[truck.filled_length_body - 1 - filled_length_body_minus][truck.filled_width_body:cargo.width + truck.filled_width_body] == [' ' for i in range(cargo.width)]:
                        filled_length_body_minus += 1

                # записываем в матрицу схематично нахождение контейнера
                for len_str in range(cargo.length):
                    for wid_str in range(cargo.width):
                        if len_str == 0:
                            char = '_'
                        elif cargo.length - 1 == len_str:
                            char = '='
                        elif cargo.length - 1 > len_str:
                            char = '#'
                        if (wid_str == 0) or (wid_str == cargo.width - 1):
                            char = '|'
                        
                        if ((len_str >= safe_distance_len) and (len_str < cargo.length - safe_distance_len ))\
                            and ((wid_str >= safe_distance_len) and (wid_str < cargo.width - safe_distance_len)):
                            char = '-'

                        if len_str == 1:
                            if (wid_str >= 1) and (len(str(cargo.id)) > wid_str - 1):
                                char = str(cargo.id)[wid_str - 1]
                        
                        layout_matrix_scheme[len_str + truck.filled_length_body - filled_length_body_minus][wid_str + truck.filled_width_body] = char

                # записываем координаты груза
                cargos_list[cargo.position].x = truck.filled_length_body - filled_length_body_minus + safe_distance_len
                cargos_list[cargo.position].y = truck.filled_width_body + safe_distance_len
                cargos_list[cargo.position].fit = 'placed'

                truck.filled_mass_body += cargo.mass
                truck.filled_width_body += cargo.width
                if truck.max_length_cargo < cargo.length:
                    truck.max_length_cargo = cargo.length
                main_cargos_list.pop(cargo_i)
                break

        # если массив с грузом пустой, то завершаем размещение
        if len(main_cargos_list) == 0:
            break

        # если были перебраны все элементы с грузом, значит не один не влез в ряд, переходим на новй
        if cargo_i == len(main_cargos_list) - 1:
            truck.filled_width_body = 0
            truck.filled_length_body += truck.max_length_cargo
            truck.max_length_cargo = 0

            # если в грузовик больше не влазит, то завершаем 
            sort_normal_cargos_now = list(main_cargos_list)
            sort_normal_cargos_now.sort(key=lambda x: x.length)
            min_length = sort_normal_cargos_now[0].length
            sort_normal_cargos_now.sort(key=lambda x: x.width)
            min_width = sort_normal_cargos_now[0].width
            sort_normal_cargos_now.sort(key=lambda x: x.mass)
            min_mass = sort_normal_cargos_now[0].mass
            if (min_length + truck.filled_length_body > truck.length) or (min_width + truck.filled_length_body > truck.length) or (min_mass + truck.filled_mass_body > truck.mass):
                break

    if print_schem:
        with open('output_schem.txt', 'w') as f:
            for p in layout_matrix_scheme:
                if p != []:
                    f.write(''.join(p) + '\n')

    return cargos_list

if __name__ == '__main__':
    ''' Получаем все данные '''
    cargos_dicts = get_input_data_from_file()
    cargos_list = [Cargo(*get_params_from_json(cargo_dict)) for cargo_dict in cargos_dicts]
    truck = Truck(length=truck_length, width=truck_width, height=truck_height, mass=truck_mass)

    cargos_list = make_placement(cargos_list, truck)

    ''' Формируем ответ с координамами всех посылок '''
    return_data = [cargo.data_to_dict() for cargo in cargos_list]

    with open('output_json.txt', 'w') as f:
        json.dump(return_data, f, indent=4)