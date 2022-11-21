from pioneer_sdk import Pioneer, Camera
import cv2
import numpy as np
import time
import os


# Функция, которая сканирует QR-код и возвращает команды дрону для передвижения и выполнения задания. Функция
# обрабатывает только QR-коды в формате, указанном в инструкции.
def read_qr(camera_frame):
    try:
        gray = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2GRAY)
        detector = cv2.QRCodeDetector()
        # встроенная функция библиотеки OpenCV, возвращает зашифрованный текст в виде строки
        string, _, _ = detector.detectAndDecode(gray)
        t1_x = float(0)
        t1_y = float(0)
        t2_x = float(0)
        t2_y = float(0)
        t3_x = float(0)
        t3_y = float(0)
        shift = 0
        if '.' in string:  # проверка на то, что QR-код обработан
            text = string.split()  # создаём список, содержащий каждое из полученных чисел в отдельности
            print("[INFO] Получен набор команд: ", text)
            new_x = float(text[0])  # присваиваем x координату, к которой полетит дрон после выполнения задания
            new_y = float(text[1])  # присваиваем y координату, к которой полетит дрон после выполнения задания
            # если обе координаты равны нулю, дрон выполнит задание и сядет, для этого задействуем флаг finish
            if new_x == 0 and new_y == 0:
                print('[INFO] Дрон ')
                shift = int(text[2])
            else:
                t1_x = float(text[2])
                t1_y = float(text[3])
                t2_x = float(text[4])
                t2_y = float(text[5])
                t3_x = float(text[6])
                t3_y = float(text[7])
            return new_x, new_y, t1_x, t1_y, t2_x, t2_y, t3_x, t3_y, shift
        return None
    except cv2.error:  # если возникла ошибка, возвращает нули и finish = False, т.е. не отдаёт команд
        return None


# Функция, обрабатывающая команды с QR-кодов. Она циклично получает с камеры кадры и сканирует их на наличие
# зашифрованных команд. После получения команд, выполняет их.
def drone_flight(drone, camera_ip):
    command_x = 0
    command_y = 0
    flight_height = float(0.5)
    proximity_height = float(0.3)
    new_point = True
    finish = False
    t1 = False
    t2 = False
    t3 = False

    while True:
        try:
            camera_frame = camera_ip.get_cv_frame()  # получаем кадр встроенным в pioneer_sdk методом
            if np.sum(camera_frame) == 0:  # если не получил кадр, продолжает цикл (а не завершает скрипт)
                continue

            if new_point:  # подаёт команду дрону двигаться к следующему QR-коду после выполнения задания
                if finish:
                    break
                new_point = False
                drone.go_to_local_point(x=command_x, y=command_y, z=flight_height, yaw=0)

            if drone.point_reached():  # если точка достигнута
                if not t1:
                    if read_qr(camera_frame) is not None:
                        n_x, n_y, t1_x, t1_y, t2_x, t2_y, t3_x, t3_y, shift = read_qr(camera_frame)
                        if shift != 0:
                            finish = True
                        else:
                            if t1_x != 0 or t1_y != 0:
                                t1 = True
                                if t2_x != 0 or t2_y != 0:
                                    t2 = True
                                    if t1_x != 0 or t1_y != 0:
                                        t3 = True
                            else:
                                print("[INFO] Координаты символов не заложены в набор команд")
                                command_x += n_x
                                command_y += n_y
                                new_point = True

                if t1:  # если дрон получил задание и пришёл в нужную точку
                    t1 = False
                    t2 = False
                    t3 = False

                    print("[INFO] Дрон направляется к первой точке")
                    drone.go_to_local_point(x=command_x+t1_x, y=command_y+t1_y, z=proximity_height, yaw=0)
                    while True:
                        if drone.point_reached():
                            break
                    # yan

                    if t2:
                        print("[INFO] Дрон направляется к второй точке")
                        drone.go_to_local_point(x=command_x+t2_x, y=command_y+t2_y, z=proximity_height, yaw=0)
                        while True:
                            if drone.point_reached():
                                break
                        # yan

                        if t3:
                            print("[INFO] Дрон направляется к третьей точке")
                            drone.go_to_local_point(x=command_x+t3_x, y=command_y+t3_y, z=proximity_height, yaw=0)
                            while True:
                                if drone.point_reached():
                                    break
                            # yan
                    command_x += n_x
                    command_y += n_y
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
