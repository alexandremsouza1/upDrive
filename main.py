import logging
import time
import os

from tempfile import NamedTemporaryFile
from typing import IO
from fastapi import Depends, FastAPI, Header, HTTPException,File,UploadFile
from fastapi_utils.tasks import repeat_every

from tasks import upload_file, get_files, download_file, delete_file, delete_files_after_week


logger = logging.getLogger(__name__)
app = FastAPI(title="Google Drive Backup")


async def save_file(file: IO):
    with NamedTemporaryFile("wb", delete=False) as tempfile:
        tempfile.write(file.read())
        return tempfile.name


@app.get('/files', tags=['List of File from  Drive'])
async def get_file():
    return get_files()

@app.delete('/delete-file', tags=['Delete file from Drive'])
async def delete_drive_file(file_id):
    return delete_file(file_id)

@app.delete('/delete-weekly_backup_files', tags=['Delete file from Weekly backup folder'])
async def delete_weekly_backup_files():
    return delete_files_after_week()

@app.get('/download-files', tags=['Download file from Drive'])
async def download_files(file_id):
    return download_file(file_id=file_id)

@app.post("/buckup", tags=['Upload file to Drive (Backup)'])
async def backup(file: bytes=File(...)):
     return upload_file(file)

@app.post("/backup")
async def store_file(file: UploadFile = File(...)):
    name = file.filename
    path = await save_file(file.file)
    return upload_file(name,path)



@app.on_event("startup")
@repeat_every(seconds=86400, logger=logger, wait_first=True)
def periodic():
    upload_file()
   
