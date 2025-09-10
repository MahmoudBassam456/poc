# Faiss_controller.py
from ..Vector_db.Vector_dbEnums import VectorDbType
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from sentence_transformers import CrossEncoder
from langchain_community.chat_models import ChatOpenAI
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.schema import HumanMessage, SystemMessage
import faiss
import os


class FaissController:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.embeddings = HuggingFaceEmbeddings(
    model_name=VectorDbType.HUGGINGFACE_EMBEDDING_ID.value,
    
)
        self.full_project_base =None
        self.files_path =None
        self.reranker =CrossEncoder(VectorDbType.RERANKER_MODEL_ID2.value)
        self.dimension = VectorDbType.RERANKER_MODEL_DIMENSION.value  # لأن all-MiniLM-L6-v2 له 384 بُعدًا
        self.db = None
        self.reteriver = None
        self._initialize_db()

    def _initialize_db(self):
        """تهيئة FAISS من الصفر أو تحميل من القرص"""
        if os.path.exists(self.db_path
                          ):
            # تحميل قاعدة بيانات موجودة
            self.db = FAISS.load_local(
                self.db_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            # إنشاء قاعدة بيانات جديدة
            index = faiss.IndexFlatL2(self.dimension)
            docstore = InMemoryDocstore()
            index_to_docstore_id = {}
            self.db = FAISS(
                embedding_function=self.embeddings,  # ← كائن كامل، مش دالة
                index=index,
                docstore=docstore,
                index_to_docstore_id=index_to_docstore_id
            )

    def add_documents(self, docs):
        """إضافة وثائق إلى FAISS"""
        if self.db is None:
            self._initialize_db()

        self.db.add_documents(docs)
        self.save()

    def save(self):
        """حفظ قاعدة البيانات على القرص"""
        if self.db:
            self.db.save_local(self.db_path)

    def search(self, query: str, k: int = 3):
        """البحث عن أقرب النتائج"""
        if self.db is None:
            return []
        results = self.db.as_retriever(search_kwargs={"k": 5})
        self.reteriver = results
        results = results.get_relevant_documents(query)
        return [
            {
                "text": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in results
        ]


    def llms_answer(self, query: str):
      llm = ChatOpenAI(
        openai_api_key="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",
        openai_api_base="https://openrouter.ai/api/v1",
        model="openai/gpt-4-turbo",
        temperature=0.7
    )

      retriever = self.db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 20, "fetch_k": 80, "lambda_mult": 0.3}
    )

      candidates = retriever.get_relevant_documents(query)
      if not candidates:
        return "No documents found in the database to answer the query."

      ranked_docs = self.rerank(query, candidates)
      context = " ".join([doc.page_content for doc in ranked_docs[:5]])
      if not context.strip():
        return "No usable content found in the top documents."
    
      messages = [
    SystemMessage(
        content=(
            "You are an Expert, practical, and friendly maintenance assistant for industrial machines, "
            "especially CNC systems and fiber laser cutting machines.\n\n"
            "### Response Style:\n"
            "- Always answer in **Egyptian Arabic (colloquial)**.\n"
            "- Keep all technical terms in **English** (e.g., spindle, servo motor, PLC, G-code, parameters, focus, speed, power).\n"
            "- Structure the answer **step by step** using numbered steps or bullet points.\n"
            "- For each step, show the **English command/action first**, then explain in Arabic after the colon.\n"
            "- Keep paragraphs short, concise, and easy to read — no walls of text.\n"
            "- If context is missing, say clearly: 'ما عنديش كفاية دلوقتي، بس ممكن نبحث مع بعض.'\n"
            "- Use a practical technician-to-technician tone, like giving clear instructions in a workshop.\n"
            "- Include **Tips (نصائح)** and **Warnings (تحذيرات)** whenever relevant.\n"
            "- Add small real-world **examples with numbers** where possible (e.g., speed = 1500 mm/min for 5mm sheet).\n"
            "- Make sure instructions follow a **logical sequence**.\n"
            "- At the end, include a short **summary/reminder in Arabic**.\n"
            "- Example formatting:\n"
            "  1. **Command / Action**: شرح بالعربي.\n"
            "     - ⚡ Tip: نصيحة.\n"
            "     - ⚠️ Warning: تحذير.\n\n"
            "- Write English first, then Arabic , for clarity (like this: 'CNC machine موجودة في مصر which is used في مصر والعالم العربي').\n"
            "### Always answer based on the provided context and write for a technician in a workshop."
        )
    ),
    HumanMessage(
        content=f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    )
]








    # استدعاء LLM بالطريقة الصحيحة
      answer = llm(messages)
      return answer.content

    def rerank(self,query:str, candidates: list):
       pairs = [(query, doc.page_content) for doc in candidates]
       scores = self.reranker.predict(pairs)
       ranked = [doc for _, doc in sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)]
       return ranked
    def create_data_db_path(self, project_id: str) -> str:
        self.full_project_base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.files_path =os.path.join(self.full_project_base, "assets/Files")
        project_path = os.path.join(base_path, project_id)
        os.makedirs(project_path, exist_ok=True)
        return os.path.join(project_path, "faiss_index")