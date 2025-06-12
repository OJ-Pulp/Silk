# Analyst Questions & Graph Tools

## Questions

What questions would an analyst ask the LLM:

1. Which suppliers are **critical** to delivering a complete aircraft *on time*?
2. What happens if a particular manufacturing **location** goes *offline*?
3. Simulate the cascade effects of a closure of a location.
4. Which *parts* have the highest **failure rates** and how do they affect *production*?
5. Which **component** has the **highest vulnerability** (percentage) in this supply chain?
6. How *vulnerable*, in general, is **this** supply chain?
7. What are single points of **failure** in the supply chain network?
8. Which suppliers have the highest **concentration risk** (serving multiple critical functions)?
9. Identify **redundant** supplier relationships that could be **consolidated**.
10. If this supplier goes **offline**, which *products* would be affected and by when?
11. Which products have supply chains passing through **restricted** territories?
12. Find **underutilized** suppliers that could handle **additional volume**.
13. How can we reduce the average path length in our supply network?
14. What are the **most vulnerable** paths between our key suppliers and manufacturing facilities?
15. What *alternative* supply paths exist if our primary manufacturer is **disrupted**?

## Question Breakdown

### Question 1

1. Identify critical path for specific aircraft
2. Find suppliers on critical path with the longest lead time.

#### Cypher Query

```cypher
// For a specific aircraft, find the critical path and assign it to 'path'
MATCH path = (s:Supplier)-[:SUPPLIES]->(c:Component)-[:REQUIRED_FOR]->(p:Product {name: 'Aircraft'})

// Group edges together as rels
WITH s, c, p, relationships(path) as rels
UNWIND rels as rel

// Sum the lead_time edge characteristic for all edges in path
WITH s, c, p, sum(rel.lead_time) as total_lead_time

// Order suppliers by longest lead times, return them, and limit to top 10
ORDER BY total_lead_time DESC
RETURN s.name, c.name, total_lead_time
LIMIT 10
```

#### Other Tools

- Lead times may need to be determined by another analyst tool and added to graph database.
  - Project Management and Review Technique (PERT)
  - Critical Path Method (CPM)

### Question 2

1. Identify all products manufactured at said location
2. Trace the downstream dependent components
3. Calculate the affected production volumes and the affected customers (if customers are to be included as nodes)

#### Cypher Query

```cypher
// Match all manufacturers from a location
MATCH (loc:Location {name: $location_name})<-[:LOCATED_AT]-(m:Manufacturer)

// Match products from manufacturer
MATCH (m)-[:PRODUCES]->(p:Product)

// Match affected customers
MATCH (p)-[:SHIPS_TO]->(customer:Customer)
RETURN p.name as affected_product, 
       collect(customer.name) as affected_customers,
       // Sum daily volume from product as the lost daily production
       sum(p.daily_volume) as lost_daily_production
```

### Question 3

- Start with the failed location
- Propagate impact through network layers
- Model time-based delays, and inventory buffers

#### Cypher Query

```cypher
// Find failed location
MATCH (failed:Location {name: $failed_location})

// Call relationship filter to yield our path of edges
CALL apoc.path.expandConfig(failed, {
    relationshipFilter: "SUPPLIES>|SHIPS_TO>|REQUIRES>",
    minLevel: 1,
    maxLevel: 5
}) YIELD path

// Set variables, using the length of the path as the impact level
WITH nodes(path) as cascade_nodes, length(path) as impact_level

// Unwind nodes from our cascade path
UNWIND cascade_nodes as node

// Return nodes based on the described impact level
RETURN labels(node)[0] as node_type, 
       node.name as name,
       impact_level,
       node.daily_capacity as capacity_at_risk
ORDER BY impact_level
```

#### Other Tools

- Discrete Event Simulations
- Monte Carlo Method

### Question 4

1. Aggregate failure rate data by components
2. Calculate production impact per failure
3. Rank by total production risk

#### Cipher Query

```cypher
// Match all components required for a product
MATCH (c:Component)-[:REQUIRED_FOR]->(p:Product)

// Set failure rate variables
WITH c, collect(p) as products, c.failure_rate as failure_rate

// Product variables
UNWIND products as product

// Sum the daily volume as total volume at risk
WITH c, failure_rate, sum(product.daily_volume) as total_volume_at_risk

// Calculate risk score and order components by risk score
RETURN c.name, 
       failure_rate,
       total_volume_at_risk,
       (failure_rate * total_volume_at_risk) as risk_score
ORDER BY risk_score DESC
```

### Question 5

1. Calculate vulnerability as $(\text{failure rate}* \text{impact} * \text{concentration})$
2. Consider alternate sourcing options
3. Order by business criticality, revenue impact, reliability, etc.

#### Cipher Query

```cypher
// Find number of suppliers that supply a component, create reliability score variable
MATCH (c:Component)<-[:SUPPLIES]-(s:Supplier)
WITH c, count(s) as supplier_count, avg(s.reliability_score) as avg_reliability

// Match components required for a product
MATCH (c)-[:REQUIRED_FOR]->(p:Product)

// Sum total revenue impact
WITH c, supplier_count, avg_reliability, sum(p.revenue_impact) as total_revenue_impact

// Do lots of math to create vulnerability score
// A lot of these calculations could probably be done using Python instead with the data given
RETURN c.name,
       (1.0/supplier_count) as concentration_risk,
       (1.0 - avg_reliability) as supply_risk,
       total_revenue_impact,
       ((1.0/supplier_count) * (1.0 - avg_reliability) * total_revenue_impact) as vulnerability_score
ORDER BY vulnerability_score DESC
```

### Question 6

1. Calculate the network topology metrics
2. Analyze redundancy levels (higher is better)
3. Assess geographic concentration (more concentrated the better)
4. Create an overall network resilience score

#### Cypher Query

```cypher
// Create node summary
MATCH (n)
WITH labels(n)[0] as node_type, count(n) as node_count
WITH collect({type: node_type, count: node_count}) as node_summary

// Create edge sum
MATCH ()-[r]->()
WITH node_summary, type(r) as relationship_type, count(r) as rel_count
WITH node_summary, collect({type: relationship_type, count: rel_count}) as rel_summary

// Calculate clustering coefficient and path redundancy
// Create a graph projection for the GDS algorithms
CALL gds.graph.project('supply_chain', '*', '*')

// Calculate triangle count for each node
CALL gds.triangleCount.stream('supply_chain') YIELD nodeId, triangleCount

// Calculate degree of each node 
CALL gds.degree.stream('supply_chain') YIELD nodeId, score as degree

// Convert node IDs back to actual node objects and combine the metrics
WITH gds.util.asNode(nodeId) as node, triangleCount, degree

// Calculate clustering coeficient for the entire network
WITH avg(triangleCount * 2.0 / (degree * (degree - 1))) as avg_clustering

// Comprehensive network resilience summary
// Higher clustering coefficient is better, more resilience and redundancy
// Lower clustering coefficient is worse, represents more of a tree-like structure
RETURN node_summary, rel_summary, avg_clustering as network_resilience_score
```

#### Additional Tools

- Network analysis libraries (Python)
  - NetworkX
  - igraph
- Resilience metrics

### Question 7

1. Identify bridge nodes
2. Find critical edges whose removal disconnects graph
    - Complete disconnection => supply chain interruption
3. Calculate edge betweenness centrality

```cypher
// Find nodes with high betweenness centrality (bottlenecks)
CALL gds.graph.project('supply_network', '*', '*')
CALL gds.betweenness.stream('supply_network') 
YIELD nodeId, score
WITH gds.util.asNode(nodeId) as node, score
WHERE score > 0

// Create bottleneck score based on score returned earlier
RETURN labels(node)[0] as node_type, 
       node.name, 
       score as bottleneck_score

ORDER BY bottleneck_score DESC
LIMIT 20
```

### Question 8

### Question 9

### Question 10

### Question 11

### Question 12

### Question 13

### Question 14

### Question 15

## Required Tools & Descriptions
