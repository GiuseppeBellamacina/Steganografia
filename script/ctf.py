from os import system

def decryptCaesarCode(text, key):
    result = ""
    for i in range(len(text)):
        char = text[i]
        # If char is not a letter, leave it as it is
        if (not char.isalpha()):
            result += char
            continue
        # Encrypt uppercase characters in plain text
        if (char.isupper()):
            result += chr((ord(char) + key - 65) % 26 + 65) # 65 = ord('A')
        else:
            result += chr((ord(char) + key - 97) % 26 + 97) # 97 = ord('a')
    return result

def findWord(text, word):
    if word == "":
        return text
    if word in text:
        text = text + "\33[1;32m <-- FOUND\33[0m"
    return text

def main():
    system("cls")
    text = "hd kdvxxdjij d Xvkdwvmv"
    word = ""
    
    pointer = ""
    for i in range(1,26,1):
        res = decryptCaesarCode(text, i)
        size1 = len(res)
        res = findWord(res, word)
        size2 = len(res)
        if size1 != size2:
            pointer = str(i)
        print("\33[1;33m"+str(i)+"\33[0m", res, sep=": ")
        
    if pointer != "":
        print("\nThe text has been encrypted with a key of \33[1;32m"+pointer+"\33[0m")
    else:
        if word != "":
            print("\nThe word \33[1;31m"+word+"\33[0m has not been found in the text")

main()