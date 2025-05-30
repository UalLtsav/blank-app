import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from geopy.distance import geodesic

# Session state for pair data
if 'data' not in st.session_state:
    st.session_state.data = [
        {"pair_id": "P1", "donor_bg": "A", "recipient_bg": "B", "hla_match": 3, "urgency": 2},
        {"pair_id": "P2", "donor_bg": "B", "recipient_bg": "A", "hla_match": 4, "urgency": 3},
        {"pair_id": "P3", "donor_bg": "O", "recipient_bg": "A", "hla_match": 5, "urgency": 1},
        {"pair_id": "P4", "donor_bg": "A", "recipient_bg": "O", "hla_match": 2, "urgency": 2},
        {"pair_id": "P5", "donor_bg": "B", "recipient_bg": "AB", "hla_match": 3, "urgency": 1},
        {"pair_id": "P6", "donor_bg": "AB", "recipient_bg": "O", "hla_match": 1, "urgency": 3},
        {"pair_id": "P7", "donor_bg": "O", "recipient_bg": "B", "hla_match": 4, "urgency": 2}
    ]

compatibility = {
    "O": ["O", "A", "B", "AB"],
    "A": ["A", "AB"],
    "B": ["B", "AB"],
    "AB": ["AB"]
}

st.title("Kidney Matching Demo")
st.markdown("Prototype built with match scoring and graph-based cycles.")

# Form
with st.form("add_pair"):
    pair_id = st.text_input("Pair ID", value=f"P{len(st.session_state.data)+1}")
    donor_bg = st.selectbox("Donor Blood Group", ["O", "A", "B", "AB"])
    recipient_bg = st.selectbox("Recipient Blood Group", ["O", "A", "B", "AB"])
    hla_match = st.slider("HLA Match Score (1-5)", 1, 5, 3)
    urgency = st.slider("Urgency Score (1-3)", 1, 3, 2)
    submit = st.form_submit_button("Add Pair")
    if submit:
        st.session_state.data.append({
            "pair_id": pair_id,
            "donor_bg": donor_bg,
            "recipient_bg": recipient_bg,
            "hla_match": hla_match,
            "urgency": urgency
        })
        st.success(f"Added pair {pair_id}.")

# Table
df = pd.DataFrame(st.session_state.data)
st.subheader("🔍 Current Pairs")
st.dataframe(df)

# Graph
G = nx.DiGraph()
for row in st.session_state.data:
    G.add_node(row["pair_id"], **row)

for i in range(len(st.session_state.data)):
    for j in range(len(st.session_state.data)):
        if i != j:
            src = st.session_state.data[i]
            tgt = st.session_state.data[j]
            if src["donor_bg"] in compatibility[tgt["recipient_bg"]]:
                score = tgt["hla_match"] + tgt["urgency"]
                G.add_edge(src["pair_id"], tgt["pair_id"], score=score)

# Find cycles
def find_cycles(graph, max_length=3):
    cycles = []
    for cycle in nx.simple_cycles(graph):
        if 2 <= len(cycle) <= max_length:
            total_score = sum(graph.edges[cycle[i], cycle[(i+1)%len(cycle)]]['score']
                              for i in range(len(cycle)))
            cycles.append((cycle, total_score))
    return sorted(cycles, key=lambda x: -x[1])

match_chains = find_cycles(G)

st.subheader("✅ Suggested Match Chains")
if match_chains:
    for cycle, score in match_chains:
        st.markdown(f"**{' → '.join(cycle)} → {cycle[0]}** | Score: {score}")
else:
    st.info("No match chains found.")

# Graph viz
st.subheader("📊 Compatibility Graph")
fig, ax = plt.subplots(figsize=(8, 6))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, ax=ax)
edge_labels = nx.get_edge_attributes(G, 'score')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='green', ax=ax)
st.pyplot(fig)



