import os
import re
from fastapi import UploadFile
from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ResponseSignal

class DataController(BaseController):
    
    def __init__(self, ):
        super().__init__()
        self.size_scale = 1048576 # convert MB to bytes
        
    def validate_uploaded_file(self, file: UploadFile):
        """
        Validates an uploaded file by checking its type and size.
        Args:
            file (UploadFile): The file object to validate.
        Returns:
            tuple: A tuple (bool, str) where the boolean indicates if the file is valid,
                   and the string provides a validation message.
        The method ensures that the file's content type is among the allowed types and that
        its size does not exceed the maximum permitted limit.
        """
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        return True, ResponseSignal.FILE_VALIDATED_SUCCESS.value
    
    def generate_unique_filepath(self, orig_file_name: str, project_id: str) -> str:
        """
        Generates a unique file path and file name for the uploaded file.
        Args:
            orig_file_name (str): The original name of the file.
            project_id (str): The ID of the project to which the file belongs.
        Returns:
            tuple: (new_file_path, new_file_name) where new_file_path is the full unique path,
               and new_file_name is the unique file name.
        The method constructs a file path that includes the project path and a sanitized version
        of the original file name prefixed with a random key, ensuring uniqueness and file system safety.
        """
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id)
        cleaned_file_name = self.get_clean_file_name(
            orig_file_name=orig_file_name
        )
        
        new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_file_name
        )

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_file_name
            )
            
        return new_file_path, random_key + "_" + cleaned_file_name
        


    def get_clean_file_name(self, orig_file_name: str):

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name