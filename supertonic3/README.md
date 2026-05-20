# 📻 Supertonic 3 Local Voice Studio & Evaluator

An on-device, studio-grade speech synthesis (TTS) application and LLM-as-a-Judge evaluation suite utilizing **Supertone's Supertonic 3** model. It runs 100% locally on your Mac's CPU using ONNX Runtime.

## 🚀 Reorganized Folder Layout

```
supertonic3/
├── app.py                  # Gradio Web Interface
├── evaluate.py             # LLM-as-a-Judge Evaluation Script
├── test_cases.csv          # 15 Multilingual/expressive evaluation scenarios
├── eval_results.csv        # Generated CSV report containing ratings
├── docs/
│   └── evaluation_report.md # Summary report of the evaluation findings
├── pyproject.toml          # UV project configuration and dependencies
├── uv.lock                 # UV exact dependency lockfile
└── .python-version         # Python version setting
```

---

## 🛠️ Installation & Setup

This repository uses [uv](https://github.com/astral-sh/uv) for fast, reliable, and isolated Python package management.

### Prerequisites

Make sure you have `uv` installed. If not, install it with:
```bash
curl -LsSf https://astral-sh.uv.cache.org/install.sh | sh
```

Also, ensure you have the `GEMINI_API_KEY` set in your `.env` file at the project root for running evaluations:
```env
GEMINI_API_KEY="your_api_key_here"
```

---

## 🖥️ Running the Gradio Web Application

The Gradio web app provides a premium user interface to experiment with speech synthesis. It supports built-in factory voice presets (`M1`, `M2`, `F1`, `F2`), multilingual options, and custom voice profile (`.json`) uploads generated via the official Supertonic Voice Builder.

To launch the web interface:
```bash
uv run app.py
```
Open **`http://127.0.0.1:7860`** in your browser.

---

## 📊 Running the LLM-as-a-Judge Evaluator

The evaluator script [evaluate.py](evaluate.py) automates TTS generation across the 15 scenarios defined in [test_cases.csv](test_cases.csv). Rather than evaluating text accuracy via standard ASR, it uses **`gemini-3.1-flash-lite`** to judge the naturalness, clarity, and human-likeness of the synthesized audio files against five key dimensions:

1. **Pronunciation & Clarity** (1-5)
2. **Prosody & Intonation** (1-5)
3. **Pacing & Rhythm** (1-5)
4. **Presence of Artifacts** (1-5)
5. **Expressiveness & Emotion** (1-5)

To run the evaluation pipeline:
```bash
uv run evaluate.py
```
This generates `.wav` audio files inside `eval_outputs/` and writes a detailed evaluation report to `eval_results.csv`.

---

## 📈 Evaluation Results

To see a summary of the latest model evaluations, performance metrics, strengths, and language-specific findings, refer to the [Evaluation Report](docs/evaluation_report.md).
