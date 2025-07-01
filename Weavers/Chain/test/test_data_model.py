import pytest
from Weavers.Chain.data_model import Component, Requires


def test_component_creation():
    comp = Component(
        name="Test Component",
        manufacturer="Test Manufacturer",
        locations=["Test Location"],
        full_product=True,
        component_type="Widget",
        variant=False,
        vital=True,
        designation="TC-001",
        popular_name="Testy",
        category="TestCat",
        part_type="TypeA",
        dimensions=[1, 2, 3],
        cost=10.5,
        failure_rate=0.01,
        substitutions=["Sub1", "Sub2"],
        breakability=0.5,
        year_range=[2020, 2021],
    )
    assert comp.name == "Test Component"
    assert comp.manufacturer == "Test Manufacturer"
    assert comp.locations == ["Test Location"]
    assert comp.metadata["cost"] == 10.5
    assert comp.metadata["dimensions"] == [1, 2, 3]
    assert comp.metadata["breakability"] == 0.5


def test_component_metadata_validation():
    comp = Component(
        name="MetaTest",
        manufacturer="MetaManu",
        locations="MetaLoc",
        full_product=False,
    )
    with pytest.raises(ValueError):
        comp.set_metadata("cost", -1)
    with pytest.raises(ValueError):
        comp.set_metadata("dimensions", [1, 2])  # Not length 3
    with pytest.raises(TypeError):
        comp.set_metadata("substitutions", [1, 2, 3])  # Not all strings


def test_edge_creation_and_to_dict():
    comp1 = Component(
        name="A",
        manufacturer="M1",
        locations="L1",
        full_product=True,
    )
    comp2 = Component(
        name="B",
        manufacturer="M2",
        locations="L2",
        full_product=False,
    )
    # Provide required arguments for Edge constructor
    edge = Requires(
        start_node=comp1,
        end_node=comp2,
        base_model=True,
        lead_time=5,
    )
    d = edge.to_dict()
    assert d["start_id"] == comp1.id
    assert d["end_id"] == comp2.id
    assert d["base_model"] is True
    assert d["lead_time"] == 5


def test_component_to_dict():
    comp = Component(
        name="DictTest",
        manufacturer="DictManu",
        locations="DictLoc",
        full_product=True,
        cost=5.0,
    )
    d = comp.to_dict()
    assert d["name"] == "DictTest"
    assert d["manufacturer"] == "DictManu"
    assert d["cost"] == 5.0


def test_edge_equality_and_hash():
    comp1 = Component(
        name="X",
        manufacturer="M",
        locations="L",
        full_product=True,
    )
    comp2 = Component(
        name="Y",
        manufacturer="M",
        locations="L",
        full_product=False,
    )
    edge1 = Requires(comp1, comp2, base_model=False, lead_time=2)
    edge2 = Requires(comp1, comp2, base_model=False, lead_time=2)
    assert edge1 != edge2
    assert hash(edge1) != hash(edge2)
    assert edge1 == edge1
    assert hash(edge1) == hash(edge1)


def test_component_metadata_all_fields():
    comp = Component(
        name="MetaFull",
        manufacturer="MetaManu",
        locations=["MetaLoc"],
        full_product=True,
        variant=True,
        variant_base_product="BaseProd",
        vital=False,
        designation="D-001",
        popular_name="MetaPopular",
        category="MetaCat",
        part_type="MetaType",
        dimensions=[10, 20, 30],
        cost=100.0,
        failure_rate=0.001,
        substitutions=["Alt1", "Alt2"],
        breakability=0.2,
        year_range=[2010, 2020],
    )
    d = comp.to_dict()
    assert d["variant"] is True
    assert d["variant_base_product"] == "BaseProd"
    assert d["vital"] is False
    assert d["designation"] == "D-001"
    assert d["popular_name"] == "MetaPopular"
    assert d["category"] == "MetaCat"
    assert d["part_type"] == "MetaType"
    assert d["dimensions"] == [10, 20, 30]
    assert d["cost"] == 100.0
    assert d["failure_rate"] == 0.001
    assert d["substitutions"] == ["Alt1", "Alt2"]
    assert d["breakability"] == 0.2
    assert d["year_range"] == [2010, 2020]


def test_component_invalid_metadata_types():
    comp = Component(
        name="InvalidMeta",
        manufacturer="MetaManu",
        locations=["MetaLoc"],
        full_product=True,
    )
    with pytest.raises(ValueError):
        comp.set_metadata("cost", -100)
    with pytest.raises(ValueError):
        comp.set_metadata("breakability", 2)
    with pytest.raises(ValueError):
        comp.set_metadata("failure_rate", -0.1)
    with pytest.raises(ValueError):
        comp.set_metadata("dimensions", [1, 2])  # Not length 3
    with pytest.raises(TypeError):
        comp.set_metadata("substitutions", [1, 2, 3])  # Not all strings
    with pytest.raises(TypeError):
        comp.set_metadata("year_range", ["2010", "2020"])  # Not all ints
    with pytest.raises(ValueError):
        comp.set_metadata("variant_base_product", "")  # Empty string
    with pytest.raises(ValueError):
        comp.set_metadata("designation", "")  # Empty string
    with pytest.raises(ValueError):
        comp.set_metadata("category", "")  # Empty string
    with pytest.raises(ValueError):
        comp.set_metadata("part_type", "")  # Empty string
