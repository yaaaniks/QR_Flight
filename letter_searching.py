from pioneer_sdk import Pioneer, Camera
import cv2
import time
import os


def read_qr(buffer_coordinates, camera_frame): #функция для чтения qr-кодов
    detector = cv2.QRCodeDetector() #задаем
    string, _, _ = detector.detectAndDecode(camera_frame)
    if '.' in string: #если есть точка, значит получаем координаты в виде строки
        text = string.split()
        for i in range(len(text)): #перезаписываем строку в список координат типа float
            text[i] = float(text[i])
        if text != buffer_coordinates: #если координаты еще не были получены, значит возваращаем их, новый буфер и флаг на окончание полета
            buffer_coordinates = text
            return buffer_coordinates, text, False
        else: #если координаты были, значит отправляем дрону команду на окончание полета
            print("Такие координаты уже были получены!")
            return 0, 0, True
    elif len(string) == 1 | len(string) == 2: #если есть минус, значит возвращаем ключ от шифра, обнуляем буфер и флаг на окончание полета
        return 0, float(string), True
    else: #если ничего нет
        return None


def drone_flight(drone, camera_ip): #основная функция скрипта
    global list_of_cor, finish, buff  #задаем начальные данные
    buff = 0
    list_of_cor = []
    counter = 1 #счетчик для корректного сохранения фотографий
    finish = False #флаг на завершение полета
    command_x = 0
    command_y = 0
    flight_height = float(0.7)
    new_point = True
    while True: #бесконечный цикл
        camera_frame = camera_ip.get_cv_frame() #получаем снимок с камеры дрона
        cv2.imshow('flight', camera_frame) #выводим в отдельное окно
        if new_point: #если флаг на новую точку с qr-кодом, то отправляем команду дрону лететь на эту точку
            drone.go_to_local_point(x=command_x, y=command_y, z=flight_height, yaw=0)
            new_point = False
        if drone.point_reached(): #если заданная точка достигнута
            if read_qr(buff, camera_frame) is not None: #если qr-код обнаружен
                buff, list_of_cor, finish = read_qr(buff, camera_frame) #получаем новый буффер с координатами последней точки
                print("[INFO] Получен набор команд: ", list_of_cor)
                if finish: #если в qr-коде ключ от шифра
                    break
                elif list_of_cor: #если в qr-коде координаты точек
                    if list_of_cor[2] != 0 or list_of_cor[3] != 0:
                        print("[INFO] Дрон направляется к " + str(counter) + " точке")
                        drone.go_to_local_point(x=list_of_cor[2], y=list_of_cor[3], z=flight_height, yaw=0)
                        while True:
                            image = camera_ip.get_cv_frame() #получаем снимок с точки, где расположена буква
                            if drone.point_reached(): #если заданная точка достигнута
                                time.sleep(1)
                                cv2.imwrite('Photos/point' + str(counter) + '.jpg', image) #сохраняем снимок буквы с названием точки
                                print('success', counter)
                                counter += 1
                                break
                        if list_of_cor[4] != 0 or list_of_cor[5] != 0:
                            print("[INFO] Дрон направляется к " + str(counter) + " точке")
                            drone.go_to_local_point(x=list_of_cor[4], y=list_of_cor[5], z=flight_height, yaw=0)
                            while True:
                                image = camera_ip.get_cv_frame() #получаем снимок с точки, где расположена буква
                                if drone.point_reached(): #если заданная точка достигнута
                                    time.sleep(1)
                                    cv2.imwrite('Photos/point' + str(counter) + '.jpg', image) #сохраняем снимок буквы с названием точки
                                    print('success', counter)
                                    counter += 1
                                    break
                            if list_of_cor[6] != 0 or list_of_cor[7] != 0:
                                print("[INFO] Дрон направляется к " + str(counter) + " точке")
                                drone.go_to_local_point(x=list_of_cor[6], y=list_of_cor[7], z=flight_height, yaw=0)
                                while True:
                                    image = camera_ip.get_cv_frame() #получаем снимок с точки, где расположена буква
                                    if drone.point_reached(): #если заданная точка достигнута
                                        time.sleep(1)
                                        cv2.imwrite('Photos/point' + str(counter) + '.jpg', image) #сохраняем снимок буквы с названием точки
                                        print('success 3', counter)
                                        command_x = list_of_cor[0] #задаем координату x новой точки с qr-кодом
                                        command_y = list_of_cor[1] #задаем координату y новой точки с qr-кодом
                                        list_of_cor.clear() #обновляем список координат, чтобы дрон не зацикливался
                                        new_point = True #обновляем флаг на новую точку
                                        time.sleep(1)
                                        break
                else:
                    print("[INFO] Координаты не заложены в набор команд")
                    break
            else:
                print("[INFO] В данной точке нет qr-кода")
                break

        key = cv2.waitKey(1)
        if key == 27:
            print('[INFO] ESC нажат, программа завершается')
            break


if __name__ == '__main__':
    Photos = os.path.join(os.getcwd(), "Photos")  # создаёт папку Photos для сохранения фотографий
    if not os.path.isdir(Photos):
        os.mkdir(Photos)

    pioneer_mini = Pioneer()  # pioneer_mini как экземпляр класса Pioneer
    camera = Camera() #camera как экземпляр класса Camera
    pioneer_mini.arm()
    pioneer_mini.takeoff()

    drone_flight(pioneer_mini, camera)

    pioneer_mini.land() #сажаем дрон
    time.sleep(2)
    cv2.destroyAllWindows()  # закрывает окно с выводом изображения
    exit(0)