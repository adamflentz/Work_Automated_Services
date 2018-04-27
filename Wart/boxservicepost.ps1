#####################################################################
#
# Name: boxservicepost.ps1
# Purpose: POST a file to the EIS box webservice for storage
# Author: Scott Stewart
# Version 1.0
# Params: 
# 1) URI: the url  to POST to
# 2) TOKEN: security token for authorization
# 3) PATH: Box "path" to place the file
# 4) ENV: Box environment to place the file (e.g. PRD, PPRD)
# 5) FILE: path to local file to POST
# 6) MD5: Option to also upload MD5 File.  'Y' or 'N' required.
#
# NOTES: requires Powershell >=3.0
######################################################################

#check args length
if ($args.Length -ne 6)
{
	Write-Error "Wrong Command Format: boxservicepost.ps1 <host> <security token> <remote box path> <box environment> <local file path>"
	Exit 1
}

$uri = $args[0] 
$json_token = $args[1] 
$path = $args[2] 
$env = $args[3] 
$file = $args[4] 
$md5 = $args[5]
Write-Host $json_token
#read file
$fileBin = [IO.File]::ReadAllBytes($file)
$enc = [System.Text.Encoding]::GetEncoding("iso-8859-1")
$fileEnc = $enc.GetString($fileBin)


#create POST body
$boundary = [System.Guid]::NewGuid().ToString()    
$LF = "`r`n"
$bodyLines = (
	"--$boundary",
	"Content-Disposition: form-data; name=`"file`"; filename=`"$file`"$LF",   
	$fileEnc,
	"--$boundary--$LF"
	) -join $LF

#create header
$headers = @{}
$headers.Add("Authorization", "Token "+$json_token)

#add path and environment to header
$values = @{}
$headers.Add("environment",$env)
$headers.Add("path",$path)


#invoke the service
try {
	$result = Invoke-WebRequest -UseBasicParsing -Uri $uri -Method POST -Headers $headers -Body $bodyLines -ContentType "multipart/form-data; boundary=`"$boundary`"" 
	Write-Host $result
	Write-Host "File Uploaded."
}
catch [System.Net.WebException] {
    Write-Error( "FAILED to reach '$uri': $_" )
    throw $_
}

#md5 upload
if($md5 -eq 'Y'){
	#check powershell version
	[int]$MajorVersion = $PSVersionTable.PSVersion.Major
	Write-Host Version $MajorVersion

	#get file path and name from argument
	$filename = Split-Path $file -leaf

	#converter for powershell 3.0 or less
	if($MajorVersion -lt 4){
		Write-Host "Old version.  Files greater than 2.0 GB cannot be converted."
		$md5 = New-Object -TypeName System.Security.Cryptography.MD5CryptoServiceProvider
		$hash = [System.BitConverter]::ToString($md5.ComputeHash([System.IO.File]::ReadAllBytes($file)))
		Write-Host $hash
	}

	#converter for powershell 4.0 or greater
	else{
		Write-Host "Simple algorithm possible"
		$hash = Get-FileHash $file -Algorithm MD5
		Write-Host $hash.Hash
		$hash.hash | Out-File ($filename+".md5")
	}

	#read file
	$fileBin = [IO.File]::ReadAllBytes($file+".md5")
	$enc = [System.Text.Encoding]::GetEncoding("iso-8859-1")
	$fileEnc = $enc.GetString($fileBin)


	#create POST body
	$boundary = [System.Guid]::NewGuid().ToString()    
	$LF = "`r`n"
	$bodyLines = (
		"--$boundary",
		"Content-Disposition: form-data; name=`"file`"; filename=`"$file`"$LF"".md5",   
		$fileEnc,
		"--$boundary--$LF"
		) -join $LF

	#invoke the service
	try {
		$result = Invoke-WebRequest -UseBasicParsing -Uri $uri -Method POST -Headers $headers -Body $bodyLines -ContentType "multipart/form-data; boundary=`"$boundary`"" 
		Write-Host $result
		Write-Host "MD5 Uploaded."
	}
	catch [System.Net.WebException] {
		Write-Error( "FAILED to reach '$uri': $_" )
		throw $_
	}

	Remove-Item $file".md5"
}

