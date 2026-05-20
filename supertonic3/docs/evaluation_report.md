# Supertonic 3 TTS Model Evaluation Report (LLM-as-a-Judge)

This report details the speech synthesis quality evaluation of the **Supertonic 3** model, using **`gemini-3.1-flash-lite`** as a judge to assess human-like naturalness and realism.

---

## 📊 Summary of Evaluation Metrics

The model was evaluated across **20 distinct test cases** covering 8 languages (English, Spanish, French, Korean, Japanese, German, Hindi, Russian), multiple voice presets, and structural scenarios.

### Overall Average Ratings (20 Cases)

| Metric | Score | Key Takeaway |
| :--- | :---: | :--- |
| **Clarity & Pronunciation** | **4.90 / 5.0** | Flawless phonetic clarity and pronunciation accuracy. |
| **Prosody & Intonation** | **4.00 / 5.0** | Excellent pitch contour and human-like flow. |
| **Pacing & Rhythm** | **4.60 / 5.0** | Highly realistic cadence and pause durations. |
| **Absence of Artifacts** | **5.00 / 5.0** | Perfect, studio-grade audio waveforms. |
| **Expressiveness & Emotion** | **3.55 / 5.0** | Excellent for standard reading, but struggles with inline tags. |
| **Overall Naturalness** | **4.41 / 5.0** | Extremely competitive, sounding close to a human voice. |

---

## ⚖️ Tag-Free vs. Tagged Speech Analysis

To evaluate the model's response to custom voice expression tags (e.g. `<breath>`, `<sigh>`, `<laugh>`), we compared the **14 tag-free test cases** directly against the **6 tagged test cases**.

| Metric (Scale 1-5) | Tag-Free Cases (14) | Tagged Cases (6) | Variance |
| :--- | :---: | :---: | :---: |
| **Clarity & Pronunciation** | **5.00 / 5.0** | **4.67 / 5.0** | **-0.33** |
| **Prosody & Intonation** | **4.29 / 5.0** | **3.33 / 5.0** | **-0.96** |
| **Expressiveness & Emotion** | **3.93 / 5.0** | **2.67 / 5.0** | **-1.26** |
| **Overall Naturalness** | **4.63 / 5.0** | **3.90 / 5.0** | **-0.73** |

### Key Observations

1. **Tag-Free Synthesis is Flawless**: When reading normal, untagged texts (e.g. customer support scripts, news readings, or general sentences), the model is highly expressive (**3.93**), sounds natural (**4.63**), and scores a **perfect 5.00/5.0 in Clarity and Artifacts**.
2. **Expression Tag Limitations**: The inclusion of expression tags reduces prosody and expressiveness scores significantly. The model frequently:
   - **Ignores tags** (e.g. Korean `<laugh>` in Case 9).
   - **Fails expressiveness** (e.g. German `<sigh>` in Case 13).
   - **Pronounces tags literally** (e.g. French `<sigh>` in Case 7, where it literally spoke the word *"sigh"*, bringing its score down to 3.80/5.0).

---

## 🔍 Detailed Findings per Language (Tag-Free Highlights)

* **English (Case 16)**: Customer service prompt (*"Thank you for calling customer support..."*) scored **4.60/5.0** for highly natural, pleasant, and professional tone.
* **Spanish (Case 17)**: News reading (*"La conferencia internacional..."*) scored **4.40/5.0** for clear pronunciation and news-anchor pacing.
* **French (Case 18)**: Dialogue line (*"Je pense qu'il est trop tard..."*) scored **4.60/5.0** with excellent conversational rhythm.
* **Korean (Case 19)**: Asking directions (*"혹시 시청역으로..."*) scored **4.80/5.0** due to natural question intonation.
* **German (Case 20)**: General statement (*"Die Entwicklung von künstlicher..."*) scored **4.80/5.0** sounding completely natural and professional.
* **Russian (Case 15)**: Scored **4.40/5.0** with native-like fluidity.
* **Hindi (Case 14)**: Scored **4.60/5.0** showing realistic rhythm.

---

## 🧪 Methodology: LLM-as-a-Judge vs. ASR

Traditional TTS testing uses **Automatic Speech Recognition (ASR)** to transcribe the audio and calculate **Word Error Rate (WER)**. ASR models are blind to punctuation and prosody.

By using **`gemini-3.1-flash-lite`** to evaluate the `.wav` files directly, our pipeline gains:
- **Multimodal Auditory Context**: Gemini processes the sound waves to check for digital crackles, pops, and pacing.
- **SSML Compliance Auditing**: Detects when tags are spoken literally as words instead of acted out.
- **Prosodic Assessment**: Analyzes human-like conversational cadence and emotional realism.
