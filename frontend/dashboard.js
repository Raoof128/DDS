const apiUrl = window.location.origin;

const imageInput = document.getElementById('imageInput');
const videoInput = document.getElementById('videoInput');
const audioInput = document.getElementById('audioInput');
const analyzeBtn = document.getElementById('analyzeBtn');

const visionScoreEl = document.getElementById('visionScore');
const temporalScoreEl = document.getElementById('temporalScore');
const audioScoreEl = document.getElementById('audioScore');
const metadataScoreEl = document.getElementById('metadataScore');
const deepfakeScoreEl = document.getElementById('deepfakeScore');
const classificationEl = document.getElementById('classification');
const riskLevelEl = document.getElementById('riskLevel');
const confidenceEl = document.getElementById('confidence');
const explainabilityEl = document.getElementById('explainability');

async function analyze() {
  const formData = new FormData();
  if (imageInput.files[0]) formData.append('image', imageInput.files[0]);
  if (videoInput.files[0]) formData.append('video', videoInput.files[0]);
  if (audioInput.files[0]) formData.append('audio', audioInput.files[0]);

  if (!formData.has('image') && !formData.has('video') && !formData.has('audio')) {
    alert('Please upload at least one media file.');
    return;
  }

  const response = await fetch(`${apiUrl}/analyze_multimodal/`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    alert(`Analysis failed: ${error.detail}`);
    return;
  }

  const data = await response.json();
  visionScoreEl.textContent = `Score: ${data.components.vision_score.toFixed(2)}`;
  temporalScoreEl.textContent = `Score: ${data.components.temporal_score.toFixed(2)}`;
  audioScoreEl.textContent = `Score: ${data.components.audio_score.toFixed(2)}`;
  metadataScoreEl.textContent = `Score: ${data.components.metadata_score.toFixed(2)}`;
  deepfakeScoreEl.textContent = `Deepfake Score: ${data.deepfake_score.toFixed(2)}`;
  classificationEl.textContent = `Classification: ${data.classification}`;
  riskLevelEl.textContent = `Risk Level: ${data.risk_level}`;
  confidenceEl.textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
  explainabilityEl.textContent = JSON.stringify(data, null, 2);
}

analyzeBtn.addEventListener('click', analyze);
