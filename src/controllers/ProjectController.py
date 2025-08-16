from .BaseController import basecontroller
from models import ResponseSignalsFile
from fastapi import UploadFile
import os
import re

class ProjectController(basecontroller):
    def __init__(self):
        super().__init__()

    # Additional methods for ProjectController can be added here
    # For example, methods to handle project creation, updates, deletions, etc.
   

    def get_project_path(self, file_id :str):
      PA = os.path.join(self.files_path, file_id)
      return PA
    
 
       
        