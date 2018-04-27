from KeyGrabber import KeySettings
from Crypto.Cipher import AES
from Crypto import Random
import time, base64, json, sys, requests

keygen = KeySettings()
key = keygen.key
host = keygen.host
jsonrequest = {}
params = {}
jsonrequest["timestamp"] = time.time()
print(sys.getsizeof(key))
print(key)
BLOCK_SIZE = 16
def encrypt(message, key):
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

print base64.b64encode(key)
jsonrequest["verb"] = ""
while jsonrequest["verb"] != "upload" or jsonrequest["verb"] != "download":
    jsonrequest["verb"] = raw_input('Enter a verb (upload|download):\n')
    if jsonrequest["verb"] == "upload":
        params["token"] = raw_input('Enter a token:\n')
        params["host"] = raw_input('Enter a URI:\n')
        params["local_file"] = raw_input('Enter a local file path:\n')
        params["remote_path"] = raw_input('Enter a remote path:\n')
        params["env"] = raw_input('Enter an env:\n')
        jsonrequest["params"] = params
        jsonstring = json.dumps(jsonrequest)
        encryptedrequest = encrypt(jsonstring, key)
        print(encryptedrequest)
        headers = {"Authorization": "Token " + params["token"]}
        data = encryptedrequest
        r = requests.post('http://128.239.123.231:8080',
                          headers=headers,
                          data=data)
    elif jsonrequest["verb"] == "download":
        pass
    else:
        message = encrypt("hello", key)
        iv = base64.b64decode(message)[:16]
        decoder = AES.new(key, AES.MODE_CBC, iv).decrypt(base64.b64decode(message)[16:])
        print(decoder)