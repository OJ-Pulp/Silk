# connector.py
import tkinter as tk
from tkinter import filedialog
import spider
import pickle
import json
from config import get_dir_path
import os


class Connector:
    def __init__(self):
        self.current_state = {}
        self.spider: spider.Spider
        self.load_state()

    def save_state(self):
        print(f"Saving state to: {get_dir_path()}")
        state_path = os.path.join(get_dir_path(), "state.pkl")
        state = {"db_path": getattr(self.spider, "current_db_path", ":memory:")}
        with open(state_path, "wb") as f:
            pickle.dump(state, f)

    def load_state(self):
        state_path = os.path.join(get_dir_path(), "state.pkl")
        if os.path.exists(state_path):
            print(f"Loading state from: {get_dir_path()}")
            try:
                with open(state_path, "rb") as f:
                    state = pickle.load(f)
                db_path = state.get("db_path", ":memory:")
                self.spider = spider.Spider(db_path=db_path)
                self.spider.reconnect()
                print("State loaded successfully.")
            except (EOFError, pickle.UnpicklingError) as e:
                print(f"Failed to load state ({e}). Creating a new Spider instance.")
                self.spider = spider.Spider()
                self.spider.disconnect()
                self.save_state()
                self.spider.reconnect()
        else:
            print("No saved state found. Creating a new Spider instance.")
            self.spider = spider.Spider()
            self.spider.disconnect()
            self.save_state()
            self.spider.reconnect()

    def new_database(self):
        # Open file explorer to select where to create a new database file
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        filepath = filedialog.asksaveasfilename(
            title="Create New Database",
            defaultextension=".db",
            filetypes=[("SQLite DB", "*.db"), ("All Files", "*.*")],
        )
        if filepath:
            self.spider.create_database(filepath)
            self.save_state()
            print(f"New database created at {filepath}.")
            return filepath
        else:
            return None

    def upload_database(self):
        # Open file explorer to select an existing database
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title="Open Existing Database",
            filetypes=[("SQLite DB", "*.db"), ("All Files", "*.*")],
        )
        if filepath:
            self.spider.change_database(filepath)
            self.save_state()
            print(f"Database loaded from {filepath}.")
            return filepath
        else:
            return None

    def import_data(self):
        # Open file explorer to select a data file to import
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title="Import Data",
            filetypes=[("Data Files", "*.json"), ("All Files", "*.*")],
        )
        if filepath:
            # Implement the logic to import data into the current graph
            data = json.load(open(filepath, "r"))
            # Check if data has keys "nodes" and "edges"
            # Nodes should be a list of dictionaries
            # Each dictionary should have a graph_id, node_id, and any other attributes
            if "nodes" in data and isinstance(data["nodes"], list):
                for node in data["nodes"]:
                    if (
                        not isinstance(node, dict)
                        or "graph_ids" not in node
                        or "node_id" not in node
                        or not isinstance(node["graph_ids"], list)
                    ):
                        print(f"Invalid node format: {node}")
                    self.spider.create_node(node["graph_ids"], node["node_id"], **node)

            # For edges, check if they are a list of dictionaries
            # Each dictionary should have "source", "target", and any other attributes
            if "edges" in data and isinstance(data["edges"], list):
                for edge in data["edges"]:
                    if (
                        not isinstance(edge, dict)
                        or "source" not in edge
                        or "target" not in edge
                    ):
                        print(f"Invalid edge format: {edge}")

                    self.spider.create_edge(edge["source"], edge["target"], **edge)

            print(f"Data imported from {filepath}.")
            return filepath
        else:
            return None

    def export_data(self):
        # Open file explorer to select where to save the exported data
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.asksaveasfilename(
            title="Export Data",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
        )
        if filepath:
            data = {}
            edge_matrix, _node_weights, node_ids = self.spider.get_current_graph()
            edge_ids = [
                (node_ids[source], node_ids[target])
                for source, target in zip(*edge_matrix.nonzero())
            ]
            data["nodes"] = [self.spider.get_node(node_id) for node_id in node_ids]
            data["edges"] = [
                self.spider.get_edge(source, target) for source, target in edge_ids
            ]
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Data exported to {filepath}.")
            return filepath
        else:
            return None

    def get_current_graph(self):
        node_weights, edge_matrix, node_idxs = self.spider.get_current_graph()

        return {
            "edge_matrix": edge_matrix.tolist(),
            "node_weights": node_weights.tolist(),
            "node_idxs": node_idxs,
        }
        # Return a fake large testing data of 20 nodes and 30 edges
        # return {
        #     "edge_matrix": [[1] * 20 for _ in range(20)],
        #     "node_weights": [4.0] * 20,
        #     "node_idxs": [f"node_{i}" for i in range(20)],
        # }

    def check_id(self, id):
        return self.spider.check_id(id)

    def get_graphs(self):
        return self.spider.get_graphs()

    def get_node_entities(self):
        return self.spider.get_node_entities()

    def get_edge_entities(self):
        return self.spider.get_edge_entities()

    def create_node(self, graph_ids, node_id, **kwargs):
        self.spider.create_node(graph_ids, node_id, **kwargs)
        return {
            "status": "success",
            "message": f"Node '{node_id}' created in graphs.",
        }

    def create_edge(self, source, target, **kwargs):
        self.spider.create_edge(source, target, **kwargs)
        return {"status": "success", "message": "Edge created."}

    def get_node(self, graph_id, node_id):
        return self.spider.get_node(graph_id, [node_id])

    def get_edge(self, source, target):
        return self.spider.get_edge(source, target)

    def edit_node(self, graph_id, node_id, **kwargs):
        self.spider.change_node(graph_id, node_id, **kwargs)
        return {
            "status": "success",
            "message": f"Node '{node_id}' edited in graph '{graph_id}'.",
        }

    def edit_edge(self, source, target, **kwargs):
        self.spider.change_edge(source, target, **kwargs)
        return {
            "status": "success",
            "message": f"Edge from {source} to {target} edited.",
        }

    def delete_edge(self, source, target):
        self.spider.delete_edge(source, target)
        return {
            "status": "success",
            "message": f"Edge from {source} to {target} deleted.",
        }

    def delete_node(self, graph_id, node_id):
        self.spider.delete_node(graph_id, node_id)
        return {
            "status": "success",
            "message": f"Node '{node_id}' deleted from graph '{graph_id}'.",
        }

    def create_graph(self, id):
        self.spider.create_graph(id)
        return {"status": "success", "message": f"Graph '{id}' created."}

    def delete_graph(self, id):
        self.spider.delete_graph(id)
        return {"status": "success", "message": f"Graph '{id}' deleted."}

    def save_current_graph(self, graph_id):
        self.spider.save_current_graph(graph_id)
        return {"status": "success", "message": f"Current graph saved as '{graph_id}'."}

    def get_tools(self):
        self.spider.get_tools()
        return {"status": "success", "tools": ["Tool1", "Tool2", "Tool3"]}

    def generate_chainweaver_graph(self, num_products, variant_distribution):
        from Weavers.Chain.ChainWeaver import ChainWeaver

        def as_generator(seq):
            yield from seq

        # Create ChainWeaver instance
        weaver = ChainWeaver(
            num_products=int(num_products),
            variant_distribution=float(variant_distribution),
        )

        # --- Generate base products ---
        base_products = list(weaver.generate_base_products())
        for node in base_products:
            self.spider.create_node(["default"], node.id, **node.__dict__)

        # --- Generate base product sprues ---
        base_product_sprues = list(
            weaver.generate_base_product_sprues((n for n in base_products))
        )
        for node in base_product_sprues:
            self.spider.create_node(["default"], node.id, **node.__dict__)

        # --- Generate base product sprue edges ---
        base_product_sprue_edges = []
        for edge in weaver.generate_base_product_sprue_edges(
            as_generator(base_products), as_generator(base_product_sprues)
        ):
            self.spider.create_edge(edge.start_node, edge.end_node, **edge.__dict__)
            base_product_sprue_edges.append(edge)

        # --- Generate vital base product sprues ---
        vital_base_product_sprues = []
        for node in weaver.generate_vital_base_product_sprues(
            as_generator(base_products), as_generator(base_product_sprues)
        ):
            self.spider.create_node(["default"], node.id, **node.__dict__)
            vital_base_product_sprues.append(node)

        # --- Generate base product parts ---
        base_product_parts = []
        for node in weaver.generate_base_product_parts(as_generator(base_products)):
            self.spider.create_node(["default"], node.id, **node.__dict__)
            base_product_parts.append(node)

        # --- Generate base product part edges ---
        base_product_part_edges = []
        for edge in weaver.generate_base_product_part_edges(
            as_generator(base_product_parts), as_generator(base_product_sprues)
        ):
            self.spider.create_edge(edge.start_node, edge.end_node, **edge.__dict__)
            base_product_part_edges.append(edge)

        # --- Generate variant products ---
        num_variants = int(weaver.num_products * weaver.variant_distribution)
        variant_products = []
        for node in weaver.generate_variant_products(as_generator(base_products)):
            self.spider.create_node(["default"], node.id, **node.__dict__)
            variant_products.append(node)

        # --- Generate variant sprues ---
        variant_sprues = []
        for node in weaver.generate_variant_product_sprues(
            as_generator(variant_products), as_generator(vital_base_product_sprues)
        ):
            self.spider.create_node(["default"], node.id, **node.__dict__)
            variant_sprues.append(node)

        # --- Generate variant sprue edges ---
        variant_sprue_edges = []
        for edge in weaver.generate_variant_product_sprue_edges(
            as_generator(variant_products),
            as_generator(variant_sprues),
            as_generator(vital_base_product_sprues),
        ):
            self.spider.create_edge(edge.start_node, edge.end_node, **edge.__dict__)
            variant_sprue_edges.append(edge)

        # --- Generate variant parts ---
        variant_parts = []
        for node in weaver.generate_variant_parts(as_generator(variant_products)):
            self.spider.create_node(["default"], node.id, **node.__dict__)
            variant_parts.append(node)

        # --- Generate variant part edges ---
        variant_part_edges = []
        for edge in weaver.generate_variant_part_edges(
            as_generator(variant_parts), as_generator(variant_sprues)
        ):
            self.spider.create_edge(edge.start_node, edge.end_node, **edge.__dict__)
            variant_part_edges.append(edge)

        weaver.close()
        return {
            "base_products": len(base_products),
            "base_product_sprues": len(base_product_sprues),
            "base_product_sprue_edges": len(base_product_sprue_edges),
            "vital_base_product_sprues": len(vital_base_product_sprues),
            "base_product_parts": len(base_product_parts),
            "base_product_part_edges": len(base_product_part_edges),
            "variant_products": len(variant_products),
            "variant_sprues": len(variant_sprues),
            "variant_sprue_edges": len(variant_sprue_edges),
            "variant_parts": len(variant_parts),
            "variant_part_edges": len(variant_part_edges),
        }

    def weight_nodes(self, edge_matrix, node_vector, index_keys):
        self.spider.weight_nodes(edge_matrix, node_vector, index_keys)
        return {"status": "success", "message": "Nodes weighted."}

    def weight_edges(self, edge_matrix, edge_vector, index_keys):
        self.spider.weight_edges(edge_matrix, edge_vector, index_keys)
        return {"status": "success", "message": "Edges weighted."}

    def traverse_graph(self, edge_matrix, node_vector, index_keys, **kwargs):
        self.spider.traverse_graph(edge_matrix, node_vector, index_keys, **kwargs)
        return {"status": "success", "message": "Graph traversal complete."}

    def cluster_graph(self, edge_matrix, node_vector, index_keys):
        self.spider.cluster_graph(edge_matrix, node_vector, index_keys)
        return {"status": "success", "message": "Graph clustered."}

    def compare_graphs(self, graph1_id, graph2_id):
        self.spider.compare_graphs(graph1_id, graph2_id)
        return {"status": "success", "message": "Graphs compared."}

    def filter_graphs(self, graph_filter, node_filter, edge_filter):
        self.spider.filter_graphs(graph_filter, node_filter, edge_filter)
        return {"status": "success", "message": "Graphs filtered."}
