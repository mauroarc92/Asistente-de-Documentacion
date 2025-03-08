📚 Asistente de Documentación con RAG

Este proyecto es un asistente de documentación basado en Retrieval-Augmented Generation (RAG). Permite cargar archivos en diferentes formatos (PDF, TXT, DOCX, XLSX) y hacer preguntas sobre su contenido utilizando modelos de lenguaje.

✨ Características

Carga de documentos: Soporta PDF, TXT, Word y Excel.

Búsqueda eficiente: Utiliza FAISS para almacenar y recuperar información relevante.

Respuesta estructurada: Proporciona respuestas organizadas en resumen, pasos detallados y notas adicionales.

Interfaz amigable: Implementado con Streamlit para una experiencia de usuario intuitiva.

🛠 Tecnologías utilizadas

Python

Streamlit

LangChain

FAISS

OpenAI API

PyMuPDF, Pandas (para procesar documentos)

🚀 Instalación y uso

1️⃣ Clonar el repositorio

git clone https://github.com/mauroarc92/Asistente-de-Documentacion.git
cd Asistente-de-Documentacion

Crear un entorno virtual e instalar dependencias

python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

Configurar variables de entorno

Crea un archivo .env en la carpeta principal y agrega tu clave de API de OpenAI:

OPENAI_API_KEY=tu_api_key_aqui

Ejecutar la aplicación

streamlit run app.py

📌 Uso

Sube un documento en formato PDF, TXT, Word o Excel.

Haz una pregunta sobre su contenido en el chat.

Obtén respuestas estructuradas con información relevante.

📌 Mejoras futuras

Soporte para visualización de imágenes.

Mejor procesamiento de tablas en documentos.

Integración con bases de datos para almacenamiento de documentos.

