#!/usr/bin/env python3
"""The Excuse That Almost Works — make.fun entry.

Writes one line to $MAKEFUN_OUTPUT_DIR/entry.txt (default /output):
the single text a gamer sends their boss to skip work on GTA 6
launch week. Gate: UTF-8, 1-140 characters, not only whitespace,
at most 20 words, one line, plain text, reads like a hurried text.

Deterministic: five hand-written candidates are scored against the
judge's brief (believable boring workplace detail first, funny on
its own terms second, hurried-text feel third, fresh angle fourth)
and the best is written out. No network, no randomness, no secrets.
"""

import os
import sys

# Five candidate excuses. Each is one line, at most 20 words, and
# leans on a specific boring detail a tired manager has heard before
# rather than a wild story. No dead grandmother, no flat tyre, no
# sudden fever anywhere in this file.
CANDIDATES = [
    "Sorry, the lift in my building broke and I'm stuck between "
    "floors with the maintenance guy.",
    "My dentist moved my filling to 9am today and the numbing "
    "hasn't worn off yet, I can barely talk.",
    "The plumber is finally here fixing the leak under my sink, "
    "I have to stay home to let him in.",
    "Sorry, my building's doing fire alarm testing all morning "
    "and I can't hear anything on calls.",
    "My laptop died mid-update last night and IT said not to "
    "touch it till they remote in this morning.",
    "The train I take got cancelled and the next one doesn't "
    "leave for two hours, sorry.",
]

# Words that mark a specific, boring, believable workplace detail.
DETAIL_WORDS = (
    "lift", "building", "maintenance", "plumber", "leak", "sink",
    "dentist", "filling", "numbing", "fire", "alarm", "laptop",
    "update", "it", "remote", "train", "cancelled",
)

# Words that mark the laugh coming from the excuse's own logic.
HUMOUR_WORDS = ("barely", "stuck", "died", "can't hear")

# Cliches the judge explicitly discounts; any candidate carrying
# one is heavily penalised (none of the candidates above has one).
CLICHE_WORDS = (
    "grandmother", "grandma", "flat tyre", "flat tire",
    "fever", "food poisoning", "sick",
)

# Hurried-text markers: a quick apology or a contraction.
HURRIED_WORDS = ("sorry", "i'm", "can't", "hasn't", "doesn't", "till")


def _words(text):
    """Lowercase words of a line, punctuation stripped."""
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() else " "
                      for ch in text.lower())
    return cleaned.split()


def score(text):
    """Score one candidate against the judge's brief.

    Believability (specific boring detail) weighs most, then the
    laugh from the excuse's own logic, then hurried-text feel,
    then length fit. Returns (total, breakdown dict).
    """
    words = _words(text)
    word_set = set(words)
    chars = len(text)

    detail = sum(3 for w in DETAIL_WORDS if w in word_set)
    humour = sum(2 for w in HUMOUR_WORDS if w in word_set)
    hurried = sum(2 for w in HURRIED_WORDS if w in word_set)
    cliche = sum(-10 for w in CLICHE_WORDS if w in text.lower())

    # Length fit: 14-19 words and 80-120 characters read like a
    # hurried text; shorter feels thin, longer sounds rehearsed.
    length = 0
    if 14 <= len(words) <= 19:
        length += 3
    elif 10 <= len(words) <= 20:
        length += 1
    if 80 <= chars <= 120:
        length += 3
    elif 60 <= chars <= 140:
        length += 1

    total = detail + humour + hurried + cliche + length
    breakdown = {
        "detail": detail, "humour": humour, "hurried": hurried,
        "cliche": cliche, "length": length,
        "words": len(words), "chars": chars,
    }
    return total, breakdown


def pick_best():
    """Return (best_line, best_score, breakdown) deterministically.

    Ties break toward the earlier candidate, so the result is
    stable across runs and machines.
    """
    best_line = None
    best_score = None
    best_breakdown = None
    for candidate in CANDIDATES:
        total, breakdown = score(candidate)
        if best_score is None or total > best_score:
            best_line, best_score, best_breakdown = (
                candidate, total, breakdown)
    return best_line, best_score, best_breakdown


def main():
    line, total, breakdown = pick_best()
    # Word count the way the task counts it: whitespace-separated
    # tokens, so "mid-update" is one word, not two.
    words = line.split()
    assert 1 <= len(line) <= 140, "gate: 1-140 characters"
    assert line.strip(), "gate: not only whitespace"
    assert len(words) <= 20, "task: at most 20 words"
    assert "\n" not in line, "task: one line"

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError:
        out_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(line)

    print("wrote %s (%d chars, %d words, score %d)"
          % (out_path, len(line), len(words), total))
    print("entry: %s" % line)
    print("breakdown: %s" % (breakdown,))
    return 0


if __name__ == "__main__":
    sys.exit(main())
