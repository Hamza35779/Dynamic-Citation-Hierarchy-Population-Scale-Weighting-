# Dynamic Citation Hierarchy & Population-Scale Weighting

An advanced Natural Language Processing and network science application built for the **National University of Technology Computer Science Department (Artificial Intelligence Program, Course: NLP CS386)**. 

Designed and submitted by:
* **Muhammad Usman** (Reg No: F23607004)
* **Ahad Imran** (Reg No: F23607034)
* **Zain-Ul-Abidin** (Reg No: F23607031)
* **Raja Mahad** (Reg No: F23607035)
* **Hamza Abdul Karim** (Reg No: F23607046)

---

## 🌟 Key Application Features

1. **📁 Multi-Modal Input Engine**: Accept direct PDF uploads, scholarly DOIs, or search-by-title queries.
2. **🔍 Advanced NLP & Regex Extractor**: Automatically parses scientific methodologies to extract and normalize cohort/sample sizes (e.g. *N = 10,000*, *cohort of 50,000*), scoring their confidence levels.
3. **📡 Scholarly REST Traverser**: Seamlessly connects to the free **OpenAlex API** and **Semantic Scholar API** to trace backward citation reference paths recursively in real-time.
4. **📊 Dynamic Citation Weighted DAGs**: NetworkX compiling engine utilizing the proposed multi-factor formula:
   $$W(u, v) = \alpha \times \log_{10}(\text{Population Size}_v) + \beta \times \text{Journal Impact Factor}_v$$
   with interactive frontend sliders for $\alpha$ and $\beta$.
5. **🛤️ Evidence Critical Path Solver**: Renders the heaviest paths of evidence, highlighting how foundational concepts evolved over time into modern studies.
6. **💡 Presentation Demo Cases**: Pre-compiled epidemiological and genetic association networks (**COVID-19** and **Diabetes GWAS**) for flawless, high-speed, 100% offline live pitches.
7. **🔧 Explainability Dashboard**: Includes a complete diagnostic panel showcasing exact regex rules, matching sentence snippets, raw API request bodies, and edge-by-edge math calculation tables.
8. **📥 Tabular Data Export**: Fully interactive data viewer allowing instant CSV downloads of all parsed bibliographical data.

---

## 🛠️ Installation & Setup

1. **Verify Python Installation**:
   Ensure you have Python 3.10 or higher installed:
   ```bash
   python --version
   ```

2. **Install Dependencies**:
   Navigate to the project root directory and run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Dashboard**:
   Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

4. **Run Unit Tests**:
   Verify pipeline mathematics and text extraction matching logic:
   ```bash
   python -m unittest tests/test_pipeline.py
   ```

---

## 📂 Project Directory Structure

```
NLP-Project/
│
├── app.py                       # Main Streamlit Dashboard (Visual Layout & Routing)
├── requirements.txt             # Python Package Dependencies
├── README.md                    # This document (Overview & Defense script)
│
├── core/                        # Pluggable Core Processing System (Enterprise Ready)
│   ├── __init__.py
│   ├── interfaces.py            # Abstract Base Classes (easy future upgrades)
│   ├── pdf_parser.py            # PDF Text extractor & Section Segmenter
│   ├── nlp_extractor.py         # Regex + NLP Population Extractor & Normalizer
│   ├── citation_traverser.py    # Scholarly API connector with local disk caching
│   ├── graph_manager.py         # NetworkX compiler & weighted path solver
│   └── visualizer.py            # PyVis dark-indigo interactive graph designer
│
├── demo_cases/                  # Offline pre-compiled presentation networks
│   ├── case_covid.json          # Preloaded COVID-19 Clinical & Aerosol Studies (6 nodes)
│   └── case_genetics.json       # Preloaded Diabetes GWAS multi-ethnic cohorts (5 nodes)
│
└── tests/                       # Complete automated verification suite
    └── test_pipeline.py         # Unit tests checking NLP extraction & Weight equations
```

---

## 🎓 Ultimate Grade-A Presentation & Defense Script

Use this sequence to deliver a flawless, high-scoring live presentation to **Lec. Rooshan Saleem**:

### Step 1: Establish the Problem & Abstract (Usman & Ahad)
* *Talking Point:* "Conventional academic search engines rank papers purely based on citation counts. However, in clinical, biomedical, and genetic research, a study's **evidence strength** depends highly on its **dataset scale or cohort size**. A study with 150,000 individuals provides significantly stronger empirical evidence than a study with 10 individuals, even if their raw citation counts are similar. Our project solves this by constructing a weighted Knowledge Graph where citation edges are mathematically augmented using both **Population Size** and **Journal Impact Factor**."

### Step 2: Pitch the Architecture & Scalability (Zain-Ul-Abidin)
* *Talking Point:* "Our system is built with a highly decoupled, future-proof Object-Oriented design. By utilizing abstract base interfaces in `core/interfaces.py`, we can easily scale this to an enterprise level—for instance, replacing local regex parsers with deep-learning BioBERT or Gemini LLMs, swapping NetworkX with large-scale Neo4j databases, and using Celery distributed task workers, all without modifying the user dashboard."

### Step 3: Run the Flawless Offline Demo (Raja Mahad)
* *Action:* Select **Tab 3: Interactive Presentation Cases** in the Streamlit UI, and click **Load COVID-19 Demo Case**. Go to **Tab 1** and show the gorgeous interactive graph.
* *Talking Point:* "As you can see, our graph settles beautifully using a customized dark-indigo neon theme. The input transit study (cyan node) cites NEJM and JAMA papers. Our system color-codes the root historical foundational papers in red. Hovering over a node displays an elegant evidence card containing its author metadata, citation counts, and exactly *how* our NLP pipeline extracted its cohort size."

### Step 4: Prove the NLP & Math Under the Hood (Hamza)
* *Action:* Click **Tab 2: Step-by-Step Working & Explanations**. Show the parsed sections, the regex rule that matched, and the active mathematical tables showing:
  $$Weight = \alpha \log_{10}(\text{Population}) + \beta \text{IF}$$
* *Talking Point:* "To ensure 100% explainability for researchers, we provide a complete pipeline diagnostic trace. Here we see the active regex matching rules, the exact methodology text sentences where population size was discovered, and a real-time mathematical table showing step-by-step calculations as we adjust the $\alpha$ and $\beta$ sliders on the sidebar. Adjusting these sliders dynamically scales edge thickness and recalculates the **Evidence Backbone Pathway** (the primary critical chains of research evidence) in real-time."
