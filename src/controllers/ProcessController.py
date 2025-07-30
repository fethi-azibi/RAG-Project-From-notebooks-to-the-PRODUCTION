import os
from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessingEnum


class ProcessController(BaseController):
    """
    Controller for processing text files and PDFs.
    Handles file loading, content extraction, and text chunking operations.
    
    Args:
        project_id (str): Unique identifier for the project
    """
    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)
        
    def get_file_extension(self, file_id: str) -> str:
        """
        Extract file extension from file_id.
        
        Args:
            file_id (str): Identifier of the file
            
        Returns:
            str: File extension (e.g., '.txt', '.pdf')
        """
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id: str):
        """
        Get appropriate document loader based on file extension.
        
        Args:
            file_id (str): Identifier of the file
            
        Returns:
            Union[TextLoader, PyMuPDFLoader, None]: Document loader instance or None if extension not supported
        """
        file_ext = self.get_file_extension(file_id)
        file_path = os.path.join(self.project_path, file_id)
        
        #if file does not exist
        if not os.path.exists(file_path):
            return None
        
        # Handle text files
        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        
        # Handle PDF files
        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        
        return None
    
    def get_file_content(self, file_id:str):
        """
        Load file content using appropriate loader.
        
        Args:
            file_id (str): Identifier of the file
            
        Returns:
            list: Loaded document content
        """
        loader = self.get_file_loader(file_id=file_id)
        if  loader:
            return loader.load()
        return None
    
    def process_file_content(self, file_content:list, file_id: str,
                             chunk_size: int=100, overlap_size: int=20):
        """
        Split file content into overlapping chunks for processing.
        
        Args:
            file_content (list): List of document content
            file_id (str): Identifier of the file
            chunk_size (int, optional): Size of each chunk. Defaults to 100
            overlap_size (int, optional): Size of overlap between chunks. Defaults to 20
            
        Returns:
            list: List of document chunks with metadata
        """
        # Initialize text splitter with specified parameters
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len
        )
        
        # Extract page content from documents
        file_content_text = [
            rec.page_content for rec in file_content
        ]
        
        # Extract metadata from documents
        file_content_metadata = [
            rec.metadata for rec in file_content
        ]
        
        # Create document chunks with associated metadata
        chunks = text_splitter.create_documents(file_content_text, metadatas=file_content_metadata)
        
        return chunks