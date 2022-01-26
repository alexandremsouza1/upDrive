from pydrive.auth import GoogleAuth,ServiceAccountCredentials
from pydrive.drive import GoogleDrive
from googleapiclient.discovery import build 
from starlette.responses import FileResponse

import json
import os, glob,shutil, sys

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../key/system-backup-1-53687ddf7502.json"
google_login = GoogleAuth()
scope = ['https://www.googleapis.com/auth/drive']
google_login.credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)
drive = GoogleDrive(google_login)
service = build('drive', 'v3', credentials=google_login.credentials) 


def delete_file(file_id):
    file_to_delete = drive.CreateFile({'id': file_id})
    file_name = file_to_delete['title']
    file_to_delete.Delete()
    return "file: " + file_name + " has successfully Deleted from the Drive"
   

def download_file(file_id):
    file_to_download = drive.CreateFile({'id': file_id})
    os.chdir("download")
    file_to_download.GetContentFile(str(file_to_download['title']))
    os.chdir("..")
    return file_to_download['title']
    return FileResponse(str(file_to_download['title'])
    )


def upload_file(name,patch):
    message = ""
    for doc in glob.glob(patch):
        
    #Uploads a file to the Google Drive.
        if doc != 'client_secrets.json':
            source_file_name = doc
        
            with open(source_file_name,"r") as f:
                # file_name = os.path.basename(f.name)
                # file_drive = drive.CreateFile({'title': file_name })  
                # file_drive.SetContentFile(source_file_name) 
                # file_drive.Upload()
                f = drive.CreateFile({'title': name})
                f.SetContentFile(os.path.join("/var/lib/pgsql/schema_backups/", source_file_name))
                f.Upload()

                # Due to a known bug in pydrive if we
                # don't empty the variable used to
                # upload the files to Google Drive the
                # file stays open in memory and causes a
                # memory leak, therefore preventing its
                # deletion
                permission = f.InsertPermission({
                                        'type': 'anyone',
                                        'value': 'anyone',
                                        'role': 'reader'}) #sets permissions so anyone can read
                if f:
                    message = f['alternateLink']
                else:
                    message = "failed"
                f = None
    # has to call email or sms  function to notify after process being done
    # move_files()
    return {'patch': message }


def get_files():
    resource = service.files()
    files = resource.list(pageSize=1000, fields="files(id, name)").execute() 
    return files


def move_files():
  
    # print(os.getcwd())
    destination = '/backup/weekly_backup'
    source_dir = '/var/lib/pgsql/schema_backups'
 
    file_names = glob.glob('/var/lib/pgsql/schema_backups/*')
    file = ''
    for file_name in file_names:
         if file_name != 'client_secrets.json':
            shutil.move((file_name), destination)
            file = file + ',' + file_name
    message = "File(s): " + file + ' has successfully Moved to ' + destination + ' directory'

def delete_files_after_week():
    files = glob.glob('weekly_backup/*')
   
    for doc in files:
        os.remove(doc)
    return "All files has been deleted from the Weekly_backup folder"

    # docker run -d --name shulesoft_backup -P \ -v /home/db_repository: /home/db_repository  backup:latest
    #docker run -d -v /home/db_repository:/home/db_repository backup:latest usefull


