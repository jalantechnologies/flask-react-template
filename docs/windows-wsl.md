# Running on Windows (WSL)

Native Windows is not a supported development environment for this project. The setup scripts,
`make` targets, and `npm run` commands assume a Unix-like shell, and several tools (Gunicorn, the
Celery workers, the Docker test stack) behave differently or not at all under native Windows.

The supported path for Windows contributors is **WSL2** (Windows Subsystem for Linux, version 2).
Inside WSL2 you get a real Linux userspace, so every command in [Getting Started](getting-started.md)
runs exactly as documented for Linux and macOS. There is no separate Windows workflow to learn: you
install the toolchain once inside your WSL2 distribution and use the same commands as everyone else.

## 1. Install WSL2

From an elevated (Administrator) PowerShell, install WSL with the default Ubuntu distribution:

```powershell
wsl --install
```

Reboot when prompted, then launch **Ubuntu** from the Start menu and create your Linux username and
password. Confirm you are on version 2:

```powershell
wsl --list --verbose
```

The `VERSION` column must read `2`. If a distribution shows `1`, upgrade it:

```powershell
wsl --set-version Ubuntu 2
```

Run every command in the rest of this guide inside the WSL2 (Ubuntu) shell, not PowerShell.

## 2. Clone into the Linux filesystem

Clone the repository into your Linux home directory (for example `~/code`), **not** into a Windows
path under `/mnt/c`. Working out of `/mnt/c` forces every file read and write to cross the
Windows/Linux boundary, which makes installs, builds, and hot reload dramatically slower and can
break file-watching.

```bash
mkdir -p ~/code && cd ~/code
git clone https://github.com/jalantechnologies/flask-react-template.git
cd flask-react-template
```

Edit the code from Windows using VS Code with the **WSL** extension: run `code .` from inside the WSL
shell and it opens the project with the editor's backend running in Linux.

## 3. Install the toolchain inside WSL

Install Node 22.13.1 (per `.nvmrc`) and Python 3.12 (per the backend `Pipfile`). Managing them with
[asdf](https://asdf-vm.com/) keeps the versions pinned per project:

```bash
# Install asdf (see https://asdf-vm.com/guide/getting-started.html for the latest instructions)
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.1
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
source ~/.bashrc

# Node (matches .nvmrc)
asdf plugin add nodejs
asdf install nodejs 22.13.1
asdf global nodejs 22.13.1

# Python (the backend Pipfile requires 3.12)
asdf plugin add python
asdf install python 3.12
asdf global python 3.12
```

If you prefer not to use asdf, install Node 22.13.1 and Python 3.12 with any manager you like
(`nvm`, `pyenv`, the Ubuntu packages), as long as the versions match. Then install `pipenv`:

```bash
pip install --user pipenv
```

MongoDB and Redis can run either as native Ubuntu services inside WSL or through the Docker Compose
stack described below.

## 4. Run the app

From the project root inside WSL, the commands are identical to the Linux and macOS instructions in
[Getting Started](getting-started.md#running-the-app):

```bash
npm install
pipenv install --dev
npm run serve
```

The frontend is served at `http://localhost:3000` and the backend at `http://localhost:8080`. WSL2
forwards these ports to Windows automatically, so you open them in your Windows browser as usual.

## 5. Docker Desktop and the test stack

The Docker Compose files (`docker-compose.dev.yml` for the full stack, `docker-compose.test.yml` for
the test stack) run through Docker Desktop with WSL2 integration:

1. Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/).
2. In **Settings → General**, confirm **Use the WSL 2 based engine** is enabled.
3. In **Settings → Resources → WSL Integration**, enable integration for your Ubuntu distribution.

With integration on, the `docker` and `docker compose` commands are available inside the WSL shell
and the compose commands from [Getting Started](getting-started.md#running-the-app) work unchanged:

```bash
docker compose -f docker-compose.dev.yml up --build
```

## Common issues

- **`git` reports the whole tree as modified after cloning.** This is line-ending translation from a
  Windows Git installation leaking in. Clone from inside WSL with the WSL copy of `git`, not from
  Windows, so files keep Unix (`LF`) line endings.
- **Hot reload does not pick up file changes.** The project lives under `/mnt/c`. Move it into the
  Linux filesystem (`~/code/...`) as described in step 2.
- **`localhost` ports are unreachable from Windows.** Restart WSL with `wsl --shutdown` from
  PowerShell, then relaunch the distribution.
