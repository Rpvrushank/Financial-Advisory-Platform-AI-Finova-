from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import nest_asyncio
from acp_sdk.client import Client
from fastacp import AgentCollection, ACPCallingAgent
from smolagents import LiteLLMModel
import os
from dotenv import load_dotenv
import threading
from concurrent.futures import ThreadPoolExecutor
from werkzeug.utils import secure_filename
import os
from pathlib import Path

# Add this after your existing imports
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

# Create uploads directory if it doesn't exist
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

load_dotenv()
nest_asyncio.apply()

app = Flask(__name__)
CORS(app)

# Initialize the model
model = LiteLLMModel(
    model_id="anthropic/claude-sonnet-4-20250514",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Global variables
acp_agent = None
main_loop = None
executor = ThreadPoolExecutor(max_workers=1)

def start_event_loop():
    """Start the main event loop in a separate thread"""
    global main_loop
    main_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main_loop)
    main_loop.run_forever()

# Start the event loop thread
loop_thread = threading.Thread(target=start_event_loop, daemon=True)
loop_thread.start()

async def initialize_agents_async():
    """Initialize the ACP agents"""
    global acp_agent
    
    try:
        # Create persistent clients
        financial_client = Client(base_url="http://localhost:8000")
        market_client = Client(base_url="http://localhost:8001")
        
        # Start the clients
        await financial_client.__aenter__()
        await market_client.__aenter__()
        
        # Create agent collection
        agent_collection = await AgentCollection.from_acp(financial_client, market_client)
        acp_agents = {agent.name: {'agent': agent, 'client': client} for client, agent in agent_collection.agents}
        
        acp_agent = ACPCallingAgent(acp_agents=acp_agents, model=model)
        print("✅ ACP agents initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize agents: {e}")
        return False

def run_async_in_loop(coro):
    """Run async function in the main event loop"""
    future = asyncio.run_coroutine_threadsafe(coro, main_loop)
    return future.result()

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests from frontend with document enhancement"""
    try:
        data = request.get_json()
        query = data.get('message', '')
        service = data.get('service', 'all')
        
        if not query.strip():
            return jsonify({'error': 'Empty message'}), 400
        
        if acp_agent is None:
            return jsonify({'error': 'Agents not initialized. Please initialize agents first.'}), 500
        
        # Check if we have uploaded files and enhance the query
        enhanced_query = enhance_query_with_documents(query)
        
        # Run the agent call in the main event loop
        response = run_async_in_loop(acp_agent.run(enhanced_query))
        
        return jsonify({
            'response': response,
            'service': service,
            'timestamp': '12:00 PM'
        })
            
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

def enhance_query_with_documents(query):
    """Enhance query with context from uploaded documents"""
    upload_dir = Path(UPLOAD_FOLDER)
    
    # Check if uploads directory exists and has files
    if upload_dir.exists() and any(upload_dir.iterdir()):
        file_list = [f.name for f in upload_dir.iterdir() if f.is_file()]
        
        if file_list:
            # Add context about available documents to the query
            file_context = f"\\n\\nAvailable uploaded documents: {', '.join(file_list)}. Please analyze these documents if they're relevant to the user's question about: {query}"
            enhanced_query = query + file_context
            return enhanced_query
    
    return query

def get_uploaded_files_list():
    """Get list of uploaded files for reference"""
    upload_dir = Path(UPLOAD_FOLDER)
    if upload_dir.exists():
        return [f.name for f in upload_dir.iterdir() if f.is_file()]
    return []

@app.route('/api/files', methods=['GET'])
def list_uploaded_files():
    """Get list of uploaded files"""
    try:
        files = get_uploaded_files_list()
        return jsonify({
            'files': files,
            'count': len(files)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'agents_initialized': acp_agent is not None
    })

@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize agents endpoint"""
    try:
        success = run_async_in_loop(initialize_agents_async())
        if success:
            return jsonify({'status': 'success', 'message': 'Agents initialized'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to initialize agents'}), 500
    except Exception as e:
        print(f"Error initializing agents: {e}")
        return jsonify({'status': 'error', 'message': f'Initialization failed: {str(e)}'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and add to knowledge base"""
    try:
        if 'file0' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        uploaded_files = []
        file_index = 0
        
        while f'file{file_index}' in request.files:
            file = request.files[f'file{file_index}']
            
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                uploaded_files.append(filename)
                
                # Process file for knowledge base
                try:
                    process_uploaded_file(filepath)
                    print(f"✅ Processed {filename} for knowledge base")
                except Exception as e:
                    print(f"⚠️ Failed to process {filename}: {e}")
                
            file_index += 1
        
        if uploaded_files:
            return jsonify({
                'status': 'success',
                'uploaded_files': uploaded_files,
                'message': f'Successfully uploaded and processed {len(uploaded_files)} files'
            })
        else:
            return jsonify({'error': 'No valid files uploaded'}), 400
            
    except Exception as e:
        print(f"Error in file upload: {e}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

def process_uploaded_file(filepath):
    """Process uploaded file and add to knowledge base"""
    # This function will extract text and add to your vector database
    # Implementation depends on your specific vector_database.py setup
    pass

if __name__ == '__main__':
    print("🚀 Starting Financial Advisory API Server...")
    print("📡 Make sure your ACP servers are running:")
    print("   - Terminal 1: python crewai_agent.py (port 8000)")
    print("   - Terminal 2: python smolagent_agent.py (port 8001)")
    print("\n🌐 API Server starting on http://localhost:5001")
    
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)