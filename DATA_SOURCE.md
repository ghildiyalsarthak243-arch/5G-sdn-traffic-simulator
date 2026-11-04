# API data source

The app fetches pages from Hugging Face Dataset Viewer `/rows`:

`https://datasets-server.huggingface.co/rows`

Query parameters: `dataset=transformer112/cicids2017-ids-dataset`, `config=default`, `split=train`, `offset=<row offset>`, and `length=<1..100>`.

The selected Dataset Viewer schema includes `Destination Port`, `Flow Duration`, `Total Fwd Packets`, `Total Backward Packets`, `Packet Length Mean`, `Flow Packets/s`, `Label`, `Source IP`, and `Destination IP`. The API client also tolerates some alternate column names and skips rows without valid IPv4 source and destination addresses.

**Interpretation:** CIC-IDS-2017 rows are flow-level records. They aggregate characteristics of network flows; they are not individual real-time packets. The app uses `Packet` as an internal processing-object name only. The original dataset label is not changed by Trie classification.

Dataset: https://huggingface.co/datasets/transformer112/cicids2017-ids-dataset
API docs: https://huggingface.co/docs/dataset-viewer/rows
