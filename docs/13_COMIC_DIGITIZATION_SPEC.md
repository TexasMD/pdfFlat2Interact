# Comic Digitization Spec

## Goal
Parse comic/graphic novel page images and create interactive HTML versions where text is selectable and accurately positioned over the original artwork, while the original baked-in text is erased.

## Pipeline Architecture & Alternative Pathways

### 1. Text Detection & Bounding Box Accuracy
*   **Current POC Limitation:** Simple OpenCV thresholding and morphological dilation (e.g., `cv2.dilate`) is too blunt. Tests show it generates masks that are improperly positioned and overly large, accidentally covering and destroying important non-text material (like balloon borders or high-contrast artwork).
*   **Alternative/Optimal Pathway:** Implement a specialized Machine Learning object detection model trained specifically on manga/comic text (e.g., CRAFT or a fine-tuned YOLO model). This allows for precise, tight bounding polygons around characters rather than coarse rectangular blocks, ensuring only text pixels are masked.

### 2. Text Erasure (Masking & Inpainting)
*   **Current POC Limitation:** Classic algorithms like `cv2.inpaint` (Telea/Navier-Stokes) struggle with complex comic backgrounds and can leave blurry artifacts, especially if the input mask is imprecise.
*   **Alternative/Optimal Pathway:** Deep learning-based inpainting (e.g., LAMA) provides vastly superior results by hallucinating the missing background structures based on surrounding context, preventing the "smudged" look typical of classic OpenCV inpainting.

### 3. Classification & Speaker Attribution
*   **Classification:** Distinguishing between character speech, narrative, and SFX (sound effects) requires analyzing bounding box context. Speech is typically centered in bright, closed contours (balloons). Narrative is usually in rigid rectangles at panel edges. SFX often lacks a bounding shape and integrates directly with the art.
*   **Attribution (Optimal Pathway):**
    1.  Detect Character Bounding Boxes (via ML or manual review).
    2.  Detect Balloon "Tails" via contour analysis (looking for sharp, acute angles projecting outward from the main balloon contour).
    3.  Cast a vector from the tail tip; the character bounding box it intersects is the attributed speaker.

### 4. Interactive HTML Generation
*   Render the cleanly inpainted comic page image as the background.
*   Generate absolute-positioned HTML `<div>` elements using the highly accurate bounding boxes from Step 1.
*   Inject the OCR text into these `<div>`s so it aligns perfectly with the erased text's original position, allowing user selection and editing without obscuring the artwork.

## Validation & Review Requirements
*   All text regions must be assigned an ID (`comic-text-1`, etc.).
*   A `comic.json` file must be generated with `review_targets` to allow manual correction of OCR mistakes, bounding boxes, or classification (Speech vs. Narrative).
