from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from connector import Connector  # your logic module


app = FastAPI()
backend = Connector()

# Allow frontend on a different port (e.g., localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/new_database")
async def new_database(request: Request = None):
    print("Creating a new database...")
    status = backend.new_database()
    if status:
        return {"status": "success", "message": f"New database created at {status}."}
    else:
        return {"status": "cancelled", "message": "No file selected."}


@app.post("/upload_database")
async def upload_database(request: Request = None):
    print("Uploading a database...")
    status = backend.upload_database()
    if status:
        return {"status": "success", "message": f"Database uploaded at {status}."}
    else:
        return {"status": "cancelled", "message": "No file selected."}


@app.post("/import_data")
async def import_data(request: Request = None):
    print("Importing data...")
    status = backend.import_data()
    if status:
        return {"status": "success", "message": f"Data imported from {status}."}
    else:
        return {"status": "cancelled", "message": "No file selected."}


@app.post("/export_data")
async def export_data(request: Request = None):
    print("Exporting data...")
    status = backend.export_data()
    if status:
        return {"status": "success", "message": f"Data exported to {status}."}
    else:
        return {"status": "error", "message": "Failed to export data."}


@app.post("/check_id")
async def check_id(request: Request):
    data = await request.json()
    result = backend.check_id(data["id"])
    print(f"Checking ID: {data['id']}, Result: {result}")
    return {"exists": result}


@app.get("/get_graphs")
async def get_graphs():
    print("Retrieving all graphs...")
    graphs = backend.get_graphs()
    return {"graphs": graphs}


@app.get("/get_network")
async def get_network():
    return backend.get_current_graph()


@app.get("/get_node_entities")
async def get_node_entities():
    data = backend.get_node_entities()
    print(f"Node entities: {data}")
    return data


@app.get("/get_edge_entities")
async def get_edge_entities():
    data = backend.get_edge_entities()
    print(f"Edge entities: {data}")
    return data


@app.post("/create_node")
async def create_node(request: Request):
    print("Creating a new node...")
    data = await request.json()
    print(f"Creating node with data: {data}")
    node_id = data["node_id"]
    graph_ids = data["graph_ids"]
    kwargs = {k: v for k, v in data.items() if k not in ["node_id", "graph_ids"]}
    return backend.create_node(graph_ids, node_id, **kwargs)


@app.post("/get_node")
async def get_node(request: Request):
    print("Retrieving a node...")
    data = await request.json()
    node_id = data["node_id"]
    graph_id = data["graph_id"]
    return backend.get_node(graph_id, node_id)


@app.post("/edit_node")
async def edit_node(request: Request):
    print("Editing a node...")
    data = await request.json()
    node_id = data["node_id"]
    graph_id = data["graph_id"]
    kwargs = {k: v for k, v in data.items() if k not in ["node_id", "graph_id"]}
    return backend.edit_node(graph_id, node_id, **kwargs)


@app.post("/delete_node")
async def delete_node(request: Request):
    print("Deleting a node...")
    data = await request.json()
    return backend.delete_node(data["graph_id"], data["node_id"])


@app.post("/create_edge")
async def create_edge(request: Request):
    print("Creating a new edge...")
    data = await request.json()
    print(data)
    source = data["source"]
    target = data["target"]
    kwargs = {k: v for k, v in data.items() if k not in ["source", "target"]}
    return backend.create_edge(source, target, **kwargs)


@app.post("/get_edge")
async def get_edge(request: Request):
    print("Retrieving an edge...")
    data = await request.json()
    edge_source = data.get("source", None)
    edge_target = data.get("target", None)
    return backend.get_edge(edge_source, edge_target)


@app.post("/edit_edge")
async def edit_edge(request: Request):
    print("Editing an edge...")
    data = await request.json()
    source = data["source"]
    target = data["target"]
    kwargs = {k: v for k, v in data.items() if k not in ["source", "target"]}
    return backend.edit_edge(source, target, **kwargs)


@app.post("/delete_edge")
async def delete_edge(request: Request):
    print("Deleting an edge...")
    data = await request.json()
    return backend.delete_edge(data["source"], data["target"])


@app.post("/create_graph")
async def create_graph(request: Request):
    print("Creating a new graph...")
    data = await request.json()
    return backend.create_graph(data["id"])


@app.post("/delete_graph")
async def delete_graph(request: Request):
    print("Deleting a graph...")
    data = await request.json()
    return backend.delete_graph(data["id"])


@app.post("/save_current_graph")
async def save_current_graph(request: Request):
    print("Saving the current graph...")
    data = await request.json()
    return backend.save_current_graph(data["id"])


@app.get("/get_tools")
async def get_tools():
    print("Retrieving available tools...")
    return backend.get_tools()


@app.post("/weight_nodes")
async def weight_nodes(request: Request):
    print("Weighting nodes...")
    data = await request.json()
    return backend.weight_nodes(
        data["current_edge_matrix"], data["vector"], data["index_keys"]
    )


@app.post("/weight_edges")
async def weight_edges(request: Request):
    print("Weighting edges...")
    data = await request.json()
    return backend.weight_edges(
        data["current_edge_matrix"], data["vector"], data["index_keys"]
    )


@app.post("/traverse_graph")
async def traverse_graph(request: Request):
    print("Traversing the graph...")
    data = await request.json()
    kwargs = {
        k: v
        for k, v in data.items()
        if k not in ["current_edge_matrix", "vector", "index_keys"]
    }
    return backend.traverse_graph(
        data["current_edge_matrix"], data["vector"], data["index_keys"], **kwargs
    )


@app.post("/cluster_graph")
async def cluster_graph(request: Request):
    print("Clustering the graph...")
    data = await request.json()
    return backend.cluster_graph(
        data["current_edge_matrix"], data["vector"], data["index_keys"]
    )


@app.post("/compare_graphs")
async def compare_graphs(request: Request):
    print("Comparing two graphs...")
    data = await request.json()
    return backend.compare_graphs(data["graph1_id"], data["graph2_id"])


@app.post("/filter_graphs")
async def filter_graphs(request: Request):
    print("Filtering graphs...")
    data = await request.json()
    return backend.filter_graphs(
        data["graph_filters"], data["node_filters"], data["edge_filters"]
    )


# Start server with: uvicorn server:app --reload

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001, log_level="info")
