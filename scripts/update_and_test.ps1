$ErrorActionPreference = "Stop"

$RepoPath = "C:\Projetos\p7"
$RepoUrl = "https://github.com/gestbrito/podium7.git"

if (-not (Test-Path $RepoPath)) {
    git clone $RepoUrl $RepoPath
}

Set-Location $RepoPath

git pull --ff-only
python scripts\run_tests_one_by_one.py