# Quant Apprentice 📈

Quant Apprentice is an autonomous AI agent for advanced financial research, powered by Google's Gemini family of models. 
This project demonstrates how an agentic system can intelligently plan research, use external tools and APIs, critique its own findings, 
and provide motivated investment analysis on publicly traded companies.

The entire project is designed to run seamlessly in a Google Colab environment, leveraging modern agentic AI patterns 
like prompt chaining, task routing, and self-refinement loops.

## 🤖 Agent Functions & Capabilities

The core of Quant Apprentice is an autonomous agent built to replicate and automate the workflow 
of a human financial analyst. Its primary capabilities include:

  * **Plan Generation**: The agent dynamically creates a multi-step research plan when given a stock symbol
  * (e.g., `GOOGL`, `TSLA`). It outlines the necessary information, from quantitative financial data to qualitative news sentiment.
  * **Dynamic Tool Use**: It intelligently selects and utilizes external APIs to gather data. This includes fetching price history
  * from **Yahoo Finance**, company news from **NewsAPI.org**, and macroeconomic data from the **FRED API**.
  * **Self-Reflection**: After generating an initial analysis, the agent critically assesses its own output. It identifies gaps in its reasoning, potential biases, or areas that require deeper investigation before reaching a conclusion.
  * **Learning & Adaptation**: The agent maintains a simple memory to learn from its operations. This allows it to refine its strategies over time, noting which data sources were most useful for specific types of analysis.

-----

## ⚙️ Agentic Workflow Patterns

Quant Apprentice implements three key workflow patterns to achieve its complex, end-to-end analysis capabilities.

### 1\. Sequential Prompt Chaining

This pattern is used for structured data processing, especially for news analysis. The agent executes a series of dependent tasks to transform raw news articles into actionable insights.
**Workflow Example:** `Ingest Raw News → Preprocess Text → Classify Market Sentiment → Extract Key Financial Entities → Generate Concise Summary`

### 2\. Task Routing

To handle diverse types of information, the main agent acts as a dispatcher, routing tasks to specialized sub-agents. Each sub-agent is an expert fine-tuned for a specific domain.

  * **Earnings Analyzer**: Focuses on parsing quarterly earnings reports and financial statements (Revenue, Net Income, EPS).
  * **News Analyzer**: Specializes in sentiment analysis, event detection, and summarization of market-moving news.
  * **Market Analyzer**: Analyzes quantitative market data, including price action, trading volume, and key technical indicators.

### 3\. Evaluator–Optimizer Loop

This is the agent's self-improvement mechanism. It allows the system to iteratively refine the quality of its financial analysis through a feedback cycle.
**Workflow:** `Generate Initial Analysis → Evaluate Output Against Quality Rubric → Generate Constructive Feedback → Refine Analysis Using Feedback`

-----

## 🛠️ Technology Stack

  * **Core Engine**: Google Gemini Pro
  * **Development Environment**: Google Colab
  * **Key Libraries**:
      * `google-generativeai`
      * `langchain` or a similar agent framework
      * `yfinance`
      * `pandas`
      * `requests`
  * **Data & APIs**:
      * Yahoo Finance (Stock prices, financials)
      * NewsAPI.org (Financial news)
      * FRED API (Economic data)

-----

## 🚀 Getting Started in Google Colab

This project is optimized for Google Colab. Follow these steps to get it running.

### 1\. Create Your Project Repository on GitHub

Before you begin, create a new repository on [GitHub](https://github.com/) named `Quant-Apprentice`. Upload your project notebook (`.ipynb`) and a `requirements.txt` file to this repository.

### 2\. Clone the Repository in Colab

Open a new Colab notebook and run the following command to clone your project files into the environment.

```python
# Replace 'your_username' with your actual GitHub username
!git clone https://github.com/your_username/Quant-Apprentice.git

# Navigate into your project directory
%cd Quant-Apprentice
```

### 3\. Securely Add API Keys 🔑

Use Colab's built-in "Secrets" manager to keep your API keys safe.

1.  Click the **key icon** (🔑) in the left sidebar.
2.  Click **"Add a new secret"** for each key you need:
      * **Name:** `GOOGLE_API_KEY` | **Value:** `Your_Google_AI_Studio_Key`
      * **Name:** `NEWS_API_KEY` | **Value:** `Your_NewsAPI.org_Key`
3.  Enable the "Notebook access" toggle for each secret.

### 4\. Install Dependencies

Run the following cell to install all the necessary Python libraries from your `requirements.txt` file.

```python
!pip install -r requirements.txt -q
```

### 5\. Configure the Agent

In a code cell at the top of your notebook, load your secrets and configure the Gemini client.

```python
from google.colab import userdata
import google.generativeai as genai
import os

# Load keys from Colab Secrets
GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')

# Configure the Gemini client
genai.configure(api_key=GOOGLE_API_KEY)

# Set API keys as environment variables for other libraries to use
os.environ['NEWS_API_KEY'] = userdata.get('NEWS_API_KEY')
```

You are now ready to run the cells in your notebook to initialize and operate the Quant Apprentice agent\!
