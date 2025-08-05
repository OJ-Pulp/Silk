import pandas as pd
from Weavers.graph_model import Node, Edge


class DummyNode(Node):
    __csv_fields__ = ["id", "name", "extra"]

    def __init__(self, name, extra, id=None):
        super().__init__(name, id=id)
        self.extra = extra
        self.metadata = {"meta": "value"}


class DummyEdge(Edge):
    __csv_fields__ = ["start_id", "end_id", "id", "relation"]

    def __init__(self, start_node, end_node, relation="rel"):
        super().__init__(start_node, end_node)
        self.relation = relation


def test_node_equality_and_hash():
    n1 = DummyNode("A", 1)
    n2 = DummyNode("A", 1, id=n1.id)
    n3 = DummyNode("B", 2)
    assert n1 == n2
    assert n1 != n3
    assert hash(n1) == hash(n2)


def test_node_to_dict_and_csv_fields():
    n = DummyNode("A", 42)
    d = n.to_dict()
    assert d["name"] == "A"
    assert d["extra"] == 42
    assert set(d.keys()) == {"id", "name", "extra"}


def test_node_write_to_csv(tmp_path):
    nodes = [DummyNode("A", 1), DummyNode("B", 2)]
    out = tmp_path / "nodes.csv"
    Node.write_to_csv(nodes, out)
    df = pd.read_csv(out)
    assert set(df.columns) == {"id", "name", "extra"}
    assert len(df) == 2


def test_edge_equality_and_hash():
    n1 = DummyNode("A", 1)
    n2 = DummyNode("B", 2)
    e1 = DummyEdge(n1, n2, relation="x")
    e2 = DummyEdge(n1, n2, relation="x")
    e2.id = e1.id
    assert e1 == e2
    assert hash(e1) == hash(e2)


def test_edge_to_dict_and_csv_fields():
    n1 = DummyNode("A", 1)
    n2 = DummyNode("B", 2)
    e = DummyEdge(n1, n2, relation="friend")
    d = e.to_dict()
    assert d["relation"] == "friend"
    assert set(d.keys()) == {"start_id", "end_id", "id", "relation"}


def test_edge_write_to_csv(tmp_path):
    n1 = DummyNode("A", 1)
    n2 = DummyNode("B", 2)
    e = DummyEdge(n1, n2, relation="peer")
    out = tmp_path / "edges.csv"
    Edge.write_to_csv([e], out)
    df = pd.read_csv(out)
    assert set(df.columns) == {"start_id", "end_id", "id", "relation"}
    assert len(df) == 1
