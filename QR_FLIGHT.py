from pioneer_sdk import Pioneer, Camera
import cv2
import numpy as np
import time
import re


def read_qr(camera_frame, def_x, def_y):

    gray = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2GRAY)  # кадр переводим в серый формат
    detector = cv2.QRCodeDetector()
    # встроенная функция библиотеки OpenCV, возвращает зашифрованный текст в виде строки
    string, _, _ = detector.detectAndDecode(gray)
    if string is not None:  # проверка на то, что QR-код обработан
        text = string.split()  # создаём список, содержащий каждое из полученных чисел в отдельности
        return text
    else:
         return None


def drone_flight(drone, camera_ip):
    command_x = 0
    command_y = 0
    flight_height = float(0.5)
    new_point = True

    while True:
        try:
            camera_frame = camera_ip.get_cv_frame()
            if np.sum(camera_frame) == 0:  # если не получил кадр, продолжает цикл (а не завершает скрипт)
                continue

            key = cv2.waitKey(1) & 0xFF
            if key == ord('p'):
                print(read_qr(camera_frame, command_x, command_y))

            # if new_point:  # подаёт команду дрону двигаться на следующую точку, если он достиг прошлой
            #     drone.go_to_local_point(x=command_x, y=command_y, z=flight_height, yaw=0)
            #     new_point = False
            # if drone.point_reached():  # если точка достигнута
            #     if read_qr(camera_frame, command_x, command_y) is not None:
            #         command_x, command_y = read_qr(camera_frame, command_x, command_y)
            #         new_point = True
            #     else:
            #         break
            cv2.imshow('QR Reading', camera_frame)  # вывод изображения на компьютер
        except cv2.error:  # в случае ошибки не завершает скрипт предварительно, а продолжает работу в цикле
            continue

        key = cv2.waitKey(1)
        if key == 27:  # завершает скрипт, если нажата клавиша ESC
            print('[INFO] ESC нажат, программа завершается')
            break


if __name__ == '__main__':
    pioneer_mini = Pioneer()  # pioneer_mini как экземпляр класса Pioneer
    # pioneer_mini.arm()
    # pioneer_mini.takeoff()
    camera = Camera()

    drone_flight(pioneer_mini, camera)

    pioneer_mini.land()
    time.sleep(5)
    cv2.destroyAllWindows()  # закрывает окно с выводом изображения
    exit(0)
