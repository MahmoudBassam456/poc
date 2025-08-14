from helpers.config import get_config, Config
import os
class basecontroller:
    def __init__ (self):
        self.conf= get_config()
        self.full_project_base = os.path.dirname(os.path.dirname(__file__))
        self.files_path =os.path.join(self.full_project_base, "assets/Files")

