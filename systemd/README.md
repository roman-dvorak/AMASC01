# Reverse SSH tunnel

Systemd service for reverse SSH tunnel to `tunnel.astrometers.eu`.

## Files

- `reverse-ssh.service.template` — systemd service template (`{{PORT}}` is replaced during installation)
- `install.sh` — installation script
- `reverse-ssh.service` — generated service file (not tracked in git)

## Prerequisites

- SSH key `/root/.ssh/tunnel_key` (ed25519)
- Host key of `tunnel.astrometers.eu` in `/root/.ssh/known_hosts`

Generate key:

```bash
sudo ssh-keygen -t ed25519 -f /root/.ssh/tunnel_key -N "" -C "reverse-ssh-$(hostname)"
```

Add host key:

```bash
sudo ssh-keyscan tunnel.astrometers.eu 2>/dev/null | sudo tee -a /root/.ssh/known_hosts
```

Public key (`/root/.ssh/tunnel_key.pub`) needs to be added to the tunnel server.

## Installation

```bash
./install.sh
```

The script generates a random port (10000–65000), creates the service file and installs it into systemd. It prints the `~/.ssh/config` entry at the end.

## Service management

```bash
sudo systemctl status reverse-ssh
sudo systemctl restart reverse-ssh
sudo journalctl -u reverse-ssh -f
```
