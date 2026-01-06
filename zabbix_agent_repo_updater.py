#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

WORKDIR = Path("/var/lib/zabbix-agent-updater")
LOGFILE = Path("/var/log/zabbix-agent-updater.log")
SERVICE_PATH = Path("/etc/systemd/system/zabbix-agent-update.service")
TIMER_PATH = Path("/etc/systemd/system/zabbix-agent-update.timer")


# Função de log simples
def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOGFILE.parent.mkdir(parents=True, exist_ok=True)
    with LOGFILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

# Função para executar comandos
def run(cmd):
    log("RUN: " + " ".join(cmd))
    subprocess.run(
        cmd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

# Verifica se o script está sendo executado como root
def must_be_root():
    if os.geteuid() != 0:
        print("Este script deve ser executado como root")
        sys.exit(1)


# Identifica a versão major do Debian (ex: Debian 10.x)
def get_debian_major_version():
    
    os_release = {}

    with open("/etc/os-release", "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                os_release[k] = v.strip('"')

    if os_release.get("ID") != "debian":
        raise RuntimeError("Sistema não é Debian")

    version_id = os_release.get("VERSION_ID")
    if not version_id:
        raise RuntimeError("VERSION_ID não encontrado")

    return version_id.split(".")[0]

# Garante que os pré-requisitos estão instalados
def ensure_prereqs():
    run(["apt-get", "update"])
    run(["apt-get", "install", "-y", "ca-certificates", "curl", "apt-transport-https"])


# Garante que o repositório do Zabbix está instalado
def ensure_zabbix_repo():
    debian_major = get_debian_major_version()

    ZABBIX_RELEASE_DEB_URL = (
        "https://repo.zabbix.com/zabbix/7.4/release/debian/pool/main/z/zabbix-release/"
        f"zabbix-release_latest+debian{debian_major}_all.deb"
    )

    WORKDIR.mkdir(parents=True, exist_ok=True)
    deb_path = WORKDIR / f"zabbix-release_latest+debian{debian_major}_all.deb"

    log(f"Debian detectado: {debian_major}")
    log(f"Usando repo: {ZABBIX_RELEASE_DEB_URL}")

    run(["curl", "-fsSL", "-o", str(deb_path), ZABBIX_RELEASE_DEB_URL])
    run(["dpkg", "-i", str(deb_path)])
    run(["apt-get", "update"])

# Realiza a atualização do Zabbix Agent
def upgrade_agent():
    run(["apt-get", "install", "-y", "zabbix-agent"])
    run(["apt-get", "install", "-y", "--only-upgrade", "zabbix-agent"])
    run(["systemctl", "restart", "zabbix-agent"])

# Instala o timer do systemd
def install_timer():
    SERVICE_PATH.write_text(f"""[Unit]
Description=Atualizacao mensal do Zabbix Agent
After=network-online.target

[Service]
Type=oneshot
ExecStart={sys.executable} {Path(__file__).resolve()} run
""", encoding="utf-8")

    TIMER_PATH.write_text("""[Unit]
Description=Checagem mensal do Zabbix Agent

[Timer]
OnCalendar=monthly
Persistent=true
RandomizedDelaySec=6h

[Install]
WantedBy=timers.target
""", encoding="utf-8")

    run(["systemctl", "daemon-reload"])
    run(["systemctl", "enable", "--now", "zabbix-agent-update.timer"])

# Função principal
def main():
    must_be_root()

    if len(sys.argv) < 2:
        print("Uso: install-timer | run")
        sys.exit(2)

    if sys.argv[1] == "install-timer":
        ensure_prereqs()
        install_timer()
    elif sys.argv[1] == "run":
        ensure_prereqs()
        ensure_zabbix_repo()
        upgrade_agent()
    else:
        print("Parâmetro inválido")
        sys.exit(2)


if __name__ == "__main__":
    main()
