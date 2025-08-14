from .BaseController import basecontroller
from fastapi import UploadFile
from models import ResponseSignalsFile
class DataController(basecontroller):
    def __init__(self):
        super().__init__()
    #validate configuration
    def validate_config(self,file :UploadFile):
        if file.content_type not in self.conf.FILE_ALOWED_TYPES:
            return False,ResponseSignalsFile.Invalid_File_Type.value
        if file.size > self.conf.FILE_MAX_SIZE:
           return False,ResponseSignalsFile.File_Size_Exceeded
        return True, ResponseSignalsFile.File_Valid.value
    