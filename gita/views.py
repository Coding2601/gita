import random as rand
from django.http import JsonResponse
import os
from django.shortcuts import render

#file_path = "/Users/Ravi Mishra/OneDrive/Desktop/gita-backend/gita"

curr_dir = os.path.dirname(__file__)

def no_of_verses(v):

    if v == 1:
        return 47
    elif v == 2:
        return 72
    elif v == 3:
        return 43
    elif v == 4:
        return 42
    elif v == 5:
        return 29
    elif v == 6:
        return 47
    elif v == 7:
        return 30
    elif v == 8:
        return 28
    elif v == 9:
        return 34
    elif v == 10:
        return 42
    elif v == 11:
        return 55
    elif v == 12:
        return 20
    elif v == 13:
        return 34
    elif v == 14:
        return 27
    elif v == 15:
        return 20
    elif v == 16:
        return 24
    elif v == 17:
        return 28
    elif v == 18:
        return 78

def getRandomSloka(request):

    v = rand.randint(1,18)

    if v == 1:
        s = rand.randint(1,47)
    elif v == 2:
        s = rand.randint(1,72)
    elif v == 3:
        s = rand.randint(1,43)
    elif v == 4:
        s = rand.randint(1,42)
    elif v == 5:
        s = rand.randint(1,29)
    elif v == 6:
        s = rand.randint(1,47)
    elif v == 7:
        s = rand.randint(1,30)
    elif v == 8:
        s = rand.randint(1,28)
    elif v == 9:
        s = rand.randint(1,34)
    elif v == 10:
        s = rand.randint(1,42)
    elif v == 11:
        s = rand.randint(1,55)
    elif v == 12:
        s = rand.randint(1,20)
    elif v == 13:
        s = rand.randint(1,34)
    elif v == 14:
        s = rand.randint(1,27)
    elif v == 15:
        s = rand.randint(1,20)
    elif v == 16:
        s = rand.randint(1,24)
    elif v == 17:
        s = rand.randint(1,28)
    elif v == 18:
        s = rand.randint(1,78)

    print(s, v, curr_dir)

    try:

        with open(os.path.join(curr_dir, f"Verses/chapter {v}/{v}.{s}.txt"), encoding="utf-8") as f:
            verse = f.read()

        with open(os.path.join(curr_dir, f"Slokas/chapter {v}/{v}.{s}.txt"), encoding="utf-8") as f:

            slok = f.read()

        with open(os.path.join(curr_dir, f"Chapters/chapter {v}/{v}.txt"), encoding="utf-8") as f:

            name = f.read().split(".")[1]

    except Exception as e:
            
            return JsonResponse({'error': str(e), 'sloka': s, 'verse': v})

    '''return render(request, f"{file_path}/templates/random.html", {
        "verse": verse,
        "slok": slok,
        "verse_no": v,
        "slok_no": s,
        "name": name
    })'''

    return JsonResponse({'verse_no': v, 'slok_no': s, 'name': name, 'slok': slok, 'verse': verse})

def verses(request, chpt_no):
    return render(request, f"{file_path}/templates/verses.html", {
        "chpt_no": chpt_no
    })

def getVerse(chpt_no, verse_no):
    try:
        with open(os.path.join(curr_dir, f"Verses/chapter {chpt_no}/{chpt_no}.{verse_no}.txt"), encoding="utf-8") as f:
            verse = f.read()
    except Exception as e:
        return JsonResponse({'error': str(e), 'sloka': s, 'verse': v})
    return verse

def getEngSloka(chpt_no, verse_no):
    try:
        with open(os.path.join(curr_dir, f"Slokas/chapter {chpt_no}/{chpt_no}.{verse_no}.txt"), encoding="utf-8") as f:
            slok = f.read()
    except Exception as e:
        return JsonResponse({'error': str(e), 'sloka': s, 'verse': v})
    return slok

def getSansSloka(chpt_no, verse_no):
    try:
        with open(os.path.join(curr_dir, f"Sanskrit Slokas/chapter {chpt_no}/{chpt_no}.{verse_no}.txt"), encoding="utf-8") as f:
            slok = f.read()
    except Exception as e:
        return JsonResponse({'error': str(e), 'sloka': s, 'verse': v})
    return slok

def getName(chpt_no):
    try:
        with open(os.path.join(curr_dir, f"Chapters/chapter {chpt_no}/{chpt_no}.txt"), encoding="utf-8") as f:
            name = f.read().split(".")[1]
    except Exception as e:
        return JsonResponse({'error': str(e), 'sloka': s, 'verse': v})
    return name

def getVerses(request, chpt_no, verse_no):
    num_verses = no_of_verses(chpt_no)
    eng_sloka = getEngSloka(chpt_no, verse_no)
    sans_sloka = getSansSloka(chpt_no, verse_no)
    verse = getVerse(chpt_no, verse_no)
    chapterName = getName(chpt_no)
    res = {
        'eng_sloka': eng_sloka,
        'sans_sloka': sans_sloka,
        'verse': verse,
        'num_verses': num_verses,
        'chapterName': chapterName
    }
    response = JsonResponse(res)
    response['Access-Control-Allow-Origin'] = 'https://bhagavad-gita.netlify.app'
    return response

def getChapterName(request):
    names = []
    for v in range(1, 19):
        names.append(getName(v))
    res = JsonResponse({'names': names, "length": len(names)})
    res['Access-Control-Allow-Origin'] = 'https://bhagavad-gita.netlify.app'
    return res

def getRandomVerse(request):
    v = rand.randint(1,18)
    s = rand.randint(1, no_of_verses(v))
    verse = getVerse(v, s)
    eng_sloka = getEngSloka(v, s)
    sans_sloka = getSansSloka(v, s)
    chapterName = getName(v)
    res = {
        'chpt_no': v,
        'verse_no': s,
        'chapterName': chapterName,
        'eng_sloka': eng_sloka,
        'sans_sloka': sans_sloka,
        'verse': verse
    }
    response = JsonResponse(res)
    response['Access-Control-Allow-Origin'] = 'https://bhagavad-gita.netlify.app'
    return response

def start(request):
    return JsonResponse({'message': 'Welcome to the Bhagavad Gita API!'})