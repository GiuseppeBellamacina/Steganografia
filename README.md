# Steganografia

Il file principale è **steganografia.py** il quale possiede funzioni con le quali è possibile nascondere diverse tipologie di dati all'interno di immagini.


# Dati che è possibile nascondere:

Ecco di seguito una lista di dati che è possibile nascondere con funzioni dirette

## Stringhe

Tramite **hideMessage()** e **getMessage()** è possibile nascondere stringhe all'interno delle immagini. Queste verranno inserite 1 bit alla volta all'interno di ogni canale di colore (RGB) dell'immagine andando a modificare solo il bit meno significativo di ciascuno.

## File di testo

Tramite **hideFile()** e **getFile()** è possibile nascondere file di caratteri nelle immagini potendo specificare il numero di bit meno significativi da modificare e l'indice di dispersione dei bit. Esistono anche le versioni che fanno utilizzo di una matrice di dati piuttosto che l'array lineare (che è meno intuitivo ma molto più veloce).

## Immagini

Tramite **hideImage()** e **getImage()** è possibile nascondere altre immagini all'interno di immagini stesse. Si può scegliere il numero di bit più significativi dell'immagine da nascondere (msb) ed il numero di bit meno significativi dell'immagine su cui si vuole nascondere l'altra immagine da modificare (lsb)


## File binari

Tramite **hideBinFile()** e **getBinFile()** è possibile nascondere file binari (pdf, immagini, video, eseguibili...) all'interno delle immagini. Si possono specificare le stesse cose delle funzioni per i file a caratteri, in più si puo' decidere di comprimere i dati prima di eseguire il processo. Si puo' anche operare con le directory purché vengano prima compresse in un unico file '.zip'.

___
## Per ulteriori informazioni
Non lo so, già è assai che ho fatto sto coso, se volete sapere altro studiatevi sta roba e via
Un'ultima cosa che forse ti starai chiedendo (a parte se sono pazzo, la cui risposta è sì), se hai problemi
nell'inserimento delle foto quando ti chiede di inserire il path, prova a separare le cartelle con '\\\\' (doppio slash inverso), su Python si fa così
