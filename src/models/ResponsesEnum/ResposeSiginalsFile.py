from enum import Enum
class ResponseSignalsFile(Enum):
    File_Size_Exceeded = "File size exceeded the maximum limit"
    Invalid_File_Type = "Invalid file type"
    File_Valid = "File is valid"