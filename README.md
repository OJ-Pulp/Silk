# Silk

## 📦 Supply Chain Network Analyzer

This project applies **graph theory** and **network analysis** to model and visualize supply chains. The system is designed to represent key entities (like suppliers, distributors, warehouses) as **nodes**, and their relationships (flows, contracts, dependencies) as **edges**.

🔧 It includes:
- A **backend** for managing node/edge data using a relational graph database structure
- A **UI** for interactively visualizing and querying the network

---

### 🚀 Features

- Graph-based storage and querying of supply chain data
- JSON-configurable schema for flexibility
- Visualization of complex supply networks
- Easily adaptable to other domains: logistics, social networks, power grids, etc.

---

### 🔍 Use Cases

- Identify bottlenecks or vulnerable nodes in a supply chain
- Visualize dependencies between suppliers and products
- Extend to simulate disruptions or alternate routing

---

### 🛠️ Tech Stack

- **Python** backend using SQLite for structured graph storage
- **JSON-based schema** configuration
- **UI (upcoming)** for interactive graph visualization (e.g. using D3.js or NetworkX with a web frontend)
- **Pickled NumPy matrices** for fast adjacency matrix operations

---
