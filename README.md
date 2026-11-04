# 5G Network Traffic Simulator — API Edition

A Python + Streamlit educational simulation that fetches **historical network-flow records** from a public REST API and processes them through a Trie, circular ring buffer, least-loaded server assignment, and Min-Heap scheduler.

## Important: what the API returns

This project uses the Hugging Face Dataset Viewer REST API to fetch CIC-IDS-2017 flow rows. These rows are **aggregated network-flow records**, not live individual packets or raw PCAP frames. The app wraps each record in a `Packet` object as a work item for the data-structure demonstration. It preserves the dataset's original `Label` separately from the simulated Trie traffic class.

- Dataset: `transformer112/cicids2017-ids-dataset`
- Configuration: `default`
- Split: `train`
- API: `https://datasets-server.huggingface.co/rows`
- Dataset page: https://huggingface.co/datasets/transformer112/cicids2017-ids-dataset

## Modules

| File | Responsibility |
|---|---|
| `app.py` | Windows 95-inspired Streamlit dashboard |
| `packet.py` | Packet/flow work-item model |
| `api_client.py` | Calls REST API and converts dataset rows |
| `trie.py` | Binary IPv4 Trie with longest-prefix matching |
| `ringbuffer.py` | 10-entry FIFO circular buffer |
| `load_balancer.py` | Least-loaded simulated server assignment |
| `qos_scheduler.py` | Min-Heap priority scheduler |
| `simulation.py` | Connects ingestion and processing stages |

## Run on Windows

From PowerShell in the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Demo workflow

1. Click **Fetch records from API**. Choose 5–100 records per request.
2. Inspect the API records, Trie class, 10-slot ring buffer and overflow backlog.
3. Click **Dispatch buffer + backlog** to assign records to servers and add them to the QoS Min-Heap.
4. Click **Process next record** or **Process all pending**.
5. Fetch another page to continue from the next API offset.

The ring buffer remains fixed at 10 entries. Additional API rows are retained in a separate FIFO backlog rather than discarded.

## Trie rule note

The sample prefix rules in `trie.py` are illustrative classroom mappings, not official standardized 5G slice definitions. Change them to match an IP-to-class mapping specified by your instructor. The dataset's original label is always kept in `Original Dataset Label`.

## Data source references

- Dataset page: https://huggingface.co/datasets/transformer112/cicids2017-ids-dataset
- Dataset Viewer `/rows` documentation: https://huggingface.co/docs/dataset-viewer/rows
- Dataset Viewer REST API quickstart: https://huggingface.co/docs/dataset-viewer/en/quick_start

## Academic note

CIC-IDS-2017 was published by Iman Sharafaldin, Arash Habibi Lashkari, and Ali A. Ghorbani, “Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization,” ICISSP, 2018. Cite the dataset and its paper according to your institution's required citation style.

This application is an educational software simulation. It does not capture or transmit live network traffic, implement real 5G network slices, or perform actual network routing.
