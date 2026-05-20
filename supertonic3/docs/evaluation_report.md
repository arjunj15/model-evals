# Supertonic 3 TTS Model Evaluation Report (LLM-as-a-Judge)

This report details the speech synthesis quality evaluation of the **Supertonic 3** model, using **`gemini-3.1-flash-lite`** as a judge to assess human-like naturalness and realism.

---

## 📊 Summary of Evaluation Metrics

The model was tested across **15 distinct test cases** covering 8 languages (English, Spanish, French, Korean, Japanese, German, Hindi, Russian), multiple voice presets, punctuation structures, and expression tags (`<breath>`, `<sigh>`, `<laugh>`).

### Average Ratings (Scale 1.0 - 5.0)

| Metric | Score | Key Takeaway |
| :--- | :---: | :--- |
| **Clarity & Pronunciation** | **4.73 / 5.0** | Exceptional pronunciation accuracy and phonetic clarity. |
| **Prosody & Intonation** | **3.93 / 5.0** | Natural pitch contours in standard sentences; slightly stiff in tagged contexts. |
| **Pacing & Rhythm** | **4.53 / 5.0** | Highly realistic cadence, cadence adjustments, and pause lengths. |
| **Absence of Artifacts** | **4.87 / 5.0** | Extremely clean studio-grade output. Near zero digital distortion, click, or pop noise. |
| **Expressiveness & Emotion** | **3.47 / 5.0** | Mixed. Realistic breath rendering, but fails or misinterprets emotional tags (e.g. sigh/laugh). |
| **Overall Naturalness** | **4.31 / 5.0** | Highly competitive and human-like for general text synthesis. |

---

## 🔍 Key Findings & Analysis

### 1. Strengths
* **Exceptional Intelligibility (4.73/5.0)**: Across all 8 languages, the model produced extremely clear speech, preserving accurate phonetic boundaries even for complex terms and proper names (e.g., "Madrid", "Paris", "인공지능").
* **Flawless Audio Quality (4.87/5.0)**: The ONNX runtime CPU execution synthesizes clean, click-free, studio-quality 44.1kHz audio waveforms without pops or electrical background noise.
* **Realistic Cadence**: Natural pausing patterns at commas, periods, and sentence transitions.

### 2. Areas for Improvement (Expressiveness & Tag Limits)
* **Tag Failures (3.47/5.0)**: 
  - **Ignores Tags**: In Case 9 (Korean), the model produced high-quality speech but ignored the `<laugh>` instruction completely.
  - **Tag Misinterpretation (Critical Bug)**: In Case 7 (French: *"Le vent souffle fort ce soir. <sigh> C'est si calme pourtant"*), the model **literally pronounced the word "sigh"** instead of performing a sighing action. The LLM judge rated this case a **2.20/5.0** because pronouncing the SSML tags destroys conversational realism.
* **Intonation Flatness**: In longer English scripts with expression tags (Case 2, rating **3.40/5.0**), the delivery felt flat and lacked emotional variety.

---

## 🌐 Language-Specific Performance Summary

* **Spanish & French**: 
  - Spanish Case 5 (*"¿Cómo estás hoy? <breath> Espero..."*) scored a perfect **5.00/5.0**. It successfully rendered the `<breath>` tag naturally.
  - French Case 6 (*"Bonjour! C'est un réel plaisir..."*) scored a perfect **5.00/5.0** due to native-sounding intonation and fluent rhythm.
* **Korean**:
  - Case 8 scored a perfect **5.00/5.0** for outstanding clarity and native prosody.
* **Russian & German**:
  - Russian Case 15 scored a perfect **5.00/5.0** (*"Привет! Это автоматический тест..."*).
  - German Case 12 scored **4.80/5.0** for a professional and highly natural recording.
* **Hindi**:
  - Case 14 scored **4.40/5.0** showing highly realistic rendering.

---

## 🧪 Methodology: LLM-as-a-Judge vs. ASR

Traditional TTS testing uses **Automatic Speech Recognition (ASR)** to transcribe the audio and calculate **Word Error Rate (WER)**. While useful for checking word correctness, ASR has major limitations:
1. **Punctuation Blindness**: ASR models often strip punctuation or casing, making it impossible to evaluate question/exclamation intonation.
2. **Ignorance of Naturalness**: A robotically spoken sentence and a beautifully acted human sentence get the exact same ASR WER/CER score (0.0).
3. **No Emotional Grading**: ASR cannot evaluate if a `<breath>`, `<sigh>`, or `<laugh>` was rendered naturally, or if it was pronounced literally.

### LLM-as-a-Judge Advantage
By using **`gemini-3.1-flash-lite`** to evaluate the `.wav` file directly, the pipeline gains:
- **Multimodal Auditory Context**: Gemini physically processes the sound waves, checking for crackles, pauses, and speech contours.
- **SSML Compliance Auditing**: Immediate detection of cases where the engine incorrectly reads tags as text (like Case 7 pronouncing "sigh").
- **Prosodic Assessment**: Direct analysis of human-like inflection, rhythm, and realism.
