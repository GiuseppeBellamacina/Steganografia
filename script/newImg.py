from PIL import Image

# Crea un'immagine in scala di grigi di 500x500 pixel
img = Image.new('L', (500, 500), color = 128)

# Ottieni l'accesso ai pixel dell'immagine
pixels = img.load()

# Modifica alcuni pixel
for i in range(100):
    for j in range(100):
        pixels[i, j] = 255

# Salva l'immagine
img.save('new_image.png')
