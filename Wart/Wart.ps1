#####################################################################
#
# Name: Wart.ps1
# Purpose: Listen for encrypted JSON file over a network.  
# Decrypt message with private key and run task based on JSON.
# Author: Adam Lentz
# Version 1.0
# NOTES: requires Powershell >=3.0
######################################################################

function ProcessRequest($context, $key)
{
	# Grabs message body and sends to decryption function
	$postdata = $context.Request.InputStream
	$body = New-Object System.IO.StreamReader ($postdata)
	$msg = $body.ReadToEnd()
	$body.Close()
	Write-Host $msg
	$decryptbody = Decrypt-String $key "VwnPmjYa6A8SZwhgqfpqferM8Kxa/RFKsun7jT3m/feNrRT67S2e2+dE7ZLQQoQG/hnZSp7FKsXacMz8Yt223JaaHuJwldJrsc8eWtxJuF0WvB1wI14ur9bPlXyTeHTE6OeRNa8sEIYRvdzuMaNhzOFamPPFPBw/Fl/eMZh5J26ng3YsCtg11dtuRgkAUdHGfOqcM5s6BHhmvuF3ZDA4WP5ul3G/FthNxUUJa+Kn8SBSwXgRr9mEuGrgW7T0Be7Y3HQKLvlH+mEVmcdPjTv+DyguhQAVhIkohdxTKXLHCTki0vP9NxMKJ25Racd/IneWAeSM9wJFflsgmy8xSBMtayjQ4DZ41SMMWo6fjRDARk7IGPmDmPxud8ty14o6W8pw"
	$decryptbody
}

function Decrypt-String($key, $Encrypted)
{
	# Decrypts message using AES, private key, and IV sent through message

	# If the value in the Encrypted is a string, convert it to Base64
	if($Encrypted -is [string]){
		$Encrypted = [Convert]::FromBase64String($Encrypted)
   	}
	$message = $Encrypted[16..($Encrypted.length - 1)]
	# Create a COM Object for aesManaged Cryptography
	$r = new-Object System.Security.Cryptography.aesManaged
	$r.Mode = [System.Security.Cryptography.CipherMode]::CBC
    $r.Padding = [System.Security.Cryptography.PaddingMode]::Zeros

	# Create the Encryption Key
	$enc = [system.Text.Encoding]::UTF8
	$key = "EHgYGBpM2HkRxaOa8hcWvL5NeJPzTiqH"
	$r.Key = $enc.GetBytes($key) 
	# Create the Intersecting Vector Cryptology Hash with the init
	$r.IV = $Encrypted[0..15]


	# Create a new Decryptor
	$d = $r.CreateDecryptor()
	# Create a New memory stream with the encrypted value.
	$ms = new-Object IO.MemoryStream @(,$message)
	# Read the new memory stream and read it in the cryptology stream
	$cs = new-Object Security.Cryptography.CryptoStream $ms,$d,"Read"
	# Read the new decrypted stream
	$sr = new-Object IO.StreamReader $cs
	# Return from the function the stream
	Write-Output $sr.ReadToEnd()
	# Stops the stream	
	$sr.Close()
	# Stops the crypology stream
	$cs.Close()
	# Stops the memory stream
	$ms.Close()
	# Clears the aesManaged Cryptology IV and Key
	$r.Clear()
}

function ParseJSON($message) {
	# Parses JSON and finds correct powershell job

	$message = $message.trim([char]0)
	Write-Host $type
    $jsonFile = ConvertFrom-Json $message
    $params = $jsonFile.params
    $verb = $jsonFile.verb
    if($verb -eq "upload") {
		# Upload task
		$uri = $params.host
        $env =  $params.env
        $local_file = $params.local_file
        $remote_path = $params.remote_path
        $token = $params.token
		Write-Host $token
		# Upload the file
		$scriptpath = "C:\Users\aflentz\Downloads"
		$scriptpath += '\'
		$scriptpath += 'boxservicepost.ps1'
		$argumentList = ''
		$argumentList += $uri
		$argumentList += ' '
		$argumentList += $token
		$argumentList += ' '
		$argumentList += $remote_path
		$argumentList += ' "'
		$argumentList += $env
		$argumentList += '" "'
		$argumentList += $local_file
		$argumentList += '" '
		$argumentList += ' '
		$argumentList += 'N'
		$argumentList += ' '
		Invoke-Expression "$scriptPath $argumentList"
    }

	if($verb -eq "download") {
		# Download task
		$uri = $params.host
        $env =  $params.env
        $file = $params.file_name
		$local_path = $params.local_path
        $remote_path = $params.remote_path
        $token = $params.token
		# download the file
		$scriptpath = "C:\Users\aflentz\Downloads"
		$scriptpath += '\'
		$scriptpath += 'boxservicedownload.ps1'
		$argumentList = ''
		$argumentList += $uri
		$argumentList += ' '
		$argumentList += $env
		$argumentList += ' '
		$argumentList += $token
		$argumentList += ' "'
		$argumentList += $remote_path
		$argumentList += '" "'
		$argumentList += $file
		$argumentList += '" "'
		$argumentList += $local_path
		$argumentList += '" '
		$argumentList += ' '
		$argumentList += 'N'
		$argumentList += ' '
		$argumentList += 'N'
		$argumentList += ' '
		Invoke-Expression "$scriptPath $argumentList"
    }
    $process
}

# Creates key and http listener.  Should only be https when it goes live, remove http.
$key = "EHgYGBpM2HkRxaOa8hcWvL5NeJPzTiqH"
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add('http://+:8080/')
$listener.Prefixes.Add('https://+:8000/')
$listener.Start()

try {
	# Waits for incoming encrypted message
	Write-Host "Listening on port, press CTRL+C to cancel"
	$context = $listener.GetContext()
}
catch {
    Write-Error $_          
}
finally{
	# Catches response and sends it to parse
	$URL = $context.Request.Url
	$response = $context.Response
	$decryptedMessage = ProcessRequest $context $key
	$type = $decryptedMessage.GetType()
	Write-Host $decryptedMessage
    $listener.Stop()
    $finalresponse = ParseJSON $decryptedMessage
    Write-host "Listener Closed Safely"
}