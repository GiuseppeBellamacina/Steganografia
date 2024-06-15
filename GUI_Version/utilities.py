from os import system, remove, walk
from os.path import getsize, join, relpath, isfile, isdir, exists
import pickle
from PIL import Image
import numpy as np
import zipfile
import time

# zipModes
NO_ZIP = 0
FILE = 1
DIR = 2

# messages
error_msg = ""
progress_msg = ""
time_msg = ""
finished_msg = ""
saved_msg = ""

def timeDisplay(seconds: int) -> str:
    """Converte i secondi in minuti e secondi"""
    seconds = round(seconds)
    minutes, seconds = divmod(seconds, 60)
    if minutes:
        return f"{minutes:02d} minuti {seconds:02d} secondi"
    else:
        return f"{seconds:02d} secondi"

def setLastNBits(value: int, bits: str, n: int) -> int:
    """Imposta gli ultimi n bits di un numero"""
    value = format(value, '08b')
    if len(bits) < n:
        n = len(bits)
    value = value[:-n] + bits
    value = int(value, 2)
    value = min(255, max(0, value))
    return value

def findDiv(dim: int, file: str, n: int) -> float:
    image_dim = dim * n
    div = ((image_dim - n) / (getsize(file) * 8))
    return div

def zipdir(path: str, ziph: zipfile.ZipFile) -> None:
    """Comprime una directory"""
    for root, dirs, files in walk(path):
        for file in files:
            file_path = join(root, file)
            arcname = relpath(file_path, path)
            ziph.write(file_path, arcname)

def getDirSize(path: str) -> int:
    """Ottiene la dimensione di una directory"""
    size = 0
    for root, dirs, files in walk(path):
        for file in files:
            file_path = join(root, file)
            size += getsize(file_path)
    return size

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
    print("RICERCA FILE")
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
                print("RICERCA FILE")
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
        print("RICERCA FILE")
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

