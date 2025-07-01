import pytest
from Weavers.Chain import ChainWeaver
from Weavers.Chain.data_model import Component, Requires


@pytest.fixture
def sample_designations():
    return {
        "Fighter": {
            "Parts": {"Engine": ["Jet"], "Wing": ["Delta"]},
            "Vital Parts": ["Jet"],
        },
        "Bomber": {
            "Parts": {"Engine": ["Prop"], "Wing": ["Straight"]},
            "Vital Parts": ["Prop"],
        },
    }


@pytest.fixture
def sample_manufacturers():
    return {
        "Acme": {"Locations": ["USA", "EU"]},
        "Globex": {"Locations": ["Asia"]},
    }


def test_create_base_products(sample_designations, sample_manufacturers):
    products = ChainWeaver.create_base_products(
        3, sample_designations, sample_manufacturers
    )
    assert len(products) == 3
    for p in products:
        assert isinstance(p, Component)
        assert p.full_product is True
        assert p.manufacturer in sample_manufacturers


def test_create_base_product_sprues(sample_designations, sample_manufacturers):
    base_products = ChainWeaver.create_base_products(
        2, sample_designations, sample_manufacturers
    )
    # Patch MANUFACTURERS global for test
    sprues, edges = ChainWeaver.create_base_product_sprues(
        base_products, sample_manufacturers
    )
    assert all(isinstance(s, Component) for s in sprues)
    assert all(isinstance(e, Requires) for e in edges)
    assert len(sprues) > 0
    assert len(edges) > 0


def test_create_base_product_parts(sample_designations, sample_manufacturers):
    base_products = ChainWeaver.create_base_products(
        1, sample_designations, sample_manufacturers
    )
    sprues, _ = ChainWeaver.create_base_product_sprues(
        base_products, sample_manufacturers
    )
    parts, part_edges, vital_sprues = ChainWeaver.create_base_product_parts(
        base_products, sprues, sample_designations, sample_manufacturers
    )
    assert all(isinstance(p, Component) for p in parts)
    assert all(isinstance(e, Requires) for e in part_edges)
    assert isinstance(vital_sprues, list)


def test_resolve_base_product_sprues(sample_designations, sample_manufacturers):
    base_products = ChainWeaver.create_base_products(
        1, sample_designations, sample_manufacturers
    )
    sprues, sprue_edges = ChainWeaver.create_base_product_sprues(
        base_products, sample_manufacturers
    )
    parts, part_edges, _ = ChainWeaver.create_base_product_parts(
        base_products, sprues, sample_designations, sample_manufacturers
    )
    kept_sprues, kept_edges = ChainWeaver.resolve_base_product_sprues(
        sprues, sprue_edges, part_edges
    )
    assert isinstance(kept_sprues, list)
    assert isinstance(kept_edges, list)


def test_get_next_letter_wrap():
    assert ChainWeaver.get_next_letter("A") == "B"
    assert ChainWeaver.get_next_letter("Z") == "A"
