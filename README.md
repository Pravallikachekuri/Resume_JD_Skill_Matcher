Absolutely! Here's your updated **README.md** with your GitHub username (`Pravallikachekuri`) properly inserted:

````markdown
# 📄 Resume_JD_Skill_Matcher + LLM Judge + ✉️ Email Notifier

A powerful Streamlit web app that automates resume screening by matching resumes against job descriptions using advanced NLP and LLM models. It scores, judges, and categorizes candidates, then notifies them via email — streamlining recruitment workflows with AI!

---

## Features

- **Resume Parsing**: Extracts text from PDF resumes using PDFMiner, PyMuPDF, and OCR (EasyOCR) for high accuracy.
- **Skill Extraction**: Uses SpaCy to identify and highlight technical skills from resumes.
- **AI-Powered Matching & Scoring**: Utilizes Groq LLM (via `agno` library) to score how well a resume matches a job description (scale 0-100).
- **Automated Judgement**: LLM judges whether a resume is a good match and provides a brief reason.
- **Candidate Categorization**: Categorizes candidates into Low, Medium, or High match buckets based on score.
- **Email Notifications**: Sends customized email updates to candidates about their application status using Gmail SMTP.
- **Interactive Streamlit UI**: Easy drag-and-drop uploads for job descriptions and multiple resumes, with real-time progress and results display.
- **Rate Limit Handling**: Implements retry mechanisms for Groq API rate limits.

---

## Tech Stack

- Python 3.9+
- Streamlit — Web UI framework
- SpaCy — NLP for skill extraction
- EasyOCR — OCR for scanned PDFs
- PyMuPDF (fitz) & PDFMiner.six — PDF text extraction
- Groq LLM (via `agno`) — Resume matching and judgement
- Pandas — Data manipulation and display
- SMTP (smtplib) — Email notifications
- dotenv — Environment variable management

---

## Installation

1. Clone this repo:

   ```bash
   git clone https://github.com/Pravallikachekuri/Resume_JD_Skill_Matcher.git
   cd Resume_JD_Skill_Matcher
````

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate      # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Download SpaCy model:

   ```bash
   python -m spacy download en_core_web_sm
   ```

5. Set up environment variables by creating a `.env` file in the root directory:

   ```
   GROQ_API_KEY=your_groq_api_key_here
   EMAIL_ADDRESS=your_email@gmail.com
   EMAIL_PASSWORD=your_email_password_or_app_password
   ```

---

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

* Upload a **Job Description** (.txt file).
* Upload one or multiple **Resumes** (.pdf files).
* Click **Match & Analyze** to start AI-powered screening.
* View candidate scores, categories, and AI judge decisions.
* Emails are sent automatically to candidates based on their match status.

---

## Project Structure

```
.
├── app.py               # Main Streamlit app
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── .env.example         # Example environment variables file
```

---

## Future Enhancements

* Support for DOCX resume parsing.
* Integration with more advanced LLM models or embeddings.
* Resume anonymization for bias reduction.
* Dashboard for HR teams with analytics and filtering.

---

## License

MIT License © Pravallikachekuri

```

