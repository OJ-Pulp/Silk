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

- **Other Tools:** Lead times may need to be determined by another analyst tool and added to graph database.
  - Project Management and Review Technique (PERT)
  - Critical Path Method (CPM)

### Question 2

1. Identify all products manufactured at said location
2. Trace the downstream dependent components
3. Calculate the affected production volumes and the affected customers (if customers are to be included as nodes)

#### Cypher Query

```cypher
// 
MATCH (loc:Location {name: $location_name})<-[:LOCATED_AT]-(m:Manufacturer)
MATCH (m)-[:PRODUCES]->(p:Product)
MATCH (p)-[:SHIPS_TO]->(customer:Customer)
RETURN p.name as affected_product, 
       collect(customer.name) as affected_customers,
       sum(p.daily_volume) as lost_daily_production
```

### Question 3

### Question 4

### Question 5

### Question 6

### Question 7

### Question 8

### Question 9

### Question 10

### Question 11

### Question 12

### Question 13

### Question 14

### Question 15

## Required Tools & Descriptions
