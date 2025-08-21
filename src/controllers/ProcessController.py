from .BaseController import basecontroller
from .ProjectController import ProjectController
import os
from models import ProcessEnum
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from langchain_community.document_loaders import (
    TextLoader,
    Docx2txtLoader    # ← قارئ PDF من LangChain
)

from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.text import partition_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document



import nltk

class ProcessController(basecontroller):
    def __init__(self,file_path: str):
        super().__init__()
        self.file_path = file_path
        self.project_path = ProjectController().get_project_path(file_id=self.file_path)
    def get_file_extension(self):
        """Returns the file extension of the file."""
        return os.path.splitext(self.file_path)[-1]
    def get_pdf_file_loader(self,file_path :str):
        """Returns a DocumentFile loader for PDF files."""
        doc = DocumentFile.from_pdf(file_path)
        predictor = ocr_predictor(pretrained=True)
        result = predictor(doc)
        all_text = []
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    all_text.append(" ".join([word.value for word in line.words]))
        return all_text
    def get_file_loader(self, file_path: str):
      file_extension = self.get_file_extension()  # دائمًا خلي الامتداد صغير
      base_name = os.path.basename(file_path)

    # تجاهل ملفات Word المؤقتة

      if file_extension == ProcessEnum.TXT.value:
        return ProcessEnum.TXT.value, partition_text(file_path)
      elif file_extension == ProcessEnum.PDF.value:
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")

        try:
            nltk.data.find("tokenizers/punkt_tab")
        except LookupError:
            nltk.download("punkt_tab")

        try:
            nltk.data.find("taggers/averaged_perceptron_tagger_eng")
        except LookupError:
            nltk.download("averaged_perceptron_tagger_eng")

        return ProcessEnum.PDF.value, partition_pdf(file_path,
                                                    strategy="hi_res")
                                                  
      elif file_extension == ProcessEnum.DOCX.value:
        try:
            loader = partition_docx(file_path)
            return ProcessEnum.DOCX.value, loader
        except Exception as e:
            print(f"Error loading DOCX file: {e}")
            return None, None
      else:
        return None, None

    def get_file_content(self):
       file_ext, loader = self.get_file_loader(file_path=self.file_path)
       if loader and file_ext in [ProcessEnum.TXT.value, ProcessEnum.DOCX.value]:
        return loader
       elif loader and file_ext == ProcessEnum.PDF.value:
        return loader
       else:
        return ProcessEnum.NOTSUPPORTED.value

    def get_chunked_content(self, file_content: list, chunk_size: int = 100, overlap_size: int = 20):
      """Splits the file content into chunks using langchain TextSplitter."""

    # تحويل كل عنصر إلى Document مؤقت
      docs = [Document(page_content=el.text, metadata=el.metadata.to_dict() if hasattr(el.metadata, "to_dict") else {}) for el in file_content]

    # إعداد TextSplitter
      text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap_size,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
      )

    # تقسيم النصوص إلى chunks
      chunked_docs = text_splitter.split_documents(docs)
      return chunked_docs