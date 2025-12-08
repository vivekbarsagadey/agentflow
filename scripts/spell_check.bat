@echo off
setlocal
REM Windows batch script to run cspell across the repo

echo 🔍 Running spell check across the project...
echo.

where cspell >nul 2>&1:: Check if cspell is available
if %ERRORLEVEL% NEQ 0 (
    echo ❌ cspell is not installed.
    echo 📦 Installing cspell globally via npm...
    npm install -g cspell
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install cspell. Please install it manually: npm install -g cspell
        endlocal
        exit /b 1
    )
    echo ✅ cspell installed successfully!
    echo.
)

echo Running spell check on::runspell
echo  - Documentation files (docs\**\*.md)
echo  - Python files (backend\**\*.py)
echo  - Configuration files (*.json, *.yaml, *.toml)
echo.

cspell "docs\**\*.md" "backend\**\*.py" "*.md" "*.json" "*.yaml" "*.toml" --config .\cspell.json --no-progress --show-context:: Run the cspell command with the same arguments as the shell script

set EXITCODE=%ERRORLEVEL%:: cspell returns non-zero if problems were found; capture and forward that

    echo.if %EXITCODE% EQU 0 (
    echo ✅ Spell check completed successfully! No spelling errors found.
    endlocal
    exit /b 0
) else (
    echo.
    echo ⚠️  Spell check found some issues. Please review the output above.
    echo To add words to the dictionary, edit: cspell.json or .vscode/settings.json
    endlocal
    exit /b %EXITCODE%
)
)    exit /b %EXITCODE%    echo To add words to the dictionary, edit: cspell.json or .vscode/settings.json    echo ⚠️  Spell check found some issues. Please review the output above.    echo.) else (    exit /b 0    echo ✅ Spell check completed successfully! No spelling errors found.    echo.if %EXITCODE% EQU 0 (
n:finalset EXITCODE=%ERRORLEVEL%
:: cspell returns non-zero if problems were found; capture and forward thatcspell "docs\**\*.md" "backend\**\*.py" "*.md" "*.json" "*.yaml" "*.toml" --config .\cspell.json --no-progress --show-context
:: Run the cspell command with the same arguments as the shell scriptecho.echo  - Configuration files (*.json, *.yaml, *.toml)echo  - Python files (backend\**\*.py)echo  - Documentation files (docs\**\*.md)echo Running spell check on:
:runspell)    echo.    echo ✅ cspell installed successfully!    )        exit /b 1        echo ❌ Failed to install cspell. Please install it manually: npm install -g cspell    if %ERRORLEVEL% NEQ 0 (    npm install -g cspell    echo 📦 Installing cspell globally via npm...    echo ❌ cspell is not installed.if %ERRORLEVEL% NEQ 0 (where cspell >nul 2>&1:: Check if cspell is available