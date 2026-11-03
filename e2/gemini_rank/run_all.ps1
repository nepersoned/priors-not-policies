$agy = "$env:LOCALAPPDATA\agy\bin\agy.exe"
$dir = ".\paper4\e2\gemini_rank"
$files = Get-ChildItem $dir -Filter 'r*g*.txt' | Where-Object { -not (Test-Path (Join-Path $dir ($_.BaseName + '.out'))) }
$jobs = @()
foreach ($f in $files) {
    while ((Get-Job -State Running).Count -ge 6) { Start-Sleep -Seconds 3 }
    $jobs += Start-Job -ArgumentList $agy, $f.FullName, (Join-Path $dir ($f.BaseName + '.out')) -ScriptBlock {
        param($agy, $in, $out)
        $q = (Get-Content $in -Raw -Encoding utf8).Replace('"', "'")
        $r = & $agy -p $q --model gemini-3.8-flash-high
        $r | Out-File $out -Encoding utf8
    }
}
$jobs | Wait-Job | Out-Null
"done: " + (Get-ChildItem $dir -Filter '*.out').Count + " outputs"
