from os import system
from os.path import getsize
from PIL import Image
# this version changes the first bit of the color instead of the last one

def binaryConvert(text):
    """Converts a string of text to binary"""
    return ''.join(format(ord(char), '08b') for char in text)

def binaryConvertBack(text):
    """Converts a string of binary to text"""
    return ''.join(chr(int(text[i*8:i*8+8],2)) for i in range(len(text)//8))

def setLastBit(value, bit):
    value = format(value, '08b') # convert int to binary string
    value = list(value) # convert string to list
    value[0] = bit # change last bit
    value = ''.join(value) # convert list to string
    value = int(value, 2) # convert binary string to int
    return value

def setComponetOfColor(mat, i, j, color, component):
    if component == 0:
        mat[i,j] = (color, mat[i,j][1], mat[i,j][2])
    elif component == 1:
        mat[i,j] = (mat[i,j][0], color, mat[i,j][2])
    elif component == 2:
        mat[i,j] = (mat[i,j][0], mat[i,j][1], color)
    return mat
    

def hideMessage(img, msg, new_img):
    """Hides a message in a image"""
    # check if image is big enough
    if (img.width * img.height) * 3 < len(msg) * 8:
        print("\33[1;31mERROR\33[0m: Image too small to hide message")
        return
    # convert image to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    # start hiding message
    print("\33[1;32mHIDING MESSAGE...\33[0m")
    mat = img.load()
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
                    color = max(0, min(color, 255)) # check if color is in range
                    mat = setComponetOfColor(mat, i, j, color, z) # set color
                else:
                    break
    print(f"\33[1;32mFINISHED\33[0m\nPercentage of pixels used: {((len(msg)) / ((img.width * img.height) * 3)) * 100}%")
    img.save(new_img)
    return img

def getMessage(img):
    """Gets a message from a image"""
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

def hideFile(img, path, new_img):
    """Hides a file in a image"""
    # check if image is big enough
    if (img.width * img.height) * 3 < getsize(path) * 8:
        print("\33[1;31mERROR\33[0m: Image too small to hide file")
        return
    # convert image to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    # start hiding file
    print("\33[1;32mHIDING FILE...\33[0m")
    mat = img.load()
    x, y, z = 0, 0, 0
    # read file by line
    with open(path, 'r') as file:
        total_lines = sum(1 for line in file)
        file.seek(0)  # go back to the start of the file
        for i, line in enumerate(file): # enumerate() returns a tuple with the index and the value
            line = binaryConvert(line)
            if i == total_lines - 1:
                line = line + "00000000"
            for bit in line:
                color = mat[x,y][z]
                color = setLastBit(color, bit)
                color = max(0, min(color, 255))
                mat = setComponetOfColor(mat, x, y, color, z)
                z = (z + 1) % 3
                if z == 0:
                    y = (y + 1) % img.height
                    if y == 0:
                        x = (x + 1) % img.width
            if (i + 1) % 500 == 0:  # Change this number to control how often the progress is printed
                print(f"Elaboration {i + 1} of {total_lines} lines ({((i + 1) / total_lines) * 100}%)")
    file.close()
    # print percentage of pixels used
    print(f"\33[1;32mFINISHED\33[0m\nPercentage of pixels used: {((getsize(path) * 8) / ((img.width * img.height) * 3)) * 100}%")
    img.save(new_img)
    return img

def getFile(img, path):
    """Gets a file from a image"""
    print("\33[1;32mGETTING FILE\33[0m...")
    # convert image to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    # start getting file
    mat = img.load()
    char, stop = [], []
    with open(path, 'w') as file:
        for i in range(img.width):
            for j in range(img.height):
                for z in range(3):
                    color = mat[i,j][z]
                    bit = format(color, '08b')[0]
                    char.append(bit)
                    stop.append(bit)
                    if len(stop) == 8:
                        if ''.join(stop) == "00000000":
                            if len(char):
                                char = ''.join(char)
                                char = char[:-8]
                                char = binaryConvertBack(char)
                                file.write(char)
                                print("File saved")
                                file.close()
                            return
                        stop = []
                        if len(char) == 1024:
                            char = ''.join(char)
                            char = binaryConvertBack(char)
                            file.write(char)
                            char = []
    print("\33[1;32mFILE SAVED\33[0m")
    file.close()
    

def main():
    system("cls")
    img = Image.open("link.png")
    img1 = hideFile(img, "testo.txt", "link1.jpeg")
    getFile(img1, "testo1.txt")

main()