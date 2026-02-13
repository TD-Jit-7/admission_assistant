import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      content: '👋 Hello! I\'m your University Admission Assistant. I can help you find the right university in Bangladesh based on your preferences. What would you like to know?'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to chat
    const userMessage = { role: 'user', content: input };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    try {
      // Build conversation history (last 8 messages = 4 exchanges)
      const conversationHistory = updatedMessages
        .slice(-8)
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }));

      // Call backend API with conversation history
      const response = await axios.post('https://admission-assistant-api.onrender.com/chat', {
        message: input,
        conversation_history: conversationHistory
      }, {
        timeout: 60000
      });

      if (response && response.data && response.data.response) {
        const aiMessage = {
          role: 'ai',
          content: response.data.response
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Error details:', error);
      let errorMsg = '❌ Sorry, I\'m having trouble connecting to the server.';
      
      if (error.code === 'ECONNABORTED') {
        errorMsg = '⏱️ Server is waking up (Render free tier). Please wait 30 seconds and try again.';
      } else if (error.response) {
        errorMsg = `❌ Server error: ${error.response.status}. ${error.response.data?.error || ''}`;
      } else if (error.request) {
        errorMsg = '❌ Cannot reach the server. Please check if the backend is deployed and running.';
      }
      
      const errorMessage = {
        role: 'ai',
        content: errorMsg
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="App">
      <div className="chat-container">
        <div className="chat-header">
          <h1>🎓 University Admission Assistant</h1>
          <p>Your guide to Bangladeshi universities</p>
        </div>

        <div className="messages-container">
          {messages && messages.length > 0 && messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-role">
                  {msg.role === 'user' ? 'You' : 'AI Assistant'}
                </div>
                <div className="message-text">{msg.content}</div>
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="message ai">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="message-role">AI Assistant</div>
                <div className="message-text typing">Typing...</div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about universities, departments, or admission requirements..."
            disabled={loading}
          />
          <button onClick={sendMessage} disabled={loading || !input.trim()}>
            {loading ? '⏳' : '📤'} Send
          </button>
        </div>

        <div className="example-queries">
          <p>Try asking:</p>
          <button onClick={() => setInput("I want to study CSE, which university should I choose?")} disabled={loading}>
            CSE recommendations
          </button>
          <button onClick={() => setInput("Which universities have open admissions?")} disabled={loading}>
            Open admissions
          </button>
          <button onClick={() => setInput("My GPA is 4.5 in science, what are my options?")} disabled={loading}>
            Based on GPA
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;