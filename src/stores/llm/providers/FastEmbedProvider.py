from fastembed import TextEmbedding
import numpy as np

from ..LLMInterface import LLMInterface

class FastEmbedProvider():
    
    def __init__(self, api_key: str=None, api_url: str=None, 
                 default_input_max_characters: int=1000,
                 default_generation_max_output_tokens: int=1000,
                 default_generation_temperature: float=0.1):
        
            self.api_key = api_key
            self.api_url = api_url
            
            self.default_input_max_characters = default_input_max_characters
            self.default_generation_max_output_tokens = default_generation_max_output_tokens
            self.default_generation_temperature = default_generation_temperature
            
            self.generation_model_id = None

            self.embedding_model_id = None
            self.embedding_size = None
            
            self.client = TextEmbedding("jinaai/jina-embeddings-v2-small-en")

    
    
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int=None):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        
    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                      temperature: float=None):
        pass
    
    
    def embed_text(self, text: str, document_type: str=None):
        
                
        if not self.client:
            self.logger.error("TextEmbedding client is not initialized.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set.")
            return None
        
        embedding_array = list(self.client.embed(text))
        embedding_list_of_lists = [embedding.tolist() for embedding in embedding_array][0]
        
        return embedding_list_of_lists

    

    def construct_prompt(self, prompt: str, role: str):
        pass
