🧨 DIEXA Boretrak QA
Análisis de Chimeneas y Control de Calidad Boretrak
Herramienta corporativa para extracción de datos, análisis y generación de reportes a partir de informes Boretrak/Carlson en formato PDF.
Creada por Sebastián Zúñiga Leyton – Ingeniero Civil de Minas

📋 Descripción
DIEXA Boretrak QA es una aplicación web que permite:

Extracción robusta de datos desde PDFs Boretrak/Carlson
Análisis de desviación (inclinación, metraje, azimut)
Control de calidad con tolerancias configurables
Gráficos profesionales (polares, barras, comparativos)
Exportación a Excel con reportes estructurados
OCR opcional para PDFs escaneados
Identidad corporativa DIEXA integrada


🚀 Inicio Rápido
Opción A: Ejecutar directamente (requiere Python 3.8+)
bash# 1. Clonar o descargar el repositorio
git clone https://github.com/tu-usuario/diexa-boretrak-qa.git
cd diexa-boretrak-qa

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
streamlit run app_diexa_boretrak_v10.py
Opción B: Ejecutar en Windows sin instalar nada (Recomendado)
Descargar la versión Portable desde Releases:

Descargar DIEXA_Boretrak_Portable.zip
Descomprimir
Doble clic en EJECUTAR.bat
¡Listo!


📦 Requisitos
Para desarrollo/instalar manualmente:

Python 3.8+
pip (gestor de paquetes de Python)

Dependencias Python:
streamlit>=1.56.0
pandas>=3.0.0
numpy>=2.4.0
matplotlib>=3.10.0
PyPDF2>=3.0.0
pdfplumber>=0.11.0
PyMuPDF>=1.27.0
pytesseract>=0.3.0
Pillow>=12.0.0
openpyxl>=3.1.0
Para OCR (opcional):

Tesseract-OCR (descargable desde aquí)


💾 Instalación
Linux/Mac
bashgit clone https://github.com/tu-usuario/diexa-boretrak-qa.git
cd diexa-boretrak-qa
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Windows
batchgit clone https://github.com/tu-usuario/diexa-boretrak-qa.git
cd diexa-boretrak-qa
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

🎯 Uso
Ejecución en desarrollo:
bashstreamlit run app_diexa_boretrak_v10.py
Se abrirá automáticamente en http://localhost:8501
Uso básico:

Cargue PDFs en la sección "Carga de archivos PDF"
Configure tolerancias en el panel lateral (opcional)
Active OCR si necesita (para PDFs escaneados)
Revise resultados en las pestañas:

📊 Resumen General: indicadores globales
📝 Detalle por Tiro: análisis individual
📈 Análisis por Chimenea: gráficos comparativos
🧪 Diagnóstico: verificación de extracción


Descargue reporte Excel con todos los datos


📊 Características
Análisis de datos

Extracción inteligente de:

Desviación final (superior)
Desviación por inclinación
Metraje (Largo, DESV, DESV%, AZ, INC)
Tolerancias configurables



Visualización

Gráficos polares de desviación por tiro/chimenea
Gráficos de barras comparativos
Tablas resumen por chimenea y tiro
Dashboard interactivo con indicadores clave

Control de calidad

Semáforo visual (🟢 Conforme / 🟡 Parcial / 🔴 No conforme / ⚪ Sin datos)
Reportes de QC con observaciones automáticas
Validación de datos con alertas

Exportación

Reporte Excel con 3 hojas:

Resumen de tiros
Resumen de chimeneas
Detalle de metraje




🎨 Diseño Corporativo

Paleta de colores DIEXA (azul corporativo #00a2e5)
Interfaz profesional y técnica
Tipografía clara y legible
Footer con créditos corporativos


🔧 Estructura del Proyecto
diexa-boretrak-qa/
├── app_diexa_boretrak_v10.py      # Aplicación principal
├── requirements.txt                 # Dependencias
├── BUILD_PORTABLE.bat              # Script para generar versión portable
├── README.md                        # Este archivo
├── LICENSE                          # Licencia
└── .gitignore                       # Archivos ignorados por Git

📄 Archivos Clave
app_diexa_boretrak_v10.py
Aplicación principal con:

Extracción de PDFs (pdfplumber + PyPDF2)
OCR opcional (Tesseract)
Análisis de datos con regex y pandas
Gráficos con matplotlib
Interfaz con Streamlit

requirements.txt
Lista de todas las dependencias. Generar con:
bashpip freeze > requirements.txt
BUILD_PORTABLE.bat
Script para generar versión portable sin instalación (solo Windows).

🐛 Solución de Problemas
No aparecen gráficos

Verifique que los PDFs contienen tabla "Implementación-1"
Active OCR si los PDFs están escaneados
Ejecute check_dependencies.py para diagnosticar

OCR no funciona
bash# Instalar Tesseract (Windows)
# Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
# Instalar en: C:\Program Files\Tesseract-OCR\

# La app lo detectará automáticamente después
Python no encontrado (versión portable)

Reinicie el equipo después de instalar Python
Asegúrese de marcar "Add Python to PATH" durante instalación


📝 Versioning
Versiones disponibles:

v10.0 (actual): Primera versión corporativa con diseño DIEXA completo
v9.4: Versión base sin diseño corporativo


🤝 Contribuciones
Para reportar bugs o sugerir mejoras:

Abra un Issue
Incluya:

Descripción del problema
Pasos para reproducir
Archivo PDF problemático (si es seguro compartirlo)




📄 Licencia
Uso interno de DIEXA - Distribuidora de Explosivos y Accesorios S.A.

👤 Autor
Sebastián Zúñiga Leyton

Ingeniero Civil de Minas
Desarrollador y diseñador de esta herramienta


📞 Soporte
Para consultas técnicas, contacte al área de Ingeniería de DIEXA.

🚀 Próximas Mejoras

 Soporte para otros formatos de PDF
 API REST para integración
 Dashboard web centralizado
 Gestión de usuarios
 Historial de análisis


📊 Estadísticas

Lineas de código: ~1,300
Funciones: 50+
Tests: En desarrollo
Documentación: Completa en español


Última actualización: Abril 2025
Versión actual: 10.0
