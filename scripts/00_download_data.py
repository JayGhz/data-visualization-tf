from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from tqdm import tqdm

BASE_URL = "https://datosabiertos.mef.gob.pe"
API_URL = f"{BASE_URL}/api/3/action/package_show"
USER_AGENT = "mef-open-data-downloader/1.2"

DATASETS = [
    {"name": "Detalle de inversiones", "slug": "detalle-de-inversiones"},
    {"name": "Formato 12B de inversiones", "slug": "formato-12b-de-de-inversiones"},
    {"name": "Cierre de inversiones", "slug": "cierre-de-inversiones"},
]

STATIC_RESOURCES = {
    "detalle-de-inversiones": {
        "csv": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/DETALLE_INVERSIONES.csv",
        "dictionary": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/Detalle_Inversiones_Diccionario.csv",
    },
    "formato-12b-de-de-inversiones": {
        "csv": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/FORMATO_12B.csv",
        "dictionary": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/F12B_Diccionario.csv",
    },
    "cierre-de-inversiones": {
        "csv": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/CIERRE_INVERSIONES.csv",
        "dictionary": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/Cierre_Inversiones_Diccionario.csv",
    },
}


# ---------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------

def _http_get(url: str, timeout: int = 60) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def is_valid_file(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def _download_to(url: str, destination: Path) -> None:
    if is_valid_file(destination):
        print(f"  ✔ SKIP (already exists): {destination.name}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": USER_AGENT})

    print(f"  ↓ Downloading {destination.name}")

    with urlopen(request, timeout=120) as response:
        total_size = response.length
        chunk_size = 8192

        with destination.open("wb") as f:

            # sin tamaño
            if total_size is None:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)

            # con progreso
            else:
                with tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    desc=destination.name,
                ) as pbar:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        pbar.update(len(chunk))


# ---------------------------------------------------------------------
# Dataset fetch
# ---------------------------------------------------------------------

def _fetch_dataset(slug: str) -> dict:
    url = f"{API_URL}?{urlencode({'id': slug})}"
    raw = _http_get(url)
    return json.loads(raw.decode("utf-8"))["result"]


def _pick_best(resources: list[dict]) -> dict | None:
    csvs = [r for r in resources if (r.get("format") or "").lower() == "csv"]
    return csvs[0] if csvs else None


# ---------------------------------------------------------------------
# Main download logic
# ---------------------------------------------------------------------

def download_dataset(dataset: dict, output_root: Path) -> dict:
    slug = dataset["slug"]
    name = dataset["name"]

    print(f"\n📦 {name}")

    try:
        result = _fetch_dataset(slug)
        resources = result.get("resources", [])
    except Exception:
        resources = []
        fallback = STATIC_RESOURCES.get(slug)
        if fallback:
            resources = [
                {"url": fallback["csv"], "format": "csv"},
                {"url": fallback["dictionary"], "format": "csv"},
            ]

    csv_resource = _pick_best(resources)

    dataset_dir = output_root / slug
    dataset_dir.mkdir(parents=True, exist_ok=True)

    csv_path = None

    if csv_resource and csv_resource.get("url"):
        csv_path = dataset_dir / "data.csv"
        _download_to(csv_resource["url"], csv_path)

    return {"dataset": name, "file": str(csv_path) if csv_path else None}


def download_all(output_root: Path) -> list[dict]:
    return [download_dataset(ds, output_root) for ds in DATASETS]


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/raw")
    args = parser.parse_args()

    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    results = download_all(output_root)

    print("\n✅ Done:\n")
    for r in results:
        print(f"{r['dataset']} → {r['file']}")

def run_download() -> None:
    """
    Entry point for pipeline orchestrator.
    """
    output_root = Path("data/raw")
    output_root.mkdir(parents=True, exist_ok=True)

    results = download_all(output_root)

    print("\n✅ Done:\n")
    for r in results:
        print(f"{r['dataset']} → {r['file']}")

if __name__ == "__main__":
    main()