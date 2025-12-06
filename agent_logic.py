import time
import wikipedia
from duckduckgo_search import DDGS
from transformers import pipeline
from utils import load_memory, evaluate_source, safety_check

# Initialize Model (Lazy loading recommended for production, but loaded global here for speed)
print("Loading Summarization Model...")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    """Summarizes text based on dynamic length preference from memory."""
    memory = load_memory()
    max_len = memory["preferred_summary_length"]
    
    try:
        # Dynamic length parameters based on RL feedback
        return summarizer(text, max_length=max_len, min_length=max_len//2, do_sample=False)[0]['summary_text']
    except Exception as e:
        return f"Summarizer error: {str(e)}"

def research_agent_hybrid(topic):
    """
    Main Agent Workflow:
    1. Safety Check
    2. Try Web Search (DuckDuckGo)
    3. Fallback to Wikipedia if Search Fails
    4. Credibility Evaluation
    5. AI Summarization
    """
    if not topic.strip():
        return "⚠️ Please enter a valid topic."

    if not safety_check(topic):
        return "❌ Request denied for safety reasons."

    print(f"🔎 Researching: {topic}...")
    
    results = []
    source_type = "Search Engine"

    # --- STRATEGY A: DUCKDUCKGO ---
    # Attempts multiple backends to bypass potential rate limits
    backends = ['api', 'html', 'lite']
    for backend in backends:
        try:
            with DDGS() as ddgs:
                search_gen = ddgs.text(topic, max_results=7, backend=backend)
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
                    "body": page.summary,
                    "credibility": "High credibility (Wikipedia)"
                })
        except wikipedia.exceptions.DisambiguationError as e:
            return f"⚠️ Topic is too ambiguous. Did you mean: {', '.join(e.options[:5])}?"
        except Exception as e:
            print(f"Wikipedia error: {e}")

    if not results:
        return "⚠️ All research methods failed. Please try again later."

    # --- PROCESSING & SUMMARIZATION ---
    combined_text = ""
    report = []

    for r in results[:5]:
        title = r.get("title", "Untitled")
        snippet = r.get("body", r.get("content", ""))
        url = r.get("href", r.get("url", "#"))
        
        # Determine credibility (if not already set by Wiki)
        credibility = r.get("credibility", evaluate_source(url))
        
        report.append({
            "title": title[:100],
            "url": url,
            "credibility": credibility,
        })
        combined_text += snippet + " "

    # Synthesize Summary
    final_summary = ""
    if source_type == "Wikipedia":
        final_summary = combined_text[:1500] # Wiki is already a summary
    else:
        # Use AI model for raw web results
        if len(combined_text) < 50:
            final_summary = "Not enough data to summarize."
        else:
            final_summary = summarize_text(combined_text[:3000])

    return {
        "topic": topic,
        "summary": final_summary,
        "sources": report,
        "method": source_type
    }
