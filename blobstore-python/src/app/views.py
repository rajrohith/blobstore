import boto3
import os
from app import app
from flask.templating import render_template
from flask.helpers import send_from_directory
from flask.globals import request
from werkzeug.utils import secure_filename
from app.vcap_helper import get_configuration

@app.route('/')
def list_objects(status_message=''):
    vcap_config = get_configuration()
    client = _get_s3_client(vcap_config)
    objects = client.list_objects(Bucket=vcap_config['bucket_name'])
    
    objectKeys = []
    if not 'Contents' in objects:
        return render_template("index.html", objectKeys="Your blobstore is emty", bucket=vcap_config['bucket_name'], status_message=status_message)
    for key in objects['Contents']:
        objectKeys.append(key['Key'])
     
    return render_template("index.html", objectKeys=objectKeys, bucket=vcap_config['bucket_name'], status_message=status_message)

@app.route('/download/<object_key>')
def download_file(object_key):
    vcap_config = get_configuration()
    client = _get_s3_client(vcap_config)
    client.download_file(vcap_config['bucket_name'], object_key, '/tmp/' + object_key)
    return send_from_directory(directory='/tmp', filename=object_key)

@app.route('/upload', methods=['POST'])
def upload_file():
    uploded_file = request.files['file']
    object_key = secure_filename(uploded_file.filename)
    local_file_path = '/tmp/' + object_key
    uploded_file.save(local_file_path)

    vcap_config = get_configuration()
    client = _get_s3_client(vcap_config)
    client.upload_file(local_file_path, vcap_config['bucket_name'], object_key)
    return list_objects('File uploaded successfully')

@app.route('/delete/<path:object_key>')
def delete_file(object_key):
    vcap_config = get_configuration()
    client = _get_s3_client(vcap_config)
    client.delete_object(Bucket=vcap_config['bucket_name'], Key=object_key)
    local_file_path = '/tmp/' + object_key
    if os.path.exists(local_file_path):
        os.remove(local_file_path)
    return list_objects('File deleted successfully')

def _get_s3_client(vcap_config):
    session = boto3.session.Session(aws_access_key_id=vcap_config['access_key_id'], aws_secret_access_key=vcap_config['secret_access_key'])
    config = boto3.session.Config(signature_version='s3', s3={'addressing_style': 'virtual'})
    client = session.client('s3', endpoint_url="https://"+vcap_config['host'], config=config)
    return client
