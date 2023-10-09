@echo off
REM Controllo se python e pip sono installati
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python non trovato! Assicurati di avere Python installato e nel tuo PATH.
    exit /b
)

where pip >nul 2>nul
if %errorlevel% neq 0 (
    echo Pip non trovato! Assicurati di avere pip installato e nel tuo PATH.
    exit /b
)

REM Aggiorno pip alla versione piu recente
echo Aggiornamento pip...
pip install --upgrade pip

REM Installo le librerie
echo Installazione numpy...
pip install numpy

echo Installazione scipy...
pip install scipy

echo Installazione pandas...
pip install pandas

echo Installazione plotly...
pip install plotly

echo Installazione matplolib...
pip install matplotlib

echo Installazione jupyter...
pip install jupiter

echo Installazione termcolor...
pip install termcolor

echo Installazione pyfiglet...
pip install pyfiglet

echo Installazione colorama...
pip install colorama

echo Installazione Pillow...
pip install Pillow

echo.
echo Tutte le librerie sono state installate con successo!
pause