#!/usr/bin/env bash
set -euo pipefail

CFG="$HOME/allsky/html/allsky/configuration.json"
REMOTE_CFG="$HOME/allsky/config/remote_configuration.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq není nainstalované. Nainstaluj: sudo apt-get update && sudo apt-get install -y jq"
  exit 1
fi

# Definice polí - přepíšeme leftSidebar podle "tvé" konfigurace
read -r -d '' LEFT_SIDEBAR_JSON <<'JSON' || true
[
  {
    "comment": "Once you have modified the settings so the overlay fits, set 'display' to true.",
    "display": true,
    "title": "Show constellation overlay",
    "icon": "fa fa-2x fa-fw allsky-constellation",
    "other": "id='overlayBtn' ng-click='toggleOverlay()' ng-class=\"{'active': showOverlay}\"",
    "style": ""
  },
  {
    "display": true,
    "url": "videos/",
    "title": "Archived Timelapes",
    "icon": "fa fa-2x fa-fw fa-video",
    "style": ""
  },
  {
    "display": false,
    "url": "",
    "title": "Mini-timelapse",
    "icon": "fa fa-2x fa-fw fa-file-video",
    "style": ""
  },
  {
    "display": true,
    "url": "keograms/",
    "title": "Archived Keograms",
    "icon": "fa fa-2x fa-fw fa-barcode",
    "style": ""
  },
  {
    "display": true,
    "url": "images/",
    "title": "Archived Images Gallery",
    "icon": "fa fa-2x fa-fw fa-camera-retro",
    "style": ""
  },
  {
    "display": true,
    "url": "startrails/",
    "title": "Archived Startrails",
    "icon": "fa fa-2x fa-fw fa-star",
    "style": ""
  },
  {
    "display": false,
    "url": "meteors/",
    "title": "Archived Meteors",
    "icon": "fa fa-2x fa-fw fa-meteor",
    "style": ""
  },
  {
    "display": true,
    "variable": "imageName",
    "title": "Full-sized image",
    "icon": "fa fa-2x fa-fw fa-expand-arrows-alt",
    "style": ""
  },
  {
    "display": false,
    "title": "Display information about the camera and other settings",
    "icon": "fa fa-2x fa-fw fa-info-circle",
    "other": "ng-click='toggleInfo()' ng-class=\"{'active': showInfo}\"",
    "style": ""
  },
  {
    "display": true,
    "url": "https://astrometers.eu/products/AMASC01",
    "title": "AstroMeters AllSky Camera",
    "icon": "fa fa-2x fa-fw fa-camera",
    "style": ""
  },
  {
    "display": false,
    "comment": "Add leftSidebar items above."
  }
]
JSON

# Funkce pro úpravu jednoho konfiguračního souboru
update_config() {
  local cfg="$1"

  if [[ ! -f "$cfg" ]]; then
    echo "WARN: Soubor neexistuje, přeskakuji: $cfg"
    return 0
  fi

  # Ověření validního JSON
  jq -e . "$cfg" >/dev/null

  # Záloha
  cp -a "$cfg" "$cfg.bak.$(date +%Y%m%d_%H%M%S)"

  local tmp
  tmp="$(mktemp)"

  jq \
    --argjson leftSidebar "$LEFT_SIDEBAR_JSON" \
    '
    # --- config.* (obecné AstroMeters AMASC01) ---
    .config.location          = "AstroMeters"
  | .config.latitude          = "50N"
  | .config.longitude         = "15E"
  | .config.camera            = "AMASC01"
  | .config.lens              = "FishEye"
  | .config.computer          = "RPi 4"
  | .config.equipmentinfo     = "AstroMeters All-sky camera AMASC01"
  | .config.owner             = "AstroMeters"

    # Overlay parametry (podle tvé config)
  | .config.overlayWidth      = 660
  | .config.overlayHeight     = 660
  | .config.overlayOffsetLeft = 120
  | .config.overlayOffsetTop  = 0
  | .config.az                = 200
  | .config.imageWidth        = 900
  | .config.opacity           = 0.5
  | .config.live              = true
  | .config.id                = "starmap"
  | .config.AllskyVersion     = "AMASC01-2025"
  | .config.elevation         = 405

    # --- homePage.* ---
  | .homePage.title                = "Astrometers AMASC01 - ALLSKY camera"
  | .homePage.og_description       = "Astrometers AMASC01 - ALLSKY camera"
  | .homePage.includeLinkToMakeOwn = false
  | .homePage.og_url               = "https://astrometers.eu/products/AMASC01"

    # --- menu/ikony ---
  | .homePage.leftSidebar = $leftSidebar
  | .homePage.popoutIcons = []
    ' \
    "$cfg" > "$tmp"

  jq -e . "$tmp" >/dev/null
  mv "$tmp" "$cfg"
  chmod 664 "$cfg"
  echo "OK: Upraveno: $cfg"
  echo "Záloha: $(ls -1t "$cfg".bak.* | head -n 1)"
}

update_config "$CFG"
update_config "$REMOTE_CFG"
