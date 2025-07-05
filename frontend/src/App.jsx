import { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [descriptions, setDescriptions] = useState([]);
  const [imageUrl, setImageUrl] = useState('');
  const [output, setOutput] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.txt')) {
      setError('Only .txt files are allowed');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('https://image-description-mapper.onrender.com/upload-descriptions', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload descriptions');
      }

      const data = await response.json();
      setDescriptions(data.uploaded_descriptions);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleImageSubmit = async (e) => {
    e.preventDefault();
    if (!descriptions.length) {
      setError('Please upload descriptions file first');
      return;
    }
    if (!imageUrl.trim()) {
      setError('Please enter an image URL');
      return;
    }
  
    setIsProcessing(true);
    setError(null);
    setOutput(null); // Clear previous output
  
    try {
      const response = await fetch('https://image-description-mapper.onrender.com/map-description', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image_url: imageUrl }),
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to process image');
      }
  
      const data = await response.json();
      setOutput(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const formatOutput = (output) => {
    if (!output) return null;

    return (
      <div className="output-container">
        <div className="divider">====================================================================================================</div>
        <div className="image-url">PROCESSING IMAGE 1: {imageUrl}</div>
        <div className="divider">====================================================================================================</div>
        
        <div className="matched-section">
          <div className="matched-item">
            <strong>Matched Description Index:</strong> {output.matched_description_index}
          </div>
          <div className="matched-item">
            <strong>Matched Description:</strong> {output.matched_description}
          </div>
          <div className="matched-item">
            <strong>Reasoning:</strong> {output.reasoning}
          </div>
          <div className="matched-item">
            <strong>Confidence Score:</strong> {output.confidence_score}
          </div>
        </div>

        <div className="candidates-header">CANDIDATE DESCRIPTIONS:</div>
        <div className="divider">--------------------------------------------------</div>
        
        {output.candidate_descriptions?.map((candidate, index) => (
          <div key={index} className="candidate-section">
            <div className="candidate-item">
              <strong>Candidate Description Index:</strong> {candidate.candidate_description_index}
            </div>
            <div className="candidate-item">
              <strong>Candidate Description:</strong> {candidate.candidate_description}
            </div>
            <div className="candidate-item">
              <strong>Candidate Reasoning:</strong> {candidate.candidate_reasoning}
            </div>
            <div className="candidate-item">
              <strong>Confidence Score:</strong> {candidate.confidence_score}
            </div>
            <div className="divider">--------------------------------------------------</div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="app-container">
      <h1>Image Description Mapper</h1>
      
      <div className="panel-container">
        {/* Left Panel - Descriptions Upload */}
        <div className="panel left-panel">
          <h2>Upload Descriptions</h2>
          <p>Upload a text file with one description per line</p>
          
          <div className="upload-area" onClick={() => fileInputRef.current.click()}>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".txt"
              style={{ display: 'none' }}
            />
            <p>Click to select a .txt file</p>
            <p className="file-hint">or drag and drop here</p>
          </div>
          
          {descriptions.length > 0 && (
            <div className="descriptions-preview">
              <h3>Uploaded Descriptions ({descriptions.length})</h3>
              <ul>
                {descriptions.slice(0, 5).map((desc, index) => (
                  <li key={index}>{desc}</li>
                ))}
                {descriptions.length > 5 && <li>...and {descriptions.length - 5} more</li>}
              </ul>
            </div>
          )}
        </div>
        
        {/* Right Panel - Image URL Input */}
        <div className="panel right-panel">
          <h2>Process Image</h2>
          
          {descriptions.length === 0 ? (
            <div className="warning-message">
              <p>⚠️ Please upload descriptions file first</p>
            </div>
          ) : (
            <>
              <form onSubmit={handleImageSubmit} className="image-form">
                <div className="form-group">
                  <label htmlFor="imageUrl">Image URL:</label>
                  <input
                    type="text"
                    id="imageUrl"
                    value={imageUrl}
                    onChange={(e) => setImageUrl(e.target.value)}
                    placeholder="Enter image URL"
                  />
                </div>
                
                <button type="submit" disabled={isProcessing || !imageUrl.trim()}>
                  {isProcessing ? 'Processing...' : 'Process Image'}
                </button>
              </form>
              
              {error && <div className="error-message">{error}</div>}
            </>
          )}
          
          <div className="output-area">
            {isProcessing ? (
              <div className="loading-spinner"></div>
            ) : (
              output && formatOutput(output)
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;