# Instalace AMASC01

Tento návod vás provede instalací kamery AMASC01 a souvisejícího software.

## Hardwarové požadavky

- Počítač s operačním systémem Linux (doporučeno) nebo Windows
- Minimálně 4 GB RAM
- USB 3.0 port nebo síťové připojení
- Dostatek místa na disku pro ukládání snímků (doporučeno 100+ GB)

## Softwarové požadavky

### Linux (doporučeno)

```bash
# Instalace závislostí
sudo apt-get update
sudo apt-get install python3 python3-pip libusb-1.0-0-dev

# Instalace Python balíčků
pip3 install numpy astropy opencv-python
```

### Windows

1. Nainstalujte Python 3.8 nebo novější z https://python.org
2. Nainstalujte potřebné Python balíčky:

```cmd
pip install numpy astropy opencv-python
```

## Instalace kamery

1. Připojte kameru k počítači přes USB
2. Ověřte, že je kamera rozpoznána systémem
3. Nastavte udev pravidla (pouze Linux):

```bash
# Vytvořte soubor s pravidly
sudo nano /etc/udev/rules.d/99-amasc01.rules

# Přidejte následující řádek (upravte vendor ID a product ID podle vaší kamery)
SUBSYSTEM=="usb", ATTRS{idVendor}=="xxxx", ATTRS{idProduct}=="yyyy", MODE="0666"

# Znovu načtěte pravidla
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Konfigurace

Po instalaci pokračujte k [dokumentaci konfigurace](configuration.md).

## Testování instalace

Otestujte připojení kamery pomocí testovacího skriptu:

```bash
python3 scripts/test_camera.py
```

Pokud instalace proběhla úspěšně, měli byste vidět informace o kameře a být schopni zachytit testovací snímek.

## Řešení problémů

### Kamera není rozpoznána

- Zkontrolujte USB kabel a připojení
- Ověřte, že jsou nainstalovány správné ovladače
- Zkontrolujte udev pravidla (Linux)

### Problémy s oprávněními

Na Linuxu se ujistěte, že váš uživatel má oprávnění přistupovat k USB zařízením.

Pro další pomoc navštivte [FAQ](faq.md) nebo vytvořte issue na GitHubu.
