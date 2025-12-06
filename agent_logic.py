import time
import wikipedia
import nltk
from duckduckgo_search import DDGS
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from utils import load_memory, evaluate_source, safety_check

# --- INITIALIZATION ---
print("Loading Local Summarizer...")
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

# Initialize Sumy (LSA Algorithm)
stemmer = Stemmer("english")
summarizer = LsaSummarizer(stemmer)
summarizer.stop_words = get_stop_words("english")

def summarize_text(text):
    """
    Summarizes text using LSA (Latent Semantic Analysis).
    Converts 'preferred_length' (tokens) from memory into 'sentence_count'.
    """
    memory = load_memory()
    # Map token length (e.g., 150) to roughly sentence count (e.g., 3-5)
    # Approx 30 tokens per sentence
    target_tokens = memory.get("preferred_summary_length", 150)
    num_sentences = max(2, target_tokens // 40) 

    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summary_sentences = summarizer(parser.document, num_sentences)
        # Join sentences into a single string
        return " ".join([str(s) for s in summary_sentences])
    except Exception as e:
        return f"Summarizer error: {str(e)}"

def research_agent_hybrid(topic):
    if not topic.strip():
        return "⚠️ Please enter a valid topic."

    if not safety_check(topic):
        return "❌ Request denied for safety reasons."

    print(f"🔎 Researching: {topic}...")
    
    results = []
    source_type = "Search Engine"

    # --- STRATEGY A: DUCKDUCKGO ---
    backends = ['api', 'html', 'lite']
    for backend in backends:
        try:
            with DDGS() as ddgs:
                search_gen = ddgs.text(topic, max_results=10, backend=backend)
                results = list(search_gen)
            if results:
                break 
            time.sleep(0.5)
        except Exception:
            continue

    # --- STRATEGY B: WIKIPEDIA (Fallback) ---
    if not results:
        print("⚠️ Search engine blocked. Switching to Wikipedia fallback...")
        source_type = "Wikipedia"
        try:
            wiki_search = wikipedia.search(topic)
            if wiki_search:
                page = wikipedia.page(wiki_search[0], auto_suggest=False)
                results.append({
                    "title": page.title,
                    "url": page.url,
                    "body": page.summary, # Wiki summary is already good
                    "credibility": "High credibility (Wikipedia)"
                })
        except Exception as e:
            print(f"Wikipedia error: {e}")

    if not results:
        return "⚠️ All research methods failed. Please try again later."

    # --- PROCESSING ---
    combined_text = ""
    report = []

    # Process results
    for r in results[:5]:
        title = r.get("title", "Untitled")
        snippet = r.get("body", r.get("content", ""))
        url = r.get("href", r.get("url", "#"))
        credibility = r.get("credibility", evaluate_source(url))
        
        report.append({
            "title": title[:100],
            "url": url,
            "credibility": credibility,
        })
        combined_text += snippet + " "

    # --- SUMMARIZATION ---
    final_summary = ""
    # If using Wikipedia, we can just use the first 5 sentences of the page summary
    if source_type == "Wikipedia":
        final_summary = combined_text[:2000]
    else:
        if len(combined_text) < 50:
            final_summary = "Not enough data to summarize."
        else:
            # Use Sumy for web results
            final_summary = summarize_text(combined_text)

    return {
        "topic": topic,
        "summary": final_summary,
        "sources": report,
        "method": source_type
    }
