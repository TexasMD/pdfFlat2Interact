document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('startBtn');
  const stopBtn = document.getElementById('stopBtn');
  const saveKeyBtn = document.getElementById('saveKeyBtn');
  const apiKeyInput = document.getElementById('apiKey');
  const statusText = document.getElementById('statusText');
  const scannedCount = document.getElementById('scannedCount');
  const matchCount = document.getElementById('matchCount');
  const progressBar = document.getElementById('progressBar');
  const geminiConfig = document.getElementById('geminiConfig');
  const preFilterCheckbox = document.getElementById('preFilter');
  const classMethodRadios = document.getElementsByName('classMethod');
  const scanModeRadios = document.getElementsByName('scanMode');
  const slideshowInstr = document.querySelector('.slideshow-instr');
  const downloadOcrBtn = document.getElementById('downloadOcrBtn');

  // Load saved settings
  chrome.storage.local.get(['geminiApiKey', 'scanMode', 'classMethod', 'preFilter'], (result) => {
    if (result.geminiApiKey) {
      apiKeyInput.value = result.geminiApiKey;
    }
    if (result.scanMode) {
      document.querySelector(`input[name="scanMode"][value="${result.scanMode}"]`).checked = true;
      toggleInstructions(result.scanMode);
    }
    if (result.classMethod) {
      document.querySelector(`input[name="classMethod"][value="${result.classMethod}"]`).checked = true;
      toggleGeminiConfig(result.classMethod);
    }
    if (result.preFilter !== undefined) {
      preFilterCheckbox.checked = result.preFilter;
    }
  });

  // Save preFilter checkbox on change
  preFilterCheckbox.addEventListener('change', (e) => {
    chrome.storage.local.set({ preFilter: e.target.checked });
  });

  // Toggle API key view based on method
  classMethodRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
      toggleGeminiConfig(e.target.value);
      chrome.storage.local.set({ classMethod: e.target.value });
    });
  });

  // Toggle instruction text based on scan mode
  scanModeRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
      toggleInstructions(e.target.value);
      chrome.storage.local.set({ scanMode: e.target.value });
    });
  });

  function toggleGeminiConfig(method) {
    if (method === 'gemini') {
      geminiConfig.style.display = 'block';
    } else {
      geminiConfig.style.display = 'none';
    }
  }

  function toggleInstructions(mode) {
    if (mode === 'slideshow') {
      slideshowInstr.style.display = 'list-item';
    } else {
      slideshowInstr.style.display = 'none';
    }
  }

  // Save API key
  saveKeyBtn.addEventListener('click', () => {
    const key = apiKeyInput.value.trim();
    chrome.storage.local.set({ geminiApiKey: key }, () => {
      alert('Gemini API Key saved locally!');
    });
  });

  // Query content script status on popup load
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs[0] || !tabs[0].url || !tabs[0].url.includes('photos.google.com')) {
      updateStatus('Open Google Photos first', 'idle');
      startBtn.disabled = true;
      return;
    }

    chrome.tabs.sendMessage(tabs[0].id, { action: 'getStatus' }, (response) => {
      if (chrome.runtime.lastError) {
        updateStatus('Ready (reload page if disabled)', 'idle');
        return;
      }
      if (response) {
        updateStats(response);
      }
    });
  });

  // Listen for progress updates from content script
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'progressUpdate') {
      updateStats(message.data);
    }
  });

  // Start scanning
  startBtn.addEventListener('click', () => {
    const selectedMode = document.querySelector('input[name="scanMode"]:checked').value;
    const selectedMethod = document.querySelector('input[name="classMethod"]:checked').value;
    const apiKey = apiKeyInput.value.trim();
    const preFilter = preFilterCheckbox.checked;

    if (selectedMethod === 'gemini' && !apiKey) {
      alert('Please enter and save your Gemini API Key to use Gemini classification.');
      return;
    }

    downloadOcrBtn.style.display = 'none';

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, {
          action: 'startScan',
          config: {
            mode: selectedMode,
            method: selectedMethod,
            apiKey: apiKey,
            preFilter: preFilter
          }
        }, (response) => {
          if (chrome.runtime.lastError) {
            alert('Failed to connect to page. Please refresh Google Photos and try again.');
            return;
          }
          updateStatus('Scanning...', 'scanning');
          startBtn.disabled = true;
          stopBtn.disabled = false;
        });
      }
    });
  });

  // Stop scanning
  stopBtn.addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'stopScan' }, (response) => {
          updateStatus('Stopped', 'paused');
          startBtn.disabled = false;
          stopBtn.disabled = true;
        });
      }
    });
  });

  downloadOcrBtn.addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, { action: 'downloadOcr' });
      }
    });
  });

  function updateStats(data) {
    scannedCount.textContent = data.scanned;
    matchCount.textContent = data.matches;
    statusText.textContent = data.status.toUpperCase();
    statusText.className = `status-val ${data.status}`;

    if (data.status === 'scanning') {
      startBtn.disabled = true;
      stopBtn.disabled = false;
    } else {
      startBtn.disabled = false;
      stopBtn.disabled = true;
      if ((data.status === 'done' || data.status === 'paused') && data.hasOcrData) {
        downloadOcrBtn.style.display = 'block';
      }
    }

    if (data.mode === 'slideshow') {
      const width = Math.min(100, (data.scanned * 5) % 100 + 5);
      progressBar.style.width = `${width}%`;
    } else {
      const progress = data.total ? (data.scanned / data.total) * 100 : 100;
      progressBar.style.width = `${progress}%`;
    }
  }

  function updateStatus(text, className) {
    statusText.textContent = text;
    statusText.className = `status-val ${className}`;
  }
});
