Add-Type -AssemblyName System.Drawing

$OutDir = Join-Path (Get-Location) "medium-assets"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function New-Canvas($Path, $Title, $Subtitle, [ScriptBlock]$DrawBody) {
    $w = 1600
    $h = 900
    $bmp = New-Object System.Drawing.Bitmap($w, $h)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $g.Clear([System.Drawing.Color]::FromArgb(252, 252, 250))

    $gridPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(235, 235, 230), 1)
    for ($x = 80; $x -lt $w; $x += 80) { $g.DrawLine($gridPen, $x, 0, $x, $h) }
    for ($y = 80; $y -lt $h; $y += 80) { $g.DrawLine($gridPen, 0, $y, $w, $y) }
    $gridPen.Dispose()

    Draw-Text $g $Title 80 58 34 ([System.Drawing.FontStyle]::Bold) ([System.Drawing.Color]::FromArgb(20, 24, 28))
    Draw-Text $g $Subtitle 84 113 17 ([System.Drawing.FontStyle]::Regular) ([System.Drawing.Color]::FromArgb(76, 83, 90))

    & $DrawBody $g

    Draw-Text $g "Sean Liu / Git learning notes" 80 835 14 ([System.Drawing.FontStyle]::Regular) ([System.Drawing.Color]::FromArgb(105, 112, 120))
    $bmp.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()
}

function Brush($r, $g, $b) {
    New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb($r, $g, $b))
}

function PenC($r, $g, $b, $width = 3) {
    New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb($r, $g, $b), $width)
}

function FontC($size, $style) {
    New-Object System.Drawing.Font("Segoe UI", $size, $style)
}

function Draw-Rect($g, $x, $y, $w, $h, $brush, $pen) {
    if ($brush) { $g.FillRectangle($brush, $x, $y, $w, $h) }
    if ($pen) { $g.DrawRectangle($pen, $x, $y, $w, $h) }
}

function Draw-Text($g, $text, $x, $y, $size, $style, $color) {
    $font = FontC $size $style
    $brush = New-Object System.Drawing.SolidBrush($color)
    $g.DrawString($text, $font, $brush, $x, $y)
    $font.Dispose()
    $brush.Dispose()
}

function Draw-CenteredText($g, $text, $rect, $size, $style, $color) {
    $font = FontC $size $style
    $brush = New-Object System.Drawing.SolidBrush($color)
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    $g.DrawString($text, $font, $brush, $rect, $format)
    $format.Dispose()
    $font.Dispose()
    $brush.Dispose()
}

function Draw-Arrow($g, $x1, $y1, $x2, $y2, $color) {
    $pen = New-Object System.Drawing.Pen($color, 4)
    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::ArrowAnchor
    $g.DrawLine($pen, $x1, $y1, $x2, $y2)
    $pen.Dispose()
}

$ink = [System.Drawing.Color]::FromArgb(20, 24, 28)
$muted = [System.Drawing.Color]::FromArgb(76, 83, 90)
$line = [System.Drawing.Color]::FromArgb(50, 56, 62)
$paper = [System.Drawing.Color]::FromArgb(255, 255, 252)
$soft = [System.Drawing.Color]::FromArgb(245, 245, 240)
$accent = [System.Drawing.Color]::FromArgb(20, 116, 128)
$warn = [System.Drawing.Color]::FromArgb(140, 80, 45)

New-Canvas (Join-Path $OutDir "git-mental-model-01.png") "Git state model" "The commands make sense when the four places are separated." {
    param($g)
    $cards = @(
        @{X=90; Y=260; W=310; H=230; Title="Working Tree"; Body="current files`nexperiments`nuncommitted edits"},
        @{X=470; Y=260; W=310; H=230; Title="Staging Area"; Body="selected version`nfor the next commit"},
        @{X=850; Y=260; W=310; H=230; Title="Local Repository"; Body="commits saved`non my machine"},
        @{X=1230; Y=260; W=310; H=230; Title="Remote Repository"; Body="shared history`nGitea / GitHub / GitLab"}
    )
    foreach ($card in $cards) {
        Draw-Rect $g $card.X $card.Y $card.W $card.H (Brush 255 255 252) (PenC 50 56 62 3)
        Draw-Text $g $card.Title ($card.X + 25) ($card.Y + 28) 21 ([System.Drawing.FontStyle]::Bold) $ink
        Draw-Text $g $card.Body ($card.X + 28) ($card.Y + 92) 18 ([System.Drawing.FontStyle]::Regular) $muted
    }
    Draw-Arrow $g 415 375 455 375 $accent
    Draw-Text $g "git add" 405 330 17 ([System.Drawing.FontStyle]::Bold) $accent
    Draw-Arrow $g 795 375 835 375 $accent
    Draw-Text $g "git commit" 765 330 17 ([System.Drawing.FontStyle]::Bold) $accent
    Draw-Arrow $g 1175 375 1215 375 $accent
    Draw-Text $g "git push" 1165 330 17 ([System.Drawing.FontStyle]::Bold) $accent

    Draw-Rect $g 250 615 1100 95 (Brush 255 255 252) (PenC 50 56 62 3)
    Draw-CenteredText $g "Git is not uploading a folder. It turns selected changes into traceable history." (New-Object System.Drawing.RectangleF(280, 625, 1040, 75)) 23 ([System.Drawing.FontStyle]::Bold) $ink
}

New-Canvas (Join-Path $OutDir "git-mental-model-02.png") "Source vs generated output" "Version control should keep what the team maintains, not every file a tool creates." {
    param($g)
    Draw-Rect $g 130 245 590 390 (Brush 255 255 252) (PenC 50 56 62 3)
    Draw-Text $g "SOURCE" 180 295 31 ([System.Drawing.FontStyle]::Bold) $accent
    Draw-Text $g "Keep in Git" 182 342 20 ([System.Drawing.FontStyle]::Bold) $ink
    Draw-Text $g "code`nconfig`ndocs`ntests`nbuild scripts`nrequired assets" 185 395 22 ([System.Drawing.FontStyle]::Regular) $muted

    Draw-Rect $g 880 245 590 390 (Brush 255 255 252) (PenC 50 56 62 3)
    Draw-Text $g "GENERATED" 930 295 31 ([System.Drawing.FontStyle]::Bold) $warn
    Draw-Text $g "Usually ignore" 932 342 20 ([System.Drawing.FontStyle]::Bold) $ink
    Draw-Text $g "build output`ncache`nlogs`n__pycache__`nnode_modules`ntemporary files" 935 395 22 ([System.Drawing.FontStyle]::Regular) $muted

    Draw-Rect $g 490 690 620 70 (Brush 245 245 240) (PenC 50 56 62 2)
    Draw-CenteredText $g ".gitignore documents the project boundary." (New-Object System.Drawing.RectangleF(505, 700, 590, 50)) 22 ([System.Drawing.FontStyle]::Bold) $ink
}

New-Canvas (Join-Path $OutDir "git-mental-model-03.png") "From change to shared history" "A practical workflow for moving work through Git." {
    param($g)
    $steps = @(
        @{N="1"; T="Edit"; B="Working Tree"},
        @{N="2"; T="Inspect"; B="status / diff"},
        @{N="3"; T="Select"; B="git add"},
        @{N="4"; T="Record"; B="git commit"},
        @{N="5"; T="Share"; B="git push"}
    )
    $x = 95
    $y = 300
    $w = 250
    $h = 200
    $gap = 70
    for ($i = 0; $i -lt $steps.Count; $i++) {
        $s = $steps[$i]
        $px = $x + $i * ($w + $gap)
        Draw-Rect $g $px $y $w $h (Brush 255 255 252) (PenC 50 56 62 3)
        Draw-Text $g $s.N ($px + 25) ($y + 22) 30 ([System.Drawing.FontStyle]::Bold) $accent
        Draw-Text $g $s.T ($px + 25) ($y + 78) 24 ([System.Drawing.FontStyle]::Bold) $ink
        Draw-Text $g $s.B ($px + 25) ($y + 128) 18 ([System.Drawing.FontStyle]::Regular) $muted
        if ($i -lt ($steps.Count - 1)) {
            Draw-Arrow $g ($px + $w + 18) ($y + 100) ($px + $w + $gap - 20) ($y + 100) $line
        }
    }
    Draw-Rect $g 270 635 1060 95 (Brush 245 245 240) (PenC 50 56 62 2)
    Draw-CenteredText $g "Ask: which state am I moving forward?" (New-Object System.Drawing.RectangleF(290, 645, 1020, 75)) 25 ([System.Drawing.FontStyle]::Bold) $ink
}

Get-ChildItem -LiteralPath $OutDir -Filter "git-mental-model-*.png" | Select-Object FullName, Length
