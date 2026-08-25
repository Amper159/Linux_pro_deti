"""Konfigurace pískoviště (cesty, limity, jména kontejnerů)."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

# Data mimo git – domovské adresáře uživatelů, účty, pokrok.
DATA_DIR = Path(os.environ.get("SANDBOX_DATA", PROJECT_DIR / "sandbox_data"))
HOMES_DIR = DATA_DIR / "homes"
PROGRESS_DIR = DATA_DIR / "progress"
USERS_FILE = DATA_DIR / "users.json"
SECRET_FILE = DATA_DIR / ".flask_secret"

SKEL_DIR = BASE_DIR / "skel"
DOCKERFILE_DIR = BASE_DIR / "docker"

# --- Kontejner ---------------------------------------------------------------
IMAGE_NAME = os.environ.get("SANDBOX_IMAGE", "linux-pro-deti-sandbox:2")
CONTAINER_PREFIX = "lpd-piskoviste-"

MEMORY_LIMIT = "128m"
CPU_LIMIT = "0.5"
PIDS_LIMIT = "64"
TMPFS_SIZE = "16m"

# Kolik kontejnerů smí běžet naráz (ochrana hostitele).
MAX_CONTAINERS = int(os.environ.get("SANDBOX_MAX_CONTAINERS", "12"))

# Kontejner nečinný déle než X sekund se zastaví (domov na disku zůstává).
IDLE_TIMEOUT = int(os.environ.get("SANDBOX_IDLE_TIMEOUT", "1200"))

# --- Běh příkazů -------------------------------------------------------------
COMMAND_TIMEOUT = 10          # sekund na jeden příkaz
MAX_OUTPUT_BYTES = 16 * 1024  # ořez výstupu, ať nezahltí prohlížeč
MAX_COMMAND_LENGTH = 400

# Uživatel uvnitř kontejneru: jméno se odvozuje z hashe (viz auth.py).
CONTAINER_USER_PREFIX = "kadet_"


def ensure_dirs() -> None:
    for d in (DATA_DIR, HOMES_DIR, PROGRESS_DIR):
        d.mkdir(parents=True, exist_ok=True)
