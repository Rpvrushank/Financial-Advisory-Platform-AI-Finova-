from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import json
import subprocess
import os
import sys

class AdvisorSearchInput(BaseModel):
    """Input for advisor search"""
    location: str = Field(..., description="City and state for advisor search (e.g., 'Charlotte, NC')")

class MCPAdvisorTool(BaseTool):
    """Tool to search advisors via MCP server"""
    name: str = "mcp_advisor_search"
    description: str = "Search for financial advisors using MCP pre-made data server"
    args_schema: Type[BaseModel] = AdvisorSearchInput

    def _run(self, location: str) -> str:
        """Execute advisor search via MCP"""
        try:
           
            result = self._call_mcp_server_simple(location)
            
            if result:
                try:
                    
                    advisors = json.loads(result)
                    
                    if advisors:
                       
                        result_text = f"Found {len(advisors)} financial advisors in {location} from MCP server:\n\n"
                        
                        for i, advisor in enumerate(advisors, 1):
                            result_text += f"**ADVISOR {i}:**\n"
                            result_text += f"- Name: {advisor['name']}\n"
                            result_text += f"- Firm: {advisor['firm']}\n"
                            result_text += f"- CRD Number: {advisor['crd']}\n"
                            result_text += f"- Location: {location}\n"
                            result_text += f"- Source: MCP Pre-made Database\n\n"
                        
                        return result_text
                    else:
                        return f"No advisors found in MCP database for {location}."
                except json.JSONDecodeError:
                    
                    return f"MCP Server Response for {location}:\n{result}"
            else:
                return f"No response received from MCP server for {location}."
                
        except Exception as e:
            return f"Error connecting to MCP server: {str(e)}"

    def _call_mcp_server_simple(self, location: str) -> str:
        """Make a simple call to MCP server via subprocess"""
        try:
            
            server_path = os.path.join(os.path.dirname(__file__), "pre_made_advisor_server.py")
            
           
            
            import importlib.util
            spec = importlib.util.spec_from_file_location("mcp_server", server_path)
            mcp_server = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mcp_server)
            
          
            if hasattr(mcp_server, 'search_advisors'):
                result = mcp_server.search_advisors(location)
                print(f"Direct MCP call successful for {location}")
                return result
            else:
                return None
                
        except Exception as e:
            print(f"Error calling MCP server directly: {e}")
            
            
            try:
                return self._call_via_subprocess(location)
            except Exception as e2:
                print(f"Subprocess approach also failed: {e2}")
                return None

    def _call_via_subprocess(self, location: str) -> str:
        """Fallback: Call MCP server via subprocess"""
        try:
            server_path = os.path.join(os.path.dirname(__file__), "pre_made_advisor_server.py")
            
            
            test_script = f'''
import sys
sys.path.append("{os.path.dirname(server_path)}")
from pre_made_advisor_server import search_advisors
result = search_advisors("{location}")
print(result)
'''
            
            
            process = subprocess.run(
                [sys.executable, "-c", test_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if process.returncode == 0:
                return process.stdout.strip()
            else:
                print(f"Subprocess error: {process.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            print(f"Subprocess call failed: {e}")
            return None


def get_mcp_advisor_tool():
    """Factory function to create MCP advisor tool"""
    return MCPAdvisorTool()