from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    """
    Model for managing project-related database operations.
    Inherits from BaseDataModel for common database functionality.
    
    Attributes:
        collection: MongoDB collection for project documents
    """
    
    def __init__(self, db_client: object):
        """
        Initialize ProjectModel with database client.
        
        Args:
            db_client (object): MongoDB client instance
        """
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
        
    async def create_project(self, project: Project) -> Project:
        """
        Create a new project in the database.
        
        Args:
            project (Project): Project instance to be created
            
        Returns:
            Project: Created project with assigned MongoDB ID
        """
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
        project._id = result.inserted_id
        return project
    
    async def get_project_or_create_one(self, project_id: str) -> Project:
        """
        Retrieve existing project or create new one if not found.
        
        Args:
            project_id (str): Unique identifier for the project
            
        Returns:
            Project: Retrieved or newly created project instance
        """
        # Try to find existing project
        record = await self.collection.find_one({"project_id": project_id})
        
        # Create new project if not found
        if record is None:
            project = Project(project_id=project_id)
            project = await self.create_project(project)
            return project
        
        return Project(**record)
    
    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        """
        Retrieve paginated list of all projects.
        
        Args:
            page (int): Current page number (default: 1)
            page_size (int): Number of items per page (default: 10)
            
        Returns:
            tuple[list[Project], int]: List of projects and total number of pages
        """
        # Count total number of projects
        total_documents = await self.collection.count_documents({})
        
        # Calculate total pages with ceiling division
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1
        
        # Retrieve paginated projects
        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)
        
        # Convert database documents to Project instances
        projects = []
        async for document in cursor:
            projects.append(Project(**document))
        
        return projects, total_pages