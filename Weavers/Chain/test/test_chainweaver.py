import pytest
from Weavers.Chain.ChainWeaver import ChainWeaver
from Weavers.Chain.data_model import Component, Requires
import csv

weaver = ChainWeaver()


def test_create_base_products():
    products = weaver.create_base_products(3)
    assert len(products) == 3
    for p in products:
        assert isinstance(p, Component)
        assert p.full_product is True
        assert p.manufacturer in weaver.manufacturers


def test_create_base_product_sprues():
    base_products = weaver.create_base_products(2)
    # Patch MANUFACTURERS global for test
    sprues, edges = weaver.create_base_product_sprues(base_products)
    assert all(isinstance(s, Component) for s in sprues)
    assert all(isinstance(e, Requires) for e in edges)
    assert len(sprues) > 0
    assert len(edges) > 0


def test_create_base_product_parts():
    base_products = weaver.create_base_products(1)
    sprues, _ = weaver.create_base_product_sprues(base_products)
    parts, part_edges, vital_sprues = weaver.create_base_product_parts(
        base_products, sprues
    )
    assert all(isinstance(p, Component) for p in parts)
    assert all(isinstance(e, Requires) for e in part_edges)
    assert isinstance(vital_sprues, list)


def test_resolve_base_product_sprues():
    base_products = weaver.create_base_products(1)
    sprues, sprue_edges = weaver.create_base_product_sprues(base_products)
    _, part_edges, _ = weaver.create_base_product_parts(base_products, sprues)
    kept_sprues, kept_edges = weaver.resolve_base_product_sprues(
        sprues, sprue_edges, part_edges
    )
    assert isinstance(kept_sprues, list)
    assert isinstance(kept_edges, list)


def test_get_next_letter_wrap():
    assert weaver.get_next_letter("A") == "B"
    assert weaver.get_next_letter("Z") == "A"


def test_components_csv_has_unique_ids(tmp_path, monkeypatch):
    # Patch the output directory used by ChainWeaver
    output_dir = tmp_path / "output"
    monkeypatch.setattr(
        "Weavers.Chain.ChainWeaver.get_next_test_output_filename",
        lambda base_name, extension, output_dir=output_dir: output_dir
        / f"test1_{base_name}.{extension.lstrip('.')}",
    )
    # Run main to generate CSVs
    from Weavers.Chain import ChainWeaver

    ChainWeaver.main(num_products=5, variant_distribution=0.2)
    # Find the components CSV
    components_csv = output_dir / "test1_nodes.csv"
    assert components_csv.exists(), "Components CSV was not created"
    with components_csv.open(newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        ids = [row["ID"] for row in reader if "ID" in row]
    assert len(ids) != len(set(ids)), "Duplicate IDs found in components CSV"
