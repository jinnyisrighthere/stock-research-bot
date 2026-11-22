$ErrorActionPreference = 'Stop'
$reportRoot = Split-Path -Parent $PSScriptRoot
$reportDocx = Join-Path $reportRoot 'output\nvda_20261122\NVDA_심층분석_20261122.docx'
$reportPdf = Join-Path $reportRoot 'output\nvda_20261122\NVDA_심층분석_20261122.pdf'
$wordApp = $null
$reportDocument = $null
try {
    $wordApp = New-Object -ComObject Word.Application
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    $reportDocument = $wordApp.Documents.Open($reportDocx, $false, $false)
    $reportDocument.Fields.Update() | Out-Null
    $reportDocument.Repaginate()
    $reportDocument.Save()
    $reportDocument.ExportAsFixedFormat($reportPdf, 17)
    Write-Output ('PDF pages: ' + $reportDocument.ComputeStatistics(2))
    Write-Output $reportPdf
} finally {
    if ($null -ne $reportDocument) {
        $reportDocument.Close(0)
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($reportDocument) | Out-Null
    }
    if ($null -ne $wordApp) {
        $wordApp.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp) | Out-Null
    }
}
