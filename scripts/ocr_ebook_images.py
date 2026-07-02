import cv2
import numpy as np
import pytesseract
import os
import glob
import re

def is_highlighted(img, x, y, w, h):
    roi = img[max(0, y):y+h, max(0, x):x+w]
    if roi.size == 0: return False
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, bg_mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    bg_hsv = cv2.bitwise_and(hsv, hsv, mask=bg_mask)
    highlight_mask = (bg_hsv[:,:,1] > 20) & (bg_hsv[:,:,2] > 150)
    bg_pixels = np.count_nonzero(bg_mask)
    if bg_pixels > 0:
        return (np.count_nonzero(highlight_mask) / bg_pixels) > 0.3
    return False

def get_bold_threshold(img, data):
    ratios = []
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if len(text) > 1:
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            roi = img[max(0, y):y+h, max(0, x):x+w]
            if roi.size == 0: continue
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            text_mask = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            box_area = w * h
            if box_area > 0:
                ratios.append(np.count_nonzero(text_mask) / box_area)
    median_ratio = np.median(ratios) if ratios else 0.25
    return median_ratio * 1.3

def is_bold(img, x, y, w, h, threshold):
    roi = img[max(0, y):y+h, max(0, x):x+w]
    if roi.size == 0: return False
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    text_mask = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    box_area = w * h
    if box_area > 0:
        return (np.count_nonzero(text_mask) / box_area) > threshold
    return False

def process_image(img_path):
    img = cv2.imread(img_path)
    if img is None: return None
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    bold_threshold = get_bold_threshold(img, data)

    paragraphs = []
    current_par = []

    last_block_num = -1
    last_par_num = -1

    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        block_num = data['block_num'][i]
        par_num = data['par_num'][i]

        if (block_num != last_block_num or par_num != last_par_num):
            if current_par:
                paragraphs.append(current_par)
                current_par = []
            last_block_num = block_num
            last_par_num = par_num

        if text:
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            hl = is_highlighted(img, x, y, w, h)
            bd = is_bold(img, x, y, w, h, bold_threshold)

            fmt_text = text
            if bd: fmt_text = f"**{fmt_text}**"
            if hl: fmt_text = f"=={fmt_text}=="

            current_par.append(fmt_text)

    if current_par:
        paragraphs.append(current_par)

    return paragraphs

def format_and_clean(paragraphs):
    cleaned_pars = []
    for par in paragraphs:
        text = " ".join(par)
        text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)
        text = re.sub(r'\*\*(.*?)-\*\*\s+\*\*(.*?)\*\*', r'**\1\2**', text)
        text = re.sub(r'==(.*?)==\s+==(.*?)==', r'==\1 \2==', text)
        cleaned_pars.append(text)
    return cleaned_pars

def get_text_without_formatting(text):
    return re.sub(r'[*=]', '', text).lower()

def order_and_group_pages(pages_data):
    ordered_groups = []
    remaining_pages = list(pages_data.keys())

    while remaining_pages:
        current_group = [remaining_pages.pop(0)]

        found_match = True
        while found_match:
            found_match = False
            last_page = current_group[-1]
            last_text = get_text_without_formatting(pages_data[last_page])
            last_words = last_text.split()[-20:]

            if not last_words: break

            best_match = None
            best_score = 0

            for candidate in remaining_pages:
                candidate_text = get_text_without_formatting(pages_data[candidate])
                candidate_words = candidate_text.split()[:20]

                for i in range(1, min(len(last_words), len(candidate_words)) + 1):
                    overlap1 = " ".join(last_words[-i:])
                    overlap2 = " ".join(candidate_words[:i])
                    if overlap1 == overlap2:
                        if i > best_score:
                            best_score = i
                            best_match = candidate

            if best_match and best_score >= 3:
                current_group.append(best_match)
                remaining_pages.remove(best_match)
                found_match = True
                continue

        found_match = True
        while found_match:
            found_match = False
            first_page = current_group[0]
            first_text = get_text_without_formatting(pages_data[first_page])
            first_words = first_text.split()[:20]

            if not first_words: break

            best_match = None
            best_score = 0

            for candidate in remaining_pages:
                candidate_text = get_text_without_formatting(pages_data[candidate])
                candidate_words = candidate_text.split()[-20:]

                for i in range(1, min(len(first_words), len(candidate_words)) + 1):
                    overlap1 = " ".join(first_words[:i])
                    overlap2 = " ".join(candidate_words[-i:])
                    if overlap1 == overlap2:
                        if i > best_score:
                            best_score = i
                            best_match = candidate

            if best_match and best_score >= 3:
                current_group.insert(0, best_match)
                remaining_pages.remove(best_match)
                found_match = True

        ordered_groups.append(current_group)

    return ordered_groups

def clean_overlaps_in_group(group_pages, pages_data):
    cleaned_group_text = []

    for i in range(len(group_pages)):
        current_text = pages_data[group_pages[i]]

        if i < len(group_pages) - 1:
            next_text = pages_data[group_pages[i+1]]
            current_words_raw = current_text.split()
            next_words_raw = next_text.split()

            best_overlap = 0
            for j in range(1, min(len(current_words_raw), len(next_words_raw)) + 1):
                overlap1 = get_text_without_formatting(" ".join(current_words_raw[-j:]))
                overlap2 = get_text_without_formatting(" ".join(next_words_raw[:j]))
                if overlap1 == overlap2:
                    best_overlap = j

            if best_overlap > 0:
                words_to_keep = len(current_words_raw) - best_overlap
                match_iter = re.finditer(r'\S+', current_text)
                keep_up_to_idx = 0
                for count, match in enumerate(match_iter):
                    if count == words_to_keep - 1:
                        keep_up_to_idx = match.end()
                        break

                if words_to_keep == 0:
                    current_text = ""
                else:
                    current_text = current_text[:keep_up_to_idx].rstrip()

        cleaned_group_text.append(f"<!-- Source: {os.path.basename(group_pages[i])} -->\n" + current_text)

    return "\n\n".join(cleaned_group_text)

def identify_book(text):
    text_lower = text.lower()
    if "halyard" in text_lower and "resaint" in text_lower and "lumpsucker" in text_lower:
        return "Venomous Lumpsucker by Ned Beauman"
    if "capuchin monkeys" in text_lower and "cucumbers" in text_lower and "grapes" in text_lower:
        return "Likely a book on Primatology / Animal Behavior (e.g. Frans de Waal's work)"
    return "Unknown Book"

if __name__ == '__main__':
    images = glob.glob('/tmp/file_attachments/*.png')
    images.extend(glob.glob('/tmp/file_attachments/*.jpg'))
    images.extend(glob.glob('/tmp/file_attachments/*.jpeg'))

    all_pages = {}
    for img_path in images:
        print(f"Processing {img_path}...")
        pars = process_image(img_path)
        if pars:
            cleaned = format_and_clean(pars)
            all_pages[img_path] = "\n\n".join(cleaned)

    print("Grouping and ordering pages...")
    groups = order_and_group_pages(all_pages)

    output_lines = []
    for group_idx, group in enumerate(groups):
        combined_text = clean_overlaps_in_group(group, all_pages)
        book_title = identify_book(combined_text)

        output_lines.append(f"# Book: {book_title}")
        output_lines.append(combined_text)
        output_lines.append("\n---\n")

    with open('/tmp/file_attachments/extracted_text.md', 'w') as f:
        f.write("\n".join(output_lines))
    print("Completed. Output written to /tmp/file_attachments/extracted_text.md")
