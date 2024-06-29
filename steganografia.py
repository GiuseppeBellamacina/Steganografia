# Author: Giuseppe Bellamacina
# Attenzione: si consiglia di creare immagini in formato PNG per evitare perdita di dati

from os import system, remove, walk
from os.path import getsize, join, relpath, isfile, isdir, exists
from pyfiglet import figlet_format
import colorama
import pickle
from random import randint
from PIL import Image
import numpy as np
import zipfile
from termcolor import colored
import time

# zipModes
NO_ZIP = 0
FILE = 1
DIR = 2

def timeDisplay(seconds: int) -> str:
    """Converte i secondi in minuti e secondi"""
    seconds = round(seconds)
    minutes, seconds = divmod(seconds, 60)
    if minutes:
        return f"{minutes:02d} minuti {seconds:02d} secondi"
    else:
        return f"{seconds:02d} secondi"

def arcobaleno(str: str) -> None:
    """Arcobalenizza le sringhe"""
    colors = ["red","yellow","green","cyan","blue","magenta"]
    for i in range(len(str)):
        print(colored(str[i], colors[i%len(colors)], 'on_black', ['bold', 'blink']), end='')

def binaryConvert(text: str) -> str:
    """Converte una stringa di testo in una stringa binaria (carattere per carattere)"""
    return ''.join(format(ord(char), '08b') for char in text)

def binaryConvertBack(text: str) -> str:
    """Converte una stringa binaria in una stringa di testo (8-bit)"""
    return ''.join(chr(int(text[i*8:i*8+8],2)) for i in range(len(text)//8))

def setLastBit(value: int, bit: str) -> int:
    """Setta l'ultimo bit di un numero"""
    value = format(value, '08b') # converte un intero in una stringa di 8 caratteri (byte)
    value = value[:7] + bit # cambia l'ultimo bit
    value = int(value, 2) # riconverte la stringa in un numero
    value = min(255, max(0, value)) # controlla se il numero è fuori range
    return value

def setLastNBits(value: int, bits: str, n: int) -> int:
    """Setta gli ultimi n bits di un numero"""
    value = format(value, '08b')
    if len(bits) < n:
        n = len(bits)
    value = value[:-n] + bits
    value = int(value, 2)
    value = min(255, max(0, value))
    return value

def setComponentOfColor(mat: np.array, i: int, j: int, color: int, channel: int) -> np.array:
    """Cambia tutte e tre le componenti di colore RGB di un pixel"""
    if channel == 0:
        mat[i,j] = (color, mat[i,j][1], mat[i,j][2])
    elif channel == 1:
        mat[i,j] = (mat[i,j][0], color, mat[i,j][2])
    elif channel == 2:
        mat[i,j] = (mat[i,j][0], mat[i,j][1], color)
    return mat
    

def hideMessage(img: Image, msg: str, new_img: str) -> Image:
    """Nasconde una stringa in una foto"""
    system('cls')
    # controlla se l'immagine è abbastanza grande
    if (img.width * img.height) * 3 < len(msg) * 8:
        f = img.filename.split("\\")[-1]
        print(f"\33[1;31mERRORE\33[0m: Immagine \33[31m{f}\33[0m troppo piccola per nascondere il messaggio")
        system("pause")
        return img
    # converte in RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    # inizia a nascondere
    arcobaleno("OCCULTAMENTO MESSAGGIO")
    print("...")
    img_copy = img.copy()
    mat = img_copy.load()
    msg = binaryConvert(msg)
    msg = msg + "00000000"
    msg = list(msg)
    for i in range(img.width):
        for j in range(img.height):
            for z in range(3):
                if msg != []:
                    bit = msg.pop(0)
                    color = mat[i,j][z] # ottieni il colore
                    color = setLastBit(color, bit) # cambia l'ultimo bit
                    mat = setComponentOfColor(mat, i, j, color, z) # setta il colore
                else:
                    break
    print(f"\33[1;32mTERMINATO\33[0m\nPercentuale di pixel usati: {format(((len(msg) / ((img.width * img.height) * 3)) * 100), '.2f')}%")
    print(f"Immagine salvata come \33[33m{new_img}\33[0m")
    img_copy.save(new_img)
    return img_copy

def getMessage(img: Image) -> str:
    """Ottieni un messaggio nascosto"""
    system('cls')
    if img.mode != "RGB":
        img = img.convert("RGB")
    # inizia la procedura
    mat = img.load()
    msg, stop = [], []
    for i in range(img.width):
        for j in range(img.height):
            for z in range(3):
                color = mat[i,j][z]
                bit = format(color, '08b')[-1]
                stop.append(bit)
                msg.append(bit)
                if len(stop) == 8:
                    if ''.join(stop) == "00000000":
                        msg = ''.join(msg)
                        msg = msg[:-8]
                        msg = binaryConvertBack(msg)
                        return msg
                    stop = []
    msg = ''.join(msg)
    msg = msg[:-8]
    msg = binaryConvertBack(msg)
    return msg

def hideFile_with_mat(img: Image, file: str, new_img: str, n=0, div=0) -> (Image, int): # type: ignore # deprecato
    """Nasconde un file a caratteri"""
    system('cls')
    # controlla se n è valido
    if n < 0 or n > 8:
        print("\33[1;31mERRORE\33[0m: \33[32mn\33[0m deve essere compreso tra 1 e 8 o 0 per la modalita' automatica")
        system("pause")
        return img, -1
    # auto n
    if n == 0:
        while (img.width * img.height) * 3 * n < getsize(file) * 8:
            n += 1
            if n > 8:
                f = img.filename.split("\\")[-1]
                print(f"\33[1;31mERRORE\33[0m: Immagine \33[31m{f}\33[0m troppo piccola per nascondere il file")
                system("pause")
        return img, -1
    # controllo dimensioni
    if (img.width * img.height) * 3 * n < getsize(file) * 8:
        f = img.filename.split("\\")[-1]
        print(f"\33[1;31mERRORE\33[0m: Immagine \33[31m{f}\33[0m troppo piccola per nascondere il file")
        system("pause")
        return img, -1
    if img.mode != "RGB":
        img = img.convert("RGB")
    # controlla se div è valido
    if div == 0:
        div = ((img.width * img.height) * 3 * n) // (getsize(file) * 8)
    else:
        if img.width * img.height * 3 * n < div * getsize(file) * 8:
            print("\33[1;31mERRORE\33[0m: il valore di \33[35mdiv\33[0m e' eccessivo, prova 0")
            system("pause")
            return img, -1
    # avvio procedura
    arcobaleno("OCCULTAMENTO FILE")
    print("...")
    img_copy = img.copy()
    mat = img_copy.load() # lavoro sulla copia
    x, y, z = 0, 0, 0
    start_time = time.time()
    # lettura per riga
    with open(file, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for line in f)
        f.seek(0)
        rsv = ""
        for i, line in enumerate(f): # enumerate() ritorna una tupla con l'indice ed il valore
            line = binaryConvert(line) 
            line = rsv + line
            rsv = ""
            if i == total_lines - 1:
                line = line + "00000000"
            line = list(line)
            flag = False
            while line != []:
                bit = ""
                for k in range(n):
                    if len(line) >= n-k:
                        bit += line.pop(0)
                    else:
                        line = ''.join(line)
                        rsv += line
                        flag = True
                        break
                if flag:
                    break
                color = mat[x,y][z]
                color = setLastNBits(color, bit, n)
                mat = setComponentOfColor(mat, x, y, color, z)
                # vai avanti
                for w in range(div):
                    z = (z + 1) % 3
                    if z == 0:
                        y = (y + 1) % img.height
                        if y == 0:
                            x = (x + 1) % img.width     
            if (i + 1) % 3000 == 0:
                system('cls')
                arcobaleno("OCCULTAMENTO FILE")
                print("...")
                progress = (i + 1) / total_lines
                elapsed_time = time.time() - start_time
                print(f"Elaborate {i + 1} righe su {total_lines} ({format((progress) * 100, '.2f')}%)")
                print(f"Tempo rimanente: {timeDisplay(elapsed_time *(1 - progress) / progress)}")
    rsv = list(rsv)
    # se ci sono altri bit
    while rsv != []:
        bit = ""
        for k in range(n):
            if len(rsv) >= n-k:
                bit += rsv.pop(0)
            else:
                bit += "0"
        color = mat[x,y][z]
        color = setLastNBits(color, bit, n)
        mat = setComponentOfColor(mat, x, y, color, z)
        for w in range(div):
            z = (z + 1) % 3
            if z == 0:
                y = (y + 1) % img.height
                if y == 0:
                    x = (x + 1) % img.width
    f.close()
    system('cls')
    arcobaleno("OCCULTAMENTO FILE")
    print("...")
    print(f"Elaborate {total_lines} righe su {total_lines} (100.0%)")
    print("Tempo rimanente: 0 secondi")
    print(f"\33[1;32mTERMINATO\33[0m\nPercentuale di pixel usati con \33[32mn\33[0m={n} e \33[35mdiv\33[0m={div}: {format(((getsize(file) * 8) / ((img.width * img.height) * 3 * n)) * 100, '.2f')}%")
    img_copy.save(new_img)
    print(f"Immagine salvata come \33[33m{new_img}\33[0m")
    return (img_copy, div)

def oldfindDiv(dim: int, file: str, n: int) -> int: # da evitare
    image_dim = dim * n
    div = (image_dim // (getsize(file) * 8))
    index = (getsize(file)-1) * 8 * div
    image_dim = (div+1) * image_dim - index
    div = (image_dim // (getsize(file) * 8))
    return div

def findDiv(dim: int, file: str, n: int) -> float: # più stabile
    image_dim = dim * n
    div = ((image_dim - n) / (getsize(file) * 8))
    return div

def hideFile(img: Image, file: str, new_img: str, n=0, div=0): # -> (Image, int, float) # versione con array
    """Nasconde un file a caratteri"""
    system('cls')
    if n < 0 or n > 8:
        print("\33[1;31mERRORE\33[0m: n deve essere compreso tra 1 e 8 o 0 per la modalita' automatica")
        system("pause")
        return img, -1, -1.0
    # auto n
    if n == 0:
        while (img.width * img.height) * 3 * n < getsize(file) * 8:
            n += 1
            if n > 8:
                f = img.filename.split("\\")[-1]
                print(f"\33[1;31mERROR\33[0m: Immagine \33[31m{f}\33[0m troppo piccola per nascondere il file")
                system("pause")
                return img, -1, -1.0
    # controllo dimensioni
    if (img.width * img.height) * 3 * n < getsize(file) * 8:
        f = img.filename.split("\\")[-1]
        print(f"\33[1;31mERROR\33[0m: Immagine \33[31m{f}\33[0m troppo piccola per nascondere il file")
        system("pause")
        return img, -1, -1.0
    if img.mode != "RGB":
        img = img.convert("RGB")
    # conversione in array
    arr = np.array(img).flatten().copy()
    total_pixels_ch = len(arr)
    if div == 0:
        div = findDiv(total_pixels_ch, file, n)
    else:
        if total_pixels_ch * n < div * getsize(file) * 8:
            print("\33[1;31mERRORE\33[0m: il valore di \33[35mdiv\33[0m e' eccessivo, prova 0")
            system("pause")
            return img, -1, -1.0
    arcobaleno("OCCULTAMENTO FILE")
    print("...")
    start_time = time.time()
    with open(file, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for line in f)
        f.seek(0)
        rsv = ""
        ind, pos = 0, 0
        for i, line in enumerate(f):
            line = binaryConvert(line) 
            line = rsv + line
            rsv = ""
            if i == total_lines - 1:
                line = line + "00000000"
            line = list(line)
            flag = False
            while line != []:
                bit = ""
                for k in range(n):
                    if len(line) >= n-k:
                        bit += line.pop(0)
                    else:
                        line = ''.join(line)
                        rsv += line
                        flag = True
                        break
                if flag:
                    break
                arr[pos] = setLastNBits(arr[pos], bit, n)
                ind += div
                pos = round(ind)
            if (i + 1) % 3000 == 0:
                system('cls')
                arcobaleno("OCCULTAMENTO FILE")
                print("...")
                progress = (i + 1) / total_lines
                elapsed_time = time.time() - start_time
                print(f"Elaborate {i + 1} righe su {total_lines} ({format((progress) * 100, '.2f')}%)")
                print(f"Tempo rimanente: {timeDisplay(elapsed_time *(1 - progress) / progress)}")
    rsv = list(rsv)
    # if there are still bits left, hide them
    while rsv != []:
        bit = ""
        for k in range(n):
            if len(rsv) >= n-k:
                bit += rsv.pop(0)
            else:
                bit += "0"
        arr[pos] = setLastNBits(arr[pos], bit, n)
        ind += div
        pos = round(ind)
    f.close()
    # print percentage of pixels used
    system('cls')
    arcobaleno("OCCULTAMENTO FILE")
    print("...")
    print(f"Elaborate {total_lines} righe su {total_lines} (100.0%)")
    print("Tempo rimanente: 0 secondi")
    print(f"\33[1;32mTERMINATO\33[0m\nPercentuale di pixel usati con \33[32mn\33[0m={n} e \33[35mdiv\33[0m={div}: {format(((getsize(file) * 8) / ((img.width * img.height) * 3 * n)) * 100, '.2f')}%")
    img_copy = Image.fromarray(arr.reshape(img.height, img.width, 3))
    img_copy.save(new_img)
    print(f"Immagine salvata come \33[33m{new_img}\33[0m")
    return (img_copy, n, div)

def scan8(line: str, flag: str) -> int:
    """Scansiona una riga per un flag di 8 bit"""
    for i in range(0, len(line), 8):
        if line[i:i+8] == flag:
            return i
    return -1

def getFile_with_mat(img: Image, new_file_path: str, n: int, div: int) -> None: # deprecato
    """Gets a file from a image"""
    system('cls')
    # check if n is in range
    if n < 1 or n > 8:
        print("\33[1;31mERROR\33[0m: \33[32mn\33[0m must be between 1 and 8")
        system("pause")
        return
    arcobaleno("GETTING FILE")
    print("...")
    # convert image to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    # start getting file
    mat = img.load()
    char, stop = [], []
    i, j, z = 0, 0, 0
    with open(new_file_path, 'w', encoding='utf-8') as file:
        while (i < img.width and j < img.height):
            for k in range(n, 0, -1):
                bit = format(mat[i,j][z], '08b')[-k]
                char.append(bit)
                stop.append(bit)
            if len(stop) == n*8:
                stop = ''.join(stop)
                ind = scan8(stop, "00000000")
                if ind != -1:
                    if len(char):
                        char = ''.join(char)
                        char = char[:scan8(char, "00000000")]
                        char = binaryConvertBack(char)
                        file.write(char)
                    print(f"\33[1;32mDECRYPTION DONE\33[0m\nFile saved as \33[33m{new_file_path}\33[0m")
                    file.close()
                    return
                stop = []
                if len(char) >= 1024:
                    char = ''.join(char)
                    char = binaryConvertBack(char)
                    file.write(char)
                    char = []
            for w in range(div):
                z = (z + 1) % 3
                if z == 0:
                    j = (j + 1) % img.height
                    if j == 0:
                        i += 1

def getFile(img: Image, new_file_path: str, n: int, div: float) -> None: # with arr -> faster
    """Ottieni un file da un'immagine"""
    system('cls')
    # check if n is in range
    if n < 1 or n > 8:
        print("\33[1;31mERRORE\33[0m: \33[32mn\33[0m deve essere compreso tra 1 e 8")
        system("pause")
        return
    arcobaleno("RICERCA FILE")
    print("...")
    # convert image to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    # start getting file
    arr = np.array(img).flatten().copy()
    char, stop = [], []
    pos, inde = 0, 0
    err = len(arr)
    with open(new_file_path, 'w', encoding='utf-8') as file:
        while True:
            for k in range(n, 0, -1):
                bit = format(arr[pos], '08b')[-k]
                char.append(bit)
                stop.append(bit)
                if len(stop) == n*8:
                    stop = ''.join(stop)
                    ind = scan8(stop, "00000000")
                    if ind != -1:
                        if len(char):
                            char = ''.join(char)
                            char = char[:scan8(char, "00000000")]
                            char = binaryConvertBack(char)
                            file.write(char)
                        print(f"\33[1;32mFILE TROVATO\33[0m\nFile salvato come \33[33m{new_file_path}\33[0m")
                        file.close()
                        return
                    stop = []
                    if len(char) >= 1024:
                        char = ''.join(char)
                        char = binaryConvertBack(char)
                        file.write(char)
                        char = []
            inde += div
            pos = round(inde)
            # check if file is not found
            err -= 1
            if err < 0:
                print("\33[1;31mERRORE\33[0m: file non trovato")
                system("pause")
                return

def zipdir(path: str, ziph: zipfile.ZipFile) -> None:
    """Zips a directory"""
    for root, dirs, files in walk(path):
        for file in files:
            file_path = join(root, file)
            arcname = relpath(file_path, path)
            ziph.write(file_path, arcname)

def getDirSize(path: str) -> int:
    """Gets the size of a directory"""
    size = 0
    for root, dirs, files in walk(path):
        for file in files:
            file_path = join(root, file)
            size += getsize(file_path)
    return size

def hideBinFile(img: Image, file: str, new_img: str, zipMode=NO_ZIP, n=0, div=0): # -> (Image, int, float, int)
    """Nasconde un file binario o una cartella"""
    system('cls')
    # check if n is in range
    if n < 0 or n > 8:
        print("\33[1;31mERRORE\33[0m: \33[32mn\33[0m deve essere compreso tra 1 e 8, 0 per la modalita' automatica")
        system("pause")
        return img, -1, -1.0, -1
    # determine channels
    ch = 3
    if img.mode == "RGBA":
        ch = 4
    if img.mode != "RGB" and img.mode != "RGBA":
        img = img.convert("RGB")
    # check if zipMode is in range
    if zipMode not in [0, 1, 2]:
        print("\33[1;31mERRORE\33[0m: zipMode deve essere 0, 1 o 2")
        system("pause")
        return img, -1, -1.0, -1
    # zip file if zipMode is 1
    if zipMode == FILE:
        print("Compressione file...")
        with zipfile.ZipFile('tmp.zip', 'w') as zf:
            zf.write(file)
        file = 'tmp.zip'
        print("File compresso")
    # zip directory if zipMode is 2
    elif zipMode == DIR:
        print("Compressione directory...")
        zipf = zipfile.ZipFile('tmp.zip', 'w', zipfile.ZIP_DEFLATED)
        zipdir(file, zipf)
        file = 'tmp.zip'
        zipf.close()
        print("Directory compressa")
    # get file size
    total_bytes = getsize(file)
    # auto n
    if n == 0:
        while (img.width * img.height) * ch * n < total_bytes * 8:
            n += 1
            if n > 8:
                f = img.filename.split("\\")[-1]
                print(f"\33[1;31mERRORE\33[0m: Immagine \33[31m{f}\33[0m troppo piccola per nascondere il file")
                system("pause")
                return img, -1, -1.0, -1
    # check if image is big enough
    elif (img.width * img.height) * ch * n < total_bytes * 8:
        f = img.filename.split("\\")[-1]
        print(f"\33[1;31mERRORE\33[0m: Immagine \33[31m{f}\33[0m troppo piccola per nascondere il file")
        system("pause")
        return img, -1, -1.0, -1
    # convert image to array
    arr = np.array(img).flatten().copy()
    total_pixels_ch = len(arr)
    # check if div value is valid
    if div == 0:
        div = findDiv(total_pixels_ch, file, n)
    else:
        if total_pixels_ch * n < div * total_bytes * 8:
            print("\33[1;31mERRORE\33[0m: il valore di \33[35mdiv\33[0m e' eccessivo, prova 0")
            system("pause")
            return img, -1, -1.0, -1
    # start hiding file
    system('cls')
    arcobaleno("OCCULTAMENTO FILE")
    print("...")
    start_time = time.time()
    rsv = ""
    ind, pos = 0, 0
    # read file
    with open(file, 'rb') as f:
        f.seek(0)
        for i in range(total_bytes):
            byte = f.read(1) # read byte
            bits = format(ord(byte), '08b') # convert byte into string of bits
            bits = rsv + bits
            rsv = ""
            while len(bits) >= n:
                tmp = bits[:n]
                bits = bits[n:]
                # set last n bits of pixel
                arr[pos] = setLastNBits(arr[pos], tmp, n)
                ind += div
                pos = round(ind)
            if len(bits) > 0:
                rsv = bits
            if (i + 1) % 50000 == 0:  # Change this number to control how often the progress is printed
                system('cls')
                arcobaleno("OCCULTAMENTO FILE")
                print("...")
                progress = (i + 1) / total_bytes
                elapsed_time = time.time() - start_time
                print(f"Elaborati {i + 1} byte su {total_bytes} ({format((progress) * 100, '.2f')}%)")
                print(f"Tempo rimanente: {timeDisplay(elapsed_time *(1 - progress) / progress)}")
    f.close()
    while len(rsv) > 0:
        tmp = rsv[:n]
        rsv = rsv[n:]
        # set last n bits of pixel
        arr[pos] = setLastNBits(arr[pos], tmp, n)
        ind += div
        pos = round(ind)
    system('cls')
    arcobaleno("OCCULTAMENTO FILE")
    print("...")
    print(f"Elaborati {total_bytes} byte su {total_bytes} (100.0%)")
    print(f"\33[1;32mTERMINATO\33[0m\nPercentuale di pixel usati con \33[32mn\33[0m={n} e \33[35mdiv\33[0m={div}: {format(((total_bytes * 8) / ((img.width * img.height) * ch * n)) * 100, '.2f')}%")
    if zipMode != NO_ZIP:
        # delete tmp.zip
        remove('tmp.zip')
    img_copy = Image.fromarray(arr.reshape(img.height, img.width, ch))
    img_copy.save(new_img)
    print(f"Immagine salvata come \33[33m{new_img}\33[0m")
    return (img_copy, n, div, total_bytes)

def string_to_bytes(bit_string):
    byte_array = bytearray()
    # it is not necessary that len(bit_string) is a multiple of 8
    for i in range(0, len(bit_string), 8):
        byte = bit_string[i:i+8]
        byte_array.append(int(byte, 2))
    return byte_array

def getBinFile(img: Image, new_file_path: str, zipMode: int, n: int, div: float, size: int) -> None: # with arr -> faster
    """Ottieni un file binario da un'immagine"""
    system('cls')
    # check if n is in range
    if n < 1 or n > 8:
        print("\33[1;31mERROR\33[0m: \33[32mn\33[0m deve essere compreso tra 1 e 8")
        system("pause")
        return
    # check if zipMode is in range
    if zipMode not in [0, 1, 2]:
        print("\33[1;31mERRORE\33[0m: zipMode deve essere 0, 1 o 2")
        system("pause")
        return img, -1, -1.0, -1
    arcobaleno("RICERCA FILE")
    print("...")
    # start getting file
    arr = np.array(img).flatten().copy()
    bits, res = "", ""
    ind, pos = 0, 0
    diff = size*8
    err = round(size*8/n)
    start_time = time.time()
    if zipMode != NO_ZIP:
        res = new_file_path
        new_file_path = "tmp.zip"
    with open(new_file_path, 'wb') as file:
        for i in range(err):
            if diff < n:
                bits += format(arr[pos], '08b')[-diff:]
            else:
                bits += format(arr[pos], '08b')[-n:] # get last n bits
            if len(bits) >= 1024:
                wr = bits[:1024]
                wr = string_to_bytes(wr)
                file.write(wr)
                bits = bits[1024:]
            ind += div
            pos = round(ind)
            # check if file is not found
            if (i+1) % 1000000 == 0:
                system("cls")
                arcobaleno("RICERCA FILE")
                print("...")
                progress = i / (size*8//n)
                elapsed_time = time.time() - start_time
                print(f"Elaborazione in corso: {format(progress * 100, '.2f')}%")
                print(f"Tempo rimanente: {timeDisplay(elapsed_time *(1 - progress) / progress)}")                
        if len(bits):
            bits = string_to_bytes(bits)
            file.write(bits)
        file.close()
        system("cls")
        arcobaleno("RICERCA FILE")
        print("...")
        print("Elaborazione in corso: 100.0%")
        if zipMode == NO_ZIP:
            print(f"\33[1;32mFILE TROVATO\33[0m\nFile salvato come \33[33m{new_file_path}\33[0m")
        elif zipMode == FILE:
            print("Decompressione file...")
            # unzip file
            try:
                with zipfile.ZipFile(new_file_path, 'r') as zf:
                    old_path = zf.namelist()[0]
                    file_data = zf.read(old_path)
                    zf.close()
                remove(new_file_path)
                with zipfile.ZipFile(new_file_path, 'w') as zf:
                    zf.writestr(res, file_data)
                    zf.close()
                with zipfile.ZipFile(new_file_path, 'r') as zf:
                    zf.extractall()
                    zf.close()
                    remove(new_file_path)
                    print(f"\33[1;32mFILE TROVATO\33[0m\nFile salvato come \33[33m{res}\33[0m")
            except Exception as e:
                print(f"Errore durante l'estrazione: {e}")
        else:
            print("Decompressione directory...")
            try:
                with zipfile.ZipFile(new_file_path, 'r') as zf:
                    zf.extractall(res)
                    # delete tmp.zip
                    zf.close()
                    remove(new_file_path)
                    print(f"\33[1;32mDIRECTORY TROVATA\33[0m\nDirectory salvata come \33[33m{res}\33[0m")
            except Exception as e:
                print(f"Errore durante l'estrazione: {e}")

# big lsb -> img1 big distorsion
# small msb -> img2 low quality
def hideImage(img1: Image, img2: Image, new_img: str, lsb=0, msb=8, div=0): # -> (Image, int, int, float, int, int) # put img2 in img1 and return info for decryption
    """Nasconde un'immagine in un'altra
        lsb: number of less significant bits of img1 to change
        msb: number of most significant bits of img2 to put in img1"""
    system('cls')
    # check if lsb is valid
    if lsb < 0 or lsb > 8:
        print("\33[1;31mERRORE\33[0m: il valore di \33[36mlsb\33[0m deve essere compreso tra 1 e 8 oppure 0 per la modalita' automatica")
        system("pause")
        return img1, -1, -1, -1.0, -1, -1
    # check if msb is valid
    if msb < 0 or msb > 8:
        print("\33[1;31mERRORE\33[0m: il valore di \33[34mmsb\33[0m deve essere compreso tra 1 e 8 oppure 0 per la modalita' automatica")
        system("pause")
        return img1, -1, -1, -1.0, -1, -1
    # check if lsb is bigger than msb
    if lsb > msb:
        print("\33[1;31mERRORE\33[0m: il valore di \33[36mlsb\33[0m deve essere minore di \33[34mmsb\33[0m")
        system("pause")
        return img1, -1, -1, -1.0, -1, -1
    # determine auto lsb and msb
    while lsb == 0:
        if msb == 0:
            f1 = img1.filename.split("\\")[-1]
            f2 = img2.filename.split("\\")[-1]
            print(f"\33[1;31mERRORE\33[0m: Immagine \33[31m{f1}\33[0m troppo piccola per nascondere l'immagine \33[31m{f2}\33[0m")
            system("pause")
            return img1, -1, -1, -1.0, -1, -1
        while((lsb * img1.width * img1.height) < (msb * img2.width * img2.height)):
            lsb += 1
            if lsb > msb:
                lsb = 0
                msb -= 1
    # check if image is big enough
    if (lsb * img1.width * img1.height) < (msb * img2.width * img2.height):
        f1 = img1.filename.split("\\")[-1]
        f2 = img2.filename.split("\\")[-1]
        print(f"\33[31mERRORE\33[0m: Immagine \33[31m{f1}\33[0m troppo piccola per nascondere l'immagine \33[31m{f2}\33[0m")
        system("pause")
        return img1, -1, -1, -1.0, -1, -1
    # convert image to RGB
    if img1.mode != "RGB":
        img1 = img1.convert("RGB")
    if img2.mode != "RGB":
        img2 = img2.convert("RGB")
    # start hiding image
    # put in the lsb less significant bits of each pixel of img1
    # the msb most significant bits of each pixel of img2
    arr1 = np.array(img1).flatten().copy() # flatten() returns a copy of the array collapsed into one dimension
    arr2 = np.array(img2).flatten().copy()
    total_pixels_ch = len(arr2)
    start_time = time.time()
    if div == 0:
        div = (len(arr1) * lsb) / (len(arr2) * msb)
    else:
        if div * len(arr2) * msb > len(arr1) * lsb:
            print("\33[1;31mERRORE\33[0m: il valore di \33[35mdiv\33[0m e' eccessivo, prova 0")
            system("pause")
            return img1, -1, -1, -1.0, -1, -1
    i, j = 0, 0
    arcobaleno("OCCULTAMENTO IMMAGINE")
    print("...")
    pos = 0
    bit_queue = ""
    while i < len(arr2):
        # extract msb bits from each channel of arr2
        r, g, b = arr2[i], arr2[i + 1], arr2[i + 2]
        bit_queue += format(r, '08b')[:msb] + format(g, '08b')[:msb] + format(b, '08b')[:msb]
        while len(bit_queue) >= lsb * 3:
            # extract lsb bits from each channel of arr1
            r_bits, g_bits, b_bits = bit_queue[:lsb], bit_queue[lsb:2*lsb], bit_queue[2*lsb:3*lsb]
            arr1[j] = setLastNBits(arr1[j], r_bits, lsb)
            arr1[j + 1] = setLastNBits(arr1[j + 1], g_bits, lsb)
            arr1[j + 2] = setLastNBits(arr1[j + 2], b_bits, lsb)
            # remove lsb bits from bit_queue
            bit_queue = bit_queue[lsb*3:]
            pos += 3 * div
            j = round(pos)
        i += 3
        if i % 180000 == 0:  # Change this number to control how often the progress is printed
            system("cls")
            arcobaleno("OCCULTAMENTO IMMAGINE")
            print("...")
            progress = i / total_pixels_ch
            elapsed_time = time.time() - start_time
            print(f"Elaborazione in corso: {format(progress * 100, '.2f')}%")
            print(f"Tempo rimanente: {timeDisplay(elapsed_time * (1 - progress) / progress)}")
    # convert arr1 to image
    w, h = img2.width, img2.height
    system("cls")
    arcobaleno("OCCULTAMENTO IMMAGINE")
    print("...")
    print("Elaborazione in corso: 100.0%")
    print("Tempo rimanente: 0 secondi")
    print(f"\33[1;32mTERMINATO\n\33[0mPercentuale di pixel usati con \33[36mlsb\33[0m={lsb}, \33[34mmsb\33[0m={msb} e \33[35mdiv\33[0m={div}: {format((msb * img2.width * img2.height) / (lsb * img1.width * img1.height) * 100, '.2f')}%")
    img1_copy = Image.fromarray(arr1.reshape(img1.height, img1.width, 3)) # save the copy so img1 is not modified
    img1_copy.save(new_img)
    print(f"Immagine salvata come \33[33m{new_img}\33[0m")
    return (img1_copy, lsb, msb, div, w, h)

def getImage(img: Image, new_img: str, lsb: int, msb: int, div: float, width: int, height: int) -> Image: # get img2 from img1
    """Ottieni un'immagine da un'altra"""
    system('cls')
    arcobaleno("RICERCA IMMAGINE")
    print("...")
    start_time = time.time()
    size = width * height * 3
    arr = np.array(img).flatten().copy() 
    res = np.zeros(size , dtype = np.uint8)
    bits = ""
    pos, j, n = 0, 0, 0
    while n < size:
        # get the lsb less significant bits of each pixel of img1
        bits += format(arr[j], '08b')[-lsb:] # remove the lsb less significant bits
        if len(bits) >= msb:
            tmp = bits[:msb]
            # add 0s to tmp to get a byte
            while len(tmp) < 8:
                tmp += "0"
            # get the msb most significant bits of each pixel of img2
            res[n] = int(tmp, 2)
            n += 1
            bits = bits[msb:]
        pos += div
        j = round(pos)
        if (n+1) % 180000 == 0:
            system("cls")
            arcobaleno("RICERCA IMMAGINE")
            print("...")
            progress = n / size
            print(f"Elaborazione in corso: {format(progress * 100, '.2f')}%")
            elapsed_time = time.time() - start_time
            print(f"Tempo rimanente: {timeDisplay(elapsed_time * (1 - progress) / progress)}")
    system("cls")
    arcobaleno("RICERCA IMMAGINE")
    print("...")
    print("Elaborazione in corso: 100.0%")
    print("Tempo rimanente: 0 secondi")
    # convert res to image
    res = Image.fromarray(res.reshape(height, width, 3))
    res.save(new_img)
    print(f"\33[1;32mIMMAGINE TROVATA\n\33[0mImmagine salvata come \33[33m{new_img}\33[0m")
    return res

def subMode() -> int:
    system("cls")
    print("Cosa vuoi fare?")
    print("1. Nascondere dati")
    print("2. Recuperare dati")
    ret = input("--> ")
    while ret == "" or not str(ret).isdigit() or int(ret) not in [1, 2]:  
        print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
        system("pause")
        system("cls")
        print("Cosa vuoi fare?")
        print("1. Nascondere dati")
        print("2. Recuperare dati")
        ret = input("--> ")
    return int(ret)

def imgInput() -> Image:
    while True:
        system("cls")
        print("Inserisci il nome dell'immagine su cui nascondere i dati")
        img = input("Immagine --> ")
        try:
            img = Image.open(img)
            break
        except:
            print("\33[1;31mERRORE\33[0m: immagine non trovata")
            system("pause")
    return img

def imgInput2() -> Image:
    while True:
        system("cls")
        print("Inserisci il nome dell'immagine da nascodere")
        img = input("Immagine --> ")
        try:
            img = Image.open(img)
            break
        except:
            print("\33[1;31mERRORE\33[0m: immagine non trovata")
            system("pause")
    return img

def msginput() -> str:
    system("cls")
    print("Inserisci il messaggio da nascondere")
    msg = input("Messaggio --> ")
    return msg

def imgOutput(imgIn=None) -> str:
    system("cls")
    flag = False
    print("Inserisci il nome dell'immagine di output")
    if imgIn != None and imgIn.mode == "RGBA":
        print("NOTA: l'immagine di output dovra' essere in formato PNG per preservare la trasparenza")
        flag = True
    new_img = input("Immagine --> ")
    if flag:
        while new_img[-4:] != ".png":
            print("\33[1;31mERRORE\33[0m: l'immagine di output deve essere in formato PNG")
            system("pause")
            system("cls")
            print("Inserisci il nome dell'immagine di output")
            new_img = input("Immagine --> ")
    else:
    # controlla se il file di output è un'immagine
        while new_img[-4:] != ".png" and new_img[-4:] != ".jpg" and new_img[-5:] != ".jpeg":
            print("\33[1;31mERRORE\33[0m: il file di output deve essere un'immagine")
            system("pause")
            system("cls")
            print("Inserisci il nome dell'immagine di output")
            new_img = input("Immagine --> ")  
    return new_img

def fileOutput() -> str:
    while True:
        system("cls")
        print("Inserisci il nome del file di output")
        out = input("File --> ")
        try:
            f = open(out, 'w')
            f.close()
            break
        except:
            print("\33[1;31mERRORE\33[0m: file non trovato")
            system("pause")
    return out

def imgInputReq() -> Image:
    while True:
        system("cls")
        print("Inserisci il nome dell'immagine da cui recuperare i dati")
        img = input("Immagine --> ")
        try:
            img = Image.open(img)
            break
        except:
            print("\33[1;31mERRORE\33[0m: immagine non trovata")
            system("pause")
    return img

def fileInput() -> str:
    while True:
        system("cls")
        print("Inserisci il nome del file da nascondere")
        file = input("File --> ")
        try:
            f = open(file, 'r')
            f.close()
            break
        except:
            print("\33[1;31mERRORE\33[0m: file non trovato")
            system("pause")
    return file

def binInput() -> str:
    while True:
        system("cls")
        print("Inserisci il nome del file o directory da nascondere")
        path = input("Dati --> ")
        try:
            if isfile(path):
                f = open(path, 'rb')
                f.close()
                break
            elif isdir(path) and exists(path):
                break
        except:
            print("\33[1;31mERRORE\33[0m: percorso non trovato")
            system("pause")
    return path

def binOutput() -> str:
    while True:
        system("cls")
        print("Inserisci il nome del file o directory di output")
        out = input("Dati --> ")
        try:
            if out != "":
                break
        except:
            print("\33[1;31mERRORE\33[0m: percorso non valido")
            system("pause")
    return out

def parametriFacoltativi() -> bool:
    system("cls")
    print("Vuoi utilizzare i parametri di default? (Y/N)")
    ans = input("--> ")
    ans = ans.upper()
    while ans == "" or (ans != "Y" and ans != "N"):
        print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
        system("pause")
        system("cls")
        print("Vuoi utilizzare i parametri di default? (Y/N)")
        ans = input("--> ")
        ans = ans.upper()
    return ans == "N"

def parametriBackup(mode: int) -> bool:
    ret = False
    system("cls")
    print("Vuoi utilizzare i parametri di backup? (Y/N)")
    ans = input("--> ")
    ans = ans.upper()
    while ans == "" or (ans != "Y" and ans != "N"):
        print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
        system("pause")
        system("cls")
        print("Vuoi utilizzare i parametri di backup? (Y/N)")
        ans = input("--> ")
        ans = ans.upper()
    if ans == "N":
        return ret
    else:
        ret = True
        system("cls")
        print("Quali parametri vuoi usare?")
        print("1. Recenti")
        print("2. Da file")
        ans = input("--> ")
        while ans == "" or not str(ans).isdigit() or int(ans) not in [1, 2]:
            print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
            system("pause")
            system("cls")
            print("Quali parametri vuoi usare?")
            print("1. Recenti")
            print("2. Da file")
            ans = input("--> ")
        if int(ans) == 1:
            return ret
        if int(ans) == 2:
            while True:
                system("cls")
                print("Inserisci il nome del file")
                path = input("File di backup --> ")
                try:
                    if isfile(path):
                        f = open(path, 'rb')
                        f.close()
                        break
                except:
                    print("\33[1;31mERRORE\33[0m: percorso non trovato")
                    system("pause")
            recoverData(path)
            return ret
            
def nInput(get=1) -> int:
    system("cls")
    print("Inserisci il numero di bit da modificare nell'immagine che nasconde i dati")
    if not get: print("NOTA: 0 per la modalita' automatica")
    n = input("\33[32mn\33[0m --> ")
    if not get:
        while n == "" or not str(n).isdigit() or int(n) < 0 or int(n) > 8:
            print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
            system("pause")
            system("cls")
            print("Inserisci il numero di bit da modificare nell'immagine che nasconde i dati")
            print("NOTA: 0 per la modalita' automatica")
            n = input("\33[32mn\33[0m --> ")
    else:
        while n == "" or not str(n).isdigit() or int(n) < 1 or int(n) > 8:
            print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
            system("pause")
            system("cls")
            print("Inserisci il numero di bit da modificare nell'immagine che nasconde i dati")
            n = input("\33[32mn\33[0m --> ")
    return int(n)

def divInput(get=1) -> int:
    system("cls")
    print("Inserisci il valore di \33[35mdiv\33[0m")
    if not get: print("NOTA: 0 per la modalita' automatica")
    div = input("\33[35mdiv\33[0m --> ")
    if not get:
        while div == "" or not str(div).isdigit() or int(div) < 0:
            print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
            system("pause")
            system("cls")
            print("Inserisci il valore di \33[35mdiv\33[0m")
            print("NOTA: 0 per la modalita' automatica")
            div = input("\33[35mdiv\33[0m --> ")
    else:
        while div == "" or not str(div).isdigit() or int(div) < 1:
            print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
            system("pause")
            system("cls")
            print("Inserisci il valore di \33[35mdiv\33[0m")
            div = input("\33[35mdiv\33[0m --> ")
    return int(div)

def LMInput(get=1): # -> (int, int)
    system("cls") # msb
    print("Inserisci il valore \33[34mmsb\33[0m di bit piu' significativi da nascondere della seconda immagine")
    if not get: print("NOTA: 0 per la modalita' automatica")
    msb = input("\33[34mmsb\33[0m --> ")
    if not get:
        while msb == "" or not str(msb).isdigit() or int(msb) < 0 or int(msb) > 8:
            print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
            system("pause")
            system("cls")
            print("Inserisci il numero di bit da modificare nell'immagine che nasconde i dati")
            print("NOTA: 0 per la modalita' automatica")
            msb = input("\33[34mmsb\33[0m --> ")
    else:
        while msb == "" or not str(msb).isdigit() or int(msb) < 1 or int(msb) > 8:
            print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
            system("pause")
            system("cls")
            print("Inserisci il numero di bit da modificare nell'immagine che nasconde i dati")
            msb = input("\33[34mmsb\33[0m --> ")
    system("cls") # lsb
    print("Inserisci il valore \33[36mlsb\33[0m di bit meno significativi da modificare nella prima immagine")
    if not get: print("NOTA: 0 per la modalita' automatica")
    print("NOTA: \33[36mlsb\33[0m deve essere minore o uguale a \33[34mmsb\33[0m")
    lsb = input("\33[36mlsb\33[0m --> ")
    if not get:
        while lsb == "" or not str(lsb).isdigit() or int(lsb) < 0 or int(lsb) > 8 or int(lsb) > int(msb):
            print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
            system("pause")
            system("cls")
            print("Inserisci il numero di bit da modificare nell'immagine che nasconde i dati")
            print("NOTA: 0 per la modalita' automatica")
            print("NOTA: \33[36mlsb\33[0m deve essere minore o uguale a \33[34mmsb\33[0m")
            lsb = input("\33[36mlsb\33[0m --> ")
    else:
        while lsb == "" or not str(lsb).isdigit() or int(lsb) < 1 or int(lsb) > 8 or int(lsb) > int(msb):
            print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
            system("pause")
            system("cls")
            print("Inserisci il numero di bit da modificare nell'immagine che nasconde i dati")
            print("NOTA: \33[36mlsb\33[0m deve essere minore o uguale a \33[34mmsb\33[0m")
            lsb = input("\33[36mlsb\33[0m --> ")
    return (int(lsb), int(msb))

def WHInput(): # -> (int, int)
    system("cls")
    print("Inserisci la larghezza dell'immagine da recuperare")
    w = input("Larghezza --> ")
    while w == "" or not str(w).isdigit() or int(w) < 1:
        print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
        system("pause")
        system("cls")
        print("Inserisci la larghezza dell'immagine da recuperare")
        w = input("Larghezza --> ")
    system("cls")
    print("Inserisci l'altezza dell'immagine da recuperare")
    h = input("Altezza --> ")
    while h == "" or not str(h).isdigit() or int(h) < 1:
        print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
        system("pause")
        system("cls")
        print("Inserisci l'altezza dell'immagine da recuperare")
        h = input("Altezza --> ")
    return (int(w), int(h))

def zipModeInput(path: str) -> int:
    if isdir(path):
        return DIR
    elif isfile(path):
        system("cls")
        print("Vuoi comprimere il file? (Y/N)")
        ans = input("--> ")
        ans = ans.upper()
        while ans == "" or (ans != "Y" and ans != "N"):
            print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
            system("pause")
            system("cls")
            print("Vuoi comprimere il file? (Y/N)")
            ans = input("--> ")
            ans = ans.upper()
        if ans == "N":
            return NO_ZIP
        else:
            return FILE
    else:
        system("cls")
        print("\33[1;31mERRORE\33[0m: problema con il file")
        system("pause")
        return -1
        
def zipModeGet() -> int:
    system("cls")
    print("I dati che cerchi sono compressi? (Y/N)")
    ans = input("--> ")
    ans = ans.upper()
    while ans == "" or (ans != "Y" and ans != "N"):
        print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
        system("pause")
        system("cls")
        print("I dati che cerchi sono compressi? (Y/N)")
        ans = input("--> ")
        ans = ans.upper()
    if ans == "N":
        return NO_ZIP
    else:
        system("cls")
        print("I dati che cerchi sono in un file o in una directory? (F/D)")
        ans = input("--> ")
        ans = ans.upper()
        while ans == "" or (ans != "F" and ans != "D"):
            print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
            system("pause")
            system("cls")
            print("I dati che cerchi sono in un file o in una directory? (F/D)")
            ans = input("--> ")
            ans = ans.upper()
        if ans == "F":
            return FILE
        else:
            return DIR

def sizeInput() -> int:
    system("cls")
    print("Inserisci la dimensione del file da nascondere")
    size = input("Dimensione --> ")
    while size == "" or not str(size).isdigit() or int(size) < 1:
        print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
        system("pause")
        system("cls")
        print("Inserisci la dimensione del file da nascondere")
        size = input("Dimensione --> ")
    return int(size)

def bytes_to_kb_or_mb(bytes_value: int) -> str:
    kb = bytes_value / 1024
    if kb < 1024:  # meno di 1 MB
        return f"{kb:.2f} KB"
    mb = kb / 1024
    return f"{mb:.2f} MB"

def contains(img: Image, mode: int) -> int:
    system("cls")
    print("L'immagine selezionata puo' contenere:")
    if img.mode == "RGB":
            ch = 3
    elif img.mode == "RGBA":
            ch = 4
    pixels_ch = img.width * img.height * ch
    if mode == 2 or mode == 4:
        for i in range(1, 9):
            c = round((pixels_ch * i) / 8)
            print(f"Per \33[32mn\33[0m={i}: {bytes_to_kb_or_mb(c)}")
    else:
        for i in range(1, 9):
            c = round((pixels_ch * i) / 8)
            print(f"Per \33[32mn\33[0m={i}: {c} pixels da {ch} canali")
    system("pause")
    return c

def saveData()-> None:
    global n_backup, div_backup, lsb_backup, msb_backup, size_backup, zipMode_backup
    global w_backup, h_backup, img_with_data_name_backup, mode_backup
    system("cls")
    print("Vuoi salvare i dati? (Y/N)")
    ans = input("--> ")
    ans = ans.upper()
    while ans == "" or (ans != "Y" and ans != "N"):
        print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
        system("pause")
        system("cls")
        print("Vuoi salvare i dati? (Y/N)")
        ans = input("--> ")
        ans = ans.upper()
    if ans == "Y":
        while True:
            system("cls")
            print("Inserisci il nome del file di output")
            out = input("File --> ")
            try:
                f = open(out, 'w')
                f.close()
                break
            except:
                print("\33[1;31mERRORE\33[0m: file non creato correttamente")
                system("pause")
        backup = [n_backup, div_backup, lsb_backup, msb_backup, size_backup, w_backup, h_backup, img_with_data_name_backup, zipMode_backup, mode_backup]
        with open(out, "wb") as file:
            pickle.dump(backup, file)
        system("cls")
        print("\33[1;32mDATI SALVATI\33[0m")
        system("pause")

def recoverData(file: str) -> None:
    global n_backup, div_backup, lsb_backup, msb_backup, size_backup, zipMode_backup
    global w_backup, h_backup, img_with_data_backup, img_with_data_name_backup, mode_backup
    with open(file, "rb") as file:
        backup = pickle.load(file)
    n_backup = backup[0]
    div_backup = backup[1]
    lsb_backup = backup[2]
    msb_backup = backup[3]
    size_backup = backup[4]
    w_backup = backup[5]
    h_backup = backup[6]
    img_with_data_name_backup = backup[7]
    zipMode_backup = backup[8]
    mode_backup = backup[9]
    system("cls")
    print("Hai cambiato nome all'immagine con i dati? (Y/N)")
    ans = input("--> ")
    ans = ans.upper()
    while ans == "" or (ans != "Y" and ans != "N"):
        system("cls")
        print("Hai cambiato nome all'immagine con i dati? (Y/N)")
        ans = input("--> ")
        ans = ans.upper()
    if ans == "Y":
        while True:
            system("cls")
            print("Inserisci il nome dell'immagine con i dati")
            img = input("Immagine --> ")
            try:
                img_with_data_name_backup = img
                img = Image.open(img)
                img.close()
                break
            except:
                print("\33[1;31mERRORE\33[0m: immagine non trovata")
                system("pause")
    img_with_data_backup = Image.open(img_with_data_name_backup)
    
# AREA DI BACKUP
n_backup = 0
div_backup = 0
lsb_backup = 0
msb_backup = 0
size_backup = 0
w_backup = 0
h_backup = 0
img_with_data_backup = ""
img_with_data_name_backup = ""
zipMode_backup = NO_ZIP
mode_backup = 0
       
def mode(mod: int) -> bool:
    global n_backup, div_backup, lsb_backup, msb_backup, size_backup, zipMode_backup
    global w_backup, h_backup, img_with_data_backup, img_with_data_name_backup, mode_backup
    system("cls")
    
    # hideMessage()
    if mod == 1:
        sub = subMode()
        if sub == 1:
            img = imgInput()
            msg = msginput()
            new_img = imgOutput()
            img_with_data_backup = hideMessage(img, msg, new_img)
            img_with_data_name_backup = new_img
            mode_backup = 1
            system("pause")
            saveData()
            return True
        elif sub == 2:
            if parametriBackup(1):
                img = img_with_data_backup
            else:
                img = imgInputReq()
            print("Il messaggio e':")
            try:
                print(getMessage(img))
            except:
                print("\33[1;31mERRORE\33[0m: nessun messaggio trovato")
            system("pause")
            return True
    
    # hideFile()
    elif mod == 2:
        sub = subMode()
        if sub == 1:
            img = imgInput()
            mx = contains(img, 2)
            file = fileInput()
            while mx < getsize(file):
                system("cls")
                print("\33[1;31mERRORE\33[0m: il file e' troppo grande per essere nascosto")
                system("pause")
                file = fileInput()
            new_img = imgOutput()
            if parametriFacoltativi():
                n = nInput(0)
                div = divInput(0)
            else:
                n = 0
                div = 0
            img_with_data_backup, n_backup, div_backup = hideFile(img, file, new_img, n, div)
            img_with_data_name_backup = new_img
            mode_backup = 2
            system("pause")
            saveData()
            return True
        elif sub == 2:
            if parametriBackup(2):
                img = img_with_data_backup
                n = n_backup
                div = div_backup
                new_file = fileOutput()
            else:
                img = imgInputReq()
                new_file = fileOutput()
                n = nInput()
                div = divInput()
            getFile(img, new_file, n, div)
            system("pause")
            return True
        
    # hideImage()
    elif mod == 3:
        sub = subMode()
        if sub == 1:
            img1 = imgInput()
            mx = contains(img1, 3)
            img2 = imgInput2()
            if img2.mode == "RGB":
                ch = 3
            elif img2.mode == "RGBA":
                ch = 4
            while mx < img2.width * img2.height * ch:
                system("cls")
                print("\33[1;31mERRORE\33[0m: l'immagine e' troppo grande per essere nascosta")
                system("pause")
                img2 = imgInput2()
                if img2.mode == "RGB":
                    ch = 3
                elif img2.mode == "RGBA":
                    ch = 4
            new_img = imgOutput()
            if parametriFacoltativi():
                lsb, msb = LMInput(0)
                div = divInput(0)
            else:
                lsb = 0
                msb = 8
                div = 0
            img_with_data_backup, lsb_backup, msb_backup, div_backup, w_backup, h_backup = hideImage(img1, img2, new_img, lsb, msb, div)
            img_with_data_name_backup = new_img
            mode_backup = 3
            system("pause")
            saveData()
            return True
        elif sub == 2:
            if parametriBackup(3):
                img = img_with_data_backup
                lsb = lsb_backup
                msb = msb_backup
                div = div_backup
                w = w_backup
                h = h_backup
                new_img = imgOutput()
            else:
                img = imgInputReq()
                lsb, msb = LMInput()
                div = divInput()
                w, h = WHInput()
                new_img = imgOutput()
            getImage(img, new_img, lsb, msb, div, w, h)
            system("pause")
            return True
    
    # hideBinFile()
    elif mod == 4:
        sub = subMode()
        if sub == 1:
            img = imgInput()
            mx = contains(img, 4)
            file = binInput()
            while mx < (getsize(file) if isfile(file) else getDirSize(file)):
                system("cls")
                print("\33[1;31mERRORE\33[0m: i dati sono troppi per essere nascosti")
                system("pause")
                file = binInput()
            new_img = imgOutput(img)
            zipMode = zipModeInput(file)
            if parametriFacoltativi():
                n = nInput(0)
                div = divInput(0)
            else:
                n = 0
                div = 0
            zipMode_backup = zipMode
            img_with_data_backup, n_backup, div_backup, size_backup = hideBinFile(img, file, new_img, zipMode, n, div)
            img_with_data_name_backup = new_img
            mode_backup = 4
            system("pause")
            saveData()
            return True
        elif sub == 2:
            if parametriBackup(4):
                img = img_with_data_backup
                n = n_backup
                div = div_backup
                zipMode = zipMode_backup
                size = size_backup
                new_file = binOutput()
            else:
                img = imgInputReq()
                n = nInput()
                div = divInput()
                zipMode = zipModeGet()
                size = sizeInput()
                new_file = binOutput()
            getBinFile(img, new_file, zipMode, n, div, size)
            system("pause")
            return True 
    # exit
    else:
        return False
    
def start() -> None:
    system("cls")
    print("Con cosa vuoi operare?")
    print("1. Stringhe di testo")
    print("2. File a caratteri")
    print("3. Immagini dentro immagini")
    print("4. File binari")
    print("5. \33[31mESCI\33[0m")
    ans = input("--> ")
    while ans == "" or not str(ans).isdigit() or int(ans) not in [1,2,3,4,5]:
        print("\33[1;31mERRORE\33[0m: inserisci un valore valido")
        system("pause")
        system("cls")
        print("Con cosa vuoi operare?")
        print("1. Stringhe di testo")
        print("2. File a caratteri")
        print("3. Immagini dentro immagini")
        print("4. File binari")
        print("5. \33[31mESCI\33[0m")
        ans = input("--> ")
    ret = mode(int(ans))
    if ret:
        start()
    
def ascii_art() -> None:
    colors = ["red","yellow","green","cyan","blue","magenta"]
    str = "STEGANOGRAFIA\nversione 2.077"
    print(colored(figlet_format(str, font="slant"), colors[randint(0,5)], 'on_black', ['bold', 'blink']), end='')
    print("by ", end='')
    arcobaleno("Giuseppe Bellamacina")
    print("\n")
    system("pause")

def main():
    system("cls")
    colorama.init()
    ascii_art()
    start()

main()