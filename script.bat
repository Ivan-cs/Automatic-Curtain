@echo off
set "ACCESS_TOKEN="
set "USERNAME=mhs-legacy"
set "REPO_NAME=ec-health-lite"       
set "GITLAB_URL=gitlab.com"        
set "BRANCH=realtest"                         

if exist %REPO_NAME% (
    echo Repository already exists. Pulling latest changes from %BRANCH% branch...
    cd %REPO_NAME%

    git checkout %BRANCH%

    REM Set the remote URL with the embedded token to ensure automated pulling
    git remote set-url origin https://oauth2:%ACCESS_TOKEN%@%GITLAB_URL%/%USERNAME%/%REPO_NAME%.git

    REM Pull the latest changes from the specified branch
    git pull origin %BRANCH%

    echo Pull process completed.
) else (
    echo Cloning the repository...
    git clone https://oauth2:%ACCESS_TOKEN%@%GITLAB_URL%/%USERNAME%/%REPO_NAME%.git

    REM Check if the repo was successfully cloned
    if exist %REPO_NAME% (
        cd %REPO_NAME%
        echo Clone process completed.
    ) else (
        echo Failed to clone repository. Please check your credentials and repository name.
    )
)

set "dotnet_name=dotnet"
set "innosetup_name=ISCC"
set "msbuild_name=MSBuild"


where %dotnet_name% >nul 2>&1

if %errorlevel% equ 1 (
    echo Dotnet MSBuild tool cannot be found in PATH
    exit
)

where %innosetup_name% >nul 2>&1

if %errorlevel% equ 1 (
    echo InnoSetup compiler tool cannot be found in PATH
    exit
)


where %msbuild_name% >nul 2>&1


if %errorlevel% equ 1 (
    echo MSBuild tool cannot be found in PATH
    exit
)


%msbuild_name% /p:OutDir="C:\Downloads"

cd "C:\Downloads"

%innosetup_name% testing.iss


exit
