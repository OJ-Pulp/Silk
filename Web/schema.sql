-- Graphs and nodes (associative)
CREATE TABLE Graph_Nodes (
    Graph_ID INT NOT NULL,
    Node_ID INT,
    UNIQUE (Graph_ID, Node_ID)
);

-- Edges
CREATE TABLE Edges (
    ID INTEGER PRIMARY KEY,
    SourceID INTEGER NOT NULL,
    TargetID INTEGER NOT NULL,
    FOREIGN KEY (SourceID) REFERENCES Graph_Nodes(Node_ID),
    FOREIGN KEY (TargetID) REFERENCES Graph_Nodes(Node_ID)
);
    
-- Core entities
CREATE TABLE Entities (
    ID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Type TEXT NOT NULL CHECK (Type IN ('Real', 'Int', 'Text'))
);

-- A polymorphic reference to graph, node, or edge
-- Example values for target_type: 'graph', 'node', 'edge'
CREATE TABLE Real_Entity_Values (
    Entity_ID INTEGER NOT NULL,
    Target_Type TEXT NOT NULL CHECK (Target_Type IN ('graph', 'node', 'edge')),
    Target_ID INTEGER NOT NULL,
    Value REAL,
    PRIMARY KEY (Entity_ID, Target_Type, Target_ID),
    FOREIGN KEY (Entity_ID) REFERENCES Entities(ID)
);

CREATE TABLE Int_Entity_Values (
    Entity_ID INTEGER NOT NULL,
    Target_Type TEXT NOT NULL CHECK (Target_Type IN ('graph', 'node', 'edge')),
    Target_ID INTEGER NOT NULL,
    Value INTEGER,
    PRIMARY KEY (Entity_ID, Target_Type, Target_ID),
    FOREIGN KEY (Entity_ID) REFERENCES Entities(ID)
);

CREATE TABLE Text_Entity_Values (
    Entity_ID INTEGER NOT NULL,
    Target_Type TEXT NOT NULL CHECK (Target_Type IN ('graph', 'node', 'edge')),
    Target_ID INTEGER NOT NULL,
    Value TEXT,
    PRIMARY KEY (Entity_ID, Target_Type, Target_ID),
    FOREIGN KEY (Entity_ID) REFERENCES Entities(ID)
);