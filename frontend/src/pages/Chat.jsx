import { useState, useEffect } from 'react';
import { fetchDocuments, askQuestion } from '../api/api';

function Chat() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [docsLoading, setDocsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  async function loadDocuments() {
    try {
      setDocsLoading(true);
      const data = await fetchDocuments();
      setDocuments(data);
    } catch (err) {
      setError(`Failed to load documents: ${err.message}`);
    } finally {
      setDocsLoading(false);
    }
  }

  function handleDocSelect(docId) {
    setSelectedDocs(prev => {
      if (prev.includes(docId)) {
        return prev.filter(id => id !== docId);
      } else {
        return [...prev, docId];
      }
    });
  }

  function selectAll() {
    setSelectedDocs(documents.map(doc => doc.id));
  }

  function selectNone() {
    setSelectedDocs([]);
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (!question.trim()) {
      return;
    }

    if (selectedDocs.length === 0) {
      setError('Please select at least one document');
      return;
    }

    const userMessage = {
      type: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setQuestion('');
    setError(null);
    setLoading(true);

    try {
      const response = await askQuestion(question, selectedDocs);

      const assistantMessage = {
        type: 'assistant',
        content: response.answer,
        citations: response.citations || [],
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err.message);
      const errorMessage = {
        type: 'error',
        content: `Error: ${err.message}`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  }

  function getDocumentTitle(docId) {
    const doc = documents.find(d => d.id === docId);
    return doc ? doc.title : `Document ${docId}`;
  }

  function clearChat() {
    setMessages([]);
  }

  return (
    <div className="chat-page">
      <div className="chat-sidebar">
        <h2>Select Documents</h2>

        {docsLoading ? (
          <p>Loading documents...</p>
        ) : documents.length === 0 ? (
          <p>No documents available. Upload some first!</p>
        ) : (
          <>
            <div className="select-buttons">
              <button type="button" onClick={selectAll}>All</button>
              <button type="button" onClick={selectNone}>None</button>
            </div>

            <div className="document-checkboxes">
              {documents.map(doc => (
                <label key={doc.id} className="doc-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedDocs.includes(doc.id)}
                    onChange={() => handleDocSelect(doc.id)}
                  />
                  <span className="doc-title">{doc.title}</span>
                  <span className="doc-chunks">({doc.chunkCount} chunks)</span>
                </label>
              ))}
            </div>
          </>
        )}
      </div>

      <div className="chat-main">
        <div className="chat-header">
          <h1>Ask Questions</h1>
          {messages.length > 0 && (
            <button type="button" onClick={clearChat} className="clear-btn">
              Clear Chat
            </button>
          )}
        </div>

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-chat">
              <p>Select documents and ask a question to get started.</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className={`message ${msg.type}`}>
                <div className="message-content">
                  {msg.content}
                </div>

                {msg.type === 'assistant' && msg.citations && msg.citations.length > 0 && (
                  <div className="citations">
                    <strong>Citations:</strong>
                    <ul>
                      {msg.citations.map((citation, citIndex) => (
                        <li key={citIndex}>
                          <span className="citation-doc">
                            {getDocumentTitle(citation.documentId)}
                          </span>
                          {citation.pageNumber && (
                            <span className="citation-page">
                              {' '}(Page {citation.pageNumber})
                            </span>
                          )}
                          {citation.content && (
                            <p className="citation-text">"{citation.content}"</p>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))
          )}

          {loading && (
            <div className="message assistant loading">
              <div className="message-content">Thinking...</div>
            </div>
          )}
        </div>

        {error && <div className="chat-error">{error}</div>}

        <form onSubmit={handleSubmit} className="chat-form">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading || selectedDocs.length === 0}
          />
          <button type="submit" disabled={loading || !question.trim() || selectedDocs.length === 0}>
            {loading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Chat;
