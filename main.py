from pioneer_sdk import Pioneer, Camera
import cv2
import numpy as np
import time
import os


# Функция, которая сканирует QR-код и возвращает команды дрону для передвижения и выполнения задания. Функция
# обрабатывает только QR-коды в формате, указанном в инструкции.
def read_qr(camera_frame, drone):
    t1_x = 0
    t1_y = 0
    t2_x = 0
    t2_y = 0
    t3_x = 0
    t3_y = 0
    shift = 0
    try:
        gray = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2GRAY)
        detector = cv2.QRCodeDetector()
        # встроенная функция библиотеки OpenCV, возвращает зашифрованный текст в виде строки
        string, _, _ = detector.detectAndDecode(gray)
        if '.' in string:  # проверка на то, что QR-код обработан
            text = string.split()  # создаём список, содержащий каждое из полученных чисел в отдельности
            print("[INFO] Получен набор команд: ", text)
            com_x = float(text[0])  # присваиваем x координату, к которой полетит дрон после выполнения задания
            com_y = float(text[1])  # присваиваем y координату, к которой полетит дрон после выполнения задания
            # если обе координаты равны нулю, дрон выполнит задание и сядет, для этого задействуем флаг finish
            if com_x == 0 and com_y == 0:
                print('[INFO] Дрон ')
                shift = int(text[2])
            else:
                t1_x = float(text[3])
                t1_y = float(text[4])
                t2_x = float(text[5])
                t2_y = float(text[6])
                t3_x = float(text[7])
                t3_y = float(text[8])
            return com_x, com_y, t1_x, t1_y, t2_x, t2_y, t3_x, t3_y, shift
        return float(0), float(0), t1_x, t1_y, t2_x, t2_y, t3_x, t3_y, shift
    except cv2.error:  # если возникла ошибка, возвращает нули и finish = False, т.е. не отдаёт команд
        return float(0), float(0), t1_x, t1_y, t2_x, t2_y, t3_x, t3_y, shift


def letter_define shdh

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
                    new_x, new_y, task_x, task_y, rgb, task_num, finished = read_qr(camera_frame, drone)
                    finish = finished  # извлекаем флаг, соответствующей завершению задания
                    # если получена команда сфотографировать или приземлиться, дрон вначале переместится к координатам,
                    # в которых нужно выполнить задание
                    if task_num == 1 or task_num == 2:
                        drone.go_to_local_point(x=(command_x+task_x), y=(command_y+task_y), z=flight_height, yaw=0)
                        task_progress = True
                    elif task_num == 3:  # в случае включения светодиода никуда перемещаться не надо

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
