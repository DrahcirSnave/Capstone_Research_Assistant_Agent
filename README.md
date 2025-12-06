# Capstone_Research_Assistant_Agent
ITAI-2376 Team #1 

# 🤖 Hybrid AI Research Agent

A Python-based agent that performs autonomous web research, evaluates source credibility, and synthesizes summaries using the BART transformer model. It features a hybrid search architecture (DuckDuckGo + Wikipedia Fallback) and a Reinforcement Learning feedback loop to adapt to user preferences.

## 🚀 Features
* **Hybrid Retrieval:** Automatically switches between DuckDuckGo and Wikipedia based on availability.
* **Safety Guardrails:** Filters unsafe or prohibited topics.
* **Credibility Scoring:** Rates sources as High/Medium/Low based on domain (.edu, .gov).
* **Adaptive Memory:** Learns user preferences for summary length over time.
* **Gradio UI:** Clean, browser-based interface.

## 🛠️ Setup & Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/yourusername/research-agent.git](https://github.com/yourusername/research-agent.git)
    cd research-agent
    ```

2.  **Install Dependencies**
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Web Interface**
    Run the application using the following command:
    ```bash
    python app.py
    ```

4.  **Access the GUI**
    The terminal will display two URLs. Choose the one that works for your setup:
    * **Local URL:** `http://127.0.0.1:7860`  
        *(Try this first—works for standard setups)*
    * **Public URL:** `https://<random-id>.gradio.live`  
        *(Use this if the local link refuses to connect)*

## 📂 Project Structure
* `app.py`: The Gradio user interface.
* `agent_logic.py`: The brain of the agent (Search, Summarize, Plan).
* `utils.py`: Helper functions for memory and safety.
* `config.json`: Default configuration settings.
* `docs/`: Detailed architectural documentation.
