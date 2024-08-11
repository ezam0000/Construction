import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [imageUrl, setImageUrl] = useState('');
  const [file, setFile] = useState(null);
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleUrlChange = (e) => {
    setImageUrl(e.target.value);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.size > 5 * 1024 * 1024) {
      setError('File size should not exceed 5MB');
    } else {
      setFile(selectedFile);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResult('');
    
    const formData = new FormData();
    if (imageUrl) {
      formData.append('image_url', imageUrl);
    } else if (file) {
      formData.append('image', file);
    }

    try {
      console.log('Sending request to:', `${process.env.REACT_APP_API_URL}/analyze`);
      
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(formatResult(response.data.result));
    } catch (error) {
      console.error('Full error:', error);
      if (error.response) {
        console.error('Error response:', error.response);
        setError(`Server error: ${error.response.status} ${error.response.statusText}`);
      } else if (error.request) {
        console.error('Error request:', error.request);
        setError('No response received from server');
      } else {
        console.error('Error message:', error.message);
        setError(`Error: ${error.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const formatResult = (text) => {
    // ... (keep the existing formatResult function)
  };

  const testBackend = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/test`);
      alert(response.data.message);
    } catch (error) {
      console.error('Full error:', error);
      if (error.response) {
        alert(`Error: ${error.response.status} ${error.response.statusText}`);
      } else if (error.request) {
        alert('No response received from server');
      } else {
        alert(`Error: ${error.message}`);
      }
    }
  };

  return (
    <div className="App">
      <h1>Construction Image Analyzer</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <input
            type="text"
            placeholder="Enter image URL"
            value={imageUrl}
            onChange={handleUrlChange}
          />
        </div>
        <div>
          <input
            type="file"
            onChange={handleFileChange}
          />
        </div>
        <button type="submit" disabled={isLoading || error}>
          {isLoading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>
      <button onClick={testBackend}>Test Backend</button>
      {error && <div className="error-message">{error}</div>}
      {isLoading && <div>Loading...</div>}
      {result && (
        <div className="analysis-result">
          <h2>Analysis Result:</h2>
          {result}
        </div>
      )}
    </div>
  );
}

export default App;
