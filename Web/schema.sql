-- Nodes table
CREATE TABLE IF NOT EXISTS Nodes (
    ID TEXT PRIMARY KEY, -- REQUIRED
    Index INTEGER, -- REQUIRED
    Name TEXT,
    Full_Product BOOLEAN,
    Company TEXT,
    Location TEXT,
    Metadata BLOB
);

-- Edges table
CREATE TABLE IF NOT EXISTS Edges (
    SourceID INTEGER, -- REQUIRED
    TargetID INTEGER, -- REQUIRED
    Base_Model BOOLEAN, 
    PRIMARY KEY (SourceID, TargetID) -- REQUIRED
);