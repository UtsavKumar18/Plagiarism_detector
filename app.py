from flask import Flask, render_template, request, jsonify
from flask.cli import load_dotenv
from dotenv import load_dotenv
load_dotenv()
from spellchecker import SpellChecker
from utilis import orc
from utilis import ai_detect
import re

app = Flask(__name__)
spell = SpellChecker()

def spell_check(text):
    """Check spelling using pyspellchecker.
    Returns one entry per unique misspelled word, with all positions
    where that word appears so every occurrence gets highlighted.
    """
    matches = list(re.finditer(r'\b[a-zA-Z]+\b', text))

    # Group positions by lowercased word
    word_positions = {}
    for match in matches:
        word = match.group()
        key = word.lower()
        if len(key) <= 1:
            continue
        word_positions.setdefault(key, []).append({
            'start': match.start(),
            'end': match.end(),
            'original': word,
        })

    # Find misspelled words
    misspelled = spell.unknown(list(word_positions.keys()))

    errors = []
    for key in misspelled:
        occurrences = word_positions[key]
        display_word = occurrences[0]['original']
        suggestions = list(spell.candidates(key) or [])
        correction = spell.correction(key)
        if correction and correction in suggestions:
            suggestions.remove(correction)
            suggestions.insert(0, correction)
        errors.append({
            'word': display_word,
            'word_lower': key,
            'positions': [{'start': o['start'], 'end': o['end']} for o in occurrences],
            'suggestions': suggestions[:5],
        })

    return errors

def analyze_text(text):
    """Return various text statistics."""
    words = re.findall(r'\b\w+\b', text)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chars_no_space = len(text.replace(' ', '').replace('\n', ''))

    word_count = len(words)
    sentence_count = len(sentences)
    reading_time = max(1, round(word_count / 200))
    try:
        ai_similarity = ai_detect.ai_detection(text)
    except Exception as e:
        print(f"AI detection error: {e}")
        ai_similarity = -1
    
    return {
        'word_count': word_count,
        'char_count': len(text),
        'char_count_no_space': chars_no_space,
        'sentence_count': sentence_count,
        'paragraph_count': len(paragraphs),
        'reading_time': reading_time,
        'ai_similarity': ai_similarity
    }
    

# Assign your text here — it will be pre-loaded into the editor
text = """Paste or assign your document text here.
This is an exmaple sentance with a few speling mistaks so you can see the highliting in action."""
#url = 'your image url'
#image_path = orc.get_img(url)

textract_client = None

@app.route('/')
def index():
    return render_template('index.html', text=text)

@app.route('/check', methods=['POST'])
def check():
    global textract_client
    if textract_client is None:
        textract_client = orc.connect()
    data = request.get_json()
    url = data.get('text', '')
    print('Received URL:', url)
    image_path = orc.get_img(url)
    extracted_lines = orc.textractor(image_path , textract_client)
    text = "\n".join(extracted_lines)
    # print('text' , text)
    errors = spell_check(text)
    stats = analyze_text(text)
    
    return jsonify({
        'errors': errors,
        'stats': stats,
        'text': text
    })

@app.route('/suggest', methods=['POST'])
def suggest():
    data = request.get_json()
    word = data.get('word', '').lower()
    suggestions = list(spell.candidates(word) or [])
    correction = spell.correction(word)
    if correction and correction in suggestions:
        suggestions.remove(correction)
        suggestions.insert(0, correction)
    return jsonify({'suggestions': suggestions[:5]})

if __name__ == '__main__':
    app.run(debug=True)