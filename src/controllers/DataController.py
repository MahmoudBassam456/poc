from .BaseController import basecontroller
from fastapi import UploadFile
from models import ResponseSignalsFile
from controllers import ProjectController
import re
import os
class DataController(basecontroller):
    def __init__(self):
        super().__init__()
    #validate configuration
    def validate_config(self,file :UploadFile):
        if file.content_type not in self.conf.FILE_ALOWED_TYPES:
            return False,ResponseSignalsFile.Invalid_File_Type.value
        if file.size > self.conf.FILE_MAX_SIZE:
           return False,ResponseSignalsFile.File_Size_Exceeded.value
        return True, ResponseSignalsFile.File_Valid.value
#    def get_file_path(self, file_id: str) :
        #return os.path.join(ProjectController().get_project_path(file_id=file_id), file_id)
    def clean_filename_build(self,files_path: str, file: UploadFile) -> str:
        """Generates a random file name based on the file ID."""
        cleaned_name = re.sub(r'[^a-zA-Z0-9_.-]+', '_', self.get_random_file_name()).strip('_')
        file_path =os.path.join(files_path,cleaned_name+"_"+ file.filename)
        while os.path.exists(file_path):
            cleaned_name = re.sub(r'[^a-zA-Z0-9_.-]+', '_', self.get_random_file_name()).strip('_')
            file_path = os.path.join(files_path, cleaned_name + "_" + file.filename)
        return file_path
      
    
