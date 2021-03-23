import http.client
import pickle

from google.cloud import storage


class StorageWriter(object):
    def __init__(self, bucket_id):
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(bucket_id)

    def log_write(self, log, filename):
        blob = self.bucket.blob(filename)
        data = pickle.dumps(log.history)
        blob.upload_from_string(data, content_type="application/octet-stream")


def gcloud_meta_project_id():
    try:
        conn = http.client.HTTPConnection("metadata.google.internal")
        conn.request("GET", "/computeMetadata/v1/project/project-id",
                     headers={
                         'Metadata-Flavor': 'Google'
                     })
        response = conn.getresponse()
        value = response.read().decode()
        return value
    except Exception:
        return None
