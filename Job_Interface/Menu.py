from KeyGrabber import KeySettings
from Crypto.Cipher import AES
from Crypto import Random
import time, base64, json, sys, requests

'''
Name: Menu.py
Purpose: Ask for required job input, convert to JSON, and send to listener.
Author: Adam Lentz
Version 1.0
NOTES: requires Python 2.7.  Python 3 will need to change KeyGrabber, as it is deprecated.
'''

# Find Key and Host stored in config.
keygen = KeySettings()
key = keygen.key
host = keygen.host

# Initialize jsonrequest and parameter dictionaries
jsonrequest = {}
params = {}
jsonrequest["timestamp"] = time.time()
print(sys.getsizeof(key))
print(key)
BLOCK_SIZE = 16
def encrypt(message, key):
    # Encrypt message using AES-CBC.
    length = 16 - (len(message) % 16)
    message += chr(0) * length
    print(message)
    base_64_key = base64.b64encode(key)
    print base_64_key
    iv = Random.new().read(BLOCK_SIZE)
    print("iv: ", base64.b64encode(iv))
    cipher = AES.new(key, AES.MODE_CBC, iv)
    output = base64.b64encode(iv + cipher.encrypt(message))
    print("output: ", output)
    return output

# Initialize required verb for usage.
jsonrequest["verb"] = ""
while jsonrequest["verb"] != "upload" or jsonrequest["verb"] != "download":
    jsonrequest["verb"] = raw_input('Enter a verb (upload|download):\n')
    if jsonrequest["verb"] == "upload":
        # Asks for info to be placed in the file upload JSON.
        params["token"] = raw_input('Enter a token:\n')
        params["host"] = raw_input('Enter a URI:\n')
        params["local_file"] = raw_input('Enter a local file path:\n')
        params["remote_path"] = raw_input('Enter a remote path:\n')
        params["env"] = raw_input('Enter an env:\n')
        jsonrequest["params"] = params

        # Converts to json object and encrypts the JSON string
        jsonstring = json.dumps(jsonrequest)
        encryptedrequest = encrypt(jsonstring, key)
        print(encryptedrequest)
        headers = {"Authorization": "Token " + params["token"]}
        data = encryptedrequest

        # Sends encrypted request to web listener.  IP must change to whatever is needed, which should be an https
        # domain.
        r = requests.post('http://128.239.123.231:8080',
                          headers=headers,
                          data=data)
    elif jsonrequest["verb"] == "download":
        # Asks for info to be placed in the file download JSON.
        params["token"] = raw_input('Enter a token:\n')
        params["host"] = raw_input('Enter a URI:\n')
        params["local_path"] = raw_input('Enter a local file path:\n')
        params["remote_path"] = raw_input('Enter a remote path:\n')
        params["env"] = raw_input('Enter an env:\n')
        params["file_name"] = raw_input('Enter the file you want to download')
        jsonrequest["params"] = params

        # Converts to json object and encrypts the JSON string
        jsonstring = json.dumps(jsonrequest)
        encryptedrequest = encrypt(jsonstring, key)
        headers = {"Authorization": "Token " + params["token"]}
        data = encryptedrequest

        # Sends encrypted request to web listener.  IP must change to whatever is needed, which should be an https
        # domain.
        r = requests.post('http://128.239.123.231:8080',
                          headers=headers,
                          data=data)
