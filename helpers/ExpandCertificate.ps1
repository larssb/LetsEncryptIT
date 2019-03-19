#requires -modules PowerShellTooling

<#
    This script automatizes the process of expanding a LetsEncrypt certificate. It is tailored specifically to Brickshare's setup
    
    Assumptions:
        -- The use of CloudFlare for verification of ownership
        -- The use of Google Cloud load-balancer
            ---- Which entails using Python and the Python modules oauth2client and google-api-python-client
            ---- And the need for setting the GOOGLE_APPLICATION_CREDENTIALS environment variable
        -- The availability of a POD YAML specification file. That describes a POD for copying in files to the bs-letsencrypt-disk 
        in order for the LetsEncrypt renewal Kubernetes cron job to work
#>
###############################
# Re-usable variables & conf. #
###############################
if ($null -eq (Get-Variable -Name ExitMsg -ErrorAction SilentlyContinue)) {
    New-Variable -Name ExitMsg -Scope 0 -Option Constant -Value "> The script will now exit" -Visibility Private
    New-Variable -Name CertbotWrkDir -Scope 0 -Option Constant -Value $([Environment]::GetFolderPath("MyDocuments") + "/Documents/letsencrypt")
    New-Variable -Name BSLetsencryptPod -Scope 0 -Option Constant -Value "bs-letsencrypt-upload-data-middleman"
    New-Variable -Name UserDocsDir -Scope 0 -Option Constant -Value $([Environment]::GetFolderPath("MyDocuments"))
    New-Variable -Name CurrentDate -Scope 0 -Option Constant -Value $(get-date -Format ddMMyyyyhhmmss)
}

# Environment variable for use the --deploy-hook. In order to have one point of path configuration in the LetsEncrypt automation pipeline
[Environment]::SetEnvironmentVariable("letsencrypt-data-dir",$CertbotWrkDir)

# The GOOGLE_APPLICATION_CREDENTIALS environment variable. Used for authentication and authorization purposes when interacting with the Google Cloud Compute Engine API
[Environment]::SetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS", "$CertbotWrkDir/automation/bs-letsencrypt-gc.iam.json")

# To have a tmp file for certbot cmd output and errors
$CertbotErrStreamFile_0 = [System.IO.Path]::GetTempFileName()
$CertbotErrStreamFile_1 = [System.IO.Path]::GetTempFileName()
$CertbotErrStreamFile_2 = [System.IO.Path]::GetTempFileName()
$CertbotErrStreamFile_3 = [System.IO.Path]::GetTempFileName()
$CertbotOutStreamFile_0 = [System.IO.Path]::GetTempFileName()
$CertbotOutStreamFile_1 = [System.IO.Path]::GetTempFileName()
$CertbotOutStreamFile_2 = [System.IO.Path]::GetTempFileName()
$CertbotOutStreamFile_3 = [System.IO.Path]::GetTempFileName()

<#
    - Configure logging
#>
# Define log4net variables
$log4NetConfigFile = "$PSScriptRoot/conf/LetsEncryptAutomation.Log4Net.xml"
$LogFilesPath = "$PSScriptRoot/conf"

# Initiate the log4net logger
$global:log4netLogger = initialize-log4net -log4NetConfigFile $log4NetConfigFile -LogFilesPath $LogFilesPath -logfileName "LetsEncryptAutomation" -loggerName "LetsEncryptAutomation_Error"
$global:log4netLoggerDebug = initialize-log4net -log4NetConfigFile $log4NetConfigFile -LogFilesPath $LogFilesPath -logfileName "LetsEncryptAutomation" -loggerName "LetsEncryptAutomation_Debug"

# Make the log easier to read
$log4netLoggerDebug.debug("----------------------------------------------------------------")
$log4netLoggerDebug.debug("------------- LetsEncryptAutomation logging started ------------")
$log4netLoggerDebug.debug("------------- $((get-date).ToString()) -------------------------")
$log4netLoggerDebug.debug("----------------------------------------------------------------")

# Log the Start-Process stream redirection tmp files used by this execution
$log4netLoggerDebug.debug(">> Start-Process err stream redirection files <<")
$log4netLoggerDebug.debug("CertbotErrStreamFile_0: $CertbotErrStreamFile_0")
$log4netLoggerDebug.debug("CertbotErrStreamFile_1: $CertbotErrStreamFile_1")
$log4netLoggerDebug.debug("CertbotErrStreamFile_2: $CertbotErrStreamFile_2")
$log4netLoggerDebug.debug("CertbotErrStreamFile_3: $CertbotErrStreamFile_3")
$log4netLoggerDebug.debug(">> Start-Process out stream redirection files <<")
$log4netLoggerDebug.debug("CertbotOutStreamFile_0: $CertbotOutStreamFile_0")
$log4netLoggerDebug.debug("CertbotOutStreamFile_1: $CertbotOutStreamFile_1")
$log4netLoggerDebug.debug("CertbotOutStreamFile_2: $CertbotOutStreamFile_2")
$log4netLoggerDebug.debug("CertbotOutStreamFile_3: $CertbotOutStreamFile_3")

###################
# Sanity controls #
###################
# Certbot installed?
$Certbot = certbot --version
if(-not $Certbot) {
    [String]$CertbotNotInstalledMsg = "Certbot is not installed. Install it > https://certbot.eff.org/"
    Write-Output $CertbotNotInstalledMsg
    Write-Output $ExitMsg
    $log4netLogger.error("$CertbotNotInstalledMsg")
    exit
}

# Python installed?
$Python = which python
if ($null -eq $Python) {
    [String]$PythonNotInstalledMsg = "Python is not installed. Install it"
    Write-Output $PythonNotInstalledMsg
    Write-Output $ExitMsg
    $log4netLogger.error("$PythonNotInstalledMsg")
    exit
}

# Required Python plugins installed?
$PythonGAPI = pip show google-api-python-client
$PythonOAUTH = pip show oauth2client
if ($null -eq $PythonGAPI -or $null -eq $PythonOAUTH) {
    [String]$PythonModulesNotInstalledMsg = "The required Python modules are not installed. Install > pip install --upgrade oauth2client and pip install --upgrade google-api-python-client"
    Write-Output $PythonModulesNotInstalledMsg
    Write-Output $ExitMsg
    $log4netLogger.error("$PythonModulesNotInstalledMsg")
    exit
}

# Kubectl available (for interacting with Google Cloud)
$Kubectl = kubectl version --short
if($null -eq $Kubectl) {
    [String]$KubectlNotInstalledMsg = "Kubectl is not available. Set it up > https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl"
    Write-Output $KubectlNotInstalledMsg
    Write-Output $ExitMsg
    $log4netLogger.error("$KubectlNotInstalledMsg")
    exit
}

# Certbot CloudFlare DNS plugin installed?
Start-Process -FilePath "certbot" -ArgumentList "plugins" -RedirectStandardError $CertbotErrStreamFile_0 -RedirectStandardOutput $CertbotOutStreamFile_0 -Wait

# Control the success of the "certbot plugins" call
$CertbotErrStreamFileContent_0 = Get-Content -Path $CertbotErrStreamFile_0
if ($null -ne $CertbotErrStreamFileContent_0) {
    [String]$CertbotPluginsFailedMsg = "The Certbot plugins cmd failed with: $CertbotErrStreamFileContent_0"
    Write-Output $CertbotPluginsFailedMsg
    Write-Output $ExitMsg
    $log4netLogger.error("$CertbotPluginsFailedMsg")
    exit
}

$CloudFlarePlugin = Get-Content -Path $CertbotOutStreamFile_0 | Select-String "cloudflare"
if ($null -eq $CloudFlarePlugin) {
    [String]$CloudflarePluginNotInstalledMsg = "The CloudFlare DNS auth plugin for LetsEncrypt is not installed. The plugin is required by the script. Install it. Goto > https://pypi.org/project/certbot-dns-cloudflare/."
    Write-Output $CloudflarePluginNotInstalledMsg
    Write-Output $ExitMsg
    $log4netLogger.error("$CloudflarePluginNotInstalledMsg")
    exit
} else {
    Write-Output $CertbotOutStreamFileContent_1
}

# Control that the OS is supported
$OSType = [Environment]::OSVersion.Platform
if(-not $OSType -eq "Unix") {
    [String]$OSNotSupportedMsg = "Your OS is not supported. Only Unix type systems is supported. Bad luck sunny boy ;-)"
    Write-Output $OSNotSupportedMsg
    Write-Output $ExitMsg
    $log4netLogger.error("$OSNotSupportedMsg")
    exit
}

# Control the existence of the LetsEncrypt folder in the executing users Documents dir
if (-not (Test-Path -Path $CertbotWrkDir) ) {
    [String]$LetsEncryptDataDirNotThereMsg = "The script expects the LetsEncrypt folder to be in your users Documents folder. In order to avoid sudo/root/admin requirements.`
Copy the LetsEncrypt folder contents to: $CertbotWrkDir and try again."
    Write-Output $LetsEncryptDataDirNotThereMsg
    Write-Output $ExitMsg
    $log4netLogger.error("$LetsEncryptDataDirNotThereMsg")
    exit
}

# Ensure that the logs path exists
if (-not (Test-Path -Path $($CertbotWrkDir + "/logs"))) {
    New-Item -Name "logs" -ItemType Directory -Path $CertbotWrkDir | Out-Null
}

################
# Collect info #
################
#
# Display the currently installed certificates
#
Start-Process -FilePath "certbot" -ArgumentList "certificates","--config-dir $CertbotWrkDir","--logs-dir $($CertbotWrkDir + `"/logs`")","--work-dir $CertbotWrkDir" -RedirectStandardError $CertbotErrStreamFile_1 -Wait -RedirectStandardOutput $CertbotOutStreamFile_1

# Control the success of the "certbot certificates" call
$CertbotErrStreamFileContent_1 = Get-Content -Path $CertbotErrStreamFile_1
if ($CertbotErrStreamFileContent_1.GetType().BaseType.Name -eq "Array" -and $CertbotErrStreamFileContent_1[0] -match "error") {
    [String]$CertbotCertificatesFailedMsg_1 = "The Certbot certificates cmd failed with: $CertbotErrStreamFileContent_1"
    Write-Output$CertbotCertificatesFailedMsg_1
    Write-Output $ExitMsg
    $log4netLogger.error("$CertbotCertificatesFailedMsg_1")
    exit
}

$CertbotOutStreamFileContent_1 = Get-Content -Path $CertbotOutStreamFile_1
if ($CertbotOutStreamFileContent_1 -match "No certs found") {
    [String]$NoLetsEncryptCertsMsg = "There is no LetsEncrypt certificates on this machine. Or the LetsEncrypt data folder > $CertbotWrkDir is empty. Give it a look."
    Write-Output $NoLetsEncryptCertsMsg
    Write-Output $ExitMsg
    $log4netLogger.error("$NoLetsEncryptCertsMsg")
    exit
} else {
    Write-Output $CertbotOutStreamFileContent_1
}

#
# Get the name of the certificate to expand
#
do {
    [String]$Certname = Read-Host -Prompt "State the name of the certificate to expand with a new domain/s"
} until ($null -ne $Certname -and $Certname -match "\w") 

# Read the specific cert ($Certname)
Start-Process -FilePath "certbot" -ArgumentList "certificates","--cert-name $Certname","--config-dir $CertbotWrkDir","--logs-dir $($CertbotWrkDir + `"/logs`")","--work-dir $CertbotWrkDir" -RedirectStandardError $CertbotErrStreamFile_2 -RedirectStandardOutput $CertbotOutStreamFile_2 -Wait

# Control the success of the "certbot certificates --cert-name" call
$CertbotErrStreamFileContent_2 = Get-Content -Path $CertbotErrStreamFile_2
if ($CertbotErrStreamFileContent_2.GetType().BaseType.Name -eq "Array" -and $CertbotErrStreamFileContent_2[0] -match "error") {
    [String]$CertbotCertificatesFailedMsg_2 = "The Certbot certificates cmd failed with: $CertbotErrStreamFileContent_2"
    Write-Output $CertbotCertificatesFailedMsg_2
    Write-Output $ExitMsg
    $log4netLogger.error("$CertbotCertificatesFailedMsg_2")
    exit
}

# We now know that there is a cert. on the system named "$Certname". Set an environment variable to be used by the Certbot --deploy-hook
[Environment]::SetEnvironmentVariable("Certname",$Certname)

# Get the cert item for later comparison. To see if it was actually newly generated
try {
    $OriginalCert = Get-Item -Path $CertbotWrkDir/live/$Certname/cert.pem -ErrorAction Stop
} catch {
    [String]$OrgCertNotRetrievedMsg = "Failed to get the original certificate before generating a new one. Cannot continue."
    Write-Output $OrgCertNotRetrievedMsg
    Write-Output "Fix this error: $_"
    Write-Output $ExitMsg
    $log4netLogger.error("$OrgCertNotRetrievedMsg. Failed with: $_")
    exit
}

# Read-in data on the selected certificate & parse the domains on the cert
$Cert = Get-Content -Path $CertbotOutStreamFile_2
$Cert
$CertDomains = $Cert | Select-String "Domains"
$DomainsTrimmed = ($CertDomains -replace "Domains:","").TrimStart().TrimEnd() -replace " ",","

# The domains to expand the certificate with
do {
    [String]$ExpandDomains = Read-Host -Prompt "Write the domains that the certificate should be expanded with. Delimit them with a comma (,)"
} until ($ExpandDomains.Length -gt 0)

#
# Expand the cert
#
Write-Host "The $Certname certificate will now be tried expanded. This can take some time. Up to 1m." -ForegroundColor Green
Start-Process -FilePath "certbot" -ArgumentList "certonly","--cert-name $Certname","--config-dir $CertbotWrkDir","--logs-dir $($CertbotWrkDir + `"/logs`")","--work-dir $CertbotWrkDir",`
                                                "--dns-cloudflare","--dns-cloudflare-credentials $CertbotWrkDir/plugins/cloudflare.ini","--dns-cloudflare-propagation-seconds 60",`
                                                "-d $($DomainsTrimmed + "," + $ExpandDomains)","--deploy-hook $($CertbotWrkDir + `"/automation/deploy-hook-runner.sh`")",`
                                                "-non-interactive" -RedirectStandardError $CertbotErrStreamFile_3 -RedirectStandardOutput $CertbotOutStreamFile_3 -Wait

# Control the success of the "certbot certonly --cert-name" call
$CertbotErrStreamFileContent_3 = Get-Content -Path $CertbotErrStreamFile_3
if ($CertbotErrStreamFileContent_3.GetType().BaseType.Name -eq "Array" -and $CertbotErrStreamFileContent_3[0] -match "error") {
    [String]$CertbotCertonlyFailedMsg = "The Certbot certonly cmd failed with: $CertbotErrStreamFileContent_3"
    Write-Output $CertbotCertonlyFailedMsg
    Write-Output $ExitMsg
    $log4netLogger.error("$CertbotCertonlyFailedMsg")
    exit
}

# Display the result of expanding the certificate
$CertbotOutStreamFileContent_3 = Get-Content -Path $CertbotOutStreamFile_3
Write-Output $CertbotOutStreamFileContent_3

<#
    #### The below process is to ensure that the automated renewal of the LetsEncrypt certificate keeps on working ####
        > The renewal job runs as a Kubernetes cron job and needs the current LetsEncrypt data to work
#>
# First control that a new certificate was actually generated
try {
    $NewCert = Get-Item -Path $CertbotWrkDir/live/$Certname/cert.pem -ErrorAction Stop
} catch {
    [String]$NewCertNotRetrievedMsg = "Failed to get the newly generated certificate. Cannot continue."
    Write-Output $NewCertNotRetrievedMsg
    Write-Output "Fix this error: $_"
    Write-Output $ExitMsg
    $log4netLogger.error("$NewCertNotRetrievedMsg. Failed with: $_")
    exit
}

#  go ahead if the LastWriteTime differ
$CertGenerationStatus = $OriginalCert.LastWriteTime -eq $NewCert.LastWriteTime
if($CertGenerationStatus -eq $false) {
    kubectl apply -f $CertbotWrkDir/automation/$BSLetsencryptPod.yml
}

# Wait for the upload data middleman pod to become ready
[Int]$GoAroundForX = 1 # Semaphore to stop the below insanity
:GetOutAHere while ($GoAroundForX -lt 31) {
    # Will return data if the bs-letsencrypt pod is running
    $LetsEncryptPod = kubectl get pods -l app=$BSLetsencryptPod --field-selector="status.phase=Running"

    # Control the state of the pod
    if($null -ne $LetsEncryptPod) {
        break GetOutAHere
    }

    # The pod is not ready yet, sleep and poll again
    Start-Sleep -Seconds 1
    $GoAroundForX++
}

# Compress the LetsEncrypt data dir before to simplify management of the backup
[String]$TarFileName = "$(Get-Random -Minimum 21000000000).tar"
kubectl exec $BSLetsencryptPod -- tar -czf ./tmp/$TarFileName ./uploadedData/

# Copy out the created tar as a backup of the LetsEncrypt data on the bs-letsencrypt disk. As ensurance.
kubectl cp "$BSLetsencryptPod`:tmp/$TarFileName" $UserDocsDir
Write-Host "If needed, a backup of the remote LetsEncrypt data store is here > $UserDocsDir/$TarFileName" -ForegroundColor Green

# Continue, if the backup failed?
if (-not (Test-Path -Path $UserDocsDir/$TarFileName) ) {
    Write-Output "The backup of the remote LetsEncrypt data store failed. Do you still want to continue? Implies that local LetsEncrypt data"
    Write-Output "will overwrite the remote"
    do {
        [String]$Answer = Read-Host "Press [Y] to continue or [N] to stop the script"
    } until ($Answer -eq "Y" -or $Answer -eq "N")

    if ($Answer -eq "N") {
        Write-Output "You will need to manually ensure that the newly generated LetsEncrypt certificate ends up on the bs-letsencrypt Kubernetes persistent disk"
        Write-Output $ExitMsg
        exit
    }
}

# Clean the LetsEncrypt data folder on the bs-letsencrypt disk
kubectl exec $BSLetsencryptPod -- rm -Rf /uploadedData/*

# Remove the temp tar file
kubectl exec $BSLetsencryptPod -- rm -f ./tmp/$TarFileName

# Copy in the local LetsEncrypt data to the remote bs-letsencrypt disk
kubectl cp $CertbotWrkDir $BSLetsencryptPod`:/uploadedData

# Remove the intermediary helper pod, used for copying in new LetsEncrypt data
kubectl delete -f $CertbotWrkDir/automation/$BSLetsencryptPod.yml

############
# Clean up #
############
# Remove tmp files
Remove-Item -Path $CertbotErrStreamFile_0 -Force -Confirm:$false -ErrorAction SilentlyContinue # Okay if the file is not deleted. Just a tmp file
Remove-Item -Path $CertbotErrStreamFile_1 -Force -Confirm:$false -ErrorAction SilentlyContinue # Okay if the file is not deleted. Just a tmp file
Remove-Item -Path $CertbotErrStreamFile_2 -Force -Confirm:$false -ErrorAction SilentlyContinue # Okay if the file is not deleted. Just a tmp file
Remove-Item -Path $CertbotErrStreamFile_3 -Force -Confirm:$false -ErrorAction SilentlyContinue # Okay if the file is not deleted. Just a tmp file
Remove-Item -Path $CertbotOutStreamFile_0 -Force -Confirm:$false -ErrorAction SilentlyContinue # Okay if the file is not deleted. Just a tmp file
Remove-Item -Path $CertbotOutStreamFile_1 -Force -Confirm:$false -ErrorAction SilentlyContinue # Okay if the file is not deleted. Just a tmp file
Remove-Item -Path $CertbotOutStreamFile_2 -Force -Confirm:$false -ErrorAction SilentlyContinue # Okay if the file is not deleted. Just a tmp file
Remove-Item -Path $CertbotOutStreamFile_3 -Force -Confirm:$false -ErrorAction SilentlyContinue # Okay if the file is not deleted. Just a tmp file