# 🧠 Adobe Hackathon Round 1B - Smart PDF Section Analyzer

This project dynamically analyzes multiple PDF documents to extract and rank the most relevant sections and subsections based on a given persona and task. It was designed for the Adobe Hackathon Round 1B challenge.

---

## 📁 Project Structure

```

Round 1B/
├── Collection1/
│   ├── input/
│   │   └── \*.pdf
│   ├── output/
│   │   └── analysis.json
│   ├──  src/
│   │   └──analyzer.py
│   │   └── utils.py
│   ├── input.json
│   ├── Dockerfile
│   └── requirements.txt
├── Collection2/
│   └── ...
├── Collection3/
│   └── ...

````

Each `CollectionX` folder represents a test case input/output pair.

---

## 🚀 How It Works

1. **Input**:  
   `input.json` defines the task (`job_to_be_done`) and documents to analyze.

2. **Processing**:  
   `analyzer.py` reads PDFs from `input/`, ranks and selects top sections, and saves `analysis.json` to `output/`.

3. **Output**:  
   `analysis.json` contains:
   - Metadata (documents, persona, timestamp)
   - Extracted top sections
   - Refined subsection-level content

---

## 📦 Setup & Run

```bash
# Navigate to the Collection folder (e.g., Collection3)
cd Collection3

# Build Docker image
docker build -t pdfanalyzer .

# Run analysis
docker run --rm \
  -v "$PWD/input:/app/input" \
  -v "$PWD/output:/app/output" \
  -v "$PWD/input.json:/app/input.json" \
  pdfanalyzer
````

---

## 📄 Example `input.json`

```json
{
  "persona": {
    "role": "Buffet Menu Planner"
  },
  "job_to_be_done": {
    "task": "Design a gluten-free and vegetarian buffet-style dinner"
  },
  "documents": [
    { "filename": "Dinner Ideas - Sides_2.pdf" },
    { "filename": "Dinner Ideas - Sides_3.pdf" }
  ]
}
```

---

## ✅ Features

* Dynamic ranking using TF-IDF
* PDF parsing via PyMuPDF
* Section-level and refined paragraph-level extraction
* Fully offline and fast (<60s)

---

## 🧠 Tech Stack

* Python
* PyMuPDF
* scikit-learn
* Docker

---

## 👨‍💻 Author
Jasleen Kaur Matharoo   
📧 jasleenkaur11rps@gmail.com   
Arhasi Soni   
📧 arhasisoni@gmail.com

---

## 📝 License

MIT License
