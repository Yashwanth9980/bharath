from flask import Flask, render_template, request, jsonify
from groq import Groq
import requests
import urllib.parse
import time
import re
import os
import logging
from dotenv import load_dotenv

# ================== LOAD ENV ==================
load_dotenv()

# ================== LOGGING ==================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ================== API KEY ==================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY not found in environment variables")
    raise ValueError("GROQ_API_KEY is required")

try:
    client = Groq(api_key=GROQ_API_KEY)
    logger.info("Groq client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    raise

# ================== DATA ==================
PLACES = {
    "taj-mahal": {"name": "Taj Mahal", "lat": 27.1751, "lng": 78.0421, "img": "taj.jpg"},
    "hampi": {"name": "Hampi", "lat": 15.3350, "lng": 76.4600, "img": "hampi.jpg"},
    "konark": {"name": "Konark Sun Temple", "lat": 19.8876, "lng": 86.0945, "img": "konark.jpg"},
    "ajanta": {"name": "Ajanta Caves", "lat": 20.5519, "lng": 75.7033, "img": "ajanta.jpg"},
    "varanasi": {"name": "Varanasi Ghats", "lat": 25.3176, "lng": 82.9739, "img": "varanasi.jpg"},
    "meenakshi": {"name": "Meenakshi Temple", "lat": 9.9195, "lng": 78.1193, "img": "meenakshi.jpg"},
    "redfort": {"name": "Red Fort", "lat": 28.6562, "lng": 77.2410, "img": "redfort.jpg"},
    "statue": {"name": "Statue of Unity", "lat": 21.8380, "lng": 73.7191, "img": "statue.jpg"},
    "charminar": {"name": "Charminar", "lat": 17.3616, "lng": 78.4747, "img": "charminar.jpg"},
    "mysore": {"name": "Mysore Palace", "lat": 12.3051, "lng": 76.6551, "img": "mysore.jpg"},
    "khajuraho": {"name": "Khajuraho Temples", "lat": 24.8318, "lng": 79.9199, "img": "khajuraho.jpg"},
    "sanchi": {"name": "Sanchi Stupa", "lat": 23.4793, "lng": 77.7399, "img": "sanchi.jpg"},
}

ARTS = {
    "kathakali": {"name": "Kathakali", "img": "kathakali.jpg"},
    "bharatanatyam": {"name": "Bharatanatyam", "img": "bharatanatyam.jpg"},
    "yakshagana": {"name": "Yakshagana", "img": "yakshagana.jpg"},
    "kathak": {"name": "Kathak", "img": "kathak.jpg"},
    "madhubani": {"name": "Madhubani Painting", "img": "madhubani.jpg"},
    "chhau": {"name": "Chhau Dance", "img": "chhau.jpg"},
    "odissi": {"name": "Odissi Dance", "img": "odissi.jpg"},
    "kalaripayattu": {"name": "Kalaripayattu", "img": "kalaripayattu.jpg"},
}

FESTIVALS = {
    "diwali": {"name": "Diwali", "img": "diwali.jpg"},
    "pongal": {"name": "Pongal", "img": "pongal.jpg"},
    "navratri": {"name": "Navratri", "img": "navratri.jpg"},
    "holi": {"name": "Holi", "img": "holi.jpg"},
    "onam": {"name": "Onam", "img": "onam.jpg"},
    "durga": {"name": "Durga Puja", "img": "durga.jpg"},
    "ganesh": {"name": "Ganesh Chaturthi", "img": "ganesh.jpg"},
    "ramzan": {"name": "Ramzan (Eid-ul-Fitr)", "img": "ramzan.jpg"},
}

# ================== WIKI TITLE FIX ==================
WIKI_TITLE_FIX = {
    "Varanasi Ghats": "Ghats in Varanasi",
    "Khajuraho Temples": "Khajuraho Group of Monuments",
    "Chhau Dance": "Chhau dance",
    "Odissi Dance": "Odissi",
    "Pongal": "Pongal (festival)",
    "Ramzan (Eid-ul-Fitr)": "Eid al-Fitr",
}

# ================== MARKDOWN CLEANER ==================
def clean_markdown(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"^\s*[-*]\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()

# ================== ROUTES ==================
@app.route("/")
def home():
    try:
        return render_template("home.html")
    except Exception as e:
        logger.error(f"Error loading home page: {e}")
        return jsonify({"error": "Failed to load home page"}), 500

@app.route("/category/<cat>")
def category(cat):
    try:
        if cat not in ["places", "arts", "festivals"]:
            logger.warning(f"Invalid category requested: {cat}")
            return jsonify({"error": "Invalid category"}), 400
        
        if cat == "places":
            data = PLACES
        elif cat == "arts":
            data = ARTS
        else:
            data = FESTIVALS
        
        logger.info(f"Category page loaded: {cat}")
        return render_template("category.html", category=cat, items=data)
    except Exception as e:
        logger.error(f"Error loading category {cat}: {e}")
        return jsonify({"error": "Failed to load category"}), 500

@app.route("/detail/<cat>/<key>")
def detail(cat, key):
    try:
        if cat not in ["places", "arts", "festivals"]:
            logger.warning(f"Invalid category requested: {cat}")
            return jsonify({"error": "Invalid category"}), 400
        
        if cat == "places":
            item = PLACES.get(key)
        elif cat == "arts":
            item = ARTS.get(key)
        else:
            item = FESTIVALS.get(key)
        
        if not item:
            logger.warning(f"Item not found: {cat}/{key}")
            return jsonify({"error": "Item not found"}), 404
        
        logger.info(f"Detail page loaded: {cat}/{key}")
        return render_template("detail.html", category=cat, key=key, item=item, maps_key=GOOGLE_MAPS_API_KEY)
    except Exception as e:
        logger.error(f"Error loading detail page {cat}/{key}: {e}")
        return jsonify({"error": "Failed to load detail page"}), 500

# ================== AI GENERATION ==================
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json
        
        if not data:
            logger.warning("Empty request body for /generate")
            return jsonify({"error": "Request body cannot be empty"}), 400
        
        name = data.get("name", "").strip()
        category = data.get("category", "").strip()
        language = data.get("language", "English").strip()
        
        # Validation
        if not name:
            logger.warning("Missing 'name' parameter in /generate")
            return jsonify({"error": "Name is required"}), 400
        
        if not category:
            logger.warning("Missing 'category' parameter in /generate")
            return jsonify({"error": "Category is required"}), 400
        
        if category not in ["places", "arts", "festivals"]:
            logger.warning(f"Invalid category in /generate: {category}")
            return jsonify({"error": "Invalid category"}), 400
        
        valid_languages = ["English", "Hindi", "Kannada", "Telugu", "Marathi"]
        if language not in valid_languages:
            logger.warning(f"Invalid language in /generate: {language}")
            return jsonify({"error": "Invalid language"}), 400

        if language == "English":
            lang_instruction = "Write in English."
        elif language == "Hindi":
            lang_instruction = "Write ONLY in Hindi using Devanagari script."
        elif language == "Kannada":
            lang_instruction = "Write ONLY in Kannada script."
        elif language == "Telugu":
            lang_instruction = "Write ONLY in Telugu script."
        elif language == "Marathi":
            lang_instruction = "Write ONLY in Marathi using Devanagari script."
        else:
            lang_instruction = "Write in English."

        prompt = f"""
You are an expert Indian heritage historian.

Write a VERY LONG, DETAILED, PROFESSIONAL museum-style article about:

{name}
Category: {category}

CRITICAL RULES:
- {lang_instruction}
- Do NOT use markdown
- Do NOT use symbols
- Do NOT use bullets
- Do NOT mention AI
- Write MINIMUM 600-800 words
- Write clean natural paragraphs
"""

        logger.info(f"Generating content for {name} in {language}")
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )

        raw_text = completion.choices[0].message.content.strip()
        text = clean_markdown(raw_text)

        logger.info(f"Successfully generated content for {name}")
        return jsonify({"text": text})
    
    except requests.exceptions.Timeout:
        logger.error("Timeout calling Groq API")
        return jsonify({"error": "Request timeout. Please try again."}), 504
    except requests.exceptions.ConnectionError:
        logger.error("Connection error calling Groq API")
        return jsonify({"error": "Connection error. Please check your internet."}), 503
    except ValueError as e:
        logger.warning(f"Validation error in /generate: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error in /generate endpoint: {e}")
        return jsonify({"error": "Failed to generate content. Please try again."}), 500

# ================== WIKI IMAGES ==================
@app.route("/wiki_images")
def wiki_images():
    try:
        title = request.args.get("title", "").strip()
        
        if not title:
            logger.warning("Missing 'title' parameter in /wiki_images")
            return jsonify([])
        
        images = []
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            wiki_title = WIKI_TITLE_FIX.get(title, title)
            safe_title = wiki_title.replace(" ", "_")

            # Get page summary
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe_title}"
            r = requests.get(summary_url, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()

            if "originalimage" in data:
                images.append(data["originalimage"]["source"])
            elif "thumbnail" in data:
                images.append(data["thumbnail"]["source"])

            # Get page HTML
            try:
                page_url = f"https://en.wikipedia.org/wiki/{safe_title}"
                html = requests.get(page_url, headers=headers, timeout=10).text

                matches = re.findall(r'src="(https://upload.wikimedia.org/[^"]+)"', html)

                for m in matches:
                    if any(ext in m.lower() for ext in [".jpg", ".jpeg", ".png"]):
                        if m not in images:
                            images.append(m)
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout fetching Wikipedia page for {title}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error fetching Wikipedia page for {title}: {e}")

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching Wikipedia summary for {title}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error fetching Wikipedia data for {title}: {e}")
        except ValueError as e:
            logger.warning(f"Invalid Wikipedia response for {title}: {e}")
        
        logger.info(f"Found {len(images)} images for {title}")
        return jsonify(images[:8])
    
    except Exception as e:
        logger.error(f"Error in /wiki_images endpoint: {e}")
        return jsonify([]), 500

# ================== RUN ==================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
