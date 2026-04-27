@echo off
REM ============================================================================
REM  DIEXA Boretrak QA - Constructor de Paquete Portable
REM  Genera la carpeta DIEXA_Boretrak_Portable lista para distribuir
REM ============================================================================
REM
REM  Este script SOLO se ejecuta UNA VEZ (por Sebastian)
REM  Genera una carpeta auto-contenida con:
REM    - Python embebido
REM    - Tesseract OCR
REM    - Todas las dependencias
REM    - La aplicacion
REM
REM  Despues de ejecutar este script:
REM    1. Comprimir la carpeta DIEXA_Boretrak_Portable en ZIP
REM    2. Distribuir el ZIP a los usuarios
REM    3. Los usuarios descomprimen y hacen doble clic en EJECUTAR.bat
REM
REM ============================================================================

setlocal enabledelayedexpansion
title DIEXA - Constructor Portable

set "BUILD_DIR=%~dp0DIEXA_Boretrak_Portable"
set "TEMP_DIR=%TEMP%\diexa_build"

cls
echo.
echo  ============================================================
echo   DIEXA - Constructor de Paquete Portable
echo  ============================================================
echo.
echo  Este script generara una carpeta portable completa que NO
echo  requiere instalacion para los usuarios finales.
echo.
echo  PROCESO:
echo   1. Descargar Python embeddable          (~25 MB)
echo   2. Configurar pip
echo   3. Instalar dependencias Python         (~300 MB)
echo   4. Descargar Tesseract OCR              (~70 MB)
echo   5. Empaquetar Tesseract en la carpeta
echo   6. Copiar la aplicacion
echo   7. Crear scripts de ejecucion
echo.
echo  Tiempo estimado: 15-25 minutos
echo  Tamano final: ~500 MB (~250 MB comprimido)
echo.
echo  Carpeta destino:
echo    %BUILD_DIR%
echo.
pause

REM Verificar que la app este presente
if not exist "%~dp0app_diexa_boretrak_v10.py" (
    echo.
    echo  ERROR: No se encuentra app_diexa_boretrak_v10.py
    echo  Coloque este BAT en la misma carpeta que la app.
    echo.
    pause
    exit /b 1
)

REM Limpiar carpeta destino si existe
if exist "%BUILD_DIR%" (
    cls
    echo.
    echo  La carpeta DIEXA_Boretrak_Portable ya existe.
    echo  Sera eliminada para crear una nueva.
    echo.
    choice /C SN /M "Continuar"
    if errorlevel 2 (
        echo  Cancelado.
        pause
        exit /b 0
    )
    rmdir /S /Q "%BUILD_DIR%"
)

REM Crear carpetas de trabajo
mkdir "%BUILD_DIR%"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM ============================================================================
REM PASO 1: Descargar Python Embeddable
REM ============================================================================

cls
echo.
echo  ============================================================
echo   PASO 1 de 7: Descargando Python Embeddable
echo  ============================================================
echo.

set "PYTHON_ZIP=%TEMP_DIR%\python-embed.zip"
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"

if exist "%PYTHON_ZIP%" (
    echo  Ya descargado, usando existente.
    goto EXTRACT_PYTHON
)

echo  Descargando: %PYTHON_URL%
echo  (~25 MB, puede tardar 1-2 minutos)
echo.

powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%PYTHON_URL%', '%PYTHON_ZIP%')"

if not exist "%PYTHON_ZIP%" (
    echo  ERROR: No se pudo descargar Python.
    pause
    exit /b 1
)

:EXTRACT_PYTHON
echo  Descomprimiendo Python...
mkdir "%BUILD_DIR%\python"
powershell -NoProfile -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%BUILD_DIR%\python' -Force"

if not exist "%BUILD_DIR%\python\python.exe" (
    echo  ERROR: Python no se descomprimio correctamente.
    pause
    exit /b 1
)

echo  [OK] Python embeddable instalado en la carpeta portable.
timeout /t 2 /nobreak >nul

REM ============================================================================
REM PASO 2: Configurar pip
REM ============================================================================

cls
echo.
echo  ============================================================
echo   PASO 2 de 7: Configurando pip
echo  ============================================================
echo.

REM Modificar python311._pth para habilitar site-packages
echo  Configurando paths de Python...
(
    echo python311.zip
    echo .
    echo Lib\site-packages
    echo.
    echo import site
) > "%BUILD_DIR%\python\python311._pth"

REM Descargar get-pip.py
set "GET_PIP=%TEMP_DIR%\get-pip.py"
if not exist "%GET_PIP%" (
    echo  Descargando get-pip.py...
    powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://bootstrap.pypa.io/get-pip.py', '%GET_PIP%')"
)

if not exist "%GET_PIP%" (
    echo  ERROR: No se pudo descargar get-pip.py
    pause
    exit /b 1
)

echo  Instalando pip...
"%BUILD_DIR%\python\python.exe" "%GET_PIP%" --no-warn-script-location

if not exist "%BUILD_DIR%\python\Scripts\pip.exe" (
    echo  ERROR: pip no se instalo correctamente.
    pause
    exit /b 1
)

echo  [OK] pip configurado.
timeout /t 2 /nobreak >nul

REM ============================================================================
REM PASO 3: Instalar dependencias Python
REM ============================================================================

cls
echo.
echo  ============================================================
echo   PASO 3 de 7: Instalando librerias Python
echo  ============================================================
echo.
echo  Esto tomara 5-15 minutos. Tenga paciencia.
echo  Se descargaran aproximadamente 300 MB de dependencias.
echo.

"%BUILD_DIR%\python\python.exe" -m pip install --no-warn-script-location ^
    streamlit ^
    pandas ^
    numpy ^
    matplotlib ^
    openpyxl ^
    PyPDF2 ^
    pdfplumber ^
    PyMuPDF ^
    pytesseract ^
    Pillow

if errorlevel 1 (
    echo.
    echo  ERROR: Hubo problemas instalando las librerias.
    echo  Intentando de nuevo...
    "%BUILD_DIR%\python\python.exe" -m pip install --no-warn-script-location streamlit pandas numpy matplotlib openpyxl PyPDF2 pdfplumber PyMuPDF pytesseract Pillow
)

echo.
echo  [OK] Librerias Python instaladas.
timeout /t 2 /nobreak >nul

REM ============================================================================
REM PASO 4: Descargar Tesseract OCR
REM ============================================================================

cls
echo.
echo  ============================================================
echo   PASO 4 de 7: Descargando Tesseract OCR
echo  ============================================================
echo.

set "TESS_INSTALLER=%TEMP_DIR%\tesseract-installer.exe"
set "TESS_URL=https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0/tesseract-ocr-w64-setup-v5.3.0.exe"

if exist "%TESS_INSTALLER%" (
    echo  Ya descargado, usando existente.
    goto INSTALL_TESS
)

echo  Descargando: %TESS_URL%
echo  (~70 MB, puede tardar 2-5 minutos)
echo.

REM Intento 1: PowerShell WebClient
powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%TESS_URL%', '%TESS_INSTALLER%')" 2>nul

if exist "%TESS_INSTALLER%" goto TESS_DOWNLOADED

echo  Intento 2: Usando curl (si esta disponible)...
curl -L -o "%TESS_INSTALLER%" "%TESS_URL%" 2>nul

if exist "%TESS_INSTALLER%" goto TESS_DOWNLOADED

echo  Intento 3: URL alternativa...
powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://github.com/UB-Mannheim/tesseract/releases/latest/download/tesseract-ocr-w64-setup-v5.3.0.exe', '%TESS_INSTALLER%')" 2>nul

if exist "%TESS_INSTALLER%" goto TESS_DOWNLOADED

echo.
echo  ADVERTENCIA: No se pudo descargar Tesseract OCR.
echo  Razon probable: Firewall corporativo bloqueando GitHub.
echo.
echo  SOLUCION: Instalacion sin OCR
echo  - La aplicacion funcionara perfectamente sin OCR
echo  - OCR solo es necesario para PDFs escaneados
echo  - La mayoria de PDFs Boretrak/Carlson son nativos
echo.
echo  Si necesita OCR:
echo  1. Instale Tesseract manualmente desde:
echo     https://github.com/UB-Mannheim/tesseract/wiki
echo  2. El paquete portable lo detectara automaticamente
echo.
timeout /t 5 /nobreak >nul
goto SKIP_TESS

:TESS_DOWNLOADED

REM ============================================================================
REM PASO 5: Empaquetar Tesseract en la carpeta portable
REM ============================================================================

:INSTALL_TESS
cls
echo.
echo  ============================================================
echo   PASO 5 de 7: Empaquetando Tesseract OCR
echo  ============================================================
echo.

REM Estrategia: Instalar Tesseract en una carpeta temporal y luego copiar
set "TESS_TEMP=%TEMP_DIR%\tesseract-install"
if exist "%TESS_TEMP%" rmdir /S /Q "%TESS_TEMP%"

echo  Instalando Tesseract temporalmente...
"%TESS_INSTALLER%" /S /D=%TESS_TEMP%

REM Esperar a que termine
timeout /t 5 /nobreak >nul

if not exist "%TESS_TEMP%\tesseract.exe" (
    echo.
    echo  El instalador no respondio al modo silencioso.
    echo  Probando metodo alternativo...
    
    REM Metodo alternativo: usar el instalador en sistema y copiar
    if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
        echo  Tesseract ya esta instalado en el sistema. Copiando...
        xcopy /E /I /Y "C:\Program Files\Tesseract-OCR" "%BUILD_DIR%\tesseract" >nul
    ) else (
        echo.
        echo  ADVERTENCIA: No se pudo empaquetar Tesseract automaticamente.
        echo  Instale manualmente Tesseract desde:
        echo    https://github.com/UB-Mannheim/tesseract/wiki
        echo  Y luego copie la carpeta C:\Program Files\Tesseract-OCR
        echo  como %BUILD_DIR%\tesseract
        echo.
        timeout /t 5 /nobreak >nul
    )
) else (
    echo  Copiando Tesseract a la carpeta portable...
    xcopy /E /I /Y "%TESS_TEMP%" "%BUILD_DIR%\tesseract" >nul
)

if exist "%BUILD_DIR%\tesseract\tesseract.exe" (
    echo  [OK] Tesseract OCR empaquetado en la carpeta portable.
) else (
    echo  [!] Tesseract no se empaqueto. La app funcionara sin OCR.
)

:SKIP_TESS
timeout /t 2 /nobreak >nul

REM ============================================================================
REM PASO 6: Copiar la aplicacion
REM ============================================================================

cls
echo.
echo  ============================================================
echo   PASO 6 de 7: Copiando la aplicacion
echo  ============================================================
echo.

copy /Y "%~dp0app_diexa_boretrak_v10.py" "%BUILD_DIR%\app_diexa_boretrak_v10.py" >nul

REM Crear .streamlit/config.toml
mkdir "%BUILD_DIR%\.streamlit" 2>nul
(
    echo [theme]
    echo primaryColor = "#00a2e5"
    echo backgroundColor = "#f4f6f8"
    echo secondaryBackgroundColor = "#ffffff"
    echo textColor = "#333333"
    echo font = "sans serif"
    echo.
    echo [server]
    echo headless = true
    echo port = 8501
    echo.
    echo [browser]
    echo gatherUsageStats = false
) > "%BUILD_DIR%\.streamlit\config.toml"

echo  [OK] Aplicacion copiada.
timeout /t 2 /nobreak >nul

REM ============================================================================
REM PASO 7: Crear scripts de ejecucion
REM ============================================================================

cls
echo.
echo  ============================================================
echo   PASO 7 de 7: Creando scripts de ejecucion
echo  ============================================================
echo.

REM Crear EJECUTAR.bat (para usuarios finales)
(
    echo @echo off
    echo REM ====================================================
    echo REM  DIEXA Boretrak QA - Ejecutar
    echo REM  Doble clic para iniciar la aplicacion
    echo REM ====================================================
    echo.
    echo setlocal
    echo cd /d "%%~dp0"
    echo title DIEXA - Boretrak QA
    echo color 1F
    echo.
    echo cls
    echo echo.
    echo echo  ============================================
    echo echo   DIEXA - Boretrak QA
    echo echo   Distribuidora de Explosivos y Accesorios S.A.
    echo echo  ============================================
    echo echo.
    echo echo  Iniciando la aplicacion...
    echo echo  Se abrira una ventana del navegador.
    echo echo  NO cierre esta ventana mientras usa la herramienta.
    echo echo.
    echo.
    echo REM Configurar PATH para que pytesseract encuentre tesseract.exe
    echo set "PATH=%%~dp0tesseract;%%PATH%%"
    echo.
    echo REM Ejecutar Streamlit con Python embebido
    echo "%%~dp0python\python.exe" -m streamlit run "%%~dp0app_diexa_boretrak_v10.py" ^^
    echo     --server.headless=true ^^
    echo     --browser.gatherUsageStats=false
    echo.
    echo pause
) > "%BUILD_DIR%\EJECUTAR.bat"

REM Crear README.txt
(
    echo ================================================================
    echo  DIEXA Boretrak QA v10.0 - Version Portable
    echo  Distribuidora de Explosivos y Accesorios S.A.
    echo ================================================================
    echo.
    echo  Herramienta creada por Sebastian Zuniga Leyton
    echo  Ingeniero Civil de Minas
    echo.
    echo ================================================================
    echo.
    echo  COMO USAR
    echo  ---------
    echo  1. Haga DOBLE CLIC en: EJECUTAR.bat
    echo  2. Espere unos segundos a que abra el navegador
    echo  3. Cargue los archivos PDF Boretrak/Carlson
    echo  4. Revise los resultados en las pestanas
    echo.
    echo  IMPORTANTE: NO cierre la ventana negra mientras usa la app.
    echo.
    echo ================================================================
    echo.
    echo  CARACTERISTICAS
    echo  ---------------
    echo  - NO requiere instalar Python
    echo  - NO requiere instalar Tesseract OCR
    echo  - NO requiere instalar nada
    echo  - Solo doble clic y funciona
    echo.
    echo ================================================================
    echo.
    echo  CONTENIDO DE ESTA CARPETA
    echo  -------------------------
    echo  EJECUTAR.bat              - Doble clic para iniciar
    echo  app_diexa_boretrak_v10.py - Aplicacion principal
    echo  python\                   - Python embebido
    echo  tesseract\                - Tesseract OCR
    echo  .streamlit\               - Configuracion de tema
    echo  README.txt                - Este archivo
    echo.
    echo ================================================================
    echo.
    echo  PROBLEMAS COMUNES
    echo  -----------------
    echo.
    echo  El navegador no se abre:
    echo    - Espere 30 segundos en la primera ejecucion
    echo    - Abra manualmente: http://localhost:8501
    echo.
    echo  Antivirus bloquea EJECUTAR.bat:
    echo    - Es seguro. Agregue excepcion para esta carpeta.
    echo.
    echo  Faltan datos en los PDFs:
    echo    - Los PDFs deben ser informes Boretrak/Carlson
    echo    - Active "Usar OCR de respaldo" en el panel lateral
    echo.
    echo ================================================================
    echo.
    echo  SOPORTE
    echo  -------
    echo  Para consultas tecnicas, contacte al area de Ingenieria.
    echo.
    echo ================================================================
) > "%BUILD_DIR%\README.txt"

echo  [OK] Scripts creados.
timeout /t 2 /nobreak >nul

REM ============================================================================
REM Verificacion final
REM ============================================================================

cls
echo.
echo  ============================================================
echo   VERIFICACION FINAL
echo  ============================================================
echo.

set "ALL_OK=1"

if exist "%BUILD_DIR%\python\python.exe" (
    echo  [OK] Python embebido
) else (
    echo  [X]  Python embebido FALTA
    set "ALL_OK=0"
)

if exist "%BUILD_DIR%\python\Lib\site-packages\streamlit" (
    echo  [OK] Streamlit instalado
) else (
    echo  [X]  Streamlit FALTA
    set "ALL_OK=0"
)

if exist "%BUILD_DIR%\python\Lib\site-packages\pandas" (
    echo  [OK] Pandas instalado
) else (
    echo  [X]  Pandas FALTA
    set "ALL_OK=0"
)

if exist "%BUILD_DIR%\python\Lib\site-packages\matplotlib" (
    echo  [OK] Matplotlib instalado
) else (
    echo  [X]  Matplotlib FALTA
    set "ALL_OK=0"
)

if exist "%BUILD_DIR%\tesseract\tesseract.exe" (
    echo  [OK] Tesseract OCR
) else (
    echo  [!]  Tesseract OCR no incluido (la app funcionara sin OCR)
)

if exist "%BUILD_DIR%\app_diexa_boretrak_v10.py" (
    echo  [OK] Aplicacion
) else (
    echo  [X]  Aplicacion FALTA
    set "ALL_OK=0"
)

if exist "%BUILD_DIR%\EJECUTAR.bat" (
    echo  [OK] Script de ejecucion
) else (
    echo  [X]  EJECUTAR.bat FALTA
    set "ALL_OK=0"
)

echo.

REM Calcular tamano
echo  Calculando tamano del paquete...
for /f "tokens=3" %%a in ('dir /s /-c "%BUILD_DIR%" ^| findstr /R /C:"[0-9] File"') do set "FOLDER_SIZE=%%a"

echo.
echo  ============================================================
if "%ALL_OK%"=="1" (
    echo   [OK] PAQUETE PORTABLE GENERADO EXITOSAMENTE
) else (
    echo   [!] PAQUETE GENERADO CON ADVERTENCIAS
)
echo  ============================================================
echo.
echo  Ubicacion: %BUILD_DIR%
echo.
echo  PROXIMOS PASOS:
echo.
echo   1. Probar localmente (RECOMENDADO):
echo      Doble clic en %BUILD_DIR%\EJECUTAR.bat
echo.
echo   2. Comprimir la carpeta en ZIP:
echo      Clic derecho sobre la carpeta -^> "Enviar a" -^> "Carpeta comprimida"
echo.
echo   3. Distribuir el ZIP a sus compañeros
echo.
echo   4. Ellos solo deben:
echo      - Descomprimir el ZIP
echo      - Doble clic en EJECUTAR.bat
echo.
echo  ============================================================
echo.
pause
