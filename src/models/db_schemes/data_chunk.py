from typing import Optional
from pydantic import BaseModel, Field
from bson.objectid import ObjectId


class DataChunk(BaseModel):
    """
    Pydantic model representing a chunk of processed document data stored in MongoDB.
    
    Attributes:
        id (Optional[ObjectId]): MongoDB document ID, optional for new documents
        chunk_text (str): The actual text content of the chunk, must not be empty
        chunk_metadata (dict): Additional information about the chunk (e.g., source, page number)
        chunk_order (int): Position of chunk in the original document (1-based indexing)
        chunk_project_id (ObjectId): Reference to the parent project
        
    Config:
        arbitrary_types_allowed: Enables support for MongoDB ObjectId type
        
    Note:
        - Uses Pydantic Field validators for data validation
        - Ensures chunk text is not empty and order is positive
        - Supports MongoDB's _id field through aliasing
    """
    id: Optional[ObjectId] = Field(None, alias="_id")  # MongoDB document identifier
    chunk_text: str = Field(..., min_length=1)  # Content must not be empty
    chunk_metadata: dict  # Additional chunk information
    chunk_order: int = Field(..., gt=0)  # Position in document (1-based)
    chunk_project_id: ObjectId  # Reference to parent project
    chunk_asset_id: ObjectId

    class Config:
        arbitrary_types_allowed = True  # Required for ObjectId support
        
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("chunk_project_id", 1)
                ],
                "name": "chunk_project_id_index_1",
                "unique": False
            }
        ]
        
        
        
    
class RetrievedDocument(BaseModel):
    text: str
    score: float