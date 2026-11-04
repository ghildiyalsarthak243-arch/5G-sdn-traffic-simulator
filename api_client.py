"""Hugging Face Dataset Viewer API client for CIC-IDS-2017 flow records."""
from __future__ import annotations

import ipaddress
import math
from typing import Any

import requests

from packet import Packet

DATASET_ID = "transformer112/cicids2017-ids-dataset"
DATASET_CONFIG = "default"
DATASET_SPLIT = "train"
API_URL = "https://datasets-server.huggingface.co/rows"
DATASET_URL = f"https://huggingface.co/datasets/{DATASET_ID}"


class APIClientError(RuntimeError):
    """A clear, user-facing API or data-format problem."""


def _normalise(row: dict[str, Any]) -> dict[str, Any]:
    return {str(key).strip().lower(): value for key, value in row.items()}


def _value(row: dict[str, Any], *names: str, default=None):
    values = _normalise(row)
    for name in names:
        key = name.strip().lower()
        if key in values:
            return values[key]
    return default


def _as_float(value, default=0.0) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def _as_int(value, default=0) -> int:
    return int(_as_float(value, default))


def _ipv4(value) -> str | None:
    try:
        return str(ipaddress.IPv4Address(str(value).strip()))
    except (ipaddress.AddressValueError, TypeError, ValueError):
        return None


def flow_record_to_packet(row: dict[str, Any], row_index: int, arrival_order: int) -> Packet | None:
    """Convert one API flow row; return None if source/destination IPv4 are absent/invalid."""
    source_ip = _ipv4(_value(row, "Source IP", "Src IP", "source_ip"))
    destination_ip = _ipv4(_value(row, "Destination IP", "Dst IP", "destination_ip"))
    if source_ip is None or destination_ip is None:
        return None

    label = str(_value(row, "Label", "label", default="Unknown")).strip()
    if not label or label.lower() in {"nan", "none", "null"}:
        label = "Unknown"

    return Packet(
        packet_id=f"API-{int(row_index) + 1:06d}",
        source_ip=source_ip,
        destination_ip=destination_ip,
        dataset_label=label,
        destination_port=max(0, _as_int(_value(row, "Destination Port", "Dst Port"))),
        flow_duration=max(0.0, _as_float(_value(row, "Flow Duration"))),
        total_fwd_packets=max(0, _as_int(_value(row, "Total Fwd Packets"))),
        total_backward_packets=max(0, _as_int(_value(row, "Total Backward Packets"))),
        packet_length_mean=max(0.0, _as_float(_value(row, "Packet Length Mean", "Fwd Packet Length Mean", "Average Packet Size"))),
        flow_packets_per_second=max(0.0, _as_float(_value(row, "Flow Packets/s"))),
        arrival_order=int(arrival_order),
    )


def fetch_flow_records(offset: int = 0, length: int = 25, timeout: int = 30):
    """Fetch a page from the public API. Returns (packets, total_rows, raw_rows_count)."""
    if offset < 0:
        raise ValueError("Offset cannot be negative.")
    if not 1 <= length <= 100:
        raise ValueError("Choose between 1 and 100 records per API request.")

    params = {
        "dataset": DATASET_ID,
        "config": DATASET_CONFIG,
        "split": DATASET_SPLIT,
        "offset": offset,
        "length": length,
    }
    headers = {"User-Agent": "5G-Network-Traffic-Simulator/1.0"}
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except requests.Timeout as exc:
        raise APIClientError("The dataset API timed out. Check your internet connection and try again.") from exc
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        detail = "The dataset may be temporarily unavailable or its API configuration may have changed."
        raise APIClientError(f"Dataset API returned HTTP {status}. {detail}") from exc
    except requests.RequestException as exc:
        raise APIClientError(f"Could not connect to the dataset API: {exc}") from exc
    except ValueError as exc:
        raise APIClientError("The dataset API returned invalid JSON.") from exc

    rows = payload.get("rows")
    if not isinstance(rows, list):
        detail = payload.get("error") or payload.get("message") or "No rows array was returned."
        raise APIClientError(f"Unexpected dataset API response: {detail}")

    total_rows = int(payload.get("num_rows_total") or 0)
    packets = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        row = item.get("row", {})
        if not isinstance(row, dict):
            continue
        row_index = item.get("row_idx", offset + len(packets))
        packet = flow_record_to_packet(row, row_index, offset + len(packets) + 1)
        if packet is not None:
            packets.append(packet)

    if rows and not packets:
        raise APIClientError(
            "API rows were returned, but none contained valid Source IP and Destination IP IPv4 fields."
        )
    return packets, total_rows, len(rows)
