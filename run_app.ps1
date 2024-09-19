# Caminho da venv
$venvPath = "venv"
$requirementsPath = ".\requirements.txt"
$appFilePath = ".\app.py"

# Verifica se a venv já existe
if (-not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found. Creating venv..."
    python -m venv $venvPath
    Write-Host "venv created."

    # Instala as dependências se o arquivo requirements.txt existir
    if (Test-Path $requirementsPath) {
        Write-Host "Installing dependencies from requirements.txt..."
        & "$venvPath\Scripts\pip.exe" install -r $requirementsPath
        Write-Host "Dependencies installed."
    } else {
        Write-Host "Warning: requirements.txt not found. No dependencies installed."
    }
}

# Ativa a venv
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    Write-Host "Activating virtual environment..."
    & $activateScript

    # Após ativar, execute o app.py
    if (Test-Path $appFilePath) {
        Write-Host "Running app.py..."
        python $appFilePath
    } else {
        Write-Host "Error: app.py not found."
    }
} else {
    Write-Host "Error: Could not find activation script."
}
