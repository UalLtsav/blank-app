import streamlit as st
import pandas as pd
import networkx as nx
import random
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from web3 import Web3

# Connect to blockchain (Ganache or Infura)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))  # Replace with Infura if needed
account = w3.eth.accounts[0]

# Simulated patient-donor registry
if 'pairs' not in st.session_state:
    st.session_state.pairs = []

# Add patient-donor pair
st.sidebar.title("Add Patient-Donor Pair")
patient_name = st.sidebar.text_input("Patient Name")
donor_name = st.sidebar.text_input("Donor Name")
hla_score = st.sidebar.slider("Compatibility Score (0–100)", 0, 100, 50)
urgency = st.sidebar.selectbox("Urgency", ["Low", "Medium", "High"])

if st.sidebar.button("Add Pair"):
    st.session_state.pairs.append({
        'patient': patient_name,
        'donor': donor_name,
        'hla': hla_score,
        'urgency': urgency
    })

# 🧠 AI Matching (greedy + urgency-aware)
def match_pairs(pairs):
    G = nx.Graph()
    for i, p1 in enumerate(pairs):
        for j, p2 in enumerate(pairs):
            if i != j:
                score = (p1['hla'] + p2['hla']) / 2
                if score > 50:
                    G.add_edge(i, j, weight=score)
    matches = list(nx.max_weight_matching(G, maxcardinality=True))
    return matches

# 🪙 Blockchain Logging
def log_match_to_chain(pair1, pair2):
    tx = {
        'from': account,
        'to': account,
        'value': 0,
        'data': Web3.to_hex(text=f"Match: {pair1['patient']} & {pair2['patient']}")
    }
    tx_hash = w3.eth.send_transaction(tx)
    return tx_hash.hex()

# 🚑 Transport Optimizer (dummy logic)
def estimate_route_time(city1="City A", city2="City B"):
    return random.randint(1, 6)

# 📉 Rejection Risk Model (placeholder)
def predict_rejection(hla, urgency):
    model = RandomForestClassifier()
    X_train = [[30, 0], [60, 1], [90, 2]]
    y_train = [1, 0, 0]
    model.fit(X_train, y_train)
    urgency_map = {"Low": 0, "Medium": 1, "High": 2}
    return model.predict_proba([[hla, urgency_map[urgency]]])[0][1]

# 📊 Dashboard
st.title("Kidney Transplant Coordination Platform")
df = pd.DataFrame(st.session_state.pairs)
st.subheader("📋 Patient-Donor Registry")
st.dataframe(df)

if st.button("🔄 Run Matching"):
    matches = match_pairs(st.session_state.pairs)
    st.subheader("🔗 Matches Found")
    for a, b in matches:
        p1 = st.session_state.pairs[a]
        p2 = st.session_state.pairs[b]
        st.success(f"{p1['patient']} ⇄ {p2['patient']}")
        tx = log_match_to_chain(p1, p2)
        st.caption(f"Blockchain Tx: {tx}")
        time_est = estimate_route_time()
        st.caption(f"Estimated Transport Time: {time_est} hrs")
        risk1 = predict_rejection(p1['hla'], p1['urgency'])
        risk2 = predict_rejection(p2['hla'], p2['urgency'])
        st.warning(f"Rejection Risk - {p1['patient']}: {risk1:.2f}, {p2['patient']}: {risk2:.2f}")

# Compatibility Graph
st.subheader("🕸️ Compatibility Graph")
G = nx.Graph()
for i, p in enumerate(st.session_state.pairs):
    G.add_node(i, label=p['patient'])

for i, p1 in enumerate(st.session_state.pairs):
    for j, p2 in enumerate(st.session_state.pairs):
        if i != j and (p1['hla'] + p2['hla']) / 2 > 50:
            G.add_edge(i, j)

fig, ax = plt.subplots()
nx.draw(G, with_labels=True, labels=nx.get_node_attributes(G, 'label'), node_color='skyblue', ax=ax)
st.pyplot(fig)

# 👥 Stakeholder Access Placeholder
st.sidebar.markdown("---")
st.sidebar.subheader("User Role")
role = st.sidebar.radio("Select", ["Doctor", "Coordinator", "Patient"])

if role == "Coordinator":
    st.sidebar.success("Access: Match logs, transport estimates, blockchain logs.")
elif role == "Doctor":
    st.sidebar.info("Access: Compatibility view, risk prediction.")
elif role == "Patient":
    st.sidebar.warning("View your match status & education material.")

