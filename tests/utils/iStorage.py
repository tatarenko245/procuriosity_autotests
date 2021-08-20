import hashlib
import os
import requests

from tests.conftest import GlobalClassMetadata
from tests.utils.functions import get_project_root


class Document:
    def __init__(self, file_name="API.pdf"):
        # The 'get_project_root()' get root dir
        self.path = get_project_root() / file_name
        self.filename = file_name
        self.m = None
        self.weight = None
        self.doc_id = None

    def uploading_document(self):
        with open(self.path, 'rb') as f:
            self.m = hashlib.md5()
            while True:
                # The 'API.pdf' file was divided into 8192-byte pieces, because 'API.pdf' has big weight.
                data = f.read(8192)
                if not data:
                    break
                self.m.update(data)

        self.weight = os.stat(self.path).st_size
        payload = {
            "fileName": self.filename,
            "hash": f"{self.m.hexdigest()}",
            "weight": self.weight
        }
        self.doc_id = requests.post(
            url=f"{GlobalClassMetadata.host_for_services}:9131/storage/registration/",
            headers={'Content-Type': 'application/json'},
            json=payload).json()['data']['id']
        file = {'file': open(self.path, 'rb')}
        uploading = requests.post(
            url=f"{GlobalClassMetadata.host_for_services}:9131/storage/upload/{self.doc_id}",
            files=file).json()

        return uploading, self.filename, self.m.hexdigest(), self.weight
