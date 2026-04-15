#!/usr/bin/env bash
set -euo pipefail

CFG="$HOME/allsky/config/settings.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq není nainstalované"
  exit 1
fi

if [[ ! -f "$CFG" ]]; then
  echo "ERROR: Soubor neexistuje: $CFG"
  exit 1
fi

# záloha
cp -a "$CFG" "$CFG.bak.$(date +%Y%m%d_%H%M%S)"

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

# === aplikace ŠABLONY ===
jq '
{
  takedaytimeimages: true,
  savedaytimeimages: true,
  dayautoexposure: true,
  daymaxautoexposure: 5000,
  dayexposure: 10,
  daymean: 0.5,
  daymeanthreshold: 0.15,
  daydelay: 85000,
  dayautogain: true,
  daymaxautogain: 8,
  daygain: 1,
  imagestretchamountdaytime: 0,
  imagestretchmidpointdaytime: 10,
  daybin: 1,
  dayawb: false,
  daywbr: 2.5,
  daywbb: 1.8,
  dayskipframes: 5,
  daytuningfile: "",

  takenighttimeimages: true,
  savenighttimeimages: true,
  nightautoexposure: true,
  nightmaxautoexposure: 60000,
  nightexposure: 10000,
  nightmean: 0.3,
  nightmeanthreshold: 0.1,
  nightdelay: 30000,
  nightautogain: true,
  nightmaxautogain: 8,
  nightgain: 4,
  imagestretchamountnighttime: 0,
  imagestretchmidpointnighttime: 10,
  nightbin: 1,
  nightawb: false,
  nightwbr: 2.5,
  nightwbb: 2,
  nightskipframes: 1,
  nighttuningfile: "",

  daystokeep: 7,
  config: "[none]",
  extraargs: "",
  saturation: 1,
  contrast: 1,
  sharpness: 1,
  type: 99,
  quality: 95,
  filename: "image.jpg",
  rotation: 0,
  flip: 0,
  focusmode: false,
  determinefocus: false,
  consistentdelays: true,
  timeformat: "%Y%m%d %H:%M:%S",
  temptype: "C",
  latitude: "50N",
  longitude: "15E",
  angle: 0,
  takedarkframes: false,
  imageremovebadhighdarkframe: 0.05,
  usedarkframes: false,
  locale: "en_GB.UTF-8",
  debuglevel: 1,
  imageremovebadlow: 0,
  imageremovebadhigh: 0,

  imageremovebadcount: 5,

  imagecreatethumbnails: true,
  thumbnailsizex: 100,
  thumbnailsizey: 75,

  imageresizewidth: 0,
  imageresizeheight: 0,
  imagecroptop: 0,
  imagecropright: 0,
  imagecropbottom: 0,
  imagecropleft: 0,

  timelapsegenerate: true,
  timelapsewidth: 0,
  timelapseheight: 0,
  timelapsebitrate: 5000,
  timelapsefps: 25,
  timelapsekeepsequence: false,
  timelapseextraparameters: "",

  minitimelapsenumimages: 0,
  minitimelapseforcecreation: false,
  minitimelapsefrequency: 5,
  minitimelapsewidth: 0,
  minitimelapseheight: 0,
  minitimelapsebitrate: 2000,
  minitimelapsefps: 5,

  timelapsevcodec: "libx264",
  timelapsepixfmt: "yuv420p",
  timelapsefflog: "warning",

  keogramgenerate: true,
  keogramexpand: true,
  keogramfontname: "simplex",
  keogramfontcolor: "#ffffff",
  keogramfontsize: 2,
  keogramlinethickness: 3,
  keogramextraparameters: "",

  startrailsgenerate: true,
  startrailsbrightnessthreshold: 0.2,
  startrailsextraparameters: "",

  imageresizeuploadswidth: 0,
  imageresizeuploadsheight: 0,
  imageuploadfrequency: 1,

  timelapseupload: true,
  timelapseuploadthumbnail: true,
  keogramupload: true,
  startrailsupload: true,
  minitimelapseupload: false,
  minitimelapseuploadthumbnail: true,

  displaysettings: false,
  uselocalwebsite: false,
  daystokeeplocalwebsite: 7,

  useremotewebsite: false,
  remotewebsiteurl: "",
  remotewebsiteimageurl: "",
  remotewebsiteimagedir: "",
  remotewebsiteprotocol: "sftp",
  remotewebsiteimageuploadoriginalname: false,

  useremoteserver: false,
  remoteserverimagedir: "",
  remoteserverprotocol: "sftp",
  remoteserverimageuploadoriginalname: true,
  remoteservervideodestinationname: "allsky.mp4",
  remoteserverkeogramdestinationname: "keogram.jpg",
  remoteserverstartrailsdestinationname: "startrails.jpg",

  showonmap: true,
  location: "AstroMeters",
  owner: "astrometers.eu",
  camera: "AMASC01",
  lens: "FishEye",
  computer: "RPi 4",
  equipmentinfo: "Astrometers.eu AllSky camera AMASC01",
  imagessortorder: "descending",
  showupdatedmessage: true,
  uselogin: true,
  webuidatafiles: "",

  daytimeoverlay: "overlay-AMASC01-both.json",
  nighttimeoverlay: "overlay-AMASC01-both.json",


  enabledatabase: true,
  databasetype: "sqlite",
  cameratype: "RPi",
  cameramodel: "HQ",
  cameranumber: 0,

  uploadimages: true,
  lastchanged: (now | strftime("%Y-%m-%d %H:%M:%S"))
}
' "$CFG" > "$tmp"

# validace
jq -e . "$tmp" >/dev/null

# atomický zápis
mv "$tmp" "$CFG"

# === kopírování overlay ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OVERLAY_SRC="$SCRIPT_DIR/overlay-AMASC01-both.json"
OVERLAY_DST="$HOME/allsky/config/overlay/config/overlay-AMASC01-both.json"

if [[ -f "$OVERLAY_SRC" ]]; then
  cp "$OVERLAY_SRC" "$OVERLAY_DST"
  echo "OK: overlay-AMASC01-both.json zkopírován do overlay/config/"
else
  echo "WARN: $OVERLAY_SRC nenalezen, overlay nebyl zkopírován"
fi

# nastavení práv
chmod 664 "$CFG"

echo "OK: settings.json přepsán podle šablony"
echo "Práva nastavena na 664"
echo "Záloha: $(ls -1t "$CFG".bak.* | head -n 1)"
