# Faiss_controller.py
import os
import logging
from typing import List, Dict, Any, Optional
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.schema import HumanMessage, SystemMessage, Document
from sentence_transformers import CrossEncoder
from ..Vector_db.Vector_dbEnums import VectorDbType
from helpers import get_config, Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaissController:
    """
    A controller class for managing FAISS vector database operations.
    
    This class provides functionality to:
    - Initialize and manage FAISS vector stores
    - Add documents to the vector database
    - Search for similar documents
    - Generate AI-powered answers using retrieval-augmented generation
    - Rerank search results for better relevance
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the FAISS controller.
        
        Args:
            db_path (str): Path to the FAISS database directory
        """
        try:
            self.config: Config = get_config()
            self.db_path = db_path
            
            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=VectorDbType.HUGGINGFACE_EMBEDDING_ID.value,
            )
            
            # Initialize paths
            self.full_project_base = None
            self.files_path = None
            
            # Initialize reranker
            self.reranker = CrossEncoder(VectorDbType.RERANKER_MODEL_ID2.value)
            
            # Get embedding dimension
            self.dimension = VectorDbType.RERANKER_MODEL_DIMENSION.value
            
            # Initialize database components
            self.db: Optional[FAISS] = None
            self.retriever = None
            
            # Initialize the database
            self._initialize_db()
            
            logger.info(f"FaissController initialized with db_path: {db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize FaissController: {str(e)}")
            raise

    def _initialize_db(self) -> None:
        """
        تهيئة قاعدة بيانات FAISS من الصفر أو تحميل من القرص.
        
        إذا كانت قاعدة بيانات موجودة في المسار المحدد، سيتم تحميلها.
        وإلا، ستُنشأ قاعدة بيانات جديدة فارغة.
        """
        try:
            if os.path.exists(self.db_path) and os.listdir(self.db_path):
                # تحميل قاعدة بيانات موجودة
                logger.info(f"تحميل قاعدة بيانات FAISS موجودة من {self.db_path}")
                self.db = FAISS.load_local(
                    self.db_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("تم تحميل قاعدة البيانات بنجاح")
            else:
                # إنشاء قاعدة بيانات جديدة
                logger.info("إنشاء قاعدة بيانات FAISS جديدة")
                index = faiss.IndexFlatL2(self.dimension)
                docstore = InMemoryDocstore()
                index_to_docstore_id = {}
                
                self.db = FAISS(
                    embedding_function=self.embeddings,
                    index=index,
                    docstore=docstore,
                    index_to_docstore_id=index_to_docstore_id
                )
                logger.info("تم إنشاء قاعدة البيانات الجديدة بنجاح")
                
        except Exception as e:
            logger.error(f"فشل في تهيئة قاعدة البيانات: {str(e)}")
            raise

    def add_documents(self, docs: List[Document]) -> bool:
        """
        Add documents to the FAISS database.
        
        Args:
            docs (List[Document]): List of documents to add
            
        Returns:
            bool: True if documents were added successfully, False otherwise
        """
        try:
            if not docs:
                logger.warning("No documents provided to add")
                return False
                
            if self.db is None:
                logger.info("Database not initialized, initializing now")
                self._initialize_db()

            logger.info(f"Adding {len(docs)} documents to database")
            self.db.add_documents(docs)
            self.save()
            logger.info("Documents added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            return False

    def save(self) -> bool:
        """
        Save the database to disk.
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            if self.db is None:
                logger.warning("No database to save")
                return False
                
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            self.db.save_local(self.db_path)
            logger.info(f"Database saved to {self.db_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save database: {str(e)}")
            return False

    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for the most similar documents to the query.
        
        Args:
            query (str): Search query
            k (int): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of search results with text and metadata
        """
        try:
            if self.db is None:
                logger.warning("Database not initialized")
                return []
                
            if not query.strip():
                logger.warning("Empty query provided")
                return []

            logger.info(f"Searching for query: '{query}' with k={k}")
            
            # Create retriever
            retriever = self.db.as_retriever(search_kwargs={"k": max(k, 5)})
            self.retriever = retriever
            
            # Get relevant documents
            results = retriever.get_relevant_documents(query)
            
            # Format results
            formatted_results = [
                {
                    "text": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in results[:k]
            ]
            
            logger.info(f"Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    def llms_answer(self, query: str) -> str:
        """
        Generate an AI-powered answer using retrieval-augmented generation.
        
        Args:
            query (str): User question/query
            
        Returns:
            str: Generated answer based on retrieved context
        """
        try:
            if self.db is None:
                return "Database not initialized. Please add documents first."
                
            if not query.strip():
                return "Please provide a valid query."

            logger.info(f"Generating answer for query: '{query}'")
            
            # Initialize LLM
            llm = ChatOpenAI(
                openai_api_key=self.config.OPEN_ROUTER_API_KEY,
                openai_api_base=self.config.Open_ROUTER_URL,
                model=VectorDbType.GPT4_MODEL.value,
                temperature=0.2,
                max_retries=5,
                max_tokens=4096,
                streaming=True,
                model_kwargs={
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1,
            }
            )

            # Create retriever with MMR (Maximal Marginal Relevance)
            retriever = self.db.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 20, "fetch_k": 80, "lambda_mult": 0.3, "maximal_marginal_relevance": True}
            )

            # Get candidate documents
            candidates = retriever.get_relevant_documents(query)
            if not candidates:
                return "No documents found in the database to answer the query."

            # Rerank documents for better relevance
            ranked_docs = self.rerank(query, candidates)
            
            # Create context from top documents
            context = "\n\n".join([doc.page_content for doc in ranked_docs[:5]])
            if not context.strip():
                return "No usable content found in the top documents."
            
            # Prepare messages for LLM
            messages = [
                SystemMessage(content=VectorDbType.SYSTEM_PROMPT.value),
                HumanMessage(
                    content=f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
                )
            ]

            # Generate answer
            logger.info("Generating LLM response")
            answer = llm(messages)
            
            logger.info("Answer generated successfully")
            return answer.content
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {str(e)}")
            return f"Sorry, I encountered an error while processing your question: {str(e)}"

    def rerank(self, query: str, candidates: List[Document]) -> List[Document]:
        """
        Rerank candidate documents based on relevance to the query.
        
        Args:
            query (str): Search query
            candidates (List[Document]): List of candidate documents
            
        Returns:
            List[Document]: Reranked list of documents
        """
        top_k = 10
        try:
            if not candidates:
                return []
                
            logger.info(f"Reranking {len(candidates)} candidates")
            
            # Create query-document pairs for reranking
            pairs = [(query, doc.page_content) for doc in candidates]
            
            # Get relevance scores
            scores = self.reranker.predict(pairs)
            
            # Sort documents by relevance score (descending)
            ranked = [
                doc for _, doc in sorted(
                    zip(scores, candidates), 
                    key=lambda x: x[0],
                    reverse=True
                )
            ]
            
            logger.info("Documents reranked successfully")
            return ranked
            
        except Exception as e:
            logger.error(f"Failed to rerank documents: {str(e)}")
            return candidates[:top_k]  # Return original order if reranking fails

    def create_data_db_path(self, project_id: str) -> str:
        """
        Create a database path for a specific project.
        
        Args:
            project_id (str): Unique project identifier
            
        Returns:
            str: Full path to the project's FAISS database
        """
        try:
            # Get project base directory
            self.full_project_base = os.path.dirname(
                os.path.dirname(os.path.dirname(__file__))
            )
            
            # Set files path
            self.files_path = os.path.join(self.full_project_base, "assets/Files")
            
            # Create project-specific path
            project_path = os.path.join(self.files_path, project_id)  # Fixed: was using undefined base_path
            os.makedirs(project_path, exist_ok=True)
            
            db_path = os.path.join(project_path, "faiss_index")
            logger.info(f"Created database path: {db_path}")
            
            return db_path
            
        except Exception as e:
            logger.error(f"Failed to create database path: {str(e)}")
            raise

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current database.
        
        Returns:
            Dict[str, Any]: Database statistics including document count
        """
        try:
            if self.db is None:
                return {"status": "not_initialized", "document_count": 0}
                
            # Get document count
            doc_count = self.db.index.ntotal if hasattr(self.db.index, 'ntotal') else 0
            
            return {
                "status": "initialized",
                "document_count": doc_count,
                "dimension": self.dimension,
                "db_path": self.db_path
            }
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            return {"status": "error", "error": str(e)}

    def clear_database(self) -> bool:
        """
        Clear all documents from the database.
        
        Returns:
            bool: True if cleared successfully, False otherwise
        """
        try:
            logger.info("Clearing database")
            
            # Reinitialize empty database
            index = faiss.IndexFlatL2(self.dimension)
            docstore = InMemoryDocstore()
            index_to_docstore_id = {}
            
            self.db = FAISS(
                embedding_function=self.embeddings,
                index=index,
                docstore=docstore,
                index_to_docstore_id=index_to_docstore_id
            )
            
            # Save the empty database
            self.save()
            
            logger.info("Database cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear database: {str(e)}")
            return False