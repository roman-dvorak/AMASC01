#!/usr/bin/env bash
set -euo pipefail

CFG="$HOME/allsky/html/allsky/configuration.json"
REMOTE_CFG="$HOME/allsky/config/remote_configuration.json"


if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq není nainstalované. Nainstaluj: sudo apt-get update && sudo apt-get install -y jq"
  exit 1
fi


if [[ ! -f "$CFG" ]]; then
  echo "ERROR: Soubor neexistuje: $CFG"
  exit 1
fi

# Ověření validního JSON
jq -e . "$CFG" >/dev/null

# Záloha
cp -a "$CFG" "$CFG.bak.$(date +%Y%m%d_%H%M%S)"

# Definice polí - přepíšeme leftSidebar a popoutIcons podle "tvé" konfigurace,
# ale popout pak hromadně vypneme.

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


read -r -d '' POPOUT_ICONS_JSON <<'JSON' || true
[
  {
    "display": true,
    "label": "Location",
    "icon": "fa fa-fw fa-map-marker-alt",
    "variable": "location",
    "value": "",
    "style": ""
  },
  {
    "display": true,
    "label": "Latitude",
    "icon": "fa fa-fw fa-map-marker",
    "variable": "s_latitude",
    "value": "",
    "style": ""
  },
  {
    "display": true,
    "label": "Longitude",
    "icon": "fa fa-fw fa-map-marker",
    "variable": "s_longitude",
    "value": "",
    "style": ""
  },
  {
    "display": true,
    "label": "Camera",
    "icon": "fa fa-fw fa-camera-retro",
    "variable": "camera",
    "value": "",
    "style": ""
  },
  {
    "display": true,
    "label": "Lens",
    "icon": "fa fa-fw fa-dot-circle",
    "variable": "lens",
    "value": "",
    "style": ""
  },
  {
    "display": true,
    "label": "Computer",
    "icon": "fa fa-fw fa-microchip",
    "variable": "computer",
    "value": "",
    "style": ""
  },
  {
    "display": true,
    "label": "Equipment info",
    "icon": "fa fa-fw fa-keyboard",
    "variable": "equipmentinfo",
    "value": "",
    "style": ""
  },
  {
    "display": true,
    "label": "Owner",
    "icon": "fa fa-fw fa-user",
    "variable": "owner",
    "value": "",
    "style": ""
  },
  {
    "display": false,
    "label": "Allsky Settings",
    "icon": "fa fa-fw fa-cogs",
    "variable": "",
    "value": "<a href='viewSettings.php' target='_blank'>Click to view</a>",
    "style": ""
  },
  {
    "display": true,
    "label": "Allsky Version",
    "icon": "fa fa-fw fa-file-alt",
    "variable": "AllskyVersion",
    "value": "",
    "style": ""
  },
  {
    "comment": "Add popout items above."
  }
]
JSON

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

jq \
  --argjson leftSidebar "$LEFT_SIDEBAR_JSON" \
  --argjson popoutIcons "$POPOUT_ICONS_JSON" \
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

  # --- homePage.* (jen texty/OG) ---
| .homePage.title               = "ASTROMETERS ALLSKY"
| .homePage.og_description      = "AstroMeters All-sky camera AMASC01"
| .homePage.includeLinkToMakeOwn = false
| .homePage.og_url              = "https://astrometers.eu/products/AMASC01"

  # --- menu/ikony ---
| .homePage.leftSidebar = $leftSidebar
| .homePage.popoutIcons = ($popoutIcons | map(if has("display") then .display = false else . end))
  ' \
  "$CFG" > "$tmp"

jq -e . "$tmp" >/dev/null
mv "$tmp" "$CFG"

chmod 664 "$CFG"
echo "OK: Upraveno: $CFG"
echo "Záloha: $(ls -1t "$CFG".bak.* | head -n 1)"

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

