from os import system, remove, walk, getcwd, rename
from os.path import getsize, splitext, join, relpath
from PIL import Image
import numpy as np
import zipfile
from termcolor import colored
import time

# zipModes
NO_ZIP = 0
FILE = 1
DIR = 2

def arcobaleno(str: str) -> None:
    colors = ["red","yellow","green","cyan","blue","magenta"]
    for i in range(len(str)):
        print(colored(str[i], colors[i%len(colors)], 'on_black', ['bold', 'blink']), end='')

def binaryConvert(text: str) -> str:
    """Converts a string of text to binary (char by char)"""
    return ''.join(format(ord(char), '08b') for char in text)

def binaryConvertBack(text: str) -> str:
    """Converts a string of binary to text"""
    return ''.join(chr(int(text[i*8:i*8+8],2)) for i in range(len(text)//8))

def setLastBit(value: int, bit: str) -> int:
    """Sets the last bit of a value"""
    value = format(value, '08b') # convert int to binary string
    value[-1] = bit # change last bit
    value = int(value, 2) # convert binary string to int
    value = min(255, max(0, value)) # check if value is in range
    return value

def setLastNBits(value: int, bits: str, n: int) -> int:
    """Sets the last n bits of a value"""
    value = format(value, '08b')
    if len(bits) < n:
        n = len(bits)
    value = value[:-n] + bits
    value = int(value, 2)
    value = min(255, max(0, value))
    return value

def setComponetOfColor(mat: np.array, i: int, j: int, color: int, channel: int) -> np.array:
    if channel == 0:
        mat[i,j] = (color, mat[i,j][1], mat[i,j][2])
    elif channel == 1:
        mat[i,j] = (mat[i,j][0], color, mat[i,j][2])
    elif channel == 2:
        mat[i,j] = (mat[i,j][0], mat[i,j][1], color)
    return mat
    

def hideMessage(img: Image, msg: str, new_img: str) -> Image:
    """Hides a message in a image"""
    system('cls')
    # check if image is big enough
    if (img.width * img.height) * 3 < len(msg) * 8:
        f = img.filename.split("\\")[-1]
        print(f"\33[1;31mERROR\33[0m: Image \33[1;31m{f}\33[0m too small to hide message")
        exit()
    # convert image to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    # start hiding message
    arcobaleno("HIDING MESSAGE")
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
                    color = mat[i,j][z] # get color
                    color = setLastBit(color, bit) # change last bit
                    mat = setComponetOfColor(mat, i, j, color, z) # set color
                else:
                    break
    print(f"\33[1;32mFINISHED\33[0m\nPercentage of pixels used: {format(((len(msg) / ((img.width * img.height) * 3)) * 100), '.2f')}%")
    print(f"Image saved as \33[1;33m{new_img}\33[0m")
    img_copy.save(new_img)
    return img_copy

def getMessage(img: Image) -> str:
    """Gets a message from a image"""
    system('cls')
    # convert image to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    # start getting message
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

def hideFile_with_mat(img: Image, file: str, new_img: str, n=0, div=0) -> (Image, int):
    """Hides a file in a image"""
    system('cls')
    # check if n is in range
    if n < 0 or n > 8:
        print("\33[1;31mERROR\33[0m: n must be between 1 and 8 or 0 for auto")
        exit()
    # auto n
    if n == 0:
        while (img.width * img.height) * 3 * n < getsize(file) * 8:
            n += 1
            if n > 8:
                f = img.filename.split("\\")[-1]
                print(f"\33[1;31mERROR\33[0m: Image \33[1;31m{f}\33[0m too small to hide file")
                exit()
    # check if image is big enough
    if (img.width * img.height) * 3 * n < getsize(file) * 8:
        f = img.filename.split("\\")[-1]
        print(f"\33[1;31mERROR\33[0m: Image \33[1;31m{f}\33[0m too small to hide file")
        exit()
    # convert image to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    # check if div value is valid
    if div == 0:
        div = ((img.width * img.height) * 3 * n) // (getsize(file) * 8)
    else:
        if img.width * img.height * 3 * n < div * getsize(file) * 8:
            print("\33[1;31mERROR\33[0m: div value too big")
            exit()
    # start hiding file
    arcobaleno("HIDING FILE")
    print("...")
    img_copy = img.copy()
    mat = img_copy.load() # so that mat_or doesn't change
    x, y, z = 0, 0, 0
    start_time = time.time()
    # read file by line
    with open(file, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for line in f)
        f.seek(0)  # go back to the start of the file
        rsv = ""
        for i, line in enumerate(f): # enumerate() returns a tuple with the index and the value
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
                mat = setComponetOfColor(mat, x, y, color, z)
                # go to next pixel/component
                for w in range(div):
                    z = (z + 1) % 3
                    if z == 0:
                        y = (y + 1) % img.height
                        if y == 0:
                            x = (x + 1) % img.width     
            if (i + 1) % 1000 == 0:  # Change this number to control how often the progress is printed
                system('cls')
                arcobaleno("HIDING FILE")
                print("...")
                progress = (i + 1) / total_lines
                elapsed_time = time.time() - start_time
                print(f"Elaboration {i + 1} of {total_lines} lines ({format((progress) * 100, '.2f')}%)")
                print(f"Remaining time: {format(elapsed_time *(1 - progress) / progress, '.2f')} seconds")
    rsv = list(rsv)
    # if there are still bits left, hide them
    while rsv != []:
        bit = ""
        for k in range(n):
            if len(rsv) >= n-k:
                bit += rsv.pop(0)
            else:
                bit += "0"
        color = mat[x,y][z]
        color = setLastNBits(color, bit, n)
        mat = setComponetOfColor(mat, x, y, color, z)
        # go to next pixel/component
        for w in range(div):
            z = (z + 1) % 3
            if z == 0:
                y = (y + 1) % img.height
                if y == 0:
                    x = (x + 1) % img.width
    f.close()
    # print percentage of pixels used
    system('cls')
    arcobaleno("HIDING FILE")
    print("...")
    print(f"Elaboration {total_lines} of {total_lines} lines (100.0%)")
    print("Remaining time: 0.00 seconds")
    print(f"\33[1;32mFINISHED\33[0m\nPercentage of pixels used with n={n}: {format(((getsize(file) * 8) / ((img.width * img.height) * 3 * n)) * 100, '.2f')}%")
    img_copy.save(new_img)
    print(f"Image saved as \33[1;33m{new_img}\33[0m")
    return (img_copy, div)

def oldfindDiv(dim: int, file: str, n: int) -> int:
    image_dim = dim * n
    div = (image_dim // (getsize(file) * 8))
    index = (getsize(file)-1) * 8 * div
    image_dim = (div+1) * image_dim - index
    div = (image_dim // (getsize(file) * 8))
    return div

def findDiv(dim: int, file: str, n: int) -> float:
    image_dim = dim * n
    div = ((image_dim - n) / (getsize(file) * 8))
    return div

def hideFile(img: Image, file: str, new_img: str, n=0, div=0) -> (Image, int, int): # with arr -> faster and better
    """Hides a file in a image"""
    system('cls')
    # check if n is in range
    if n < 0 or n > 8:
        print("\33[1;31mERROR\33[0m: n must be between 1 and 8 or 0 for auto")
        exit()
    # auto n
    if n == 0:
        while (img.width * img.height) * 3 * n < getsize(file) * 8:
            n += 1
            if n > 8:
                f = img.filename.split("\\")[-1]
                print(f"\33[1;31mERROR\33[0m: Image \33[1;31m{f}\33[0m too small to hide file")
                exit()
    # check if image is big enough
    if (img.width * img.height) * 3 * n < getsize(file) * 8:
        f = img.filename.split("\\")[-1]
        print(f"\33[1;31mERROR\33[0m: Image \33[1;31m{f}\33[0m too small to hide file")
        exit()
    # convert image to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    # convert image to array
    arr = np.array(img).flatten().copy()
    total_pixels_ch = len(arr)
    # check if div value is valid
    if div == 0:
        div = findDiv(total_pixels_ch, file, n)
    else:
        if total_pixels_ch * n < div * getsize(file) * 8:
            print("\33[1;31mERROR\33[0m: div value too big, try 0")
            exit()
    # start hiding file
    arcobaleno("HIDING FILE")
    print("...")
    start_time = time.time()
    # read file by line
    with open(file, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for line in f)
        f.seek(0)  # go back to the start of the file
        rsv = ""
        ind = 0
        for i, line in enumerate(f): # enumerate() returns a tuple with the index and the value
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
                arr[ind] = setLastNBits(arr[ind], bit, n)
                # go to next pixel/component
                ind = (ind + div) % len(arr)
            if (i + 1) % 1000 == 0:  # Change this number to control how often the progress is printed
                system('cls')
                arcobaleno("HIDING FILE")
                print("...")
                progress = (i + 1) / total_lines
                elapsed_time = time.time() - start_time
                print(f"Elaboration {i + 1} of {total_lines} lines ({format((progress) * 100, '.2f')}%)")
                print(f"Remaining time: {format(elapsed_time *(1 - progress) / progress, '.2f')} seconds")
    rsv = list(rsv)
    # if there are still bits left, hide them
    while rsv != []:
        bit = ""
        for k in range(n):
            if len(rsv) >= n-k:
                bit += rsv.pop(0)
            else:
                bit += "0"
        arr[ind] = setLastNBits(arr[ind], bit, n)
        # go to next pixel/component
        ind = (ind + div) % len(arr)
    f.close()
    # print percentage of pixels used
    system('cls')
    arcobaleno("HIDING FILE")
    print("...")
    print(f"Elaboration {total_lines} of {total_lines} lines (100.0%)")
    print("Remaining time: 0.00 seconds")
    print(f"\33[1;32mFINISHED\33[0m\nPercentage of pixels used with n={n}: {format(((getsize(file) * 8) / ((img.width * img.height) * 3 * n)) * 100, '.2f')}%")
    img_copy = Image.fromarray(arr.reshape(img.height, img.width, 3))
    img_copy.save(new_img)
    print(f"Image saved as \33[1;33m{new_img}\33[0m")
    return (img_copy, n, div)

def scan8(line: str, flag: str) -> int:
    """Scans a line for a flag 8 bit at a time"""
    for i in range(0, len(line), 8):
        if line[i:i+8] == flag:
            return i
    return -1

def getFile_with_mat(img: Image, new_file_path: str, n: int, div: int) -> None:
    """Gets a file from a image"""
    system('cls')
    # check if n is in range
    if n < 1 or n > 8:
        print("\33[1;31mERROR\33[0m: n must be between 1 and 8")
        exit()
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
                    print(f"\33[1;32mDECRYPTION DONE\33[0m\nFile saved as \33[1;33m{new_file_path}\33[0m")
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

def getFile(img: Image, new_file_path: str, n: int, div: int) -> None: # with arr -> faster
    """Gets a file from a image"""
    system('cls')
    # check if n is in range
    if n < 1 or n > 8:
        print("\33[1;31mERROR\33[0m: n must be between 1 and 8")
        exit()
    arcobaleno("GETTING FILE")
    print("...")
    # convert image to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    # start getting file
    arr = np.array(img).flatten().copy()
    char, stop = [], []
    pos = 0
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
                        print(f"\33[1;32mDECRYPTION DONE\33[0m\nFile saved as \33[1;33m{new_file_path}\33[0m")
                        file.close()
                        return
                    stop = []
                    if len(char) >= 1024:
                        char = ''.join(char)
                        char = binaryConvertBack(char)
                        file.write(char)
                        char = []
            pos = (pos + div) % len(arr)
            # check if file is not found
            err -= 1
            if err < 0:
                print("\33[1;31mERROR\33[0m: file not found")
                exit()

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

def hideBinFile(img: Image, file: str, new_img: str, zipMode=NO_ZIP, n=0, div=0) -> (Image, int, float, int):
    """Hides a file in a image"""
    system('cls')
    # check if n is in range
    if n < 0 or n > 8:
        print("\33[1;31mERROR\33[0m: n must be between 1 and 8 or 0 for auto")
        exit()
    # determine channels
    ch = 3
    if img.mode == "RGBA":
        ch = 4
    if img.mode != "RGB" and img.mode != "RGBA":
        img = img.convert("RGB")
    # check if zipMode is in range
    if zipMode not in [0, 1, 2]:
        print("\33[1;31mERROR\33[0m: zipMode must be 0, 1 or 2")
        exit()
    # zip file if zipMode is 1
    if zipMode == FILE:
        print("Compressing file...")
        with zipfile.ZipFile('tmp.zip', 'w') as zf:
            zf.write(file)
        file = 'tmp.zip'
        print("File compressed")
    # zip directory if zipMode is 2
    elif zipMode == DIR:
        print("Compressing directory...")
        zipf = zipfile.ZipFile('tmp.zip', 'w', zipfile.ZIP_DEFLATED)
        zipdir(file, zipf)
        file = 'tmp.zip'
        zipf.close()
        print("Directory compressed")
    # get file size
    total_bytes = getsize(file)
    # auto n
    if n == 0:
        while (img.width * img.height) * ch * n < total_bytes * 8:
            n += 1
            if n > 8:
                f = img.filename.split("\\")[-1]
                print(f"\33[1;31mERROR\33[0m: Image \33[1;31m{f}\33[0m too small to hide file")
                exit()
    # check if image is big enough
    elif (img.width * img.height) * ch * n < total_bytes * 8:
        f = img.filename.split("\\")[-1]
        print(f"\33[1;31mERROR\33[0m: Image \33[1;31m{f}\33[0m too small to hide file")
        exit()
    # convert image to array
    arr = np.array(img).flatten().copy()
    total_pixels_ch = len(arr)
    # check if div value is valid
    if div == 0:
        div = findDiv(total_pixels_ch, file, n)
    else:
        if total_pixels_ch * n < div * total_bytes * 8:
            print("\33[1;31mERROR\33[0m: div value too big, try 0")
            exit()
    # start hiding file
    system('cls')
    arcobaleno("HIDING FILE")
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
            if (i + 1) % 25000 == 0:  # Change this number to control how often the progress is printed
                system('cls')
                arcobaleno("HIDING FILE")
                print("...")
                progress = (i + 1) / total_bytes
                elapsed_time = time.time() - start_time
                print(f"Elaboration {i + 1} of {total_bytes} bytes ({format((progress) * 100, '.2f')}%)")
                print(f"Remaining time: {format(elapsed_time *(1 - progress) / progress, '.2f')} seconds")
    f.close()
    while len(rsv) > 0:
        tmp = rsv[:n]
        rsv = rsv[n:]
        # set last n bits of pixel
        arr[pos] = setLastNBits(arr[pos], tmp, n)
        ind += div
        pos = round(ind)
    system('cls')
    arcobaleno("HIDING FILE")
    print("...")
    print(f"Elaboration {total_bytes} of {total_bytes} bytes (100.0%)")
    print("Remaining time: 0.00 seconds")
    print(f"\33[1;32mFINISHED\33[0m\nPercentage of pixels used with n={n}: {format(((total_bytes * 8) / ((img.width * img.height) * ch * n)) * 100, '.2f')}%")
    if zipMode != NO_ZIP:
        # delete tmp.zip
        remove('tmp.zip')
    img_copy = Image.fromarray(arr.reshape(img.height, img.width, ch))
    img_copy.save(new_img)
    print(f"Image saved as \33[1;33m{new_img}\33[0m")
    return (img_copy, n, div, total_bytes)

def string_to_bytes(bit_string):
    byte_array = bytearray()
    # it is not necessary that len(bit_string) is a multiple of 8
    for i in range(0, len(bit_string), 8):
        byte = bit_string[i:i+8]
        byte_array.append(int(byte, 2))
    return byte_array

def getBinFile(img: Image, new_file_path: str, zipMode: int, n: int, div: float, size: int) -> None: # with arr -> faster
    """Gets a file from a image"""
    system('cls')
    # check if n is in range
    if n < 1 or n > 8:
        print("\33[1;31mERROR\33[0m: n must be between 1 and 8")
        exit()
    # check if zipMode is in range
    if zipMode not in [0, 1, 2]:
        print("\33[1;31mERROR\33[0m: zipMode must be 0, 1 or 2")
        exit()
    arcobaleno("GETTING FILE")
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
            if (i+1) % 100000 == 0:
                system("cls")
                arcobaleno("GETTING FILE")
                print("...")
                progress = i / (size*8//n)
                elapsed_time = time.time() - start_time
                print(f"Elaboration progress: {format(progress * 100, '.2f')}%")
                print(f"Remaining time: {format(elapsed_time * (1 - progress) / progress, '.2f')} seconds")                
        if len(bits):
            bits = string_to_bytes(bits)
            file.write(bits)
        file.close()
        system("cls")
        arcobaleno("GETTING FILE")
        print("...")
        print("Elaboration progress: 100.0%")
        print("Remaining time: 0.00 seconds")
        if zipMode == NO_ZIP:
            print(f"\33[1;32mDECRYPTION DONE\33[0m\nFile saved as \33[1;33m{new_file_path}\33[0m")
        elif zipMode == FILE:
            print("Decompressing file...")
            # unzip file
            try:
                with zipfile.ZipFile(new_file_path, 'r') as zf:
                    zf.extractall()
                    extracted = zf.namelist()[0]
                    old_path = join(getcwd(), extracted)
                    new_path = join(getcwd(), res)
                    rename(old_path, new_path)
                    # delete tmp.zip
                    zf.close()
                    remove(new_file_path)
                    print(f"\33[1;32mDECRYPTION DONE\33[0m\nFile saved as \33[1;33m{res}\33[0m")
            except Exception as e:
                print(f"Errore durante l'estrazione: {e}")
        else:
            print("Decompressing directory...")
            try:
                with zipfile.ZipFile(new_file_path, 'r') as zf:
                    zf.extractall(res)
                    # delete tmp.zip
                    zf.close()
                    remove(new_file_path)
                    print(f"\33[1;32mDECRYPTION DONE\33[0m\nDirectory saved as \33[1;33m{res}\33[0m")
            except Exception as e:
                print(f"Errore durante l'estrazione: {e}")

# big lsb -> img1 big distorsion
# small msb -> img2 low quality
def hideImage(img1: Image, img2: Image, new_img: str, lsb=0, msb=8, div=0) -> (Image, int, int, float, int, int): # put img2 in img1 and return info for decryption
    """Hides a image in another image
        lsb: number of less significant bits of img1 to change
        msb: number of most significant bits of img2 to put in img1"""
    system('cls')
    # check if lsb is valid
    if lsb < 0 or lsb > 8:
        print("\33[1;31mERROR\33[0m: lsb value must be between 1 and 8 or 0 for auto")
        exit()
    # check if msb is valid
    if msb < 0 or msb > 8:
        print("\33[1;31mERROR\33[0m: msb value must be between 1 and 8 or 0 for auto")
        exit()
    # check if lsb is bigger than msb
    if lsb > msb:
        print("\33[1;31mERROR\33[0m: lsb value must be smaller or equal to msb value")
        exit()
    # determine auto lsb and msb
    while lsb == 0:
        if msb == 0:
            f1 = img1.filename.split("\\")[-1]
            f2 = img2.filename.split("\\")[-1]
            print(f"\33[1;31mERROR\33[0m: Image \33[1;31m{f1}\33[0m too small to hide image \33[1;31m{f2}\33[0m")
            exit()
        while((lsb * img1.width * img1.height) < (msb * img2.width * img2.height)):
            lsb += 1
            if lsb > msb:
                lsb = 0
                msb -= 1
    # check if image is big enough
    if (lsb * img1.width * img1.height) < (msb * img2.width * img2.height):
        f1 = img1.filename.split("\\")[-1]
        f2 = img2.filename.split("\\")[-1]
        print(f"\33[1;31mERROR\33[0m: Image \33[1;31m{f1}\33[0m too small to hide image \33[1;31m{f2}\33[0m")
        exit()
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
    if lsb == msb:
        if div == 0:
            div = len(arr1) / len(arr2) # how many pixels of img1 are needed to hide one pixel of img2
        else:
            if div * len(arr2) > len(arr1):
                print("\33[1;31mERROR\33[0m: div value too big")
                exit()
        i, j = 0, 0
        arcobaleno("HIDING IMAGE")
        print("...")
        pos = 0
        while i < len(arr2):
            bits = format(arr2[i], '08b') # convert to binary
            bits = bits[:msb] # take the msb most significant bits
            arr1[j] = setLastNBits(arr1[j], bits, lsb)
            i += 1
            pos += div # skip div pixels of img1 -> more uniform distribution
            j = round(pos)
            if (i) % 180000 == 0:  # Change this number to control how often the progress is printed
                system("cls")
                arcobaleno("HIDING IMAGE")
                print("...")
                progress = i / total_pixels_ch
                elapsed_time = time.time() - start_time
                print(f"Elaboration progress: {format(progress * 100, '.2f')}%")
                print(f"Remaining time: {format(elapsed_time * (1 - progress) / progress, '.2f')} seconds")
    else:
        if div == 0:
            div = (len(arr1) * lsb) / (len(arr2) * msb)
        else:
            if div * len(arr2) * msb > len(arr1) * lsb:
                print("\33[1;31mERROR\33[0m: div value too big")
                exit()
        i, j = 0, 0
        arcobaleno("HIDING IMAGE")
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
                arcobaleno("HIDING IMAGE")
                print("...")
                progress = i / total_pixels_ch
                elapsed_time = time.time() - start_time
                print(f"Elaboration progress: {format(progress * 100, '.2f')}%")
                print(f"Remaining time: {format(elapsed_time * (1 - progress) / progress, '.2f')} seconds")
    # convert arr1 to image
    w, h = img2.width, img2.height
    system("cls")
    arcobaleno("HIDING IMAGE")
    print("...")
    print("Elaboration progress: 100.0%")
    print("Remaining time: 0.00 seconds")
    print(f"\33[1;32mFINISHED\n\33[0mPercentage of pixels used: {format((msb * img2.width * img2.height) / (lsb * img1.width * img1.height) * 100, '.2f')}%")
    img1_copy = Image.fromarray(arr1.reshape(img1.height, img1.width, 3)) # save the copy so img1 is not modified
    img1_copy.save(new_img)
    print(f"Image saved as \33[1;33m{new_img}\33[0m")
    return (img1_copy, lsb, msb, div, w, h)

def getImage(img: Image, new_img: str, lsb: int, msb: int, div: float, width: int, height: int) -> Image: # get img2 from img1
    """Gets an hidden image from another image"""
    system('cls')
    arcobaleno("GETTING IMAGE")
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
            arcobaleno("GETTING IMAGE")
            print("...")
            progress = n / size
            print(f"Elaboration progress: {format(progress * 100, '.2f')}%")
            elapsed_time = time.time() - start_time
            print(f"Remaining time: {format(elapsed_time * (1 - progress) / progress, '.2f')} seconds")
    system("cls")
    arcobaleno("GETTING IMAGE")
    print("...")
    print("Elaboration progress: 100.0%")
    print("Remaining time: 0.00 seconds")
    # convert res to image
    res = Image.fromarray(res.reshape(height, width, 3))
    res.save(new_img)
    print(f"\33[1;32mFINISHED\n\33[0mImage saved as \33[1;33m{new_img}\33[0m")
    return res


def main():
    # use jpeg to improve compression, png for binary files
    system("cls")
    path1 = "pic\\fluo.jpg"
    path2 = "tex"
    new, ext = splitext(path2)
    new = "test"
    img_with_data = "new.png"
    zipMode = DIR
    n = 0
    div = 0
    
    
    img = Image.open(path1)
    ret, n, div, size = hideBinFile(img, path2, img_with_data, zipMode, n, div)
    getBinFile(ret, new + ext, zipMode, n, div, size)

main()