from pathlib import Path
import os

class FinancialKnowledgeGraph:
    def __init__(self, neo4j_password, uploads_directory="./uploads"):
        self.password = neo4j_password
        self.uploads_directory = Path(uploads_directory)
        self.uploads_directory.mkdir(exist_ok=True)
        print(f"FinancialKnowledgeGraph initialized with uploads dir: {uploads_directory}")
    
    @property
    def has_uploaded_data(self):
        """Check if there are any uploaded files"""
        if self.uploads_directory.exists():
            return any(self.uploads_directory.iterdir())
        return False
    
    def search_knowledge(self, query):
        """Basic search implementation with debugging"""
        try:
            print(f"=== FinancialKnowledgeGraph.search_knowledge ===")
            print(f"Query: {query}")
            
            uploaded_content = []
            
            print(f"Checking uploads directory: {self.uploads_directory}")
            print(f"Directory exists: {self.uploads_directory.exists()}")
            
            if self.has_uploaded_data:
                print("Processing uploaded files...")
                files = list(self.uploads_directory.iterdir())
                print(f"Found {len(files)} files: {[f.name for f in files]}")
                
                for file_path in files:
                    if file_path.is_file():
                        print(f"Processing file: {file_path.name}")
                        uploaded_content.append({
                            "source": file_path.name,
                            "text": f"Investment analysis from {file_path.name}: This document contains financial planning information relevant to: {query}",
                            "relevance_score": 0.8
                        })
            
            result = {
                "uploaded_content": uploaded_content,
                "graph_relationships": [
                    {"name": "Portfolio Analysis", "type": "Strategy"},
                    {"name": "Risk Assessment", "type": "Analysis"}
                ]
            }
            
            print(f"Returning result with {len(uploaded_content)} uploaded items")
            return result
            
        except Exception as e:
            print(f"ERROR in search_knowledge: {e}")
            import traceback
            traceback.print_exc()
            return {
                "uploaded_content": [],
                "graph_relationships": []
            }
    def get_investment_recommendations(self, risk_level, amount, time_horizon):
        """Basic investment recommendations"""
        return {
            "recommended_strategy": {
                "name": f"{risk_level} Risk Investment Strategy",
                "description": f"A {risk_level.lower()} risk approach suitable for {time_horizon} investing with ${amount:,.0f}",
                "risk_level": risk_level,
                "best_for": f"{time_horizon} investors with {risk_level.lower()} risk tolerance"
            }
        }