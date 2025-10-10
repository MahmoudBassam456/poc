from .BaseController import basecontroller
from .ProjectController import ProjectController
import os
from models import ProcessEnum
from langchain_community.document_loaders import (
    PyMuPDFLoader
)
from unstructured.partition.docx import partition_docx
from unstructured.partition.text import partition_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
import logging
from assets.services.Vector_db.Faiss_controller import FaissController



class ProcessController(basecontroller):
    def __init__(self,file_path: str):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.file_path = file_path
        self.project_path = ProjectController().get_project_path(file_id=self.file_path)
    def get_file_extension(self):
        """Returns the file extension of the file."""
        return os.path.splitext(self.file_path)[-1]
    
    def get_file_loader(self, file_path: str):
        file_extension = self.get_file_extension()
        # TXT: partition_text accepts encoding
        if file_extension == ProcessEnum.TXT.value:
            return ProcessEnum.TXT.value, partition_text(file_path, encoding="utf-8")

        # PDF: use PyMuPDFLoader without encoding; fallback to partition_pdf or OCR list
        if file_extension == ProcessEnum.PDF.value:
                self.logger.info(f"Using PyMuPDFLoader for PDF: {file_path}")
                loader = PyMuPDFLoader(file_path)  # do NOT pass encoding
                self.logger.info(f"Successfully loaded PDF with PyMuPDFLoader: {file_path}")
                return ProcessEnum.PDF.value, loader
            
        # DOCX: partition_docx does not accept encoding kw in some versions
        if file_extension == ProcessEnum.DOCX.value:
            try:
                loader = partition_docx(file_path)
                return ProcessEnum.DOCX.value, loader
            except Exception as e:
                logging.warning(f"partition_docx failed: {e}")
                return None, None

        return None, None

    def get_file_content(self):
        """Loads the file content using the appropriate loader based on file extension."""
        file_ext, loader = self.get_file_loader(file_path=self.file_path)
        if not loader:
            return ProcessEnum.NOTSUPPORTED.value

        # If loader is a LangChain-style loader object with .load()
        if hasattr(loader, "load") and callable(getattr(loader, "load")):
            try:
                return loader.load()
            except Exception as e:
                logging.warning(f"loader.load() failed: {e}")
                return ProcessEnum.NOTSUPPORTED.value

        # If loader is already a list of partitioned elements or OCR text list
        if isinstance(loader, list):
            return loader

        # If loader is an iterator/generator
        try:
            items = list(loader)
            return items
        except Exception:
            return ProcessEnum.NOTSUPPORTED.value

    def get_chunked_content(self, file_content: list, chunk_size: int = 400, overlap_size: int = 150):
        """Splits the file content into chunks using langchain TextSplitter."""

        docs = []
        for el in file_content:
            # إذا كان العنصر نص فقط
            if isinstance(el, str):
                docs.append(Document(page_content=el, metadata={}))
            # إذا كان فيه خاصية text (مثل ناتج partition_text)
            elif hasattr(el, "text"):
                docs.append(Document(page_content=el.text, metadata={}))
            # إذا كان فيه خاصية content
            elif hasattr(el, "content"):
                docs.append(Document(page_content=el.content, metadata={}))
            # إذا كان فيه خاصية page_content
            elif hasattr(el, "page_content"):
                docs.append(Document(page_content=el.page_content, metadata=getattr(el, "metadata", {})))
            else:
                # تجاهل أو سجل العنصر غير المدعوم
                continue

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        chunked_docs = text_splitter.split_documents(docs)
        return chunked_docs

    @staticmethod
    async def process_and_vectorize_files(file_paths: List[str], project_id: str):
        """
        Processes a list of files, chunks them, and adds them to the project's FAISS DB.
        """
        logging.info(f"Starting batch processing for project {project_id} with {len(file_paths)} files.")
        all_chunked_docs = []

        for file_path in file_paths:
            try:
                controller = ProcessController(file_path=file_path)
                content = controller.get_file_content()
                if content == ProcessEnum.NOTSUPPORTED.value:
                    logging.warning(f"Skipping unsupported file: {file_path}")
                    continue
                
                chunked_content = controller.get_chunked_content(file_content=content)
                all_chunked_docs.extend(chunked_content)
                logging.info(f"Successfully processed and chunked {file_path}.")
            except Exception as e:
                logging.error(f"Failed to process file {file_path}: {e}")

        if not all_chunked_docs:
            logging.warning(f"No documents were processed for project {project_id}. Aborting vectorization.")
            return

        try:
            # Get the FAISS DB path for the project
            project_path = ProjectController().get_project_path(file_id=project_id)
            faiss_db_path = os.path.join(project_path, "faiss_index")
            
            # Initialize FaissController
            faiss_controller = FaissController(db_path=faiss_db_path)
            
            # Add all documents to the FAISS index
            faiss_controller.add_documents(all_chunked_docs)
            logging.info(f"Successfully added {len(all_chunked_docs)} chunks to FAISS DB for project {project_id}.")
        except Exception as e:
            logging.error(f"Failed to vectorize documents for project {project_id}: {e}")