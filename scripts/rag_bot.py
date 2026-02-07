# scripts/rag_bot.py
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
import os
import json

# === Настройки ===
INDEX_PATH = "data/faiss_index"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CONFIG_FILE = "config.json"

# === Few-Shot Примеры ===
FEW_SHOT_EXAMPLES = """
Вопрос: Кто первым полетел на Стартуме?
Ответ: 
1. Ищу информацию о первом полёте на корабле Стартум.
2. В документе указано, что Артём Вектор совершил первый полёт на Стартуме.
3. Следовательно, первым космонавтом был Артём Вектор.

Вопрос: Что такое Мегасила?
Ответ:
1. Нужно определить, что представляет собой Мегасила.
2. В документе говорится, что Мегасила — это тяжёлая ракета-носитель, разработанная КосмоСоюзом.
3. Следовательно, Мегасила — это ракета-носитель.
"""

# === System Prompt ===
SYSTEM_PROMPT = """Ты — помощник QuantumForge Bot.
Отвечай только на основе предоставленной информации.
Если ответа нет в контексте, скажи: «Я не знаю».
Объясняй свои рассуждения по шагам (Chain-of-Thought)."""


# === Шаблон промпта ===
template = f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLES}

Контекст:
{{context}}

Вопрос: {{question}}

Рассуждение:
"""

PROMPT = PromptTemplate.from_template(template)


def get_llm_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    print("🔧 Выберите провайдера:")
    print("1) Ollama (локально)")
    print("2) OpenAI (облако)")
    choice = input("Выберите 1 или 2: ").strip()

    if choice == "1":
        config = {"llm_provider": "ollama"}
    elif choice == "2":
        key = input("Введите OpenAI API-ключ: ").strip()
        config = {"llm_provider": "openai", "openai_api_key": key}
    else:
        print("❌ Неверный выбор.")
        exit(1)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("✅ Конфиг сохранён.")
    return config


def create_llm(config):
    provider = config["llm_provider"]

    if provider == "ollama":
        try:
            return Ollama(
                model="llama3:8b-instruct-q6_K",
                base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                temperature=0.2,
            )
        except Exception as e:
            print(f"❌ Ошибка подключения к Ollama: {e}")
            print("Убедитесь, что Ollama запущена: ollama run llama3:8b-instruct-q6_K")
            exit(1)

    elif provider == "openai":
        key = config.get("openai_api_key")
        if not key:
            print("❌ Нет API-ключа OpenAI.")
            exit(1)
        return OpenAI(api_key=key, model="gpt-3.5-turbo-instruct", temperature=0.2)

    else:
        print(f"❌ Неизвестный провайдер: {provider}")
        exit(1)


def create_rag_chain():
    # Эмбеддинги
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Загружаем FAISS
    if not os.path.exists(os.path.join(INDEX_PATH, "index.faiss")):
        print("❌ Индекс не найден. Запустите: python scripts/build_index.py")
        exit(1)

    try:
        db = FAISS.load_local(
            INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True  # Для старых версий
        )
    except TypeError:
        # Поддержка старого формата
        db = FAISS.load_local(INDEX_PATH, embeddings, unsafe_allow_pickle=True)

    retriever = db.as_retriever(search_kwargs={"k": 3})

    # LLM
    config = get_llm_config()
    llm = create_llm(config)

    # Цепочка
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True,
    )
    return qa_chain


def ask_question(chain, query):
    result = chain.invoke({"query": query})
    print("\n💬 Ответ:")
    print(result["result"])

    print("\n📚 Источники:")
    for i, doc in enumerate(result["source_documents"]):
        src = doc.metadata.get("source", "неизвестно")
        print(f"  {i+1}. {src}")

    return result


if __name__ == "__main__":
    print("🚀 QuantumForge RAG-бот запущен\n")

    # Пересоздайте индекс, если нужно
    if not os.path.exists("data/faiss_index/index.faiss"):
        print("❗ Индекс не найден. Запускаю пересоздание...")
        os.system("python scripts/build_index.py")

    chain = create_rag_chain()
    print("Готов к вопросам. Введите 'exit', чтобы выйти.\n")

    # Примеры
    examples = [
        "Кто такой Артём Вектор?",
        "Что такое Мегасила?",
        "Какая страна запустила первый спутник?",
    ]
    print("🎯 Примеры запросов:")
    for ex in examples:
        print(f"  • {ex}")
    print()

    while True:
        query = input("Вопрос: ").strip()
        if query.lower() in ["exit", "выход", "quit"]:
            print("До свидания!")
            break
        if not query:
            continue
        ask_question(chain, query)
        print("-" * 60)