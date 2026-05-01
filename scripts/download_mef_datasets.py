from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = "https://datosabiertos.mef.gob.pe"
API_URL = f"{BASE_URL}/api/3/action/package_show"
USER_AGENT = "mef-open-data-downloader/1.0"

DATASETS = [
    {"name": "Detalle de inversiones", "slug": "detalle-de-inversiones"},
    {
        "name": "Formato 12B de inversiones",
        "slug": "formato-12b-de-de-inversiones",
    },
    {
        "name": "Estado situacional de inversiones",
        "slug": "estado-situacional-de-inversiones",
    },
    {
        "name": "Componentes de las inversiones",
        "slug": "proceso-de-seleccion-de-inversiones",
    },
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
    "estado-situacional-de-inversiones": {
        "csv": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/ESTADO_SITUACIONAL.csv",
        "dictionary": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/Estado_Situacional_Diccionario.csv",
    },
    "proceso-de-seleccion-de-inversiones": {
        "csv": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/PROCESO_SELECCION.csv",
        "dictionary": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/Proceso_Selecccion_Diccionario.csv",
    },
    "cierre-de-inversiones": {
        "csv": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/CIERRE_INVERSIONES.csv",
        "dictionary": "https://fs.datosabiertos.mef.gob.pe/datastorefiles/Cierre_Inversiones_Diccionario.csv",
    },
}


def _http_get(url: str, timeout: int = 60) -> bytes:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
    }
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read()
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        snippet = body[:200].strip().replace("\n", " ")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {snippet}") from exc
    except URLError as exc:
        raise RuntimeError(f"Network error for {url}: {exc.reason}") from exc


def _fetch_dataset(slug: str) -> dict:
    query = urlencode({"id": slug})
    raw = _http_get(f"{API_URL}?{query}")
    if not raw:
        raise RuntimeError(f"Empty response for dataset '{slug}'.")

    text = raw.decode("utf-8", errors="replace").strip()
    if text.startswith("<"):
        return _scrape_dataset(slug)

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        snippet = text[:200].replace("\n", " ")
        raise RuntimeError(
            f"Invalid JSON response for dataset '{slug}': {snippet}"
        ) from exc
    if not payload.get("success"):
        raise RuntimeError(f"API error for dataset '{slug}': {payload}")
    return payload["result"]


def _scrape_dataset(slug: str) -> dict:
    dataset_url = f"{BASE_URL}/dataset/{slug}"
    html = _http_get(f"{dataset_url}?format=json").decode("utf-8", errors="replace")
    if not html.strip().startswith("<"):
        html = _http_get(dataset_url).decode("utf-8", errors="replace")
    resources: list[dict] = []

    direct_pattern = r"https://fs\.datosabiertos\.mef\.gob\.pe/[^\s\"'>]+"
    direct_urls = sorted(set(re.findall(direct_pattern, html)))
    for download_url in direct_urls:
        name = Path(urlparse(download_url).path).name or download_url
        fmt = (Path(urlparse(download_url).path).suffix or "").lstrip(".")
        resources.append(
            {
                "name": name,
                "url": download_url,
                "format": fmt,
                "resource_url": dataset_url,
            }
        )

    if not resources:
        pattern = (
            rf"{re.escape(BASE_URL)}/dataset/{re.escape(slug)}/resource/[a-f0-9-]+"
        )
        resource_urls = sorted(set(re.findall(pattern, html)))
        for resource_url in resource_urls:
            resource = _scrape_resource(resource_url)
            if resource:
                resources.append(resource)

    if not resources:
        raise RuntimeError(
            "Unable to find resources in dataset page. "
            f"Open {dataset_url} to confirm availability."
        )

    return {"resources": resources, "source": dataset_url}


def _scrape_resource(resource_url: str) -> dict | None:
    html = _http_get(resource_url).decode("utf-8", errors="replace")
    download_urls = re.findall(
        r"https://fs\.datosabiertos\.mef\.gob\.pe/[^\s\"'>]+", html
    )
    if not download_urls:
        return None

    title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else Path(resource_url).name
    download_url = download_urls[0]
    fmt = (Path(urlparse(download_url).path).suffix or "").lstrip(".")

    return {
        "name": title,
        "url": download_url,
        "format": fmt,
        "resource_url": resource_url,
    }


def _size_key(resource: dict) -> int:
    size = resource.get("size")
    return size if isinstance(size, int) else 0


def _is_csv(resource: dict) -> bool:
    fmt = (resource.get("format") or "").lower()
    url = (resource.get("url") or "").lower()
    return fmt == "csv" or url.endswith(".csv")


def _pick_best(resources: list[dict], predicate) -> dict | None:
    matches = [resource for resource in resources if predicate(resource)]
    if not matches:
        return None
    return sorted(matches, key=_size_key, reverse=True)[0]


def _pick_dictionary(resources: list[dict]) -> dict | None:
    matches = []
    for resource in resources:
        text = f"{resource.get('name', '')} {resource.get('description', '')}".lower()
        if "diccionario" in text or "dictionary" in text:
            matches.append(resource)
    if not matches:
        return None
    return sorted(matches, key=_size_key, reverse=True)[0]


def _guess_extension(resource: dict) -> str:
    url = resource.get("url") or ""
    suffix = Path(urlparse(url).path).suffix
    if suffix:
        return suffix
    fmt = (resource.get("format") or "").lower()
    return {
        "csv": ".csv",
        "xlsx": ".xlsx",
        "xls": ".xls",
        "pdf": ".pdf",
        "docx": ".docx",
        "zip": ".zip",
    }.get(fmt, "")


def _download_to(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=120) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def download_dataset(dataset: dict, output_root: Path) -> dict:
    slug = dataset["slug"]
    name = dataset["name"]
    repo_root = Path(__file__).resolve().parents[1]
    used_fallback = False
    try:
        result = _fetch_dataset(slug)
        resources = result.get("resources", [])
    except RuntimeError:
        resources = []
        fallback = STATIC_RESOURCES.get(slug)
        if fallback:
            used_fallback = True
            resources = [
                {
                    "name": "data",
                    "url": fallback["csv"],
                    "format": "csv",
                },
                {
                    "name": "dictionary",
                    "url": fallback["dictionary"],
                    "format": "csv",
                },
            ]
        else:
            raise

    csv_resource = _pick_best(resources, _is_csv)
    dict_resource = _pick_dictionary(resources)

    dataset_dir = output_root / slug
    dataset_dir.mkdir(parents=True, exist_ok=True)

    csv_path = None
    if csv_resource and csv_resource.get("url"):
        csv_ext = _guess_extension(csv_resource) or ".csv"
        csv_path = dataset_dir / f"data{csv_ext}"
        _download_to(csv_resource["url"], csv_path)

    dict_path = None
    if dict_resource and dict_resource.get("url"):
        dict_ext = _guess_extension(dict_resource)
        dict_path = dataset_dir / f"dictionary{dict_ext}"
        _download_to(dict_resource["url"], dict_path)

    csv_rel = None
    if csv_path:
        try:
            csv_rel = csv_path.relative_to(repo_root).as_posix()
        except ValueError:
            csv_rel = csv_path.name

    dict_rel = None
    if dict_path:
        try:
            dict_rel = dict_path.relative_to(repo_root).as_posix()
        except ValueError:
            dict_rel = dict_path.name

    metadata = {
        "dataset": name,
        "slug": slug,
        "source": f"{BASE_URL}/dataset/{slug}",
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "used_fallback": used_fallback,
        "resources": {
            "csv": csv_resource,
            "dictionary": dict_resource,
        },
        "files": {
            "csv": csv_rel,
            "dictionary": dict_rel,
        },
    }

    with (dataset_dir / "metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, ensure_ascii=True, indent=2)

    return metadata


def download_all(output_root: Path | None = None) -> list[dict]:
    if output_root is None:
        repo_root = Path(__file__).resolve().parents[1]
        output_root = repo_root / "data" / "raw"

    output_root.mkdir(parents=True, exist_ok=True)
    results = []
    for dataset in DATASETS:
        results.append(download_dataset(dataset, output_root))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download MEF public investment datasets and dictionaries."
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output directory (default: data/raw under repo root)",
    )
    args = parser.parse_args()

    output_root = Path(args.output).expanduser().resolve() if args.output else None
    results = download_all(output_root)
    for item in results:
        dataset = item["dataset"]
        csv_path = item["files"]["csv"] or "missing"
        dict_path = item["files"]["dictionary"] or "missing"
        print(f"{dataset}: csv={csv_path} dictionary={dict_path}")


if __name__ == "__main__":
    main()
