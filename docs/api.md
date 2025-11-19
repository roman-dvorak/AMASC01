# API Reference

Tato dokumentace popisuje programové rozhraní kamery AMASC01.

## Python API

### Základní použití

```python
from amasc01 import Camera

# Inicializace kamery
camera = Camera()

# Zachycení snímku
image = camera.capture()

# Uložení snímku
camera.save_image(image, "output.fits")

# Ukončení
camera.close()
```

### Třída Camera

#### `__init__(config_path=None)`

Inicializuje připojení ke kameře.

**Parametry:**
- `config_path` (str, optional): Cesta ke konfiguračnímu souboru

**Příklad:**
```python
camera = Camera(config_path="config/camera_config.yaml")
```

#### `capture(exposure=None, gain=None)`

Zachytí jeden snímek.

**Parametry:**
- `exposure` (float, optional): Doba expozice v sekundách
- `gain` (int, optional): Zisk (0-100)

**Vrací:**
- `numpy.ndarray`: Zachycený obraz

**Příklad:**
```python
image = camera.capture(exposure=10.0, gain=50)
```

#### `set_exposure(exposure)`

Nastaví dobu expozice.

**Parametry:**
- `exposure` (float): Doba expozice v sekundách

#### `set_gain(gain)`

Nastaví zisk kamery.

**Parametry:**
- `gain` (int): Zisk (0-100)

#### `get_temperature()`

Vrací aktuální teplotu sensoru.

**Vrací:**
- `float`: Teplota v °C

#### `save_image(image, filename, format='fits')`

Uloží snímek do souboru.

**Parametry:**
- `image` (numpy.ndarray): Obraz k uložení
- `filename` (str): Cesta k výstupnímu souboru
- `format` (str): Formát ('fits', 'jpg', 'png')

#### `close()`

Ukončí připojení ke kameře a uvolní zdroje.

## Utilita pro příkazovou řádku

### amasc01-capture

Zachytí snímek z příkazové řádky.

```bash
amasc01-capture [options]

Možnosti:
  -e, --exposure SECS    Doba expozice v sekundách
  -g, --gain VALUE       Zisk (0-100)
  -o, --output FILE      Výstupní soubor
  -f, --format FORMAT    Formát výstupu (fits/jpg/png)
  -c, --config FILE      Konfigurační soubor
```

**Příklad:**
```bash
amasc01-capture -e 10 -g 50 -o sky.fits
```

### amasc01-monitor

Spustí kontinuální monitoring.

```bash
amasc01-monitor [options]

Možnosti:
  -c, --config FILE      Konfigurační soubor
  -i, --interval SECS    Interval mezi snímky
  -d, --daemon           Spustit jako daemon
```

## REST API

Pokud je aktivováno webové rozhraní, je dostupné REST API.

### Endpointy

#### GET `/api/status`

Vrací aktuální stav kamery.

**Odpověď:**
```json
{
  "status": "idle",
  "temperature": 25.3,
  "last_capture": "2024-01-15T20:30:00Z",
  "exposure": 10.0,
  "gain": 50
}
```

#### POST `/api/capture`

Zachytí nový snímek.

**Tělo požadavku:**
```json
{
  "exposure": 10.0,
  "gain": 50,
  "format": "fits"
}
```

**Odpověď:**
```json
{
  "status": "success",
  "filename": "amasc01_20240115_203000.fits",
  "url": "/api/images/amasc01_20240115_203000.fits"
}
```

#### GET `/api/config`

Vrací aktuální konfiguraci.

#### POST `/api/config`

Aktualizuje konfiguraci.

#### GET `/api/images`

Seznam zachycených snímků.

#### GET `/api/images/{filename}`

Stáhne konkrétní snímek.

## Události

Kamera vysílá události pro monitoring:

```python
def on_capture_complete(image, metadata):
    print(f"Snímek zachycen: {metadata['filename']}")

camera.on_capture_complete = on_capture_complete
```

**Dostupné události:**
- `on_capture_start`: Zahájení zachycení snímku
- `on_capture_complete`: Dokončení zachycení
- `on_error`: Chyba během operace
- `on_temperature_change`: Změna teploty sensoru
