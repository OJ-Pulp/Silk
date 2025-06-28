-- schema.sql

-- Node Entities table
CREATE TABLE Node_Entities (
    ID INTEGER PRIMARY KEY,
    Entity TEXT NOT NULL,
    Type TEXT NOT NULL CHECK (Type IN ('Real', 'Int', 'Text'))
);

-- Nodes table
CREATE TABLE Nodes (
    ID INTEGER PRIMARY KEY,
    Index INTEGER NOT NULL
);

-- Real Node Entities table
CREATE TABLE Real_Node_Entities (
    Node_ID INTEGER NOT NULL,
    Node_Entity_ID INTEGER NOT NULL,
    value REAL,
    FOREIGN KEY (Node_ID) REFERENCES Nodes(ID),
    FOREIGN KEY (Node_Entity_ID) REFERENCES Node_Entities(ID)
);

-- Text Node Entities table
CREATE TABLE Text_Node_Entities (
    Node_ID INTEGER NOT NULL,
    Node_Entity_ID INTEGER NOT NULL,
    value TEXT,
    FOREIGN KEY (Node_ID) REFERENCES Nodes(ID),
    FOREIGN KEY (Node_Entity_ID) REFERENCES Node_Entities(ID)
);

-- Int Node Entities table
CREATE TABLE Int_Node_Entities (
    Node_ID INTEGER NOT NULL,
    Node_Entity_ID INTEGER NOT NULL,
    value INTEGER,
    FOREIGN KEY (Node_ID) REFERENCES Nodes(ID),
    FOREIGN KEY (Node_Entity_ID) REFERENCES Node_Entities(ID)
);

-- Edge Entities table
CREATE TABLE Edge_Entities (
    ID INTEGER PRIMARY KEY,
    Entity TEXT NOT NULL,
    Type TEXT NOT NULL CHECK (Type IN ('Real', 'Int', 'Text'))
);

-- Edges table
CREATE TABLE Edges (
    ID INTEGER PRIMARY KEY,
    SourceID INTEGER NOT NULL,
    TargetID INTEGER NOT NULL
);

-- Real Edge Entities table
CREATE TABLE Real_Edge_Entities (
    Edge_ID INTEGER NOT NULL,
    Edge_Entity_ID INTEGER NOT NULL,
    value REAL,
    FOREIGN KEY (Edge_ID) REFERENCES Edges(ID),
    FOREIGN KEY (Edge_Entity_ID) REFERENCES Edge_Entities(ID)
);

-- Text Edge Entities table
CREATE TABLE Text_Edge_Entities (
    Edge_ID INTEGER NOT NULL,
    Edge_Entity_ID INTEGER NOT NULL,
    value TEXT,
    FOREIGN KEY (Edge_ID) REFERENCES Edges(ID),
    FOREIGN KEY (Edge_Entity_ID) REFERENCES Edge_Entities(ID)
);

-- Int Edge Entities table
CREATE TABLE Int_Edge_Entities (
    Edge_ID INTEGER NOT NULL,
    Edge_Entity_ID INTEGER NOT NULL,
    value INTEGER,
    FOREIGN KEY (Edge_ID) REFERENCES Edges(ID),
    FOREIGN KEY (Edge_Entity_ID) REFERENCES Edge_Entities(ID)
);