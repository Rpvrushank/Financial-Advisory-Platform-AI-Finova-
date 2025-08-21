import React, { useState, useRef, useEffect } from 'react';
import './App.css';

const FinancialAdvisoryPlatform = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeService, setActiveService] = useState('all');
  const [apiStatus, setApiStatus] = useState('unknown');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkApiHealth();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownOpen && !event.target.closest('.services-dropdown')) {
        setDropdownOpen(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [dropdownOpen]);

  const services = [
    { id: 'all', name: 'Smart Routing' },
    { id: 'investment', name: 'Investment Planning' },
    { id: 'advisor', name: 'Find Advisors' },
    { id: 'research', name: 'Market Research' }
  ];

  const quickPrompts = [
    "I want to invest $50,000 in a balanced portfolio",
    "Find me a financial advisor in Charlotte, NC",
    "What are the latest renewable energy investment trends?",
    "I'm 35, want to invest $100k for retirement"
  ];

  const checkApiHealth = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/health');
      if (response.ok) {
        const data = await response.json();
        setApiStatus(data.agents_initialized ? 'connected' : 'agents_not_ready');
      } else {
        setApiStatus('api_down');
      }
    } catch (error) {
      setApiStatus('api_down');
    }
  };

  const initializeAgents = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/initialize', {
        method: 'POST',
      });
      
      if (response.ok) {
        setApiStatus('connected');
        return true;
      } else {
        setApiStatus('initialization_failed');
        return false;
      }
    } catch (error) {
      setApiStatus('api_down');
      return false;
    }
  };

  const callBackendAPI = async (query, service) => {
    try {
      const response = await fetch('http://localhost:5001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: query,
          service: service
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    }
  };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    setIsUploading(true);
    const formData = new FormData();
    
    files.forEach((file, index) => {
      formData.append(`file${index}`, file);
    });

    try {
      const response = await fetch('http://localhost:5001/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadedFiles(prev => [...prev, ...result.uploaded_files]);
        
        const successMessage = {
          id: Date.now(),
          text: `Successfully uploaded ${files.length} file(s) to knowledge base. You can now ask questions about these documents.`,
          sender: 'assistant',
          timestamp: new Date().toLocaleTimeString(),
          isSuccess: true
        };
        setMessages(prev => [...prev, successMessage]);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      const errorMessage = {
        id: Date.now(),
        text: "Failed to upload files. Please try again.",
        sender: 'assistant',
        timestamp: new Date().toLocaleTimeString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSubmit = async (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { 
      id: Date.now(), 
      text: inputValue, 
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await callBackendAPI(inputValue, activeService);
      
      const assistantMessage = {
        id: Date.now() + 1,
        text: response,
        sender: 'assistant',
        timestamp: new Date().toLocaleTimeString(),
        service: activeService
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      let errorText = "I'm having trouble connecting to the financial analysis system.";
      
      if (error.message.includes('Agents not initialized')) {
        errorText = "The financial agents are not ready. Please make sure your ACP servers are running and try clicking 'Initialize Agents'.";
      } else if (error.message.includes('Failed to fetch')) {
        errorText = "Cannot connect to the API server. Please make sure the API server is running (python api_server.py).";
      }

      const errorMessage = {
        id: Date.now() + 1,
        text: errorText,
        sender: 'assistant',
        timestamp: new Date().toLocaleTimeString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickPrompt = (prompt) => {
    setInputValue(prompt);
    // Auto-focus the input after setting the prompt
    setTimeout(() => {
      const input = document.querySelector('input[type="text"]');
      if (input) input.focus();
    }, 100);
  };

  const handleServiceSelect = (service) => {
    setActiveService(service.id);
    setDropdownOpen(false);
  };

  const getStatusInfo = () => {
    switch (apiStatus) {
      case 'connected':
        return { text: 'All systems online', color: '#10B981', isOnline: true };
      case 'agents_not_ready':
        return { text: 'Agents not initialized', color: '#F59E0B', isOnline: false };
      case 'api_down':
        return { text: 'API server offline', color: '#EF4444', isOnline: false };
      case 'initialization_failed':
        return { text: 'Agent initialization failed', color: '#EF4444', isOnline: false };
      default:
        return { text: 'Checking status...', color: '#6B7280', isOnline: false };
    }
  };

  const currentService = services.find(s => s.id === activeService) || services[0];
  const status = getStatusInfo();

  const PaperclipIcon = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21.44 11.05L12.25 2.41a1.93 1.93 0 0 0-2.84 0L.62 11.05c-.83.93-.24 2.45.93 2.45h1.93v7.5a1 1 0 0 0 1 1h15a1 1 0 0 0 1-1v-7.5h1.93c1.17 0 1.76-1.52.93-2.45Z"/>
      <path d="M12 10v9"/>
      <path d="M8 14l4-4 4 4"/>
    </svg>
  );

  const BackIcon = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M19 12H5"/>
      <path d="M12 19l-7-7 7-7"/>
    </svg>
  );

  const LoadingDots = () => (
    <div className="loading-dots">
      <div className="loading-dot"></div>
      <div className="loading-dot"></div>
      <div className="loading-dot"></div>
    </div>
  );

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">F</div>
            <div>
              <h1>Finova</h1>
              <p>Premium Advisory Platform</p>
            </div>
          </div>
          <div className="header-status">
            <div className="status-indicator"></div>
            <span>Powered by Claude & CrewAI</span>
          </div>
        </div>
      </header>

      <div className="main-content">
        <div className="chat-container">
          <div className="chat-header">
            <h3 className="chat-title">Financial Assistant</h3>
            <div className="chat-status">
              <div className={`status-dot ${status.isOnline ? 'online' : 'offline'}`}></div>
              <span>{status.isOnline ? 'Online' : 'Offline'}</span>
            </div>
          </div>

          <div className="messages">
            {messages.length === 0 && (
              <div className="welcome">
                <h2>Welcome to Finova - A FinancialAI</h2>
                <p>Get personalized investment advice, find qualified advisors, and access the latest market research with our premium AI-powered platform.</p>
                
                <div className="welcome-controls">
                  <div className="service-selector">
                    <label>Choose your service:</label>
                    <div className="services-dropdown">
                      <div 
                        className={`dropdown-trigger ${dropdownOpen ? 'active' : ''}`}
                        onClick={() => setDropdownOpen(!dropdownOpen)}
                      >
                        <span>{currentService.name}</span>
                        <div className="dropdown-arrow"></div>
                      </div>
                      <div className={`dropdown-menu ${dropdownOpen ? 'show' : ''}`}>
                        {services.map((service) => (
                          <div
                            key={service.id}
                            className={`dropdown-item ${activeService === service.id ? 'active' : ''}`}
                            onClick={() => handleServiceSelect(service)}
                          >
                            {service.name}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="prompts-section">
                    <label>Or try these examples:</label>
                    <div className="quick-prompts">
                      {quickPrompts.map((prompt, index) => (
                        <button
                          key={index}
                          className="prompt-btn"
                          onClick={() => handleQuickPrompt(prompt)}
                        >
                          {prompt}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {apiStatus !== 'connected' }
              </div>
            )}

            {messages.map((message) => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className={`message-content ${message.isError ? 'error' : ''} ${message.isSuccess ? 'success' : ''}`}>
                  <div className="message-text">{message.text}</div>
                  <div className="timestamp">{message.timestamp}</div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="message assistant">
                <div className="message-content">
                  <div className="loading">
                    <span>Analyzing your request</span>
                    <LoadingDots />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            <form onSubmit={(e) => {
              e.preventDefault();
              handleSubmit(e);
            }} style={{ display: 'flex', alignItems: 'center', gap: '16px', width: '100%' }}>
              <div className="input-container">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={
                    apiStatus === 'connected' 
                      ? "Ask about investments, advisors, or market trends..." 
                      : "Please start the required servers first..."
                  }
                  disabled={isLoading || apiStatus !== 'connected'}
                />
                <button 
                  className="file-upload-btn" 
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    document.getElementById('file-input').click();
                  }}
                  disabled={isUploading}
                >
                  <PaperclipIcon />
                  {uploadedFiles.length > 0 && (
                    <span className="uploaded-files-indicator">{uploadedFiles.length}</span>
                  )}
                </button>
                <input
                  type="file"
                  id="file-input"
                  className="file-input"
                  multiple
                  accept=".pdf,.doc,.docx,.txt"
                  onChange={handleFileUpload}
                />
              </div>
              <button 
                className={`send-btn ${apiStatus === 'connected' ? 'ready' : 'disabled'}`}
                type="submit"
                disabled={isLoading || !inputValue.trim() || apiStatus !== 'connected'}
              >
                Send
              </button>
            </form>
          </div>
        </div>
      </div>

      <div className="system-status">
        <h3>System Status</h3>
        <div className="status-item">
          <div className={`status-dot ${status.isOnline ? 'online' : 'offline'}`}></div>
          <span>{status.text}</span>
        </div>
        {apiStatus === 'agents_not_ready' && (
          <button 
            onClick={initializeAgents} 
            className="init-btn"
            disabled={isLoading}
          >
            Initialize Agents
          </button>
        )}
        {apiStatus === 'api_down' && (
          <div className="status-help">
            <p>Start the API server:</p>
            <code>python api_server.py</code>
          </div>
        )}
      </div>
    </div>
  );
};

export default FinancialAdvisoryPlatform;