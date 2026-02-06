# scripts/build_index.py
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

# Настройки
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
INDEX_PATH = "data/faiss_index"
KB_DIR = "knowledge_base"

if __name__ == "__main__":
    print("Загрузка документов...")
    docs = []
    for file in os.listdir(KB_DIR):
        if file.endswith("_obfuscated.txt"):
            loader = TextLoader(os.path.join(KB_DIR, file), encoding="utf-8")
            docs.extend(loader.load())

    print(f"Загружено {len(docs)} документов")

    # Разбиение на чанки
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    print(f"Создано {len(chunks)} чанков")

    # Эмбеддинги
    print("Генерация эмбеддингов...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    db = FAISS.from_documents(chunks, embeddings)

    # Сохранение
    db.save_local(INDEX_PATH)
    print(f"✅ Индекс сохранён в {INDEX_PATH}")