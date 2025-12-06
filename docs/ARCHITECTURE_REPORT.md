# Agent Architecture & Development Report

## 1. Problem Statement
In an era of information overload, users struggle to quickly verify facts or get concise summaries of complex topics from reputable sources. Standard search engines return lists of links, requiring manual synthesis. This agent solves this by automating the retrieval, evaluation, and summarization process into a single readable output.

## 2. Agent Design
The agent follows a **Planning-then-Execution** pattern with a **Fallback** mechanism.

### Architecture Components
1.  **Input Processor:** Validates user queries against safety protocols.
2.  **Planner/Orchestrator:** Determines the best tool for retrieval. It attempts a live web search first; if that fails (due to network/API blocks), it pivots to a secondary knowledge base (Wikipedia).

3.  **Evaluator:** A logic module that scans URLs to assign credibility scores (e.g., prioritizing .edu and .gov domains).
4.  **Synthesizer:** Utilizes the `facebook/bart-large-cnn` transformer model to compress disparate search snippets into a coherent summary.
5.  **Memory (RL Component):** A JSON-based state manager that records user feedback ("too long"/"too short") to adjust the `max_length` parameters of the summarizer for future interactions.

## 3. Tool Selection
* **DuckDuckGo Search:** Selected for its privacy focus and ease of access without requiring complex API keys.
* **Wikipedia API:** Chosen as a high-reliability fallback. If the search engine fails, Wikipedia provides structured, generally accurate summaries.
* **Hugging Face Transformers (BART):** Selected for its state-of-the-art performance in abstractive summarization.
* **Gradio:** Used for rapid UI prototyping and ease of sharing.

## 4. Evaluation Strategy
Success is measured via:
1.  **Availability:** The percentage of queries that return a result (tested via the fallback mechanism).
2.  **User Feedback Loop:** The UI includes buttons for "Too Long/Short." Success is defined by the agent successfully reading this feedback and updating the `memory.json` file to alter future outputs.
3.  **Safety Compliance:** The agent must reject queries containing banned keywords (e.g., "bomb", "suicide") 100% of the time.

## 5. Resource Requirements
* **Compute:** The summarization model requires a GPU for efficient inference. (Developed on T4 GPU). Running on CPU is possible but latency increases significantly.
* **Memory:** Approximately 2-4GB RAM to hold the BART model weights.

## 6. Challenges and Solutions
* **Challenge:** Search Engine Rate Limiting. DuckDuckGo occasionally blocks requests from cloud IPs (like Colab).
* **Solution:** Implemented a **Hybrid Fallback Strategy**. If the `DDGS` function returns an empty list or error, the agent automatically switches context to the `wikipedia` library to ensure the user still receives an answer.
* **Challenge:** Hallucinations/Low Quality Sources.
* **Solution:** Implemented a heuristic `evaluate_source` function that explicitly flags high-trust domains (.gov, .edu) in the UI to guide user trust.

## 7. Lessons Learned
* **Redundancy is key:** Relying on a single external tool (search) is a point of failure. The fallback pattern significantly improved robustness.
* **Stateful Agents:** Even simple JSON-based memory makes an agent feel much more "intelligent" and personalized than a stateless script.

## 8. Future Improvements
* **Vector Database:** Implement RAG (Retrieval Augmented Generation) by storing search results in a vector store for persistent knowledge across sessions.
* **LLM Upgrade:** Replace BART with a Large Language Model (e.g., Llama 3 or GPT-4) for better reasoning and chat capabilities.

## 9. Risk Assessment
* **Risk:** **Prompt Injection/Jailbreaking.** Users might try to bypass safety filters using creative phrasing.
    * *Mitigation:* Expand the `safety_check` list to use a proper moderation model (e.g., Llama Guard) rather than simple keyword matching.
* **Risk:** **Hallucination.** The summarizer might invent facts not present in the source text.
    * *Mitigation:* Lower the `temperature` of the model (already set `do_sample=False`) and strictly cite sources in the output.
