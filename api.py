import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredExcelLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import shutil

# Cargar variables de entorno
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Verificar la API Key
if openai_api_key is None:
    st.error("La API Key de OpenAI no está configurada correctamente.")
    st.stop()

# Configurar el modelo de OpenAI
import openai
openai.api_key = openai_api_key

# Inicializar session_state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Función para cargar documentos
def load_documents(uploaded_files):
    documents = []
    os.makedirs("temp", exist_ok=True)  # Crear la carpeta temporal si no existe
    
    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        file_path = f"temp/{uploaded_file.name}"  # Guardamos en una carpeta temporal

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if file_extension == "pdf":
            loader = PyPDFLoader(file_path)
        elif file_extension == "txt":
            loader = TextLoader(file_path)
        elif file_extension == "xlsx":
            loader = UnstructuredExcelLoader(file_path)
        elif file_extension == "docx":
            loader = UnstructuredWordDocumentLoader(file_path)
        else:
            st.warning(f"Formato no soportado: {file_extension}")
            continue

        documents.extend(loader.load())

        # Borrar el archivo después de cargarlo
        os.remove(file_path)

    return documents

# Crear VectorStore con FAISS
def create_vector_store(documents):
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store

# Configurar LLM y cadena de QA con historial de chat
def create_qa_chain(vector_store):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)  # Se mantiene la temperatura

    # Definir un prompt mejorado
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "Eres un asistente experto en documentación técnica. "
            "Responde con información precisa y estructurada basada en los documentos proporcionados. "
            "Si no encuentras información en los documentos, indica que no tienes datos en lugar de inventar.\n\n"
            "### Contexto ###\n{context}\n\n"
            "### Pregunta ###\n{question}\n\n"
            "### Respuesta estructurada ###\n"
            "1. **Resumen:** Breve explicación de la respuesta.\n"
            "2. **Pasos detallados:** Explica cada paso necesario de forma clara y concisa.\n"
            "3. **Notas adicionales:** Información extra, advertencias o configuraciones opcionales."
        ),
    )

    # Crear la cadena de combinación de documentos
    combine_documents_chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt_template)

    # Crear el sistema de preguntas y respuestas con recuperación
    qa_chain = RetrievalQA(
        retriever=vector_store.as_retriever(),
        combine_documents_chain=combine_documents_chain,
    )
    
    return qa_chain

# Interfaz con Streamlit
st.title("📚 Asistente de Documentación")
st.write("Sube documentos en formato PDF, TXT, DOCX o Excel y haz preguntas sobre su contenido.")

uploaded_files = st.file_uploader("📂 Carga tus archivos", type=["pdf", "txt", "xlsx", "docx"], accept_multiple_files=True)

if uploaded_files:
    documents = load_documents(uploaded_files)
    vector_store = create_vector_store(documents)
    qa_chain = create_qa_chain(vector_store)

# Función para limpiar la entrada después de enviar la pregunta
def clear_input():
    st.session_state.user_input = st.session_state.widget  # Guarda el texto en session_state
    st.session_state.widget = ""  # Limpia el input

# Mostrar historial de chat
st.subheader("💬 Chat")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

col1, col2 = st.columns([4, 1])  # Ajusta el ancho de las columnas según necesidad

with col1:
    st.text_input("🔍 Escribe tu pregunta:", key="widget", on_change=clear_input, label_visibility="collapsed")

# Obtener la pregunta después de limpiar el input
query = st.session_state.get("user_input", "")

with col2:
    if st.button("Preguntar") and query:
        # Guardar la pregunta en el historial
        st.session_state.messages.append({"role": "user", "content": query})

        # Obtener la respuesta del modelo con manejo de errores
        try:
            response = qa_chain.run(query)
        except Exception as e:
            response = "❌ Hubo un error al procesar tu pregunta. Intenta de nuevo."

        # Guardar la respuesta en el historial
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Limpiar la variable para evitar duplicados
        st.session_state.user_input = ""

        # Refrescar la página para mostrar la conversación actualizada
        st.rerun()

