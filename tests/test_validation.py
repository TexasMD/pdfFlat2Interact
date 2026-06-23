import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from docvert.validation import validate_block_coherence

def test_validate_block_coherence_clean():
    blocks = [
        {'id': 'b1', 'role': 'instruction', 'x': 100, 'y': 100, 'w': 800, 'h': 50},
        {'id': 'b2', 'role': 'exercise_items', 'x': 100, 'y': 200, 'w': 800, 'h': 400},
        {'id': 'b3', 'role': 'footer', 'x': 100, 'y': 900, 'w': 800, 'h': 50}
    ]
    issues = validate_block_coherence(blocks)
    assert len(issues) == 0

def test_validate_block_coherence_overlap():
    blocks = [
        {
            'id': 'b1',
            'role': 'instruction',
            'x': 100,
            'y': 100,
            'w': 800,
            'h': 50,
            'source_file': 'sumbridge2.pdf',
            'page_num': 1,
            'rendered_image_path': 'renders/sumbridge2_p001.png',
            'run_id': 'pilot-run',
        },
        # Factoid overlapping instruction
        {
            'id': 'b2',
            'role': 'factoid_sidebar',
            'x': 850,
            'y': 120,
            'w': 100,
            'h': 300,
            'source_file': 'sumbridge2.pdf',
            'page_num': 1,
            'rendered_image_path': 'renders/sumbridge2_p001.png',
            'run_id': 'pilot-run',
        }
    ]
    issues = validate_block_coherence(blocks)
    assert len(issues) == 1
    assert "overlaps with factoid" in issues[0]['message']
    assert issues[0]['issue_type'] == 'possible_layout_block_merge_error'
    assert issues[0]['source_file'] == 'sumbridge2.pdf'
    assert issues[0]['page_num'] == 1
    assert issues[0]['rendered_image_path'] == 'renders/sumbridge2_p001.png'
    assert issues[0]['run_id'] == 'pilot-run'
    assert issues[0]['review_options']
    assert 'review_suggestion' in issues[0]

def test_validate_block_coherence_impossible_order():
    blocks = [
        {'id': 'b1', 'role': 'exercise_items', 'x': 100, 'y': 100, 'w': 800, 'h': 400},
        # Instruction below exercise
        {'id': 'b2', 'role': 'instruction', 'x': 100, 'y': 600, 'w': 800, 'h': 50}
    ]
    issues = validate_block_coherence(blocks)
    assert len(issues) == 1
    assert "appears below exercise" in issues[0]['message']
    assert issues[0]['issue_type'] == 'contextual_coherence_failure'

def test_validate_block_coherence_detects_text_stream_merge_without_overlap():
    blocks = [
        {
            'id': 'b1',
            'role': 'instruction',
            'x': 100,
            'y': 100,
            'w': 800,
            'h': 90,
            'text': 'Draw lines between these words and their Earthquakes can cause rivers to temporarily flow backwards abbreviations.',
            'source_file': 'sumbridge2.pdf',
            'page_num': 1,
            'rendered_image_path': 'renders/sumbridge2_p001.png',
        },
        {
            'id': 'b2',
            'role': 'exercise_items',
            'x': 100,
            'y': 240,
            'w': 800,
            'h': 400,
        }
    ]

    issues = validate_block_coherence(blocks)

    assert len(issues) == 1
    issue = issues[0]
    assert issue['issue_type'] == 'possible_layout_block_merge_error'
    assert "reading-order merge" in issue['message']
    assert issue['blocks'] == ['b1']
    assert issue['source_file'] == 'sumbridge2.pdf'
    assert issue['page_num'] == 1
    assert issue['rendered_image_path'] == 'renders/sumbridge2_p001.png'
