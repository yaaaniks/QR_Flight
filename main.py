from pioneer_sdk import Pioneer, Camera
import cv2
import numpy as np
import time
import os


# Функция, которая сканирует QR-код и возвращает команды дрону для передвижения и выполнения задания. Функция
# обрабатывает только QR-коды в формате, указанном в инструкции.
def read_qr(camera_frame):
    task_x = 0
    task_y = 0
    task_num = 0  # переменной task_num будет присваиваться номер задания, 1, 2 или 3
    rgb = [0, 0, 0]
    finish = False  # будет True, если дрон получит команду о завершении скрипта
    try:
        gray = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2GRAY)  # кадр переводим в серый формат
        detector = cv2.QRCodeDetector()
        # встроенная функция библиотеки OpenCV, возвращает зашифрованный текст в виде строки
        string, _, _ = detector.detectAndDecode(gray)
        if '0' in string:  # проверка на то, что QR-код обработан (в нём должен находится символ 0)
            text = string.split()  # создаём список, содержащий каждое из полученных чисел в отдельности
            print("[INFO] Получен следующий текст: ", text)
            com_x = float(text[0])  # присваиваем x координату, к которой полетит дрон после выполнения задания
            com_y = float(text[1])  # присваиваем y координату, к которой полетит дрон после выполнения задания
            # если обе координаты равны нулю, дрон выполнит задание и сядет, для этого задействуем флаг finish
            if com_x == 0 and com_y == 0:
                print('[INFO] Получен код, соответствующей посадке')
                finish = True
            if int(text[2]) == 1:  # если в 3 элементе стоит 1, то дрон получает координаты места для фотографии
                task_x = float(text[5])
                task_y = float(text[6])
                task_num = 1
            if int(text[3]) == 1:  # если в 4 элементе стоит 1, то дрон получает координаты места для посадки и взлёта
                task_x = float(text[5])
                task_y = float(text[6])
                task_num = 2
            # если в 5 элементе стоит 1, то дрон получает 3 числа, которые впоследствии зажгут светодиод в определённом
            # цвете, числа сохраняются в массиве rgb
            if int(text[4]) == 1:
                rgb = [int(text[7]), int(text[8]), int(text[9])]
                task_num = 3
            return com_x, com_y, task_x, task_y, rgb, task_num, finish
        return float(0), float(0), task_x, task_y, rgb, task_num, finish
    except cv2.error:  # если возникла ошибка, возвращает нули и finish = False, т.е. не отдаёт команд
        return float(0), float(0), task_x, task_y, rgb, task_num, finish


# Функция, обрабатывающая команды с QR-кодов. Она циклично получает с камеры кадры и сканирует их на наличие
# зашифрованных команд. После получения команд, выполняет их.
def drone_flight(drone, camera_ip):
    command_x = 0
    command_y = 0
    counter = 0  # счётчик для фотографий (нужен, чтобы фотографии друг друга не перезаписывали)
    flight_height = float(0.5)  # высота полёта дрона
    new_point = True
    task_progress = False
    finish = False

    while True:
        try:
            camera_frame = camera_ip.get_cv_frame()  # получаем кадр встроенным в pioneer_sdk методом
            if np.sum(camera_frame) == 0:  # если не получил кадр, продолжает цикл (а не завершает скрипт)
                continue

            if new_point:  # подаёт команду дрону двигаться к следующему QR-коду после выполнения задания
                drone.go_to_local_point(x=command_x, y=command_y, z=flight_height, yaw=0)
                new_point = False
                if finish:  # если read_qr вернула значение True для посадки, завершает программу
                    break

            if drone.point_reached():  # если точка достигнута
                # task_progress определяет, находится ли дополнительное здание в процессе выполнения, чтобы не
                # прерывать основное, False - дрон не получил задание и готов сканировать QR-код
                if task_progress is False:
                    new_x, new_y, task_x, task_y, rgb, task_num, finished = read_qr(camera_frame)
                    finish = finished  # извлекаем флаг, соответствующей завершению задания
                    # если получена команда сфотографировать или приземлиться, дрон вначале переместится к координатам,
                    # в которых нужно выполнить задание
                    if task_num == 1 or task_num == 2:
                        drone.go_to_local_point(x=(command_x+task_x), y=(command_y+task_y), z=flight_height, yaw=0)
                        task_progress = True
                    elif task_num == 3:  # в случае включения светодиода никуда перемещаться не надо
                        print("[INFO] Получена команда включить светодиод")
                        pioneer_mini.led_control(r=rgb[0], g=rgb[1], b=rgb[2])  # извлекаем значения RGB из массива
                        time.sleep(3)
                        pioneer_mini.led_control(r=0, g=0, b=0)
                        new_point = True
                        # обновление координат, new_x и new_y - положение следующего QR-кода относительно прошлого
                        command_x += new_x
                        command_y += new_y
                    else:
                        new_point = True
                        print("[INFO] Задание не получено")
                        command_x += new_x
                        command_y += new_y
                elif task_progress:  # если дрон получил задание и пришёл в нужную точку
                    task_progress = False
                    if task_num is 1:
                        counter += 1
                        # сохраняет фотографию в папку Photos как qrcodeX, где X - значение счётчика
                        cv2.imwrite(os.path.join(Photos, 'qrcode%d.jpg' % counter), camera_frame)
                        print('[INFO] Фотография сохранена')
                    elif task_num is 2:
                        drone.land()
                        time.sleep(3)
                        drone.arm()
                        drone.takeoff()
                        print('[INFO] Посадка и взлёт выполнены')
                        # после повторного запуска дрон начинает отсчёт координат заново, поэтому передаём ему
                        # старые координаты
                        command_x -= task_x
                        command_y -= task_y
                    # летит в точку, в которой дрон получил выполненное задание, чтобы продолжить полёт.
                    drone.go_to_local_point(x=command_x, y=command_y, z=flight_height, yaw=0)
                    # зацикливаем скрипт, чтобы дрон игнорировал команды на пути к изначальной точке
                    while True:
                        if drone.point_reached():  # условие выхода - точка достигнута
                            break
                    command_x += new_x
                    command_y += new_y
                    new_point = True
            cv2.imshow('QR Reading', camera_frame)  # вывод изображения на компьютер
        except cv2.error:  # в случае ошибки не завершает скрипт предварительно, а продолжает работу в цикле
            continue

        key = cv2.waitKey(1)
        if key == 27:  # завершает скрипт, если нажата клавиша ESC
            print('[INFO] ESC нажат, программа завершается')
            break


if __name__ == '__main__':
    Photos = os.path.join(os.getcwd(), "Photos")  # создаёт папку Photos для сохранения фотографий
    if not os.path.isdir(Photos):
        os.mkdir(Photos)

    pioneer_mini = Pioneer()  # pioneer_mini как экземпляр класса Pioneer
    pioneer_mini.arm()
    pioneer_mini.takeoff()
    camera = Camera()

    drone_flight(pioneer_mini, camera)

    pioneer_mini.land()
    time.sleep(5)
    cv2.destroyAllWindows()  # закрывает окно с выводом изображения
    exit(0)
