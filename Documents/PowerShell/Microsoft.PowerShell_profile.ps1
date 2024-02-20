Import-Module posh-git
Import-Module oh-my-posh
Set-PoshPrompt -Theme negligible
# Import the Chocolatey Profile that contains the necessary code to enable
# tab-completions to function for `choco`.
# Be aware that if you are missing these lines from your profile, tab completion
# for `choco` will not function.
# See https://ch0.co/tab-completion for details.
$ChocolateyProfile = "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
if (Test-Path($ChocolateyProfile)) {
  Import-Module "$ChocolateyProfile"
}

Invoke-Expression (& { (zoxide init powershell --cmd cd | Out-String) })
Set-Location C:\Users\Kiyam
