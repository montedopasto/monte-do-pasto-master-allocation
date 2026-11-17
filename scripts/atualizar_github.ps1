# Atualiza o repositório GitHub da Master Allocation com a versão da pasta partilhada.
# Copia a app e os dados de _controlo (gerados pela verificação diária das 17h) e faz commit + push.
# Uso (PowerShell, dentro da pasta do repositório clonado):
#   .\scripts\atualizar_github.ps1
# ou indicando outra pasta da app:
#   .\scripts\atualizar_github.ps1 -Origem "C:\...\App Alocação Animais"
param(
  [string]$Origem = "$env:USERPROFILE\Monte do Pasto\Monte do Pasto - Documentos Partilhados\App Alocação Animais"
)
$ErrorActionPreference = 'Stop'
$Repo = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $Origem 'App_Alocacao_Animais.html'))) { throw "Não encontrei App_Alocacao_Animais.html em $Origem" }

# 1) app -> index.html (com a indicação para os motores de busca não indexarem)
$html = Get-Content -Raw -Encoding UTF8 (Join-Path $Origem 'App_Alocacao_Animais.html')
if ($html -notmatch 'name="robots"') {
  $html = $html.Replace('<meta name="viewport" content="width=device-width, initial-scale=1">', "<meta name=`"viewport`" content=`"width=device-width, initial-scale=1`">`n<meta name=`"robots`" content=`"noindex, nofollow`">")
}
[System.IO.File]::WriteAllText((Join-Path $Repo 'index.html'), $html, (New-Object System.Text.UTF8Encoding($false)))

# 2) dados
New-Item -ItemType Directory -Force -Path (Join-Path $Repo '_controlo') | Out-Null
foreach ($f in 'dados_alocacao.js', 'analises_marrocos.js', 'angus_certificados.js', 'origens.js') {
  $src = Join-Path (Join-Path $Origem '_controlo') $f
  if (Test-Path $src) { Copy-Item $src (Join-Path $Repo "_controlo\$f") -Force; Write-Host "Copiado $f" } else { Write-Host "Em falta: $f" }
}
foreach ($f in 'gerar_dados.py', 'gerar_analises.py', 'gerar_certificados.py', 'resumo_app.js') {
  $src = Join-Path (Join-Path $Origem '_controlo') $f
  if (Test-Path $src) { Copy-Item $src (Join-Path $Repo "scripts\$f") -Force }
}

# 3) commit e push (usa as credenciais Git do próprio utilizador)
Push-Location $Repo
try {
  git add -A
  $changes = git status --porcelain
  if (-not $changes) { Write-Host 'Sem alterações para publicar.'; return }
  git commit -m ("Atualização de dados " + (Get-Date -Format 'yyyy-MM-dd HH:mm'))
  git push
  Write-Host 'Publicado. O GitHub Pages atualiza em 1–2 minutos.'
} finally { Pop-Location }
