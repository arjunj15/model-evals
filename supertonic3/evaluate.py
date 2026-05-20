# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "supertonic",
#     "google-genai",
#     "pydantic",
#     "python-dotenv",
#     "pandas",
#     "soundfile",
# ]
# ///
import os
import traceback
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from supertonic import TTS

# Load environment variables (such as GEMINI_API_KEY from .env file)
load_dotenv(find_dotenv())

# Verify GEMINI_API_KEY exists
if not os.environ.get("GEMINI_API_KEY"):
    raise ValueError(
        "❌ GEMINI_API_KEY environment variable is not set.\n"
        "Please specify it in your environment or in a '.env' file in your project root."
    )

# Language mappings for Supertonic 3
LANGUAGES = {
    "english": "en", "spanish": "es", "french": "fr", "portuguese": "pt", 
    "korean": "ko", "japanese": "ja", "german": "de", "hindi": "hi", "russian": "ru"
}

# Define the Pydantic schema for structured evaluation output
class AudioEvaluation(BaseModel):
    clarity_score: int = Field(..., description="Score 1-5 for pronunciation and clarity (5 is perfect, 1 is completely unintelligible).")
    clarity_reason: str = Field(..., description="Short rationale for the clarity score.")
    prosody_score: int = Field(..., description="Score 1-5 for prosody and intonation (5 is natural pitch/inflection, 1 is completely robotic/monotone).")
    prosody_reason: str = Field(..., description="Short rationale for the prosody score.")
    pacing_score: int = Field(..., description="Score 1-5 for pacing and rhythm (5 is natural speaking speed/pauses, 1 is too fast/slow/weird pause locations).")
    pacing_reason: str = Field(..., description="Short rationale for the pacing score.")
    artifacts_score: int = Field(..., description="Score 1-5 for absence of artifacts (5 is clean studio quality, 1 has heavy digital distortion/pops/noise).")
    artifacts_reason: str = Field(..., description="Short rationale for the artifacts score.")
    expressiveness_score: int = Field(..., description="Score 1-5 for emotional rendering and tag handling (5 renders breath/laugh/sigh naturally, 1 is completely emotionless/ignores tags).")
    expressiveness_reason: str = Field(..., description="Short rationale for the expressiveness score.")
    overall_score: float = Field(..., description="Overall naturalness score (calculated average of the 5 scores).")
    overall_summary: str = Field(..., description="Summary of the voice quality, naturalness, and realism.")

def main():
    input_csv = "test_cases.csv"
    output_csv = "eval_results.csv"
    output_dir = "eval_outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(input_csv):
        print(f"❌ Input CSV '{input_csv}' not found. Please run this script in the directory containing 'test_cases.csv'.")
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

    print("🤗 Initializing Gemini Client (loading key from environment)...")
    client = genai.Client()

    results = []

    print("\n🚀 Starting Evaluation Pipeline with LLM-as-a-Judge (gemini-3.1-flash-lite)...")
    for idx, row in df.iterrows():
        case_id = row["id"]
        original_text = row["text"]
        voice_preset = row["voice"]
        language_name = row["language"].strip().lower()
        
        print(f"\n--- Case {case_id} [{language_name.capitalize()} - {voice_preset}] ---")
        print(f"Text: '{original_text}'")
        
        audio_path = os.path.join(output_dir, f"case_{case_id}.wav")
        status = "Success"
        
        # Initialize default model outputs in case of evaluation error
        clarity_s, clarity_r = 0, "N/A"
        prosody_s, prosody_r = 0, "N/A"
        pacing_s, pacing_r = 0, "N/A"
        artifacts_s, artifacts_r = 0, "N/A"
        expressiveness_s, expressiveness_r = 0, "N/A"
        overall_s, overall_sum = 0.0, "Evaluation failed."

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
            
            # 4. Read Audio Bytes
            with open(audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()

            # 5. Evaluate Audio using Gemini LLM-as-a-Judge
            print("  [Judge] Sending audio to gemini-3.1-flash-lite for evaluation...")
            prompt = (
                f"You are an expert audio quality judge. Please listen to this synthesized speech clip and evaluate its naturalness and human-likeness.\n\n"
                f"Context details:\n"
                f"- Original script text: \"{original_text}\"\n"
                f"- Intended Voice Style: \"{voice_preset}\"\n"
                f"- Intended Language: \"{language_name.capitalize()}\"\n\n"
                f"Perform a detailed analysis and score the audio on each of the criteria using the schema provided."
            )
            
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=[
                    prompt,
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type="audio/wav"
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AudioEvaluation,
                )
            )
            
            # Parse structured Pydantic response
            eval_result: AudioEvaluation = response.parsed
            
            clarity_s = eval_result.clarity_score
            clarity_r = eval_result.clarity_reason
            prosody_s = eval_result.prosody_score
            prosody_r = eval_result.prosody_reason
            pacing_s = eval_result.pacing_score
            pacing_r = eval_result.pacing_reason
            artifacts_s = eval_result.artifacts_score
            artifacts_r = eval_result.artifacts_reason
            expressiveness_s = eval_result.expressiveness_score
            expressiveness_r = eval_result.expressiveness_reason
            overall_s = eval_result.overall_score
            overall_sum = eval_result.overall_summary

            print(f"  [Result] Overall Naturalness Score: {overall_s:.2f}/5.0")
            print(f"  [Clarity: {clarity_s}/5] [Prosody: {prosody_s}/5] [Pacing: {pacing_s}/5] [Artifacts: {artifacts_s}/5] [Expressiveness: {expressiveness_s}/5]")
            print(f"  [Summary] {overall_sum}")
            
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
            "clarity_score": clarity_s,
            "clarity_reason": clarity_r,
            "prosody_score": prosody_s,
            "prosody_reason": prosody_r,
            "pacing_score": pacing_s,
            "pacing_reason": pacing_r,
            "artifacts_score": artifacts_s,
            "artifacts_reason": artifacts_r,
            "expressiveness_score": expressiveness_s,
            "expressiveness_reason": expressiveness_r,
            "overall_score": overall_s,
            "overall_summary": overall_sum,
            "status": status
        })

    # Save results to CSV
    print(f"\n💾 Saving evaluation results to '{output_csv}'...")
    res_df = pd.DataFrame(results)
    res_df.to_csv(output_csv, index=False)
    print("✨ Evaluation complete!")

if __name__ == "__main__":
    main()
