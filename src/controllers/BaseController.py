from helpers.config import get_config, Config
import os
import string
import random
class basecontroller:
    def __init__ (self):
        self.conf= get_config()
        self.full_project_base = os.path.dirname(os.path.dirname(__file__))
        self.files_path =os.path.join(self.full_project_base, "assets/Files")
    def get_random_file_name(self,num_charater :int=12) -> str:
        """Generates a random file name based on the file ID."""
        random_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=num_charater))
        return f"{random_key}"
    
