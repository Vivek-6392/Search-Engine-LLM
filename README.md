# Search-Engine-LLM
# 🔎 LangChain Search Chatbot

An AI-powered chatbot that can search the web, Wikipedia, and research papers using LangChain agents and Groq LLM, built with Streamlit.

---

## 🚀 Features

* 🌐 Real-time web search (DuckDuckGo)
* 📚 Wikipedia integration for general knowledge
* 📄 ArXiv integration for research papers
* 🤖 LLM-powered reasoning using Groq (LLaMA 3)
* 💬 Interactive chat interface using Streamlit
* 🔄 Agent-based decision making (ReAct)

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **LLM:** Groq (LLaMA 3.1)
* **Framework:** LangChain
* **Search APIs:**

  * DuckDuckGo
  * Wikipedia
  * ArXiv

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/langchain-search-chatbot.git
cd langchain-search-chatbot
```

---

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

⚠️ Important: Ensure this is installed:

```bash
pip install -U ddgs
```

---

## 🔑 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

---

## ▶️ Run the App

```bash
streamlit run app.py
```

---

## 🧠 How It Works

1. User enters a query in the chat UI.
2. LangChain agent decides:

   * Use Wikipedia → for general knowledge
   * Use ArXiv → for research queries
   * Use DuckDuckGo → for current info
3. Groq LLM processes tool outputs.
4. Final response is shown in chat.

---

## 📁 Project Structure

```
├── app.py
├── requirements.txt
├── .env
└── README.md
```
---

## 🔮 Future Improvements

* Add memory (chat history context)
* Add document upload (RAG system)
* Support multiple LLM providers
* UI enhancements (chat history sidebar)

---

## 🤝 Contributing

Pull requests are welcome! Feel free to fork the repo and improve the project.

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 🙌 Acknowledgements

* LangChain
* Groq
* Streamlit
* Open-source community
