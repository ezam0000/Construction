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
    setFile(e.target.files[0]);
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
  
    console.log('Sending request to:', `${process.env.REACT_APP_API_URL}/analyze`);
    console.log('FormData:', formData);
  
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setResult(formatResult(response.data.result));
    } catch (error) {
      console.error('Full error:', error);
      console.error('Error response:', error.response);
      setError(`An error occurred: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };
  

  const formatResult = (text) => {
    const paragraphs = text.split('\n\n');
    const sections = {
      'Structural Components': [],
      'Materials': [],
      'Condition': [],
      'Code Compliance': [],
      'Other Observations': []
    };

    paragraphs.forEach(para => {
      if (para.toLowerCase().includes('structural') || para.toLowerCase().includes('foundation')) {
        sections['Structural Components'].push(para);
      } else if (para.toLowerCase().includes('material')) {
        sections['Materials'].push(para);
      } else if (para.toLowerCase().includes('condition') || para.toLowerCase().includes('state')) {
        sections['Condition'].push(para);
      } else if (para.toLowerCase().includes('code') || para.toLowerCase().includes('compliance') || para.toLowerCase().includes('regulation')) {
        sections['Code Compliance'].push(para);
      } else {
        sections['Other Observations'].push(para);
      }
    });

    return Object.entries(sections).map(([title, paras]) => {
      if (paras.length === 0) return null;
      return (
        <div key={title} className="analysis-section">
          <h3>{title}</h3>
          {paras.map((para, index) => (
            <p key={index}>{para}</p>
          ))}
        </div>
      );
    });
  };

  const testBackend = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/test`);
      alert(response.data.message);
    } catch (error) {
      console.error('Full error:', error);
      console.error('Error response:', error.response);
      alert(`Error: ${error.message}`);
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
        <button type="submit" disabled={isLoading}>
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
