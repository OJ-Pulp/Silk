"""
This module provides the Agent class for connecting the Spider Backend.
It is responsible for answering user queries about the web database using the tools provided by the Spider class.
"""

import re
from config import PROMPT_DIR
from jinja2 import Environment, FileSystemLoader
from typing import Dict
from spider import Spider

class Agent:
    def __init__(self, db_name: str = "web.db", db_path: str = None):
        """
        Initialize the Agent for connecting the Spider Backend.
        Args:
            db_name (str): The name of the database file. Defaults to "web.db".
            db_path (str): The path to the database save file directory. If None, uses the current working directory.
        """
        self.spider = Spider(db_name, db_path)
        self.preprocessor = Preprocessor(edge_entities=self.spider.web.edge_entities,
                                         node_entities=self.spider.web.node_entities)

    def create_filter_prompt(self, query: str) -> str:
        """
        Create a prompt for the query using the preprocessor.
        
        Args:
            query (str): The input query string.
            
        Returns:
            str: The generated prompt string.
        """
        return self.preprocessor.create_prompt(query)
    
    def extract_sql_commands(self, text: str) -> Dict[str, str]:
        """
        Extract SQL commands from the text for Node and Edge tables.
        
        Args:
            text (str): The input text containing SQL commands. In the format returned by the "create_prompt" function.
            
        Returns:
            Dict[str, str]: A dictionary with keys "Node Filter" and "Edge Filter" containing the respective SQL commands.
        """
        return self.preprocessor.extract_sql_commands(text)
    
    
class Preprocessor:
    def __init__(self, edge_entities: Dict = None, node_entities: Dict = None):
        env = Environment(loader=FileSystemLoader(PROMPT_DIR))
        self.filter_prompt = env.get_template("filter.j2")
        self.edge_entities = edge_entities if edge_entities is not None else {}
        self.node_entities = node_entities if node_entities is not None else {}

    def create_prompt(self, query: str) -> str:
        """
        Create a prompt for the query using the filter template.
        
        Args:
            query (str): The input query string.
            
        Returns:
            str: The generated prompt string.
        """
        return self.filter_prompt.render(query=query, 
                                         edge_entities_str=self.edge_entities, 
                                         node_entities_str=self.node_entities, 
                                         operators_str=self.operators)
           
    def extract_sql_commands(text: str) -> Dict[str, str]:
        # Regex patterns to match Node and Edge SQL commands with optional WHERE clauses
        node_pattern = r"Node Table:\s*SELECT Index FROM Nodes WHERE\s*(.*?);"
        edge_pattern = r"Edge Table:\s*SELECT SourceID, TargetID FROM Edges WHERE\s*(.*?);"

        # Extracting Node SQL command
        node_match = re.search(node_pattern, text, re.DOTALL)
        node_sql = node_match.group(0) if node_match else "SELECT Index FROM Nodes;"

        # Extracting Edge SQL command
        edge_match = re.search(edge_pattern, text, re.DOTALL)
        if edge_match:
            edge_sql = edge_match.group(0)
        else:
            # Default query when no filter is provided
            edge_sql = "SELECT SourceID, TargetID FROM Edges;"

        return {
            "Node Filter" : node_sql, 
            "Edge Filter" : edge_sql
        }