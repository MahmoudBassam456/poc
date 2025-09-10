from enum import Enum
class VectorDbType(Enum):
    FAISS ="FAISS"
    FAISS_FILE_NAME="Vector_db"
    HUGGINGFACE_EMBEDDING_ID = "sentence-transformers/LaBSE"
    #temporary enums
    LLM_MODEL_ID = "meta-llama/Llama-2-7b-chat-hf"
    LLM_API="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"
    LLM_URL="https://openrouter.ai/api/v1"
    RERANKER_MODEL_ID="BAAI/bge-reranker-large"
    RERANKER_MODEL_DIMENSION=768
    RERANKER_MODEL_ID2="sentence-transformers/all-MiniLM-L6-v2"