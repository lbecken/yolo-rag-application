import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadDocument } from '../api/api';

function Upload() {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();

    if (!file) {
      setError('Please select a file');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      setSuccess(null);

      const result = await uploadDocument(file, title);

      setSuccess(`Document uploaded successfully! ID: ${result.documentId}, Chunks: ${result.numChunks}`);
      setFile(null);
      setTitle('');

      // Reset file input
      e.target.reset();

      // Navigate to documents list after a delay
      setTimeout(() => {
        navigate('/');
      }, 2000);

    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  function handleFileChange(e) {
    const selectedFile = e.target.files[0];
    if (selectedFile && !selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are allowed');
      setFile(null);
      e.target.value = '';
      return;
    }
    setError(null);
    setFile(selectedFile);
  }

  return (
    <div className="upload-page">
      <h1>Upload Document</h1>

      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label htmlFor="file">PDF File *</label>
          <input
            type="file"
            id="file"
            accept=".pdf"
            onChange={handleFileChange}
            disabled={uploading}
          />
          {file && (
            <p className="file-info">
              Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
            </p>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="title">Title (optional)</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter document title"
            disabled={uploading}
          />
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <button type="submit" disabled={uploading || !file}>
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </form>
    </div>
  );
}

export default Upload;
