# Instalace reverse-ssh service

## Předpoklady

Musí existovat SSH klíč pro tunel. Vygeneruj ho (pokud ještě neexistuje) a přidej veřejný klíč na tunelovací server:

```bash
sudo ssh-keygen -t ed25519 -f /root/.ssh/tunnel_key -N ""
# Zobraz veřejný klíč a přidej ho na tunnel.astrometers.eu pro uživatele tunnel
sudo cat /root/.ssh/tunnel_key.pub
```

## 1. Zkopíruj service soubor

```bash
sudo cp reverse-ssh.service /etc/systemd/system/reverse-ssh.service
```

## 2. Přidej server do known_hosts (jako root)

Aby `StrictHostKeyChecking=yes` nezpůsobilo selhání při prvním připojení:

```bash
sudo ssh-keyscan -H tunnel.astrometers.eu | sudo tee -a /root/.ssh/known_hosts
```

## 3. Aktivuj a spusť service

```bash
sudo systemctl daemon-reload
sudo systemctl enable reverse-ssh.service
sudo systemctl start reverse-ssh.service
```

## 4. Ověř stav

```bash
sudo systemctl status reverse-ssh.service
```

---

## Parametry service

- **Tunelovací server:** `tunnel.astrometers.eu`
- **Uživatel:** `tunnel`
- **SSH klíč:** `/root/.ssh/tunnel_key`
- **Vzdálený port:** `34541` → `localhost:22`
- **Restart při pádu:** ano, každých 5 s
