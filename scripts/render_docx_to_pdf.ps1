$ErrorActionPreference = "Stop"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $docPath = (Resolve-Path "reports/Bao_cao_tien_do_Tuan_12_13_DATN_20224083_ban_cap_nhat.docx").Path
    $pdfPath = [System.IO.Path]::ChangeExtension($docPath, ".pdf")
    $doc = $word.Documents.Open($docPath)
    $wdFormatPDF = 17
    $doc.SaveAs([ref]$pdfPath, [ref]$wdFormatPDF)
    $pages = $doc.ComputeStatistics(2)
    Write-Host "PDF exported successfully to: $pdfPath"
    Write-Host "Total pages rendered: $pages"
    $doc.Close([ref]$false)
} finally {
    $word.Quit()
}
