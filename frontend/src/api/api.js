const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api';

export async function fetchDocuments() {
  const response = await fetch(`${API_BASE_URL}/documents`);
  if (!response.ok) {
    throw new Error(`Failed to fetch documents: ${response.statusText}`);
  }
  return response.json();
}

export async function uploadDocument(file, title) {
  const formData = new FormData();
  formData.append('file', file);
  if (title) {
    formData.append('title', title);
  }

  const response = await fetch(`${API_BASE_URL}/documents`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ title: response.statusText }));
    throw new Error(error.title || 'Failed to upload document');
  }
  return response.json();
}

export async function deleteDocument(id) {
  const response = await fetch(`${API_BASE_URL}/documents/${id}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error(`Failed to delete document: ${response.statusText}`);
  }
}

export async function askQuestion(question, documentIds) {
  const response = await fetch(`${API_BASE_URL}/qa`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question,
      documentIds,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(error.message || 'Failed to get answer');
  }
  return response.json();
}
