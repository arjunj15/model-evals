# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "supertonic",
#     "qwen-asr",
#     "torch",
#     "pandas",
#     "jiwer",
#     "soundfile",
# ]
# ///
import os
import re
import traceback
import pandas as pd
import torch
import jiwer
from supertonic import TTS

# Language mappings for Supertonic 3
LANGUAGES = {
    "english": "en", "spanish": "es", "french": "fr", "portuguese": "pt", 
    "korean": "ko", "japanese": "ja", "german": "de", "hindi": "hi", "russian": "ru"
}

def normalize_text(text):
    """Normalize text for fair ASR accuracy comparison (lowercase, strip punctuation)."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def parse_transcription(result):
    """Robustly parse transcription output format from Qwen3-ASR."""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        for key in ["text", "transcription", "transcript", "value"]:
            if key in result:
                return result[key]
        return str(result)
    if isinstance(result, list) and len(result) > 0:
        return parse_transcription(result[0])
    return str(result)

def main():
    input_csv = "test_cases.csv"
    output_csv = "eval_results.csv"
    output_dir = "eval_outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(input_csv):
        print(f"❌ Input CSV '{input_csv}' not found. Please create it first.")
        return

    print("📖 Loading test cases...")
    df = pd.read_csv(input_csv)
    
    # Verify required columns exist
    required_cols = ["id", "text", "voice", "language"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column in CSV: '{col}'")

    print("🤖 Initializing Supertonic TTS Engine...")
    tts = TTS(auto_download=True)

    print("🤗 Initializing Qwen3-ASR-1.7B Model on CPU (may take a moment to download)...")
    from qwen_asr import Qwen3ASRModel
    asr_model = Qwen3ASRModel.from_pretrained(
        "Qwen/Qwen3-ASR-1.7B", 
        device_map="cpu", 
        torch_dtype=torch.float32
    )

    results = []

    print("\n🚀 Starting Evaluation Pipeline...")
    for idx, row in df.iterrows():
        case_id = row["id"]
        original_text = row["text"]
        voice_preset = row["voice"]
        language_name = row["language"].strip().lower()
        
        print(f"\n--- Case {case_id} [{language_name.capitalize()} - {voice_preset}] ---")
        print(f"Text: '{original_text}'")
        
        audio_path = os.path.join(output_dir, f"case_{case_id}.wav")
        asr_transcript = ""
        wer = 1.0
        cer = 1.0
        status = "Success"
        
        try:
            # 1. Resolve Language Code
            lang_code = LANGUAGES.get(language_name, "na")
            
            # 2. Load Voice Style
            if voice_preset.endswith(".json") and os.path.exists(voice_preset):
                voice_style = tts.get_voice_style_from_path(voice_preset)
            else:
                voice_style = tts.get_voice_style(voice_name=voice_preset)
            
            # 3. Synthesize Audio
            print("  [TTS] Synthesizing speech...")
            wav, _ = tts.synthesize(original_text, voice_style=voice_style, lang=lang_code)
            tts.save_audio(wav, audio_path)
            
            # 4. Transcribe Audio
            print("  [ASR] Transcribing audio with Qwen3-ASR...")
            raw_asr_out = asr_model.transcribe(audio=audio_path)
            asr_transcript = parse_transcription(raw_asr_out)
            print(f"  [ASR Result]: '{asr_transcript}'")
            
            # 5. Compute Metrics
            ref_norm = normalize_text(original_text)
            hyp_norm = normalize_text(asr_transcript)
            
            if ref_norm and hyp_norm:
                wer = jiwer.wer(ref_norm, hyp_norm)
                cer = jiwer.cer(ref_norm, hyp_norm)
            elif not ref_norm and not hyp_norm:
                wer = 0.0
                cer = 0.0
            else:
                wer = 1.0
                cer = 1.0
                
            print(f"  [Metrics] WER: {wer:.2%}, CER: {cer:.2%}")
            
        except Exception as e:
            status = f"Error: {str(e)}"
            print(f"  ❌ Error: {status}")
            traceback.print_exc()
            
        results.append({
            "id": case_id,
            "original_text": original_text,
            "voice": voice_preset,
            "language": row["language"],
            "generated_audio_path": audio_path if os.path.exists(audio_path) else "",
            "asr_transcript": asr_transcript,
            "wer": wer,
            "cer": cer,
            "status": status
        })

    # Save results to CSV
    print(f"\n💾 Saving evaluation results to '{output_csv}'...")
    res_df = pd.DataFrame(results)
    res_df.to_csv(output_csv, index=False)
    print("✨ Evaluation complete!")

if __name__ == "__main__":
    main()
