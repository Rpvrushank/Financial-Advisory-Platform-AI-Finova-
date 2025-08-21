# FinancialAI Platform - Finova

A premium AI-powered financial advisory platform that provides personalized investment strategies, financial advisor recommendations, and market research using multiple specialized AI agents.

## Project Overview

FinancialAI is a comprehensive financial advisory system built with a modern tech stack that combines multiple AI agents to deliver expert financial guidance. The platform uses Agent Communication Protocol (ACP) to orchestrate different specialized agents, each focused on specific financial domains.

### Key Features

- **Multi-Agent Architecture**: Specialized AI agents for investment planning, advisor matching, and market research
- **Premium UI/UX**: Dark theme with glassmorphism effects and responsive design
- **Document Analysis**: Upload and analyze financial documents for personalized advice
- **Smart Routing**: Intelligent query routing to the most appropriate agent
- **Real-time Communication**: WebSocket-based agent communication with FastACP
- **Knowledge Integration**: Neo4j knowledge graph for enhanced financial insights

### Architecture

```
Frontend (React) → API Server (Flask) → ACP Agents → Specialized Tools
                                     ├── CrewAI Agents (Investment & Advisor)
                                     │   └── MCP Server (Advisor Database)
                                     └── SmolAgents (Market Research)
```

## Tech Stack

### Backend
- **Python 3.8+**
- **Flask** - API server and routing
- **CrewAI** - Agent framework for investment and advisor agents
- **SmolAgents** - Market research agent framework
- **ACP SDK** - Agent Communication Protocol
- **FastACP** - Agent orchestration and routing
- **MCP (Model Context Protocol)** - Pre-made advisor data server
- **Neo4j** - Knowledge graph database
- **LiteLLM** - Claude Sonnet 4 integration

### Frontend
- **React 18**
- **CSS3** with custom premium styling
- **Modern JavaScript (ES6+)**

### AI/ML
- **Claude Sonnet 4** (via Anthropic API)
- **DuckDuckGo Search** - Web research capabilities
- **Vector Database** - Document embedding and retrieval

## Project Structure

```
financial-advisory-platform/
├── agents/                     # ACP Agent implementations
├── financial-frontend/        # React frontend application
│   └── src/
│       ├── App.js             # Main React component
│       ├── App.css            # Premium styling
│       └── index.js           # React entry point
├── uploads/                   # Document upload storage
├── api_server.py             # Main Flask API server
├── crewai_agent.py          # Investment & Advisor agents
├── smolagent_agent.py       # Market research agent
├── fastacp.py               # Agent orchestration
├── vector_database.py       # Document analysis tools
├── neo4j_knowledge_tool.py  # Knowledge graph integration
├── mcp_advisor_tool.py      # MCP advisor tool integration
├── pre_made_advisor_server.py # MCP server for advisor database
├── client.py                # Agent testing client
├── smart_router.py          # Development testing
└── requirements.txt         # Python dependencies
```

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Node.js 16+ and npm
- Neo4j Database (optional, for knowledge graph features)

### API Keys
- **Anthropic API Key** - For Claude Sonnet 4 access
- Set in `.env` file as `ANTHROPIC_API_KEY`

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd financial-advisory-platform
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Create Environment File
```bash
# Create .env file in root directory
echo "ANTHROPIC_API_KEY=your_anthropic_api_key_here" > .env
```

#### Install Additional Requirements
```bash
# Core dependencies
pip install flask flask-cors
pip install crewai smolagents
pip install acp-sdk fastacp
pip install litellm
pip install neo4j
pip install python-dotenv
pip install nest-asyncio

# MCP (Model Context Protocol) dependencies
pip install mcp
pip install fastmcp
```

### 3. Frontend Setup
```bash
cd financial-frontend
npm install
npm start
```

## Running the Application

### Start All Services (Required Order)

#### Terminal 1: CrewAI Agents
```bash
python crewai_agent.py
```
This starts the investment planning and advisor finder agents on port 8000.

#### Terminal 2: SmolAgent
```bash
python smolagent_agent.py
```
This starts the market research agent on port 8001.

#### Terminal 3: API Server
```bash
python api_server.py
```
This starts the Flask API server on port 5001.

#### Terminal 4: Frontend
```bash
cd financial-frontend
npm start
```
This starts the React development server on port 3000.

### Access the Application
Open your browser and navigate to: `http://localhost:3000`

## MCP (Model Context Protocol) Integration

The platform uses MCP to provide structured access to pre-made advisor databases, enabling more reliable and consistent advisor recommendations.

### MCP Server Features
- **Pre-made Advisor Database**: Curated list of verified financial advisors
- **Location-Based Filtering**: Advisors organized by city (Charlotte, NC / New York, NY / Miami, FL)
- **Structured Data**: Consistent advisor profiles with credentials and firm information
- **Tool Integration**: Seamless integration with CrewAI agents via MCP tools

### MCP Server Data Structure
```json
{
  "name": "John Smith, CFP",
  "firm": "Smith Financial",
  "crd": "123456",
  "location": "Charlotte, NC"
}
```

### MCP Implementation
- **Server**: `pre_made_advisor_server.py` - FastMCP server with advisor search tool
- **Client Tool**: `mcp_advisor_tool.py` - CrewAI tool that calls MCP server
- **Fallback Strategy**: Combines MCP data with agent knowledge for comprehensive results

### Investment Agent (CrewAI)
- **Portfolio Analysis**: Risk assessment and asset allocation recommendations
- **Investment Strategies**: Personalized strategies based on goals and risk tolerance
- **Document Integration**: Analyzes uploaded financial documents
- **Knowledge Graph**: Leverages Neo4j for enhanced insights

### Advisor Finder Agent (CrewAI + MCP)
- **Location-Based Search**: Finds advisors in specific cities
- **MCP Integration**: Uses Model Context Protocol for pre-made advisor database
- **Credential Verification**: Checks CFP, CFA, ChFC certifications
- **Specialization Matching**: Matches advisors to client needs
- **Pre-made Database**: Curated advisor data for Charlotte, NY, Miami
- **Fallback Strategy**: Combines MCP data with general knowledge

### Market Research Agent (SmolAgents)
- **Real-time Research**: Web search capabilities via DuckDuckGo
- **Trend Analysis**: Market trends and sector analysis
- **News Integration**: Latest financial news and insights
- **Web Scraping**: Detailed webpage analysis

## API Endpoints

### Health Check
```
GET /api/health
```
Returns system status and agent initialization state.

### Chat Interface
```
POST /api/chat
{
  "message": "User query",
  "service": "investment|advisor|research|all"
}
```

### File Upload
```
POST /api/upload
Content-Type: multipart/form-data
```
Supports: PDF, DOC, DOCX, TXT files

### Agent Initialization
```
POST /api/initialize
```
Initializes ACP agents if not ready.

### File Listing
```
GET /api/files
```
Returns list of uploaded documents.

## Configuration

### Agent Routing Logic
The system uses intelligent keyword-based routing:

- **Investment queries**: "invest", "portfolio", "retirement", "savings"
- **Advisor queries**: "find advisor", "financial planner", "cfp"
- **Market queries**: "market", "trends", "research", "analysis"

### Environment Variables
```bash
ANTHROPIC_API_KEY=your_api_key_here

```

## Development & Testing

### Test Individual Agents
```bash
python client.py
```

### Test Agent Orchestration
```bash
python smart_router.py
```

### Debug Mode
Set `debug=True` in `api_server.py` for detailed logging.

## Troubleshooting

### Common Issues

1. **Agents Not Initialized**
   - Ensure all three servers are running in correct order
   - Click "Initialize Agents" in the UI
   - Check API key configuration

2. **Import Errors**
   - Verify all dependencies installed: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Port Conflicts**
   - Default ports: 8000 (CrewAI), 8001 (SmolAgent), 5001 (API), 3000 (Frontend)
   - Modify ports in respective files if conflicts occur

4. **Frontend Issues**
   - Clear browser cache
   - Restart React development server
   - Check console for JavaScript errors

### Logs and Debugging
- Agent logs appear in respective terminal windows
- Flask API logs show request/response details
- Browser console shows frontend errors

## Production Deployment

### Backend
- Use production WSGI server (Gunicorn)
- Configure proper environment variables
- Set up process management (PM2/systemd)
- Implement proper logging

### Frontend
```bash
npm run build
```
Serve static files via nginx or similar.

### Database
- Configure Neo4j for production use
- Set up proper backup strategies
- Implement connection pooling

## Contributing

1. Follow existing code structure and naming conventions
2. Add comprehensive error handling
3. Update documentation for new features
4. Test all agent interactions thoroughly

## License

[Specify your license here]

## Support

For issues or questions:
1. Check troubleshooting section
2. Review agent logs for specific errors
3. Ensure all prerequisites are met
4. Verify API key configuration