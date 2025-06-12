# Graph Data Model

## Database Options

### JSON

- JSON is our first option and seems to be the first real implemented option in our Python code.
- It's relational capabilities and query capabilities are rather limited.
- More useful for quick and dirty tests

### SQL

- This is the option Terry mentioned, and it has much stronger relational databases capabilities, however it is not purposely built for graph databases.

### Cypher query language

- That is where Cypher query language comes in. It is a fully open-source query language that operates specifically on graph databases, and is used by Memgraph and Neo4J.
- Memgraph may be useful for visualizing our graph information for testing.

## Node & Edge Types

### Nodes

- Location
- Component
- Product
  - Product may be a component with no outgoing edges
- Manufacturers
- Suppliers
- Companies

> [!note]
> It may be important to make a distinction between manufacturers, companies, and suppliers, or consolidate them.

### Edges

- REQUIRES
- SUPPLIES
-
