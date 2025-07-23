import os
import logging

import aiofiles
from fastapi import FastAPI,APIRouter,Depends, UploadFile, status
from fastapi.responses import JSONResponse

from models import ResponseSignal
from controllers import DataController, ProjectController
from helpers.config import get_settings, Settings


logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str, file: UploadFile, 
                      app_settings: Settings = Depends(get_settings)):
    """
    Endpoint to upload a file to a specific project.
    Args:
        project_id (str): The ID of the project to which the file will be uploaded.
        file (UploadFile): The file to be uploaded.
    Returns:
        JSONResponse: A response indicating the success or failure of the upload.
    """
    print("start uploading file")
    #validate the file properties
    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file)
    print("file validation result:", is_valid, result_signal)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": result_signal}
        )
    print("file validation passed")
    
    project_dir_path = ProjectController().get_project_path(project_id)
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )
    print("file path generated:", file_path)
    
    try:
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