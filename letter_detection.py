import time
import easyocr
import os

alphabet = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р',
            'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я']


def check_for_russian(string):
    for letter in string:
        if any(checking_letter in alphabet for checking_letter in letter):
            return letter
    else:
        return False


def letter_detection(image, let_arr):
    gpu = False
    reader = easyocr.Reader(['ru'], gpu=gpu)
    result = reader.readtext(image, detail=0)
    if result is None:
        time.sleep(1)
        return None
    else:
        for char in result:
            if any(checking_char.isdigit() for checking_char in char):
                print('number is detected')
                time.sleep(1)
                return False
        if check_for_russian(result):
            let_arr.append(check_for_russian(result))
            return True
        else:
            time.sleep(1)
            return False


if __name__ == "__main__":
    file_shift = open("shift.txt", "r+")
    shift = int(file_shift.read())
    file_shift.close()
    dirname = 'Photos'
    word = []
    if os.path.isdir(dirname):
        files = os.listdir(dirname)
        print("получены файлы: ", files)
        for file in files:
            with open(os.path.join(dirname, file), 'rb+') as f:
                image = f.read()
                if letter_detection(image, word):
                    print("сейчас список состоит из ", word)
                else:
                    print("на изображении ничего не найдено")
        for i in range(len(word)):
            word[i] = alphabet[i + shift]
        print(word)
    else:
        print('такой папки не существует')
