from abc import ABC, abstractmethod

class VectorDBInterface(ABC):
    @abstractmethod
    def set_vector_db(self, vector_db_path: str):
       pass
    @abstractmethod
    def get_vector_db(self) -> str:
        pass     
    @abstractmethod
    def get_Vector_db_path(self) -> str:
        pass
    def add_vector(self, vector: list, metadata: dict) -> str:
        pass
    @abstractmethod
    def search_vector(self, query_vector: list, top_k: int = 5) -> list:
        pass
    
  