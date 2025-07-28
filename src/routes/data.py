import os
import logging

import aiofiles
from fastapi import FastAPI,APIRouter,Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse

from models import ResponseSignal
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes import DataChunk
from .schemes.data import ProcessRequest 
from controllers import DataController, ProjectController, ProcessController
from helpers.config import get_settings, Settings

# Configure logging for the application
logger = logging.getLogger('uvicorn.error')

# Initialize router with prefix and tags for API documentation
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{project_id}")
async def upload_file(request:Request,project_id: str, file: UploadFile, 
                      app_settings: Settings = Depends(get_settings)):
    """
    Handle file upload endpoint for a specific project.
    
    Args:
        project_id (str): Unique identifier for the target project
        file (UploadFile): File object to be uploaded
        app_settings (Settings): Application configuration settings
        
    Returns:
        JSONResponse: Response containing upload status and file identifier
        
    Notes:
        - Validates file properties before upload
        - Handles file writing in chunks to manage memory efficiently
        - Generates unique file path to prevent naming conflicts
    """
    print("start uploading file")
    
    project_model = ProjectModel(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    
    # Validate incoming file against configured constraints
    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file)
    print("file validation result:", is_valid, result_signal)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": result_signal}
        )
    print("file validation passed")
    
    # Generate unique file path within project directory
    project_dir_path = ProjectController().get_project_path(project_id)
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )
    print("file path generated:", file_path)
    
    try:
        # Write file in chunks to handle large files efficiently
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
        print("file written successfully")
    except Exception as e:
        logger.error(f"Error while uploading file {file_path}: {e}")
        print("file upload failed")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )
    print("file upload successful")
    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": file_id
            }
        )

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request,project_id: str, process_request: ProcessRequest):
    """
    Process uploaded file content by splitting it into chunks.
    
    Args:
        project_id (str): Unique identifier for the project
        process_request (ProcessRequest): Contains processing parameters:
            - file_id: Identifier of the file to process
            - chunk_size: Size of each content chunk
            - overlap_size: Size of overlap between chunks
            
    Returns:
        JSONResponse: Processing result or error message
        list: List of processed file chunks with metadata
    """
    project_model = ProjectModel(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )


    # Extract processing parameters from request
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    
    # Initialize controller and load file content
    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)
    
    # Process file content into chunks with specified parameters
    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size
    )
    
    # Return error response if processing fails
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILED.value
            }
        )
        
    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i+1,
            chunk_project_id=project.id,

        )
        for i , chunk in enumerate(file_chunks)
    ]

    chunk_model = ChunkModel(
        db_client=request.app.db_client
    )
    
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )


    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records
        }
    )
    
    return file_chunks