// Content script for Google Photos ebook screenshot selector

let scanState = {
  status: 'idle', // 'idle', 'scanning', 'paused', 'done'
  scanned: 0,
  matches: 0,
  total: 0,
  mode: 'slideshow',
  scannedUrls: new Set(),
  ocrResults: [] // Stores objects: { src, date, text }
};

let lastImageSrc = '';

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

function updateStats() {
  chrome.runtime.sendMessage({
    action: 'progressUpdate',
    data: {
      status: scanState.status,
      scanned: scanState.scanned,
      matches: scanState.matches,
      total: scanState.total,
      mode: scanState.mode,
      hasOcrData: scanState.ocrResults.length > 0
    }
  }).catch(() => {});
}

function extractDateFromPage() {
  // Google Photos typically shows the date in an aria-label at the top or in an info panel
  // We'll look for common date strings in aria-labels
  const elementsWithAria = document.querySelectorAll('[aria-label]');
  const dateRegex = /\b(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s+\d{1,2}(,\s+\d{4})?\b/i;

  for (const el of elementsWithAria) {
    const label = el.getAttribute('aria-label');
    if (label && dateRegex.test(label)) {
      const match = label.match(dateRegex);
      return match[0];
    }
  }

  // Try looking in span text
  const spans = document.querySelectorAll('span');
  for (const span of spans) {
    if (span.innerText && dateRegex.test(span.innerText)) {
      const match = span.innerText.match(dateRegex);
      return match[0];
    }
  }

  return "Unknown Date";
}

function getFullscreenImage() {
  const imgs = Array.from(document.querySelectorAll('img'));
  let bestImg = null;
  let maxArea = 0;

  for (const img of imgs) {
    if (img.offsetParent === null) continue;
    const rect = img.getBoundingClientRect();
    const area = rect.width * rect.height;

    if (area > maxArea && rect.width > 150 && rect.height > 150) {
      maxArea = area;
      bestImg = img;
    }
  }

  if (!bestImg && imgs.length > 0) {
    console.log('Autopaging: No fullscreen image found. Diagnostic list of visible imgs:',
      imgs.map(i => ({
        src: i.src ? i.src.substring(0, 60) + '...' : 'none',
        width: i.width,
        height: i.height,
        visible: i.offsetParent !== null
      }))
    );
  }

  return bestImg;
}

function getFullscreenCheckbox() {
  const candidates = Array.from(document.querySelectorAll('[role="checkbox"], [aria-label*="Select"], [aria-label*="select"]'));

  for (const el of candidates) {
    const rect = el.getBoundingClientRect();
    if (rect.left >= 0 && rect.left < 150 && rect.top >= 0 && rect.top < 150) {
      return el;
    }
  }

  const checkbox = document.querySelector('[aria-label="Select this photo"], [aria-label="Select photo"]');
  if (checkbox) return checkbox;

  const buttons = Array.from(document.querySelectorAll('button, div[role="button"]'));
  for (const btn of buttons) {
    const rect = btn.getBoundingClientRect();
    if (rect.left >= 5 && rect.left < 100 && rect.top >= 5 && rect.top < 100) {
      const label = btn.getAttribute('aria-label') || '';
      if (!label.toLowerCase().includes('back') && !label.toLowerCase().includes('close')) {
        return btn;
      }
    }
  }
  return null;
}

function isPhotoSelected(checkboxElement) {
  if (!checkboxElement) return false;
  if (checkboxElement.getAttribute('aria-checked') === 'true') return true;
  const label = checkboxElement.getAttribute('aria-label') || '';
  if (label.toLowerCase().includes('deselect')) return true;

  if (checkboxElement.classList.contains('selected') || checkboxElement.classList.contains('checked')) {
    return true;
  }
  return false;
}

function getNextArrowButton() {
  const nextBtn = document.querySelector('[aria-label="Next photo"], [aria-label="View next photo"], [aria-label*="Next"]');
  if (nextBtn) return nextBtn;

  const buttons = Array.from(document.querySelectorAll('button, div[role="button"], div[aria-label]'));
  const screenWidth = window.innerWidth;
  const screenHeight = window.innerHeight;

  for (const btn of buttons) {
    const rect = btn.getBoundingClientRect();
    if (rect.left > screenWidth - 150 &&
        rect.top > screenHeight / 2 - 150 &&
        rect.top < screenHeight / 2 + 150 &&
        rect.width > 15 && rect.height > 15) {
      return btn;
    }
  }
  return null;
}

function pressRightArrow() {
  const nextBtn = getNextArrowButton();
  if (nextBtn) {
    console.log('Autopaging: Clicking physical next button', nextBtn);
    nextBtn.click();
    return;
  }

  console.log('Autopaging: Simulating right arrow keyboard events');
  const options = {
    key: 'ArrowRight',
    keyCode: 39,
    code: 'ArrowRight',
    which: 39,
    bubbles: true,
    cancelable: true
  };

  const target = document.activeElement || document.body;
  target.dispatchEvent(new KeyboardEvent('keydown', options));
  target.dispatchEvent(new KeyboardEvent('keyup', options));
  document.dispatchEvent(new KeyboardEvent('keydown', options));
  window.dispatchEvent(new KeyboardEvent('keydown', options));
}

function getGridItems() {
  const imgs = Array.from(document.querySelectorAll('img'));
  const items = [];

  for (const img of imgs) {
    if (img.width < 100 || img.height < 100) continue;

    let parent = img.parentElement;
    let checkbox = null;

    for (let i = 0; i < 6; i++) {
      if (!parent) break;
      checkbox = parent.querySelector('[role="checkbox"], [aria-label*="Select"]');
      if (checkbox) break;
      parent = parent.parentElement;
    }

    if (checkbox && img.src) {
      items.push({
        imgElement: img,
        checkboxElement: checkbox,
        src: img.src
      });
    }
  }
  return items;
}

async function convertImageToBase64Locally(src) {
  if (!src || !src.startsWith('blob:')) {
    return null;
  }
  try {
    const response = await fetch(src);
    const blob = await response.blob();
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result;
        const base64 = dataUrl.substring(dataUrl.indexOf(',') + 1);
        resolve(base64);
      };
      reader.onerror = () => reject(new Error('FileReader error'));
      reader.readAsDataURL(blob);
    });
  } catch (error) {
    console.error('Local blob base64 convert failed:', error);
    return null;
  }
}

async function classifyImage(src, config) {
  const base64Data = await convertImageToBase64Locally(src);

  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      reject(new Error('Classification request timed out after 25s'));
    }, 25000);

    chrome.runtime.sendMessage({
      action: 'classifyImage',
      imageUrl: base64Data ? null : src,
      base64Data: base64Data,
      method: config.method,
      apiKey: config.apiKey,
      preFilter: config.preFilter
    }, (response) => {
      clearTimeout(timeoutId);
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }
      if (response && response.success) {
        resolve({ isEbook: response.isEbook, text: response.text });
      } else {
        reject(new Error(response?.error || 'Classification failed'));
      }
    });
  });
}

async function startSlideshowScan(config) {
  scanState.status = 'scanning';
  scanState.mode = 'slideshow';
  updateStats();

  let consecutiveStuck = 0;

  while (scanState.status === 'scanning') {
    const img = getFullscreenImage();
    if (!img) {
      console.log('No fullscreen image found, waiting for image rendering...');
      await sleep(600);
      continue;
    }

    const src = img.src;
    if (src === lastImageSrc) {
      consecutiveStuck++;
      if (consecutiveStuck >= 8) {
        console.log('End of slideshow or image load timeout. Stopping scan.');
        scanState.status = 'done';
        updateStats();
        break;
      }
      await sleep(500);
      continue;
    }

    consecutiveStuck = 0;
    lastImageSrc = src;

    if (scanState.scannedUrls.has(src)) {
      console.log('Already scanned this image, skipping...');
      pressRightArrow();
      await sleep(1200);
      continue;
    }

    console.log('Scanning slideshow image:', src);
    scanState.scannedUrls.add(src);
    scanState.scanned++;
    updateStats();

    let result = { isEbook: false, text: '' };
    try {
      result = await classifyImage(src, config);
    } catch (e) {
      console.error('Classification error on slideshow image:', e);
    }

    if (result.isEbook) {
      scanState.matches++;

      const date = extractDateFromPage();
      scanState.ocrResults.push({
        src: src,
        date: date,
        text: result.text || "[No text extracted. Local scan used?]"
      });

      const checkbox = getFullscreenCheckbox();
      if (checkbox) {
        if (!isPhotoSelected(checkbox)) {
          checkbox.click();
          console.log('Selected ebook screenshot!');
        } else {
          console.log('Ebook screenshot already selected.');
        }
      } else {
        console.warn('Could not find checkmark to select in fullscreen view.');
      }
    }

    updateStats();
    pressRightArrow();
    await sleep(1300);
  }
}

async function startGridScan(config) {
  scanState.status = 'scanning';
  scanState.mode = 'grid';
  updateStats();

  let consecutiveNoNewItems = 0;

  while (scanState.status === 'scanning') {
    const items = getGridItems();
    let newItemsScanned = 0;

    for (const item of items) {
      if (scanState.status !== 'scanning') break;

      const src = item.src;
      if (scanState.scannedUrls.has(src)) continue;

      scanState.scannedUrls.add(src);
      scanState.scanned++;
      newItemsScanned++;
      updateStats();

      let result = { isEbook: false, text: '' };
      try {
        result = await classifyImage(src, config);
      } catch (e) {
        console.error('Classification error on grid image:', e);
      }

      if (result.isEbook) {
        scanState.matches++;

        // Grid scan makes it harder to get date for each photo, but try anyway
        const date = extractDateFromPage();
        scanState.ocrResults.push({
          src: src,
          date: date,
          text: result.text || "[No text extracted. Local scan used?]"
        });

        if (!isPhotoSelected(item.checkboxElement)) {
          item.checkboxElement.click();
          console.log('Selected matching grid item!');
        }
      }
      updateStats();
      await sleep(150);
    }

    if (newItemsScanned === 0) {
      consecutiveNoNewItems++;
      if (consecutiveNoNewItems >= 6) {
        console.log('Grid scan complete. No new items found.');
        scanState.status = 'done';
        updateStats();
        break;
      }
      window.scrollBy(0, 600);
      await sleep(1500);
    } else {
      consecutiveNoNewItems = 0;
      window.scrollBy(0, 300);
      await sleep(800);
    }
  }
}

function stopScan() {
  scanState.status = 'paused';
  updateStats();
}

function downloadOcrText() {
  if (scanState.ocrResults.length === 0) {
    alert("No OCR data to download yet.");
    return;
  }

  let fileContent = "";
  let i = 1;
  for (const res of scanState.ocrResults) {
    fileContent += `--- Ebook Screenshot ${i} ---\n`;
    fileContent += `Date: ${res.date}\n`;
    fileContent += `Source: ${res.src.substring(0, 50)}...\n\n`;
    fileContent += res.text + "\n\n";
    fileContent += `---------------------------\n\n\n`;
    i++;
  }

  const blob = new Blob([fileContent], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = `ebook_ocr_export_${new Date().toISOString().slice(0,10)}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getStatus') {
    sendResponse({
      status: scanState.status,
      scanned: scanState.scanned,
      matches: scanState.matches,
      total: scanState.total,
      mode: scanState.mode,
      hasOcrData: scanState.ocrResults.length > 0
    });
  } else if (request.action === 'startScan') {
    stopScan();

    scanState.scanned = 0;
    scanState.matches = 0;
    scanState.scannedUrls.clear();
    scanState.ocrResults = []; // clear previous OCR
    lastImageSrc = '';

    if (request.config.mode === 'slideshow') {
      startSlideshowScan(request.config);
    } else {
      startGridScan(request.config);
    }
    sendResponse({ success: true });
  } else if (request.action === 'stopScan') {
    stopScan();
    sendResponse({ success: true });
  } else if (request.action === 'downloadOcr') {
    downloadOcrText();
    sendResponse({ success: true });
  }
});
