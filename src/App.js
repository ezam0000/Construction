import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [imageUrl, setImageUrl] = useState('');
  const [file, setFile] = useState(null);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');

  const handleUrlChange = (e) => {
    setImageUrl(e.target.value);
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult('');
    const formData = new FormData();
    
    if (imageUrl) {
      formData.append('image_url', imageUrl);
    } else if (file) {
      formData.append('image', file);
    }

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(formatResult(response.data.result));
    } catch (error) {
      console.error('Error:', error);
      setError(`An error occurred: ${error.response?.data?.error || error.message}`);
    }
  };

  const formatResult = (text) => {
    return text.split('\n').map((line, index) => (
      <p key={index}>{line}</p>
    ));
  };

  const testBackend = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/test`);
      alert(response.data.message);
    } catch (error) {
      console.error('Error:', error);
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
        <button type="submit">Analyze</button>
      </form>
      <button onClick={testBackend}>Test Backend</button>
      {error && <div className="error-message">{error}</div>}
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
