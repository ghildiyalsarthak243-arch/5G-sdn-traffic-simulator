import pandas as pd
import plotly.express as px
import streamlit as st

from simulation import NetworkSimulation

st.set_page_config(
    page_title="5G Network Traffic Simulator",
    page_icon="🖥️",
    layout="wide",
)

# Windows 95-inspired styling. Simulation logic stays in simulation.py and its modules.
st.markdown(
    """
    <style>
    :root {
        --win-gray: #c0c0c0;
        --win-light: #ffffff;
        --win-mid: #dfdfdf;
        --win-dark: #808080;
        --win-black: #000000;
        --win-blue: #000080;
        --win-teal: #008080;
    }

    html, body, [class*="css"] {
        font-family: Tahoma, "MS Sans Serif", Arial, sans-serif !important;
        color: #000 !important;
    }
    .stApp {
        background: var(--win-teal) !important;
        color: #000 !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    div[data-testid="stToolbar"] { visibility: hidden; height: 0; }
    div[data-testid="stMainBlockContainer"] {
        background: var(--win-gray) !important;
        max-width: 1440px !important;
        margin: 18px auto 42px auto !important;
        padding: 0.8rem 1rem 1.2rem 1rem !important;
        border-top: 2px solid var(--win-light);
        border-left: 2px solid var(--win-light);
        border-right: 2px solid #404040;
        border-bottom: 2px solid #404040;
        box-shadow: 1px 1px 0 #000;
    }

    /* Faux application title bar and menu strip */
    .win-titlebar {
        background: var(--win-blue);
        color: #fff !important;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4px 5px 4px 8px;
        min-height: 28px;
        font-weight: bold;
        font-size: 14px;
        margin: -2px -2px 0 -2px;
    }
    .win-title-left { display: flex; align-items: center; gap: 7px; }
    .win-app-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        background: #c0c0c0;
        color: #000080;
        border-top: 1px solid #fff;
        border-left: 1px solid #fff;
        border-right: 1px solid #404040;
        border-bottom: 1px solid #404040;
        font-size: 12px;
    }
    .win-controls { display: flex; gap: 3px; }
    .win-control {
        width: 18px;
        height: 17px;
        line-height: 14px;
        text-align: center;
        color: #000 !important;
        background: #c0c0c0;
        border-top: 2px solid #fff;
        border-left: 2px solid #fff;
        border-right: 2px solid #404040;
        border-bottom: 2px solid #404040;
        font-family: Arial, sans-serif;
        font-weight: bold;
    }
    .win-menubar {
        background: var(--win-gray);
        padding: 6px 4px 8px 4px;
        color: #000;
        border-bottom: 1px solid #808080;
        font-size: 13px;
        word-spacing: 13px;
    }
    .win-subheading { padding: 10px 4px 3px 4px; }
    .win-subheading h1 {
        color: #000 !important;
        font-family: Tahoma, Arial, sans-serif !important;
        font-size: 24px !important;
        font-weight: bold !important;
        margin: 0 0 3px 0 !important;
    }
    .win-subheading p { color: #222 !important; margin: 0 0 8px 0; font-size: 13px; }

    /* Classic raised/recessed controls */
    [data-testid="stSidebar"] {
        background: var(--win-gray) !important;
        border-right: 2px solid #808080;
    }
    [data-testid="stSidebar"] > div:first-child { background: var(--win-gray) !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label { color: #000 !important; }

    div.stButton > button, div[data-testid="stDownloadButton"] > button {
        background: #c0c0c0 !important;
        color: #000 !important;
        border-radius: 0 !important;
        border-top: 2px solid #fff !important;
        border-left: 2px solid #fff !important;
        border-right: 2px solid #404040 !important;
        border-bottom: 2px solid #404040 !important;
        box-shadow: inset 1px 1px #dfdfdf, inset -1px -1px #808080 !important;
        font-weight: normal !important;
        min-height: 34px;
    }
    div.stButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {
        color: #000 !important;
        border-top-color: #fff !important;
        border-left-color: #fff !important;
        background: #d4d4d4 !important;
    }
    div.stButton > button:active {
        border-top: 2px solid #404040 !important;
        border-left: 2px solid #404040 !important;
        border-right: 2px solid #fff !important;
        border-bottom: 2px solid #fff !important;
        box-shadow: inset 1px 1px #808080 !important;
    }
    div[data-testid="stMetric"] {
        background: #c0c0c0 !important;
        border-radius: 0 !important;
        padding: 10px 12px !important;
        border-top: 2px solid #808080;
        border-left: 2px solid #808080;
        border-right: 2px solid #fff;
        border-bottom: 2px solid #fff;
        box-shadow: inset 1px 1px #404040;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p,
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] div,
    [data-testid="stMetricDelta"] { color: #000 !important; }
    [data-testid="stMetricValue"] { font-family: Tahoma, Arial, sans-serif !important; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background: transparent;
        border-bottom: 2px solid #808080;
    }
    .stTabs [data-baseweb="tab"] {
        background: #c0c0c0 !important;
        color: #000 !important;
        border-radius: 0 !important;
        border-top: 2px solid #fff !important;
        border-left: 2px solid #fff !important;
        border-right: 2px solid #808080 !important;
        padding: 6px 12px !important;
    }
    .stTabs [aria-selected="true"] {
        background: #dfdfdf !important;
        color: #000 !important;
        font-weight: bold !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { background: #000080 !important; }
    .stTabs [data-baseweb="tab-border"] { background: #808080 !important; }

    input, textarea, [data-baseweb="select"] > div {
        color: #000 !important;
        background: #fff !important;
        border-radius: 0 !important;
        border-top: 2px solid #404040 !important;
        border-left: 2px solid #404040 !important;
        border-right: 2px solid #fff !important;
        border-bottom: 2px solid #fff !important;
    }
    div[data-testid="stDataFrame"] {
        background: #fff !important;
        border-top: 2px solid #808080;
        border-left: 2px solid #808080;
        border-right: 2px solid #fff;
        border-bottom: 2px solid #fff;
    }
    div[data-testid="stAlert"] {
        background: #ffffe1 !important;
        color: #000 !important;
        border-radius: 0 !important;
        border: 1px solid #808080 !important;
    }
    div[data-testid="stAlert"] p, div[data-testid="stAlert"] svg { color: #000 !important; }
    h1, h2, h3, h4, p, label, .stCaption, [data-testid="stMarkdownContainer"] {
        color: #000;
    }
    h2, h3 { font-family: Tahoma, Arial, sans-serif !important; font-weight: bold !important; }
    hr { border-color: #808080 !important; }
    .win-statusbar {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        color: #000;
        font-size: 12px;
        margin-top: 16px;
        padding: 5px 7px;
        background: #c0c0c0;
        border-top: 1px solid #808080;
        border-left: 1px solid #808080;
        border-right: 1px solid #fff;
        border-bottom: 1px solid #fff;
    }
    @media (max-width: 700px) {
        div[data-testid="stMainBlockContainer"] { margin: 5px !important; padding: 8px !important; }
        .win-subheading h1 { font-size: 20px !important; }
        .win-menubar { word-spacing: 5px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if ("simulation" not in st.session_state
        or not hasattr(st.session_state.simulation, "backlog")):
    st.session_state.simulation = NetworkSimulation()
sim = st.session_state.simulation

st.markdown(
    """
    <div class="win-titlebar">
      <div class="win-title-left"><span class="win-app-icon">5G</span><span>5G Network Traffic Simulator</span></div>
      <div class="win-controls"><span class="win-control">_</span><span class="win-control">□</span><span class="win-control">×</span></div>
    </div>
    <div class="win-menubar">File Edit View Simulation Help</div>
    <div class="win-subheading">
      <h1>5G Network Traffic Simulator</h1>
      <p>Packet classification · Circular buffering · Load balancing · QoS scheduling</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Educational simulation only — no real 5G network is connected and no real packets are transmitted.")

with st.sidebar:
    st.markdown("### Simulation Controls")
    packet_count = st.slider("Packets to generate", min_value=1, max_value=50, value=5)
    if st.button("Generate packets", use_container_width=True):
        accepted, rejected = sim.generate(packet_count)
        st.session_state.last_message = (
            f"Generated {packet_count} packet(s): {accepted} currently in the ring buffer; "
            f"{rejected} safely waiting in the backlog. The buffer refills after dispatch."
        )
        st.rerun()
    if st.button("Dispatch buffer to servers", use_container_width=True):
        moved = sim.dispatch()
        st.session_state.last_message = f"Dispatched {moved} packet(s) to the QoS scheduler."
        st.rerun()
    if st.button("Process next packet", use_container_width=True):
        packet = sim.process_next()
        st.session_state.last_message = (
            f"Processed {packet.packet_id} ({packet.traffic_type})."
            if packet else "No packets in the QoS scheduler."
        )
        st.rerun()
    if st.button("Process all pending", use_container_width=True):
        dispatched, done = sim.process_all_pending()
        st.session_state.last_message = (
            f"Dispatched {dispatched} packet(s) from the buffer/backlog and "
            f"processed {len(done)} packet(s) by priority."
        )
        st.rerun()
    if st.button("Reset simulation", use_container_width=True):
        sim.reset()
        st.session_state.last_message = "Simulation reset."
        st.rerun()
    st.divider()
    st.markdown("**Processing pipeline**")
    st.caption("Generate → Trie → Ring Buffer → Load Balancer → Min-Heap → Process")

if st.session_state.get("last_message"):
    st.info(st.session_state.last_message)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total packets", len(sim.packets))
m2.metric("In ring buffer", len(sim.buffer), f"Capacity {sim.buffer.capacity}")
m3.metric("Backlog", len(sim.backlog))
m4.metric("In QoS heap", len(sim.scheduler))
m5.metric("Processed", len(sim.processed))

left, right = st.columns([1.15, 1])
with left:
    st.subheader("Packet Traffic")
    if sim.packets:
        df = pd.DataFrame(sim.packet_rows())
        counts = df["Type"].value_counts().rename_axis("Traffic Type").reset_index(name="Packets")
        fig = px.bar(
            counts,
            x="Traffic Type",
            y="Packets",
            color="Traffic Type",
            color_discrete_map={
                "Emergency": "#ff0000",
                "High Data": "#ff8000",
                "Smart Devices": "#d6b600",
                "Normal": "#008000",
            },
        )
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="#c0c0c0",
            plot_bgcolor="#ffffff",
            font=dict(family="Tahoma, Arial, sans-serif", color="#000000", size=12),
            margin=dict(l=10, r=10, t=20, b=10),
            showlegend=False,
            xaxis=dict(showgrid=False, linecolor="#000000", mirror=True),
            yaxis=dict(gridcolor="#d0d0d0", linecolor="#000000", mirror=True),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Generate packets to populate the traffic chart.")

with right:
    st.subheader("Server Workload")
    loads = pd.DataFrame(
        [{"Server": name, "Pending Packets": load} for name, load in sim.load_balancer.server_loads.items()]
    )
    fig = px.bar(
        loads,
        x="Server",
        y="Pending Packets",
        color="Server",
        color_discrete_sequence=["#000080", "#008080", "#800080"],
    )
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#c0c0c0",
        plot_bgcolor="#ffffff",
        font=dict(family="Tahoma, Arial, sans-serif", color="#000000", size=12),
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False,
        xaxis=dict(showgrid=False, linecolor="#000000", mirror=True),
        yaxis=dict(gridcolor="#d0d0d0", linecolor="#000000", mirror=True),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
t1, t2, t3, t4, t5 = st.tabs(["All Packets", "Ring Buffer", "Backlog", "QoS Heap", "Activity Log"])
with t1:
    st.subheader("Packet Records")
    if sim.packets:
        st.dataframe(pd.DataFrame(sim.packet_rows()), use_container_width=True, hide_index=True)
    else:
        st.write("No packets yet. Use Generate packets in the sidebar.")
with t2:
    st.subheader(f"Circular Ring Buffer ({len(sim.buffer)}/{sim.buffer.capacity})")
    st.caption("FIFO storage with wrap-around indices. The ring buffer holds at most 10 packets; excess packets are preserved in the backlog and automatically fill slots after dispatch.")
    buffer_packets = sim.waiting_packets()
    if buffer_packets:
        st.dataframe(pd.DataFrame([packet.to_dict() for packet in buffer_packets]), use_container_width=True, hide_index=True)
    else:
        st.info("The ring buffer is empty.")
with t3:
    st.subheader(f"Incoming Backlog ({len(sim.backlog)})")
    st.caption("Packets beyond the fixed ring-buffer capacity are kept here in FIFO order. Dispatching a batch frees buffer slots and automatically moves the oldest backlog packets into the buffer.")
    backlog_packets = sim.backlog_packets()
    if backlog_packets:
        st.dataframe(pd.DataFrame([packet.to_dict() for packet in backlog_packets]), use_container_width=True, hide_index=True)
    else:
        st.info("No packets waiting in the backlog.")
with t4:
    st.subheader("Min-Heap Priority Queue")
    st.caption("Priority 1 is highest. Equal priorities are processed in arrival order. Use Process all pending to move every backlog batch into the heap before processing, so priority order is respected across all packets.")
    heap_packets = sim.queued_packets()
    if heap_packets:
        st.dataframe(pd.DataFrame([packet.to_dict() for packet in heap_packets]), use_container_width=True, hide_index=True)
    else:
        st.info("The QoS heap is empty. Dispatch buffered packets to populate it.")
with t5:
    st.subheader("Recent Activity")
    if sim.activity:
        for entry in sim.activity[:30]:
            st.markdown(f"- {entry}")
    else:
        st.info("No activity yet.")

st.markdown(
    '<div class="win-statusbar"><span>Ready</span><span>Simulation only · IPv4</span><span>Buffer: '
    + str(len(sim.buffer)) + '/' + str(sim.buffer.capacity) + '</span><span>Backlog: ' + str(len(sim.backlog)) + '</span></div>',
    unsafe_allow_html=True,
)
st.caption("Traffic categories are illustrative simulation labels, not guaranteed mappings to standardized 5G network slices.")
