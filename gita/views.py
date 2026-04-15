import random as rand
import os
import logging

from django.http import JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)

CURR_DIR = os.path.dirname(__file__)

# Chapter verse counts for all 18 chapters
VERSE_COUNTS = {
    1: 47, 2: 72, 3: 43, 4: 42, 5: 29,
    6: 47, 7: 30, 8: 28, 9: 34, 10: 42,
    11: 55, 12: 20, 13: 34, 14: 27, 15: 20,
    16: 24, 17: 28, 18: 78
}


def no_of_verses(chapter):
    """Get number of verses for a chapter."""
    return VERSE_COUNTS.get(chapter, 0)


def _validate_chapter_verse(chpt_no, verse_no):
    """Validate chapter and verse numbers. Returns (is_valid, error_message)."""
    if not 1 <= chpt_no <= 18:
        return False, f"Chapter must be between 1 and 18, got {chpt_no}"
    max_verses = no_of_verses(chpt_no)
    if not 1 <= verse_no <= max_verses:
        return False, f"Verse must be between 1 and {max_verses} for chapter {chpt_no}, got {verse_no}"
    return True, None


def _read_file(path):
    """Read file content, returns (content, error)."""
    try:
        full_path = os.path.join(CURR_DIR, path)
        if not os.path.exists(full_path):
            return None, f"File not found: {path}"
        with open(full_path, encoding="utf-8") as f:
            return f.read(), None
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return None, str(e)


def getRandomSloka(request):
    """Return a random sloka from any chapter."""
    chapter = rand.randint(1, 18)
    verse = rand.randint(1, no_of_verses(chapter))

    verse_text, v_err = _read_file(f"v2Verses/chapter {chapter}/{chapter}.{verse}.txt")
    sloka_text, s_err = _read_file(f"v2English/chapter {chapter}/{chapter}.{verse}.txt")
    name_text, n_err = _read_file(f"Chapters/chapter {chapter}/{chapter}.txt")

    errors = []
    if v_err:
        errors.append(f"verse: {v_err}")
    if s_err:
        errors.append(f"sloka: {s_err}")
    if n_err:
        errors.append(f"name: {n_err}")

    if errors:
        logger.error(f"Error fetching random sloka (ch{chapter}, v{verse}): {', '.join(errors)}")
        return JsonResponse({'error': 'Failed to fetch sloka', 'details': errors, 'chapter': chapter, 'verse': verse}, status=500)

    name = name_text.split(".")[1] if "." in name_text else name_text.strip()

    return JsonResponse({
        'verse_no': chapter,
        'slok_no': verse,
        'name': name,
        'slok': sloka_text.replace("\n", "\n\n"),
        'verse': verse_text.replace("\n", "\n\n")
    })


def verses(request, chpt_no):
    return render(request, f"{CURR_DIR}/templates/verses.html", {
        "chpt_no": chpt_no
    })


def getVerse(chpt_no, verse_no):
    """Get verse commentary text. Returns string or None on error."""
    is_valid, error = _validate_chapter_verse(chpt_no, verse_no)
    if not is_valid:
        logger.error(f"Invalid verse request: {error}")
        return None

    content, err = _read_file(f"v2Verses/chapter {chpt_no}/{chpt_no}.{verse_no}.txt")
    if err:
        logger.error(f"Error reading verse {chpt_no}.{verse_no}: {err}")
        return None
    return content.replace("\n", "\n\n")


def getEngSloka(chpt_no, verse_no):
    """Get English sloka text. Returns string or None on error."""
    is_valid, error = _validate_chapter_verse(chpt_no, verse_no)
    if not is_valid:
        logger.error(f"Invalid sloka request: {error}")
        return None

    content, err = _read_file(f"v2English/chapter {chpt_no}/{chpt_no}.{verse_no}.txt")
    if err:
        logger.error(f"Error reading sloka {chpt_no}.{verse_no}: {err}")
        return None
    return content.replace("\n", "\n\n")


def getSansSloka(chpt_no, verse_no):
    """Get Sanskrit sloka text. Returns string or None on error."""
    is_valid, error = _validate_chapter_verse(chpt_no, verse_no)
    if not is_valid:
        logger.error(f"Invalid sanskrit sloka request: {error}")
        return None

    content, err = _read_file(f"Sanskrit Slokas/chapter {chpt_no}/{chpt_no}.{verse_no}.txt")
    if err:
        logger.error(f"Error reading sanskrit sloka {chpt_no}.{verse_no}: {err}")
        return None
    return content


def getName(chpt_no):
    """Get chapter name. Returns string or None on error."""
    if not 1 <= chpt_no <= 18:
        logger.error(f"Invalid chapter number: {chpt_no}")
        return None

    content, err = _read_file(f"Chapters/chapter {chpt_no}/{chpt_no}.txt")
    if err:
        logger.error(f"Error reading chapter name {chpt_no}: {err}")
        return None

    if "." in content:
        return content.split(".")[1].strip()
    return content.strip()


def getVerses(request, chpt_no, verse_no):
    """Get complete verse data for a specific chapter and verse."""
    try:
        chpt_no = int(chpt_no)
        verse_no = int(verse_no)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid chapter or verse number'}, status=400)

    is_valid, error = _validate_chapter_verse(chpt_no, verse_no)
    if not is_valid:
        return JsonResponse({'error': error}, status=400)

    eng_sloka = getEngSloka(chpt_no, verse_no)
    sans_sloka = getSansSloka(chpt_no, verse_no)
    verse = getVerse(chpt_no, verse_no)
    chapter_name = getName(chpt_no)

    if eng_sloka is None or sans_sloka is None or verse is None:
        missing = []
        if eng_sloka is None:
            missing.append("english sloka")
        if sans_sloka is None:
            missing.append("sanskrit sloka")
        if verse is None:
            missing.append("verse commentary")
        return JsonResponse({
            'error': f'Failed to load: {", ".join(missing)}',
            'chapter': chpt_no,
            'verse': verse_no
        }, status=500)

    res = {
        'eng_sloka': eng_sloka,
        'sans_sloka': sans_sloka,
        'verse': verse,
        'num_verses': no_of_verses(chpt_no),
        'chapterName': chapter_name or "Unknown"
    }
    response = JsonResponse(res)
    response['Access-Control-Allow-Origin'] = 'https://bhagavad-gita.netlify.app'
    return response


def getChapterName(request):
    """Get all chapter names."""
    names = []
    for chapter in range(1, 19):
        name = getName(chapter)
        names.append(name or f"Chapter {chapter}")

    res = JsonResponse({'names': names, "length": len(names)})
    res['Access-Control-Allow-Origin'] = 'https://bhagavad-gita.netlify.app'
    return res


def getRandomVerse(request):
    """Get a random verse from any chapter."""
    max_attempts = 10
    for _ in range(max_attempts):
        chapter = rand.randint(1, 18)
        verse = rand.randint(1, no_of_verses(chapter))

        eng_sloka = getEngSloka(chapter, verse)
        sans_sloka = getSansSloka(chapter, verse)
        verse_text = getVerse(chapter, verse)
        chapter_name = getName(chapter)

        if all(x is not None for x in [eng_sloka, sans_sloka, verse_text, chapter_name]):
            res = {
                'chpt_no': chapter,
                'verse_no': verse,
                'chapterName': chapter_name,
                'eng_sloka': eng_sloka,
                'sans_sloka': sans_sloka,
                'verse': verse_text
            }
            response = JsonResponse(res)
            response['Access-Control-Allow-Origin'] = 'https://bhagavad-gita.netlify.app'
            return response

    return JsonResponse({'error': 'Failed to fetch random verse after multiple attempts'}, status=500)


def start(request):
    """Health check endpoint."""
    return JsonResponse({'message': 'Welcome to the Bhagavad Gita API!'})