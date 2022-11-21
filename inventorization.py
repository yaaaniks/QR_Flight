from pioneer_sdk import Pioneer, Camera
import cv2
import numpy as np
import time
import os


def inventorize(drone, camera_ip):
    storage_name = np.empty(storage_height*storage_width, dtype=object)
    storage_quantity = np.empty(storage_height*storage_width, dtype=int)
    counter = 0
    command_x = float(0)
    command_z = float(1)
    x_inc = float(0.5)
    z_inc = float(0.5)
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
                gray = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2GRAY)
                string, _, _ = detector.detectAndDecode(gray)
                if string is not None:
                    text = string.split()
                    print("[INFO] Найден предмет ", text[0], " в кол-ве ", text[1])
                    np.insert(storage_name, counter, text[0])
                    np.insert(storage_quantity, counter, int(text[1]))
                    print('Сохраняю фотографию...')
                    cv2.imwrite(os.path.join(Storage, text[0]+str(text[1])+".jpg"), camera_frame)
                else:
                    print("[INFO] На данной полке предмет отсутствует")
                    np.insert(storage_name, counter, "None")
                    np.insert(storage_quantity, counter, 0)
                if counter == storage_width-1:
                    command_x = float(0)
                    command_z -= z_inc
                    if counter == storage_height*storage_width-1:
                        print("[INFO] Инвентаризация завершена:")
                        print(storage_name)
                        print(storage_quantity)
                        return storage_name, storage_quantity
                else:
                    command_x += x_inc
                new_point = True
            cv2.imshow('QR Reading', camera_frame)
        except cv2.error:
            continue

        key = cv2.waitKey(1)
        if key == 27:
            print('[INFO] ESC нажат, программа завершается')
            drone.land()
            time.sleep(5)
            cv2.destroyAllWindows()
            exit()


def find_item(result, drone):
    for j in range(storage_height-1):
        if
    command_x =
    drone.go_to_local_point()


if __name__ == '__main__':
    Storage = os.path.join(os.getcwd(), "Storage")  # создаёт папку Photos для сохранения фотографий
    if not os.path.isdir(Storage):
        os.mkdir(Storage)

    pioneer_mini = Pioneer()  # pioneer_mini как экземпляр класса Pioneer
    pioneer_mini.arm()
    pioneer_mini.takeoff()
    camera = Camera()

    storage_height = 2
    storage_width = 3
    names, quantities = inventorize(pioneer_mini, camera)

    item_found = False
    while True:
        item = input("Какой предмет нужно найти?")
        quantity = int(input("В каком количестве?"))
        if item in names:
            indexes = np.where(names == item)
            for i in range(indexes.size):
                if quantity <= quantities[indexes[i]]:
                    result_index = indexes[i]
                    item_found = True
                    print("Ячейка ", result_index, " содержит нужный предмет в нужном количестве")
                    break
            if item_found:
                break
            print("Нужный предмет в нужном количестве не найден, повторите попытку")
        else:
            print("Такого предмета нет на складе, повторите попытку")

        key = cv2.waitKey(1)
        if key == 27:
            print('[INFO] ESC нажат, программа завершается')
            pioneer_mini.land()
            time.sleep(5)
            cv2.destroyAllWindows()
            exit()

    find_item(result_index, pioneer_mini)

    pioneer_mini.land()
    time.sleep(5)
    cv2.destroyAllWindows()  # закрывает окно с выводом изображения
    exit(0)
