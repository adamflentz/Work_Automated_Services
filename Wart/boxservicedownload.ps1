############################################################################################################
#
# Name: boxservicedownload.ps1
# Purpose: DOWNLOAD a file from the EIS box webservice for storage
# Author: Adam Lentz; Scott Stewart
# Version 1.1
# Params: 
# 1) URI: the url  to download from
# 2) ENV: Box environment to download the file (e.g. PRD, PPRD)
# 2) TOKEN: security token for authorization
# 3) PATH: Box "path" to download the file
# 5) FILENAME: the name of the file to download
# 6) FILEPATH: the place the new file should be downloaded to
# 7) DELETEFLAG: Whether or not file should be deleted upon download (just moved to a folder called deleted)
# 8) VERIFY: Whether or not the file should be verified with a corresponding md5
#
# NOTES: requires Powershell >=3.0
# Version 1.0 Initial version
# Version 1.1 Fixes for binary files (pdf/images)
#############################################################################################################


#helper function to output the correct bytes or string based on type
function fileout($buffer, $path, $type)
{
	if ($type.fullname -eq 'System.String')
	{
		$buffer | Out-File $path -Encoding UTF8
	}
	else
	{
		$buffer | set-content -path $path -encoding byte
	}
}

#check args length
if ($args.Length -ne 8)
{
	Write-Error "Wrong Command Format: boxservicedownload.ps1 <host> <security token> <remote box path> <box environment> <file name> <file path> <delete flag> <md5 verification>"
	Exit 1
}

$uri = $args[0] 
$env = $args[1]
$json_token = $args[2] 
$path = $args[3] 
$filename = $args[4]
$filepath = $args[5] 
$deleteflag = $args[6]
$md5=$args[7]

#create POST body

#create headers
$headers = @{}
$headers.Add("environment",$env)
$headers.Add("path",$path)
$headers.Add("Authorization", "Token "+$json_token)
$headers.Add("deleteflag", $deleteflag)

#download md5
if($md5 -eq 'Y'){
	#check powershell version
	[int]$MajorVersion = $PSVersionTable.PSVersion.Major
	Write-Host Version $MajorVersion

	#download md5 file for powershell 3.0 or less
	if($MajorVersion -lt 4){
		$headers.Add("filename", $filename+".md5")
		try {
			$md5result = Invoke-WebRequest -UseBasicParsing -Uri $uri -Method POST -Headers $headers
			# Write-Host $result
			}
			catch [System.Net.WebException] {
				Write-Error( "FAILED to reach '$uri': $_" )
				Write-Host "Process will continue without retrieving MD5.  File cannot be verified."
				$md5 = 'N'
				throw $_
			}
		$headers.Remove("filename")
	}
}


#create file header
$headers.Add("filename", $filename)
$fullpath = $filepath
$fullpath += $filename

#invoke the service
try {
	$result = Invoke-WebRequest -UseBasicParsing -Uri $uri -Method POST -Headers $headers

	$typeof = $result.content.GetType()
	$data1 = $result.content
	

}
catch [System.Net.WebException] {
    Write-Error( "FAILED to reach '$uri': $_" )
    throw $_
}

#only runs if md5 file was found earlier.
if($md5 -eq 'Y'){
	#converter for powershell 3.0 or less
	if($MajorVersion -lt 4){
		Write-Host "WARNING: Old version of Powershell.  Files greater than 2.0 GB cannot be hashed."
		$md5object = New-Object -TypeName System.Security.Cryptography.MD5CryptoServiceProvider
		$hash = [System.BitConverter]::ToString($md5.ComputeHash([System.IO.File]::ReadAllBytes($data1)))
		if($hash.hash - $md5result)
		{
			fileout $data1 $fullpath $typeof
		}
	}

	#converter for powershell 4.0 or greater
	else{
		Write-Host "Simple algorithm possible"
		$hash = Get-FileHash $data1 -Algorithm MD5
		Write-Host $hash.Hash
		if($hash.hash - $md5result)
		{
			fileout $data1 $fullpath $typeof
		}
	}
}
else
{
	fileout $data1 $fullpath $typeof
}

