// Background service worker for handling cross-origin image retrieval, Gemini API calls, and local CV heuristics

// Cache for the selected model name to avoid querying ListModels on every single photo
let cachedModelName = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'classifyImage') {
    handleClassification(request)
      .then(result => sendResponse({ success: true, isEbook: result.isEbook, text: result.text }))
      .catch(error => {
        console.error('Classification error:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true; // Keep message channel open for async response
  }
});

async function handleClassification(request) {
  // 1. Get base64 representation of the image
  let base64Data = request.base64Data;
  if (!base64Data) {
    if (!request.imageUrl) {
      throw new Error('Neither base64Data nor imageUrl provided.');
    }
    base64Data = await fetchImageAsBase64(request.imageUrl);
  }

  // 2. Pre-filter if enabled (only relevant when using Gemini)
  if (request.method === 'gemini' && request.preFilter) {
    console.log('Local pre-filtering is ENABLED. Evaluating screenshot layout...');
    const passesScreener = await classifyImageLocal(base64Data, true);
    if (!passesScreener) {
      console.log('Local pre-filter REJECTED this screenshot (failed layout checks). Bypassing Gemini API.');
      return { isEbook: false, text: '' };
    }
    console.log('Local pre-filter PASSED this screenshot. Querying Gemini API for final verification...');
  }

  // 3. Classify based on configured method
  if (request.method === 'gemini') {
    return await classifyImageGemini(base64Data, request.apiKey);
  } else {
    const isEbook = await classifyImageLocal(base64Data, false);
    return { isEbook, text: '' }; // Local method doesn't extract text
  }
}

async function fetchImageAsBase64(imageUrl) {
  let fetchUrl = imageUrl;
  if (imageUrl.includes('googleusercontent.com') && !imageUrl.includes('=')) {
    fetchUrl = `${imageUrl}=w512`;
  }

  const response = await fetch(fetchUrl);
  if (!response.ok) {
    throw new Error(`Failed to fetch image: ${response.statusText}`);
  }

  const arrayBuffer = await response.arrayBuffer();
  return arrayBufferToBase64(arrayBuffer);
}

// Discover the best available Flash model supported on the user's API Key
async function getBestFlashModel(apiKey) {
  if (cachedModelName) {
    return cachedModelName;
  }

  try {
    console.log('Querying ListModels API to discover active Gemini models...');
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`);
    if (!response.ok) {
      throw new Error(`Failed to list models: ${response.statusText}`);
    }
    const data = await response.json();
    const models = data.models || [];

    const flashModels = models.filter(m => {
      const name = m.name.toLowerCase();
      const methods = m.supportedGenerationMethods || [];
      return name.includes('flash') && methods.includes('generateContent');
    });

    if (flashModels.length > 0) {
      flashModels.sort((a, b) => {
        const getVer = (nameStr) => {
          const matchDec = nameStr.match(/gemini-(\d+)\.(\d+)-flash/);
          if (matchDec) return parseFloat(`${matchDec[1]}.${matchDec[2]}`);
          const matchInt = nameStr.match(/gemini-(\d+)-flash/);
          if (matchInt) return parseFloat(matchInt[1]);
          return 0;
        };
        return getVer(b.name) - getVer(a.name);
      });

      cachedModelName = flashModels[0].name;
      console.log(`Discovered best model: ${cachedModelName}`);
      return cachedModelName;
    }
  } catch (e) {
    console.error('Error fetching model list, falling back to defaults:', e);
  }

  cachedModelName = 'models/gemini-2.0-flash';
  return cachedModelName;
}

async function classifyImageGemini(base64Data, apiKey) {
  const modelName = await getBestFlashModel(apiKey);
  const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/${modelName}:generateContent?key=${apiKey}`;
  const prompt =
    "Analyze this image. First, determine if it is a screenshot of ebook text (e.g., a page from a book, reader app like Kindle or Libby). " +
    "Second, if it IS an ebook text screenshot, extract all the legible text from the page via OCR. " +
    "Respond ONLY with a valid JSON object matching this schema: {\"isEbook\": boolean, \"text\": string}. " +
    "Set isEbook to false for chat logs, receipts, lists, shopping, or normal photos. If isEbook is false, leave text as an empty string.";

  const apiBody = {
    contents: [
      {
        parts: [
          { text: prompt },
          {
            inlineData: {
              mimeType: "image/jpeg",
              data: base64Data
            }
          }
        ]
      }
    ],
    generationConfig: {
      responseMimeType: "application/json",
      temperature: 0.1
    }
  };

  const apiResponse = await fetch(geminiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(apiBody)
  });

  if (!apiResponse.ok) {
    const errorJson = await apiResponse.json().catch(() => ({}));
    const errorMsg = errorJson?.error?.message || apiResponse.statusText;
    throw new Error(`Gemini API Error: ${errorMsg}`);
  }

  const resultJson = await apiResponse.json();
  const textResult = resultJson?.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || '{}';

  try {
    const parsed = JSON.parse(textResult);
    console.log(`Gemini response: isEbook=${parsed.isEbook}`);
    return {
      isEbook: !!parsed.isEbook,
      text: parsed.text || ''
    };
  } catch (e) {
    console.error("Failed to parse Gemini JSON output", textResult);
    return { isEbook: false, text: '' };
  }
}

async function classifyImageLocal(base64Data, isPreFilter = false) {
  const dataUrl = `data:image/jpeg;base64,${base64Data}`;
  const response = await fetch(dataUrl);
  const blob = await response.blob();
  const bitmap = await createImageBitmap(blob);

  const canvas = new OffscreenCanvas(200, 300);
  const ctx = canvas.getContext('2d');
  ctx.drawImage(bitmap, 0, 0, 200, 300);

  const imgData = ctx.getImageData(0, 0, 200, 300);
  const data = imgData.data;

  let totalLuminance = 0;
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i+1];
    const b = data[i+2];
    const y = 0.299 * r + 0.587 * g + 0.114 * b;
    totalLuminance += y;
  }
  const avgLuminance = totalLuminance / (200 * 300);
  const isLightBg = avgLuminance > 120;

  const foreground = new Uint8Array(200 * 300);
  for (let y = 0; y < 300; y++) {
    for (let x = 0; x < 200; x++) {
      const idx = (y * 200 + x) * 4;
      const r = data[idx];
      const g = data[idx+1];
      const b = data[idx+2];
      const lum = 0.299 * r + 0.587 * g + 0.114 * b;

      const isHighlight =
        (r > 175 && g > 175 && b < 150) ||
        (g > 175 && r < 170 && b < 170) ||
        (b > 175 && r < 170 && g < 185);

      let isFg = false;
      if (isHighlight) {
        isFg = true;
      } else {
        isFg = isLightBg ? (lum < 135) : (lum > 115);
      }

      foreground[y * 200 + x] = isFg ? 1 : 0;
    }
  }

  const colDensity = new Float32Array(200);
  for (let x = 0; x < 200; x++) {
    let count = 0;
    for (let y = 0; y < 300; y++) {
      count += foreground[y * 200 + x];
    }
    colDensity[x] = count / 300;
  }

  const marginLimit = isPreFilter ? 0.18 : 0.10;
  const minMiddleAvg = isPreFilter ? 0.02 : 0.04;
  const minLines = isPreFilter ? 4 : 6;
  const maxLines = 45;
  const stdDevLimit = isPreFilter ? 12.0 : 7.0;

  let leftMarginSum = 0;
  for (let x = 0; x < 15; x++) leftMarginSum += colDensity[x];
  const leftMarginAvg = leftMarginSum / 15;

  let rightMarginSum = 0;
  for (let x = 185; x < 200; x++) rightMarginSum += colDensity[x];
  const rightMarginAvg = rightMarginSum / 15;

  let middleSum = 0;
  for (let x = 40; x < 160; x++) middleSum += colDensity[x];
  const middleAvg = middleSum / 120;

  const hasGoodMargins = leftMarginAvg < marginLimit && rightMarginAvg < marginLimit && middleAvg > minMiddleAvg;

  const rowDensity = new Float32Array(300);
  for (let y = 0; y < 300; y++) {
    let count = 0;
    for (let x = 0; x < 200; x++) {
      count += foreground[y * 200 + x];
    }
    rowDensity[y] = count / 200;
  }

  const smoothed = new Float32Array(300);
  for (let y = 1; y < 299; y++) {
    smoothed[y] = (rowDensity[y-1] + rowDensity[y] + rowDensity[y+1]) / 3;
  }

  let peakCount = 0;
  const peakIndices = [];
  const peakThreshold = 0.025;

  for (let y = 4; y < 296; y++) {
    if (smoothed[y] > peakThreshold &&
        smoothed[y] >= smoothed[y-1] &&
        smoothed[y] >= smoothed[y-2] &&
        smoothed[y] > smoothed[y+1] &&
        smoothed[y] > smoothed[y+2]) {
      peakCount++;
      peakIndices.push(y);
      y += 4;
    }
  }

  const hasExpectedLineCount = peakCount >= minLines && peakCount <= maxLines;

  let regularityCheck = false;
  if (peakCount >= 4) {
    const gaps = [];
    for (let i = 1; i < peakIndices.length; i++) {
      gaps.push(peakIndices[i] - peakIndices[i-1]);
    }
    const avgGap = gaps.reduce((a, b) => a + b, 0) / gaps.length;
    const variance = gaps.map(g => Math.pow(g - avgGap, 2)).reduce((a, b) => a + b, 0) / gaps.length;
    const stdDev = Math.sqrt(variance);
    regularityCheck = stdDev < stdDevLimit;
  } else if (peakCount >= 2) {
    regularityCheck = true;
  }

  const isEbook = hasGoodMargins && hasExpectedLineCount && regularityCheck;
  console.log(`Local CV scan (preFilter=${isPreFilter}): margins=${hasGoodMargins} (L:${leftMarginAvg.toFixed(3)} R:${rightMarginAvg.toFixed(3)} M:${middleAvg.toFixed(3)}), lines=${peakCount}, regular=${regularityCheck} -> isEbook=${isEbook}`);

  return isEbook;
}

function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  const len = bytes.byteLength;
  const chunk = 8192;
  for (let i = 0; i < len; i += chunk) {
    const subArray = bytes.subarray(i, i + chunk);
    binary += String.fromCharCode.apply(null, subArray);
  }
  return btoa(binary);
}
