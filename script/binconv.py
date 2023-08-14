def binaryConvert(text):
    """Converts a string of text to binary"""
    return ''.join(format(ord(char), '08b') for char in text)

def binaryConvertBack(text):
    """Converts a string of binary to text"""
    return ''.join(chr(int(text[i*8:i*8+8],2)) for i in range(len(text)//8))

def main():
    string = "ciao"
    string2 = binaryConvert(string)
    string3 = binaryConvertBack(string)
    print(string2)
    print(string3)

main()