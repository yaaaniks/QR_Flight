from pioneer_sdk import Pioneer, Camera
from more_itertools import locate
import cv2
import numpy as np
import time
import os


def inventorize(drone, camera_ip):
    storage_name = []
    storage_quantity = []
    counter = 0
    command_x = float(0)
    command_z = float(0.92)
    detector = cv2.QRCodeDetector()
    new_point = True
    while True:
        try:
            camera_frame = camera_ip.get_cv_frame()
            if np.sum(camera_frame) == 0:
                continue

            if new_point:
                new_point = False
                drone.go_to_local_point(x=command_x, y=0, z=command_z, yaw=0)

            if drone.point_reached():
                timer = time.time()
                while True:
                    try:
                        gray = cv2.cvtColor(camera_ip.get_cv_frame(), cv2.COLOR_BGR2GRAY)
                        string, _, _ = detector.detectAndDecode(gray)  # получать кадр 3 секунды!
                        if ' ' in string or (time.time() - timer > float(5)):
                            break
                    except:
                        continue
                if ' ' in string:
                    text = string.split()
                    print("[INFO] Найден предмет", text[0], "в количестве", int(text[1]))
                    storage_name.append(str(text[0]))
                    storage_quantity.append(int(text[1]))
                    print('Сохраняю фотографию...')
                    cv2.imwrite(os.path.join(Storage, text[0] + str(text[1]) + ".jpg"), camera_frame)
                else:
                    print("[INFO] На данной полке предмет отсутствует")
                    storage_name.append("None")
                    storage_quantity.append(int(0))
                if counter == storage_height * storage_width - 1:
                    print("[INFO] Инвентаризация завершена:")
                    print(storage_name)
                    print(storage_quantity)
                    drone.go_to_local_point(x=0, y=0, z=command_z, yaw=0)
                    while True:
                        if drone.point_reached():
                            time.sleep(1)
                            drone.land()
                            break
                    return storage_name, storage_quantity
                elif counter == storage_width - 1:
                    command_x = float(0)
                    command_z -= z_inc
                else:
                    command_x += x_inc
                new_point = True
                counter += 1
            cv2.imshow('QR Reading', camera_frame)
        except cv2.error:
            continue

        key_ip = cv2.waitKey(1)
        if key_ip == 27:
            print('[INFO] ESC нажат, программа завершается')
            drone.land()
            time.sleep(5)
            cv2.destroyAllWindows()
            exit()


def find_item(result, drone):
    col = result+1
    row = float(0.92)
    # for j in range(storage_height-1):
    #     if temp < storage_width:
    #         col = temp
    #         row = storage_height-j  #!
    #         break
    #     else:
    #         temp -= storage_width
    cmd_x = float(x_inc*col)
    cmd_z = float(0.92)
    drone.go_to_local_point(x=cmd_x, y=0, z=cmd_z, yaw=0)
    while True:
        if drone.point_reached():
            break
    print("[INFO] Дрон нашёл предмет под номером", result+1)
    drone.led_control(r=0, g=255, b=0)
    time.sleep(3)
    drone.led_control(r=0, g=0, b=0)


if __name__ == '__main__':
    Storage = os.path.join(os.getcwd(), "Storage")  # создаёт папку Photos для сохранения фотографий
    if not os.path.isdir(Storage):
        os.mkdir(Storage)

    pioneer_mini = Pioneer()  # pioneer_mini как экземпляр класса Pioneer
    pioneer_mini.arm()
    pioneer_mini.takeoff()
    camera = Camera()

    storage_height = 1
    storage_width = 4
    x_inc = float(0.4475)
    z_inc = float(0.25)
    names, quantities = inventorize(pioneer_mini, camera)

    item_found = False
    while True:
        item = input("Какой предмет нужно найти? ")
        if item == "exit":
            print("[INFO] Программа завершается предварительно")
            pioneer_mini.land()
            time.sleep(5)
            cv2.destroyAllWindows()  # закрывает окно с выводом изображения
            exit(0)
        if item in names:
            quantity = int(input("В каком количестве? "))
            indexes = list(locate(names, lambda x: x == item))
            for i in range(len(indexes)):
                if quantity <= quantities[indexes[i]]:
                    result_index = indexes[i]
                    item_found = True
                    print("Ячейка", result_index + 1, "содержит", item, "в нужном количестве")
                    break
            if item_found:
                break
            print(item, "в нужном количестве не найден, повторите попытку")
        else:
            print("Такого предмета нет на складе, повторите попытку")

    pioneer_mini.arm()
    pioneer_mini.takeoff()
    find_item(result_index, pioneer_mini)

    pioneer_mini.land()
    time.sleep(5)
    cv2.destroyAllWindows()  # закрывает окно с выводом изображения
    exit(0)
