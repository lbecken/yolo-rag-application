import { useState, useEffect } from 'react';
import { fetchDocuments, deleteDocument } from '../api/api';

function DocumentList() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  async function loadDocuments() {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchDocuments();
      setDocuments(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    if (!confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await deleteDocument(id);
      setDocuments(documents.filter(doc => doc.id !== id));
    } catch (err) {
      setError(err.message);
    }
  }

  function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  }

  if (loading) {
    return <div className="loading">Loading documents...</div>;
  }

  if (error) {
    return (
      <div className="error">
        <p>Error: {error}</p>
        <button onClick={loadDocuments}>Retry</button>
      </div>
    );
  }

  return (
    <div className="document-list">
      <h1>Documents</h1>

      {documents.length === 0 ? (
        <p className="empty-message">No documents uploaded yet. Go to Upload to add some!</p>
      ) : (
        <table className="documents-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Filename</th>
              <th>Chunks</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map(doc => (
              <tr key={doc.id}>
                <td>{doc.id}</td>
                <td>{doc.title}</td>
                <td>{doc.filename}</td>
                <td>{doc.chunkCount}</td>
                <td>{formatDate(doc.createdAt)}</td>
                <td>
                  <button
                    className="delete-btn"
                    onClick={() => handleDelete(doc.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <button className="refresh-btn" onClick={loadDocuments}>
        Refresh
      </button>
    </div>
  );
}

export default DocumentList;
