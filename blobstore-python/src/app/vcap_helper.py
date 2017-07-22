import os, json

def get_configuration():
    vcap_config = os.environ.get('VCAP_SERVICES')
    decoded_config = json.loads(vcap_config)
    
    for key, value in decoded_config.iteritems():
        if key.startswith('predix-blobstore'):
            blobstore_creds = decoded_config[key][0]['credentials']

    return blobstore_creds;
