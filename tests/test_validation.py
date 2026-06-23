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
        {'id': 'b1', 'role': 'instruction', 'x': 100, 'y': 100, 'w': 800, 'h': 50},
        # Factoid overlapping instruction
        {'id': 'b2', 'role': 'factoid_sidebar', 'x': 850, 'y': 120, 'w': 100, 'h': 300}
    ]
    issues = validate_block_coherence(blocks)
    assert len(issues) == 1
    assert "overlaps with factoid" in issues[0]['message']

def test_validate_block_coherence_impossible_order():
    blocks = [
        {'id': 'b1', 'role': 'exercise_items', 'x': 100, 'y': 100, 'w': 800, 'h': 400},
        # Instruction below exercise
        {'id': 'b2', 'role': 'instruction', 'x': 100, 'y': 600, 'w': 800, 'h': 50}
    ]
    issues = validate_block_coherence(blocks)
    assert len(issues) == 1
    assert "appears below exercise" in issues[0]['message']
