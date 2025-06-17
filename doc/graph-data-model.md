# Graph Data Model

It is important to describe our graph data model going forward, such as:

- What query language we are using
- What are all the node & edge types we have
- All the properties of each node (metadata)

## Database Options

### JSON

- JSON is our first option and seems to be the first real implemented option in our Python code.
- It's relational capabilities and query capabilities are rather limited.
- More useful for quick and dirty tests

### SQL

- This is the option Terry mentioned, and it has much stronger relational databases capabilities, however it is not purposely built for graph databases.

### Cypher query language

- That is where Cypher query language comes in. It is a fully open-source query language that operates specifically on graph databases, and is used by Memgraph and Neo4J.

### Memgraph

- Memgraph is an open-source graph database system that can be locally hosted using Docker.
- Go to `localhost:3000` for local hosted Memgraph Lab.
- Can easily import **CSV** files, Kafka or Pulsar streams, or `CYPHERL` files.
  - I would assume the native storage file for these databases is `CYPHERL`.

#### Memgraph Resources

- Memgraph Docs: <https://memgraph.com/docs/getting-started>
- Memgraph OSS Github: <https://github.com/memgraph/memgraph>
- Memgraph Cypher Examples: <https://memgraph.com/docs/querying>
- Memgraph GOT Example: <https://playground.memgraph.com/sandbox/game-of-thrones-deaths>

## Questions

These are questions asking ourselves what is important for the data model to include:

- Why is `base_model` an edge characteristic?
- What differentiates between what is stored in metadata and what is stored in plain node data?

- If a part is manufactured in multiple places, should that variable be a list?
  - Our edges should tell us this information

- Should materials of parts be included?
  - Unless gaining materials contributes significantly to lead time, I think that materials should be ignored - Corbin

## Node & Edge Types & Characteristics

### Node Types

- Location
- Component
- Product
  - Product may be a component with no outgoing edges
- Manufacturers
- Suppliers
- Companies

> [!note]
> It may be important to make a distinction between manufacturers, companies, and suppliers, or consolidate them.

### Node Characteristics

#### Component

- `part_number` : \[List\[ID\]\]
- `dimensions` : \[int,int,int\]
- `full_product` : \[bool\]
  - It may not be necessary to include this as a component characteristic, it can be inferred if it has no outgoing edges
- `cost` : \[int\]
- `criticality` : \[%\]
- `failure_rate` : \[?\]
- `substitutions` : \[list\[ID\]\]
- `breakability` : \[?\]

#### Manufacturer

- `restricted_territory` : \[bool\]
- `capacity` : \[int\]

### Edge Types

- `:REQUIRED_FOR`
- `:SUPPLIES`
- `:LOCATED_AT`
- `:SHIPS_TO`
- `:ASSEMBLES`

### Edge Characteristics

#### `:REQUIRES`

- `base_model` : \[bool\]
- `lead_time` : \[int\]
