import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ExifTags
import utilities as oth

class Application(TkinterDnD.Tk):
    def __init__(self):
        super().__init__() # Inizializza la classe base TkinterDnD.Tk

        self.title("Steganography Tool") # Imposta il titolo della finestra
        self.geometry("660x470") # Imposta le dimensioni della finestra

        self.container = tk.Frame(self) # Crea un frame per contenere le pagine
        self.container.pack(fill="both", expand=True) # Espandi il frame per riempire la finestra

        self.frames = {} # Dizionario per contenere le pagine
        for F in (MainMenu, HideData, RecoverData): # Aggiungi le pagine al dizionario
            frame = F(parent=self.container, controller=self) # Crea la pagina con il frame come genitore mentre il controller è l'istanza corrente
            self.frames[F] = frame # Aggiungi la pagina al dizionario
            frame.grid(row=0, column=0, sticky="nsew") # Allinea la pagina al centro con sticky

        self.show_frame(MainMenu) # Mostra la pagina iniziale

    def show_frame(self, cont):
        frame = self.frames[cont] # Prendi la pagina dal dizionario
        frame.tkraise() # Porta la pagina in primo piano

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=2000, height=300) # Inizializza la classe base tk.Frame
        self.controller = controller # Riferimento al controller

        # Sfondo colorato
        self.configure(bg="#000000") # Imposta il colore di sfondo
        
        main_frame = tk.Frame(self, bg="#000000")
        main_frame.pack(fill="both", expand=True)
        
        mainLabel = tk.Label(main_frame, text="Steganography Tool", font=("Helvetica", 24), bg="#000000", fg="#ffffff")
        mainLabel.pack(pady=20)
        
        label = tk.Label(main_frame, text="Menu Principale", font=("Helvetica", 20), bg="#000000", fg="#ffffff") # Etichetta per il titolo
        label.pack(pady=20) # Aggiungi l'etichetta al frame

        # Frame per contenere i pulsanti quadrati
        button_frame = tk.Frame(main_frame, bg="#000000")
        button_frame.pack(fill="both", expand=True)

        # Pulsante quadrato 1
        button1 = tk.Button(button_frame, text="Nascondi Dati", width=20, height=3,
                            font=("Helvetica", 18),
                            bg="#4CAF50", fg="white",
                            command=lambda: controller.show_frame(HideData))
        button1.grid(row=0, column=0, padx=20, pady=40)

        # Pulsante quadrato 2
        button2 = tk.Button(button_frame, text="Recupera Dati", width=20, height=3,
                            font=("Helvetica", 18),
                            bg="#008CBA", fg="white",
                            command=lambda: controller.show_frame(RecoverData))
        button2.grid(row=0, column=1, padx=20, pady=40)

        # Pulsante per chiudere il programma
        button_close = tk.Button(button_frame, text="Chiudi", font=("Helvetica", 12),
                                 bg="#f44336", fg="white",
                                 command=self.quit)
        button_close.grid(row=1, column=0, pady=40, padx=0, columnspan=2) # columnspan per allargare il pulsante su due colonne

class HideData(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.image_data = None
        
        # Frame principale
        main_frame = tk.Frame(self, bg="#000000")
        main_frame.pack(fill="both", expand=True)

        # Frame per l'area sinistra
        left_frame = tk.Frame(main_frame, bd=2, relief="groove", bg="#ffffff")
        left_frame.pack(side="left", fill="both", expand=True)
        
        upper_left_frame = tk.Frame(left_frame, bg="#ffffff")
        upper_left_frame.pack(fill="both", expand=True)

        label = tk.Label(upper_left_frame, text="Trascina la tua immagine qui sotto", font=("Helvetica", 12), bg="#ffffff")
        label.grid(row=0, column=0, pady=10, padx=10)
        
        upload_button = tk.Button(upper_left_frame, text="Carica Immagine", command=lambda: self.file_dialog("cazzo"))
        upload_button.grid(row=0, column=1, pady=10, padx=10)

        self.canvas = tk.Canvas(left_frame, bg="#ffffff")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', self.load_image)

        # Frame per l'area destra
        right_frame = tk.Frame(main_frame, bd=2, relief=tk.GROOVE, bg="#ffffff")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.info_label = tk.Label(right_frame, text="Informazioni", font=("Helvetica", 14), bg="#ffffff")
        self.info_label.pack(pady=10, padx=10)
        

        # Aggiunta del pulsante per tornare alla pagina principale
        back_button = tk.Button(right_frame, text="Torna al Menu Principale", command=lambda: controller.show_frame(MainMenu))
        back_button.pack(side=tk.BOTTOM, padx=10, pady=10)

        # Aggiunta del pulsante per aprire un'area per inserire dati opzionali
        optional_data_button = tk.Button(right_frame, text="Menu Avanzato", command=self.open_optional_data_area)
        optional_data_button.pack(side=tk.BOTTOM, padx=10, pady=10)
        
        hide_button = tk.Button(right_frame, text="Nascondi Dati", command=lambda: self.hideBinFile(self.image_data, "j.jpg", "test.png", 0, 8, 1))
        hide_button.pack(side=tk.BOTTOM, padx=10, pady=10)

    def open_optional_data_area(self):
        # Codice per aprire un'area per inserire dati opzionali
        pass
    
    def hideBinFile(self, img: Image, file: str, new_img: str, zipMode=oth.NO_ZIP, n=0, div=0) -> (Image, int, float, int):
        """Nasconde un file binario o una cartella"""
        # determine channels
        ch = 3
        if img.mode == "RGBA":
            ch = 4
        if img.mode != "RGB" and img.mode != "RGBA":
            img = img.convert("RGB")
        # zip file if zipMode is 1
        if zipMode == oth.FILE:
            with oth.zipfile.ZipFile('tmp.zip', 'w') as zf:
                zf.write(file)
            file = 'tmp.zip'
        # zip directory if zipMode is 2
        elif zipMode == oth.DIR:
            zipf = oth.zipfile.ZipFile('tmp.zip', 'w', oth.zipfile.ZIP_DEFLATED)
            oth.zipdir(file, zipf)
            file = 'tmp.zip'
            zipf.close()
        # get file size
        total_bytes = oth.getsize(file)
        # auto n
        if n == 0:
            while (img.width * img.height) * ch * n < total_bytes * 8:
                n += 1
                if n > 8:
                    f = img.filename.split("\\")[-1]
                    error_msg = "ERRORE: Immagine " + f + " troppo piccola per nascondere il file"
                    return
        # check if image is big enough
        elif (img.width * img.height) * ch * n < total_bytes * 8:
            f = img.filename.split("\\")[-1]
            error_msg = "ERRORE: Immagine " + f + " troppo piccola per nascondere il file"
            return
        # convert image to array
        arr = oth.np.array(img).flatten().copy()
        total_pixels_ch = len(arr)
        # check if div value is valid
        if div == 0:
            div = oth.findDiv(total_pixels_ch, file, n)
        else:
            if total_pixels_ch * n < div * total_bytes * 8 or div < 0:
                error_msg = "ERRORE: il valore di div non e' valido"
                return
        # start hiding file
        start_time = oth.time.time()
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
                    arr[pos] = oth.setLastNBits(arr[pos], tmp, n)
                    ind += div
                    pos = round(ind)
                if len(bits) > 0:
                    rsv = bits
                if (i + 1) % 50000 == 0:  # Change this number to control how often the progress is printed
                    progress = (i + 1) / total_bytes
                    elapsed_time = oth.time.time() - start_time
                    progress_msg = f"Elaborati {i + 1} byte su {total_bytes} ({format((progress) * 100, '.2f')}%)"
                    time_msg = f"Tempo rimanente: {oth.timeDisplay(elapsed_time *(1 - progress) / progress)}"
                    self.info_label.config(text=time_msg)
        f.close()
        while len(rsv) > 0:
            tmp = rsv[:n]
            rsv = rsv[n:]
            # set last n bits of pixel
            arr[pos] = oth.setLastNBits(arr[pos], tmp, n)
            ind += div
            pos = round(ind)
        progress_msg = f"Elaborati {total_bytes} byte su {total_bytes} (100.0%)"
        finished_msg = f"TERMINATO\nPercentuale di pixel usati con n={n} e div={div}: {format(((total_bytes * 8) / ((img.width * img.height) * ch * n)) * 100, '.2f')}%"
        if zipMode != oth.NO_ZIP:
            # delete tmp.zip
            oth.remove('tmp.zip')
        img_copy = Image.fromarray(arr.reshape(img.height, img.width, ch))
        img_copy.save(new_img)
        saved_msg = f"Immagine salvata come {new_img}"
        return (img_copy, n, div, total_bytes)
    
    def file_dialog(self, param):
        file_path = filedialog.askopenfilename()
        self.image_data = Image.open(file_path)
        image = self.image_data
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())

        if exif.get(orientation) == 3:
            image = image.rotate(180, expand=True)
        elif exif.get(orientation) == 6:
            image = image.rotate(270, expand=True)
        elif exif.get(orientation) == 8:
            image = image.rotate(90, expand=True)
            
        self.info_label.config(text=f"Nome: {self.image_data.filename}\nDimensioni: {self.image_data.width}x{self.image_data.height}\n{param}")
        dims = self.dim_calc(image.width, image.height)
        image.thumbnail((dims[0], dims[1]))
        photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo
    
    def dim_calc(self, width, height):
        dims = [width, height]
        if dims[0] > dims[1]:
            dims[0] = 400
            dims[1] = int((400/width)*height)
        else:
            dims[1] = 400
            dims[0] = int((400/height)*width)
        return dims

    def load_image(self, event):
        file_path = event.data
        if file_path:
            image = Image.open(file_path)
            self.image_data = image
            
            # Correggi l'orientamento dell'immagine se necessario
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(image._getexif().items())

            if exif.get(orientation) == 3:
                image = image.rotate(180, expand=True)
            elif exif.get(orientation) == 6:
                image = image.rotate(270, expand=True)
            elif exif.get(orientation) == 8:
                image = image.rotate(90, expand=True)
            
            self.info_label.config(text=f"Nome: {self.image_data.filename}\nDimensioni: {self.image_data.width}x{self.image_data.height}")
            dims = self.dim_calc(image.width, image.height)
            image.thumbnail((dims[0], dims[1]))
            photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo  # manteniamo il riferimento all'immagine per evitare garbage collection

class RecoverData(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Frame principale
        main_frame = tk.Frame(self, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame per l'area sinistra
        left_frame = tk.Frame(main_frame, bd=2, relief=tk.GROOVE, bg="#ffffff")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        label = tk.Label(left_frame, text="Seconda Pagina", font=("Helvetica", 12), bg="#ffffff")
        label.pack(pady=10, padx=10)

        # Frame per l'area destra
        right_frame = tk.Frame(main_frame, bd=2, relief=tk.GROOVE, bg="#ffffff")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        info_label = tk.Label(right_frame, text="Area per le informazioni", font=("Helvetica", 12), bg="#ffffff")
        info_label.pack(pady=10, padx=10)
        
        button1 = tk.Button(right_frame, text="Torna alla Pagina Iniziale",
                            font=("Helvetica", 10),
                            command=lambda: controller.show_frame(MainMenu))
        button1.pack(side=tk.BOTTOM, pady=10)

        # Pulsante per caricare la chiave di cifratura da file
        load_button = tk.Button(right_frame, text="Carica Chiave di Cifratura",
                                font=("Helvetica", 10),
                                command=self.load_key)
        load_button.pack(side=tk.BOTTOM, pady=10)
        
    def load_key(self):
         # Qui puoi scrivere il codice per caricare la chiave di cifratura da un file
        messagebox.showinfo("Caricare Chiave di Cifratura", "Funzionalità ancora da implementare.")

def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()