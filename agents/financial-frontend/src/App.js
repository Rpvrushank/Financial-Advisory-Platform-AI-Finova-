import React, { useState, useRef, useEffect } from 'react';
import { Send, DollarSign, TrendingUp, Users, FileText, Loader2, Sparkles } from 'lucide-react';

const FinancialAdvisoryPlatform = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeService, setActiveService] = useState('all');
  const messagesEndRef = useRef(null);

  // Add this new component after the existing state declarations
const [uploadedFiles, setUploadedFiles] = useState([]);
const [isUploading, setIsUploading] = useState(false);

// Add this function for file upload
const handleFileUpload = async (event) => {
  const files = Array.from(event.target.files);
  if (files.length === 0) return;

  setIsUploading(true);
  const formData = new FormData();
  
  files.forEach((file, index) => {
    formData.append(`file${index}`, file);
  });

  try {
    const response = await fetch('http://localhost:5002/api/upload', {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const result = await response.json();
      setUploadedFiles(prev => [...prev, ...result.uploaded_files]);
      
      // Show success message
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
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const services = [
    {
      id: 'investment',
      name: 'Investment Planning',
      icon: DollarSign,
      description: 'Portfolio strategies and investment advice',
      color: 'from-emerald-500 to-teal-600'
    },
    {
      id: 'advisor',
      name: 'Find Advisors',
      icon: Users,
      description: 'Discover qualified financial advisors',
      color: 'from-blue-500 to-indigo-600'
    },
    {
      id: 'research',
      name: 'Market Research',
      icon: TrendingUp,
      description: 'Latest market trends and analysis',
      color: 'from-purple-500 to-violet-600'
    },
    {
      id: 'all',
      name: 'Smart Routing',
      icon: Sparkles,
      description: 'AI determines the best approach',
      color: 'from-gradient-to-r from-orange-500 to-pink-600'
    }
  ];

  const quickPrompts = [
    "I want to invest $50,000 in a balanced portfolio",
    "Find me a financial advisor in Charlotte, NC",
    "What are the latest renewable energy investment trends?",
    "I'm 35, want to invest $100k for retirement"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
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
      const response = await simulateBackendCall(inputValue, activeService);
      
      const assistantMessage = {
        id: Date.now() + 1,
        text: response,
        sender: 'assistant',
        timestamp: new Date().toLocaleTimeString(),
        service: activeService
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: "I'm having trouble connecting to the financial analysis system. Please try again.",
        sender: 'assistant',
        timestamp: new Date().toLocaleTimeString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const simulateBackendCall = async (query, service) => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    if (service === 'investment' || query.toLowerCase().includes('invest')) {
      return `**INVESTMENT ANALYSIS**

**YOUR INVESTMENT PROFILE:**
- Investment Amount: $50,000
- Risk Tolerance: Moderate
- Time Horizon: Long-term

**BALANCED STRATEGY:**
- Asset Allocation: 60% Stocks, 40% Bonds
- Focus: Growth and value mix with bond stability
- Recommended ETFs: VTI (Total Stock), BND (Total Bond)
- Expected Return: 6-8% annually

**DOLLAR ALLOCATION:**
- Stocks/Equity: $30,000
- Bonds/Fixed Income: $20,000

**IMPLEMENTATION STEPS:**
1. Open a low-cost brokerage account (Vanguard, Fidelity, Schwab)
2. Start with broad market index funds/ETFs
3. Set up automatic monthly investments
4. Review and rebalance quarterly

**Powered by:** Investment Agent + Market Analysis`;
    }
    
    if (service === 'advisor' || query.toLowerCase().includes('advisor')) {
      return `**ADVISOR RECOMMENDATIONS**

**TOP ADVISOR MATCHES**

**1. John Smith, CFP**
- Firm: Smith Financial
- Credentials: CFP, 15 years experience
- Specialization: Retirement Planning
- Location: Charlotte, NC
- Match Score: 95%

**2. Sarah Johnson, CFA**
- Firm: Johnson Wealth
- Credentials: CFA, ChFC, 12 years experience
- Specialization: Portfolio Management
- Location: Charlotte, NC
- Match Score: 92%

**3. Amanda Williams, ChFC**
- Firm: Williams Advisory Group
- Credentials: ChFC, CFP, 18 years experience
- Specialization: Estate Planning
- Location: Charlotte, NC
- Match Score: 88%

**NEXT STEPS:**
- Schedule initial consultations
- Ask about fee structures
- Verify credentials with FINRA

**Powered by:** MCP Advisor Database + Location Matching`;
    }
    
    if (service === 'research' || query.toLowerCase().includes('market') || query.toLowerCase().includes('trends')) {
      return `**MARKET RESEARCH ANALYSIS**

**RENEWABLE ENERGY INVESTMENT TRENDS**

**Key Findings:**
- Clean energy investments reached $1.8T globally in 2024
- Solar and wind continue to dominate new capacity additions
- Battery storage market growing at 25% CAGR

**Investment Opportunities:**
- Renewable Energy ETFs: ICLN, QCLN, PBW
- Individual stocks: ENPH, SEDG, NEE
- Infrastructure REITs: BEP, NEP

**Market Outlook:**
- Government incentives driving growth
- Declining technology costs
- Corporate sustainability commitments

**Risk Factors:**
- Policy changes
- Supply chain disruptions
- Grid integration challenges

**Powered by:** Market Research Agent + Real-time Data`;
    }
    
    return `**COMPREHENSIVE FINANCIAL ANALYSIS**

**INVESTMENT STRATEGY:**
Based on your query, I recommend a diversified approach with 60% stocks and 40% bonds for moderate risk tolerance.

**ADVISOR RECOMMENDATIONS:**
Found 3 qualified advisors in your area specializing in your needs.

**MARKET INSIGHTS:**
Current market conditions favor long-term investment strategies with focus on sustainable sectors.

**Integrated Guidance:** This analysis combines insights from 3 specialized financial experts to provide comprehensive guidance tailored to your needs.

**Powered by:** Smart Routing + Multi-Agent Analysis`;
  };

  const handleQuickPrompt = (prompt) => {
    setInputValue(prompt);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">FinancialAI</h1>
                <p className="text-sm text-gray-500">Smart Financial Advisory Platform</p>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              Powered by Claude & CrewAI
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Services</h2>
              <div className="space-y-3">
                {services.map((service) => {
                  const Icon = service.icon;
                  return (
                    <button
                      key={service.id}
                      onClick={() => setActiveService(service.id)}
                      className={`w-full text-left p-3 rounded-lg transition-all duration-200 ${
                        activeService === service.id
                          ? 'bg-gradient-to-r ' + service.color + ' text-white shadow-md'
                          : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <Icon className="w-5 h-5" />
                        <div>
                          <div className="font-medium">{service.name}</div>
                          <div className={`text-sm ${
                            activeService === service.id ? 'text-white/80' : 'text-gray-500'
                          }`}>
                            {service.description}
                          </div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Start</h3>
              <div className="space-y-2">
                {quickPrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickPrompt(prompt)}
                    className="w-full text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors duration-200 text-gray-700"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 h-[600px] flex flex-col">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Financial Assistant</h3>
                    <p className="text-sm text-gray-500">
                      {activeService === 'all' ? 'Smart routing enabled' : 
                       services.find(s => s.id === activeService)?.name + ' mode'}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm text-gray-500">Online</span>
                  </div>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Sparkles className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Welcome to FinancialAI</h3>
                    <p className="text-gray-500 max-w-md mx-auto">
                      Get personalized investment advice, find qualified advisors, and access the latest market research. 
                      Ask me anything about your financial goals.
                    </p>
                  </div>
                )}

                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg px-4 py-3 ${
                        message.sender === 'user'
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                          : message.isError
                          ? 'bg-red-50 border border-red-200 text-red-800'
                          : 'bg-gray-50 text-gray-800'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{message.text}</div>
                      <div className={`text-xs mt-2 ${
                        message.sender === 'user' ? 'text-white/70' : 'text-gray-500'
                      }`}>
                        {message.timestamp}
                      </div>
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-50 rounded-lg px-4 py-3 flex items-center space-x-2">
                      <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                      <span className="text-gray-600">Analyzing your request...</span>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              <div className="p-4 border-t border-gray-200">
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSubmit(e)}
                    placeholder="Ask about investments, advisors, or market trends..."
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                    disabled={isLoading}
                  />
                  <button
                    onClick={handleSubmit}
                    disabled={isLoading || !inputValue.trim()}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    <Send className="w-4 h-4" />
                    <span>Send</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FinancialAdvisoryPlatform;