# 5G Network Traffic Simulator (Windows 95 UI)

Educational Python/Streamlit project demonstrating:
- IPv4 longest-prefix matching using a bitwise Trie
- A capacity-10 FIFO circular ring buffer
- A FIFO backlog that preserves any extra packets and refills the ring buffer as slots free up
- Least-loaded assignment across three simulated servers
- Min-Heap QoS scheduling (priority 1 is highest)
- A retro Windows 95-inspired Streamlit dashboard

## Run on Windows PowerShell

```powershell
cd "D:\ouu shi\5g_sdn"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If your project folder uses a different path, change the `cd` command to that path.

## Demo workflow
1. Generate up to 50 packets at a time. The first 10 fit in the ring buffer; remaining packets are retained in the backlog.
2. Dispatch buffer to servers. A batch is assigned to servers and put into the Min-Heap; the buffer is then refilled from the backlog.
3. Repeat dispatch, or use **Process all pending** to dispatch every batch before processing all packets in global priority order.
4. Inspect All Packets, Ring Buffer, Backlog, QoS Heap, server workload and activity log.

This is a software simulation only. It does not capture or transmit real network traffic or implement an actual 5G core network.
