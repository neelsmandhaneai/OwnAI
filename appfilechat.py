import streamlit as st
from langchain_ollama.chat_models import ChatOllama
from langchain.schema import HumanMessage
import fitz  # PyMuPDF for PDF
import docx  # for .docx files
import csv
import io

# Set up page
st.set_page_config(page_title="DeepSeek Chat", layout="centered")
st.title("🧠 DeepSeek Chatbot")
st.markdown("Chat with the DeepSeek model using Ollama + LangChain")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# File upload section
uploaded_file = st.file_uploader("📁 Upload a file (TXT, CSV, PDF, DOCX)", type=["txt", "csv", "pdf", "docx"])
file_text = ""

def extract_text_from_file(file):
    file_type = file.name.split('.')[-1].lower()
    try:
        if file_type == "txt":
            return file.read().decode("utf-8", errors="ignore")
        elif file_type == "csv":
            decoded = file.read().decode("utf-8", errors="ignore")
            reader = csv.reader(io.StringIO(decoded))
            return "\n".join([", ".join(row) for row in reader])
        elif file_type == "docx":
            doc = docx.Document(file)
            return "\n".join([para.text for para in doc.paragraphs])
        elif file_type == "pdf":
            text = ""
            with fitz.open(stream=file.read(), filetype="pdf") as pdf:
                for page in pdf:
                    text += page.get_text()
            return text
        else:
            return "Unsupported file type."
    except Exception as e:
        return f"Error reading file: {e}"

if uploaded_file is not None:
    file_text = extract_text_from_file(uploaded_file)
    if file_text:
        st.success("✅ File uploaded and content extracted.")

# Set up model
# llm = ChatOllama(model="deepseek-r1:latest")
llm = ChatOllama(model="deepseek-r1:latest", base_url="http://localhost:11434")
# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Chat input
prompt = st.chat_input("Type your message...")

if prompt:
    # Merge file content with prompt if available
    full_prompt = f"File Content:\n{file_text}\n\nUser Question:\n{prompt}" if file_text else prompt

    # Add user message to session
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    # Generate response
    with st.spinner("Thinking..."):
        response = llm.invoke([HumanMessage(content=full_prompt)])
        bot_reply = response.content

    # Add bot response to session
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    st.chat_message("assistant").markdown(bot_reply)
