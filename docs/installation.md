# Installation

This guide installs the tools needed to run the project on a fresh machine.

## Required Tools

| Tool | Required for | Version used by this project |
| --- | --- | --- |
| Git | Cloning the repository | Any recent version |
| Python | Backend | Python 3.11 or newer |
| Node.js and npm | Frontend | Node.js 18 or newer |
| Docker | Container builds and local container testing | Any recent Docker Engine or Docker Desktop |
| Google Cloud CLI | Firestore, Vertex AI, Translation, Cloud Run deployment | Any recent `gcloud` version |

## Linux Installation

### Ubuntu or Debian

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip curl ca-certificates gnupg
```

Install Node.js 18:

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

Install Docker:

```bash
sudo apt install -y docker.io
sudo usermod -aG docker "$USER"
```

Log out and log back in after adding your user to the `docker` group.

Install Google Cloud CLI:

```bash
sudo apt install -y apt-transport-https ca-certificates gnupg curl
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt update
sudo apt install -y google-cloud-cli
```

### Fedora

```bash
sudo dnf install -y git python3 python3-pip nodejs npm docker google-cloud-cli
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Log out and log back in after adding your user to the `docker` group.

## macOS Installation

Install Homebrew if it is not already installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install project tools:

```bash
brew install git python@3.11 node@18 docker google-cloud-sdk
```

Start Docker Desktop after installing it:

```bash
open -a Docker
```

If `node` is not found after installing `node@18`, add it to your shell path:

```bash
echo 'export PATH="/opt/homebrew/opt/node@18/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

On Intel Macs, use this path instead:

```bash
echo 'export PATH="/usr/local/opt/node@18/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## Windows Installation

Open PowerShell as Administrator.

Install Git:

```powershell
winget install --id Git.Git -e
```

Install Python 3.11:

```powershell
winget install --id Python.Python.3.11 -e
```

Install Node.js 18:

```powershell
winget install --id OpenJS.NodeJS.LTS -e
```

Install Docker Desktop:

```powershell
winget install --id Docker.DockerDesktop -e
```

Install Google Cloud CLI:

```powershell
winget install --id Google.CloudSDK -e
```

Close and reopen PowerShell after installation.

If PowerShell blocks virtual environment activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Verify Tool Installation

Linux and macOS:

```bash
git --version
python3 --version
node --version
npm --version
docker --version
gcloud --version
```

Windows PowerShell:

```powershell
git --version
py --version
node --version
npm --version
docker --version
gcloud --version
```

## Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd Election_Process_Education
```

## Install Backend Dependencies

Linux and macOS:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Install Frontend Dependencies

```bash
cd frontend
npm ci
```

Use `npm ci` because the repository includes `frontend/package-lock.json`.

## Next Step

Continue with [Setup](setup.md).
