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
        self.reranker =CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.dimension = 768  # لأن all-MiniLM-L6-v2 له 384 بُعدًا
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
        model="qwen/qwen2.5-vl-72b-instruct:free",
        temperature=0.2
    )

      retriever = self.db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 20, "fetch_k": 80, "lambda_mult": 0.3}
    )

      candidates = retriever.get_relevant_documents(query)
      if not candidates:
        return "No documents found in the database to answer the query."

      ranked_docs = self.rerank(query, candidates)
      context = " ".join([doc.page_content for doc in ranked_docs[:3]])
      if not context.strip():
        return "No usable content found in the top documents."

    # استخدام SystemMessage و HumanMessage
      messages = [
        SystemMessage(content="You are a smart maintenance assistant, expert in CNC and industrial machines answer in Egyptian Arabic with maintaining the terminology  ."),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {query}\nAnswer:")
    ]

    # استدعاء LLM بالطريقة الصحيحة
      answer = llm(messages)
      return answer.content

    def rerank(self,query:str, candidates: list):
       pairs = [(query, doc.page_content) for doc in candidates]
       scores = self.reranker.predict(pairs)
       ranked = [doc for _, doc in sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)]
       return ranked