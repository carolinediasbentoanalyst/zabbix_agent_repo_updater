# Automação de Atualização do Zabbix Agent 

## Visão geral

Projeto em andamento.

Esta documentação descreve uma automação em **Python**, executada como **root**, para:

- Manter o **repositório oficial do Zabbix 7.4** configurado no Debian
- Verificar qual versão do Debian está sendo utilizada
- Verificar e aplicar atualizações do pacote **zabbix-agent**
- Executar a checagem **automaticamente a cada 1 mês** usando **systemd timer**

A automação segue o método oficial de instalação descrito pela Zabbix, utilizando o pacote `zabbix-release`.

O script foi escrito para Debian com função dedicada a identificar a versão do sistema operacional, mas pode ser reutilizado em outras distribuições Linux ajustando a forma como o pacote `zabbix-release` é obtido.
---

## Requisitos

- Sistema operacional: **Debian GNU/Linux 10 (buster) ou superior**
- Acesso root
- Python 3 instalado
- systemd habilitado
- Acesso à internet para o repositório oficial da Zabbix

---

## Estrutura da automação

| Componente | Caminho |
|----------|--------|
| Script Python | `/usr/local/sbin/zabbix_agent_repo_updater.py` |
| Log | `/var/log/zabbix-agent-updater.log` |
| Working dir | `/var/lib/zabbix-agent-updater/` |
| systemd service | `/etc/systemd/system/zabbix-agent-update.service` |
| systemd timer | `/etc/systemd/system/zabbix-agent-update.timer` |

---

## Script Python

Crie o arquivo:

```bash
vi /usr/local/sbin/zabbix_agent_repo_updater.py
chmod 750 /usr/local/sbin/zabbix_agent_repo_updater.py
````

Insira o conteúdo do ````zabbix_agent_repo_updater.py````

--- 

## Ativação da automação

Executar apenas uma vez:

````
/usr/local/sbin/zabbix_agent_repo_updater.py install-timer
````
---
## Validação
Verificar se o timer está ativo:
````
systemctl status zabbix-agent-update.timer
systemctl list-timers --all | grep zabbix-agent-update
````
Executar manualmente para teste:
````
/usr/local/sbin/zabbix_agent_repo_updater.py run
````
Ver logs:
````
tail -n 100 /var/log/zabbix-agent-updater.log
````

--- 
## Comportamento da automação

- Executa uma vez por mês

- Atualiza o repositório oficial do Zabbix

- Atualiza apenas o pacote zabbix-agent

- Reinicia automaticamente o serviço zabbix-agent após upgrade

Se o servidor estiver desligado no agendamento, a execução ocorre no próximo boot

---

## Considerações finais

Caso seja necessário não reiniciar automaticamente o serviço, basta remover do script a linha:

````
systemctl restart zabbix-agent
````


Para ambientes com controle de mudanças, recomenda-se executar o script manualmente antes de habilitar o timer.

