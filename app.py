import pandas as pd
import plotly.express as px
import streamlit as st

from api_client import DATASET_ID, DATASET_URL
from simulation import NetworkSimulation

st.set_page_config(page_title="5G Network Traffic Simulator", page_icon="📡", layout="wide")

# Windows 95-inspired UI. Simulation/data logic stays in separate modules.
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] { background:#008080 !important; color:#111 !important; font-family:Tahoma,Arial,sans-serif !important; }
[data-testid="stHeader"] { background:#008080 !important; }
.block-container { max-width:1500px; padding-top:1rem; padding-bottom:2rem; }
[data-testid="stSidebar"] { background:#c0c0c0 !important; border-right:2px solid #fff; }
[data-testid="stSidebar"] * { color:#111 !important; }
.win-title { background:#000080; color:#fff; padding:8px 12px; font-weight:bold; border:2px solid; border-color:#fff #404040 #404040 #fff; margin-bottom:0; }
.win-panel { background:#c0c0c0; color:#111; padding:12px; border:2px solid; border-color:#fff #404040 #404040 #fff; margin-bottom:12px; }
.win-caption { color:#222; font-size:12px; margin-top:5px; }
div.stButton > button, div.stDownloadButton > button { background:#c0c0c0 !important; color:#111 !important; border:2px solid !important; border-color:#fff #404040 #404040 #fff !important; border-radius:0 !important; box-shadow:1px 1px 0 #000 !important; font-family:Tahoma,Arial,sans-serif !important; font-weight:600 !important; }
div.stButton > button:active { border-color:#404040 #fff #fff #404040 !important; box-shadow:none !important; }
[data-testid="stMetric"] { background:#c0c0c0; padding:10px; border:2px solid; border-color:#fff #404040 #404040 #fff; }
[data-testid="stMetric"] label, [data-testid="stMetric"] div { color:#111 !important; }
.stTabs [data-baseweb="tab-list"] { gap:2px; background:#c0c0c0; padding:5px 5px 0; }
.stTabs [data-baseweb="tab"] { background:#c0c0c0; border:2px solid; border-color:#fff #404040 #404040 #fff; border-radius:0; color:#111 !important; padding:5px 12px; }
.stTabs [aria-selected="true"] { background:#fff !important; }
[data-testid="stDataFrame"] { background:#fff; border:2px inset #aaa; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

if "simulation" not in st.session_state:
    st.session_state.simulation = NetworkSimulation()
sim = st.session_state.simulation

st.markdown('<div class="win-title">📡 5G Network Traffic Simulator — API Edition</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="win-panel"><b>Network Operations Center</b><br>'
    'Dataset API → IPv4 Trie → Circular Ring Buffer → Load Balancer → QoS Min-Heap'
    '<div class="win-caption">Historical network-flow records are imported from an external API. This is a software simulation, not live 5G traffic.</div></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="win-title">Control Panel</div>', unsafe_allow_html=True)
    st.markdown('<div class="win-panel"><b>External data source</b><br>Hugging Face Dataset Viewer API</div>', unsafe_allow_html=True)
    page_size = st.select_slider("Records per API request", options=[5, 10, 20, 25, 50, 75, 100], value=25)
    if st.button("↓ Fetch records from API", use_container_width=True):
        with st.spinner("Contacting dataset API..."):
            try:
                result = sim.fetch_from_api(page_size)
                st.session_state.notice = (
                    f"Imported {result['imported']} valid flow record(s). "
                    f"{result['buffered']} buffered; {result['backlogged']} in backlog."
                )
                st.session_state.notice_kind = "success"
            except Exception as exc:
                st.session_state.notice = str(exc)
                st.session_state.notice_kind = "error"
        st.rerun()

    if st.button("⇄ Dispatch buffer + backlog", use_container_width=True):
        moved = sim.dispatch()
        st.session_state.notice = f"Dispatched {moved} record(s) into the QoS Min-Heap."
        st.session_state.notice_kind = "success"
        st.rerun()

    if st.button("▶ Process next record", use_container_width=True):
        packet = sim.process_next()
        st.session_state.notice = f"Processed {packet.packet_id}." if packet else "No records available to process."
        st.session_state.notice_kind = "info"
        st.rerun()

    if st.button("▶▶ Process all pending", use_container_width=True):
        completed = sim.process_all()
        st.session_state.notice = f"Processed {len(completed)} pending record(s)."
        st.session_state.notice_kind = "success"
        st.rerun()

    if st.button("↻ Reset session", use_container_width=True):
        sim.reset()
        st.session_state.notice = "Simulation reset. API paging returned to row zero."
        st.session_state.notice_kind = "info"
        st.rerun()

    st.divider()
    st.markdown("**API paging status**")
    st.caption(f"Next row offset: {sim.api_offset:,}")
    if sim.api_total_rows:
        st.caption(f"Dataset Viewer rows: {sim.api_total_rows:,}")
    if not sim.has_more_api_rows:
        st.success("End of available dataset rows reached.")

if st.session_state.get("notice"):
    kind = st.session_state.get("notice_kind", "info")
    if kind == "error":
        st.error(st.session_state.notice)
    elif kind == "success":
        st.success(st.session_state.notice)
    else:
        st.info(st.session_state.notice)

total, buffered, backlog, queued, processed = len(sim.packets), len(sim.buffer), len(sim.backlog), len(sim.scheduler), len(sim.processed)
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Imported records", total)
m2.metric("Ring buffer", f"{buffered}/10")
m3.metric("Backlog", backlog)
m4.metric("QoS Min-Heap", queued)
m5.metric("Processed", processed)

left, right = st.columns([1.15, 1])
with left:
    st.markdown('<div class="win-title">Traffic Classes (Trie)</div>', unsafe_allow_html=True)
    if sim.packets:
        frame = pd.DataFrame(sim.packet_rows())
        counts = frame["Traffic Class (Trie)"].value_counts().rename_axis("Traffic Class").reset_index(name="Records")
        fig = px.bar(counts, x="Traffic Class", y="Records", color="Traffic Class", color_discrete_map={"Emergency":"#c00000", "High Data":"#e87500", "Smart Devices":"#b49a00", "Normal":"#16833c"})
        fig.update_layout(template="plotly_white", paper_bgcolor="#c0c0c0", plot_bgcolor="#fff", margin=dict(l=10,r=10,t=15,b=10), showlegend=False, font=dict(family="Tahoma",color="#111"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Fetch records from the API to populate the chart.")
with right:
    st.markdown('<div class="win-title">Pending Server Workload</div>', unsafe_allow_html=True)
    server_frame = pd.DataFrame([{"Server": name, "Pending Records": count} for name, count in sim.load_balancer.server_loads.items()])
    fig = px.bar(server_frame, x="Server", y="Pending Records", color="Server", color_discrete_sequence=["#000080", "#008080", "#808000"])
    fig.update_layout(template="plotly_white", paper_bgcolor="#c0c0c0", plot_bgcolor="#fff", margin=dict(l=10,r=10,t=15,b=10), showlegend=False, font=dict(family="Tahoma",color="#111"))
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="win-title">Flow Record Processing Workspace</div>', unsafe_allow_html=True)
tab_all, tab_buffer, tab_backlog, tab_heap, tab_log, tab_source = st.tabs(["All Records", "Ring Buffer", "Backlog", "QoS Min-Heap", "Activity Log", "API Source"])
with tab_all:
    if sim.packets:
        st.dataframe(pd.DataFrame(sim.packet_rows()), use_container_width=True, hide_index=True)
    else:
        st.info("No records imported yet. Use Fetch records from API.")
with tab_buffer:
    st.caption(f"Fixed-capacity FIFO circular buffer: {buffered}/{sim.buffer.capacity} entries.")
    items = sim.waiting_packets()
    st.dataframe(pd.DataFrame([p.to_dict() for p in items]), use_container_width=True, hide_index=True) if items else st.info("Ring buffer is empty.")
with tab_backlog:
    st.caption("Overflow records are retained in a separate FIFO backlog; they are not dropped when the 10-slot ring buffer is full.")
    items = sim.backlog_packets()
    st.dataframe(pd.DataFrame([p.to_dict() for p in items]), use_container_width=True, hide_index=True) if items else st.info("Backlog is empty.")
with tab_heap:
    st.caption("Min-Heap: priority 1 is processed first; arrival order breaks ties.")
    items = sim.queued_packets()
    st.dataframe(pd.DataFrame([p.to_dict() for p in items]), use_container_width=True, hide_index=True) if items else st.info("QoS heap is empty. Dispatch records to populate it.")
with tab_log:
    for line in sim.activity[:40]:
        st.markdown(f"- {line}")
with tab_source:
    st.markdown(f"**Dataset:** [{DATASET_ID}]({DATASET_URL})")
    st.markdown("**REST endpoint:** `https://datasets-server.huggingface.co/rows`")
    st.markdown("**Configuration / split:** `default` / `train`")
    st.markdown("The API returns historical flow-level feature rows. Source IP, Destination IP, Destination Port, flow measurements and the original Label are retained. Each row is represented as a Packet work item for the data-structure demonstration; it is not reconstructed as an individual live packet.")
    st.markdown("Trie categories are illustrative IP-prefix rules in `trie.py`, not official 5G slice assignments. The original dataset label is preserved separately.")
    st.markdown("The Dataset Viewer `/rows` API supports pages of up to 100 rows. The app advances the offset after each successful fetch.")

st.markdown('<div class="win-panel"><b>Status:</b> API-backed historical flow-record simulator. No live packet capture, injection, or real 5G routing is performed.</div>', unsafe_allow_html=True)
