# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "gradio>=4.0.0",
#     "supertonic",
# ]
# ///
import gradio as gr
from supertonic import TTS
import os
import traceback

print("Initializing Supertonic 3 Local Voice-Cloning Radio...")
tts = TTS(auto_download=True)

LANGUAGES = {
    "English": "en", "Spanish": "es", "French": "fr", "Portuguese": "pt", 
    "Korean": "ko", "Japanese": "ja", "German": "de", "Hindi": "hi", "Russian": "ru"
}
PRESET_VOICES = ["M1", "M2", "F1", "F2"]

def generate_radio_broadcast(text, mode, voice_preset, custom_file_path, language_name):
    try:
        lang_code = LANGUAGES[language_name]
        
        # --- Voice Selection Logic ---
        if mode == "Use Custom Voice Style JSON":
            if not custom_file_path:
                return None, "❌ Please upload a custom voice style .json file!"
            
            # Check file extension
            _, ext = os.path.splitext(custom_file_path.lower())
            if ext in [".wav", ".mp3", ".m4a", ".ogg", ".flac"]:
                # Guide the user gracefully when they try to clone a raw audio file directly
                audio_filename = os.path.basename(custom_file_path)
                error_msg = (
                    f"⚠️ Direct voice cloning from raw audio files ({audio_filename}) is not supported locally by the Supertonic SDK.\n\n"
                    "💡 How to clone this voice:\n"
                    "1. Visit the Supertonic Voice Builder: https://supertonic.supertone.ai/voice-builder\n"
                    "2. Upload your audio file there to extract the voice print.\n"
                    "3. Download the generated voice-style .json file.\n"
                    "4. Upload the downloaded .json file here to run synthesis locally!"
                )
                return None, error_msg
                
            # Load the custom style from the JSON file (downloaded from Supertonic Voice Builder)
            print(f"Loading custom voice style from: {custom_file_path}")
            voice_style = tts.get_voice_style_from_path(custom_file_path)
            status_prefix = "👤 Successfully Loaded Custom Voice Style"
        else:
            # Fallback to the built-in presets
            voice_style = tts.get_voice_style(voice_name=voice_preset)
            status_prefix = f"📻 Using Preset Voice '{voice_preset}'"
        
        # Synthesize audio using the selected style vector
        wav, duration = tts.synthesize(text, voice_style=voice_style, lang=lang_code)
        
        output_filename = "cloned_radio_output.wav"
        tts.save_audio(wav, output_filename)
        
        # Safely convert duration to float
        try:
            duration_val = float(duration[0])
        except (TypeError, IndexError, KeyError):
            try:
                duration_val = float(duration)
            except TypeError:
                duration_val = 0.0

        return output_filename, f"✨ {status_prefix}. Generated {duration_val:.2f} seconds of audio."
        
    except Exception as e:
        error_details = traceback.format_exc()
        return None, f"❌ Error during synthesis: {str(e)}\n\n{error_details}"

# Define custom premium styling/theme
theme = gr.themes.Glass(
    primary_hue="violet",
    secondary_hue="indigo",
    neutral_hue="slate",
).set(
    body_background_fill="*neutral_950",
    block_background_fill="*neutral_900",
    block_border_color="*neutral_800",
    button_primary_background_fill="linear-gradient(90deg, *primary_600 0%, *secondary_600 100%)",
    button_primary_background_fill_hover="linear-gradient(90deg, *primary_500 0%, *secondary_500 100%)",
    button_primary_text_color="*white",
)

custom_css = """
/* Make the main container have a subtle glow */
.gradio-container {
    font-family: 'Outfit', 'Inter', sans-serif !important;
    max-width: 1200px !important;
    margin: 0 auto !important;
    padding: 2rem !important;
}

/* Glassmorphism accent lines */
h1 {
    background: linear-gradient(90deg, #a78bfa 0%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    letter-spacing: -0.025em;
}

/* Make logs look like a terminal output */
textarea {
    font-family: 'Fira Code', 'Courier New', monospace !important;
}

/* Custom visual cards for documentation and tips */
.tip-card {
    background: rgba(139, 92, 246, 0.05);
    border: 1px solid rgba(139, 92, 246, 0.15);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
}

.tip-card code {
    background: rgba(139, 92, 246, 0.15);
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    color: #c084fc;
    font-family: monospace;
}
"""

js_func = """
function forceDarkTheme() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""

with gr.Blocks(title="Supertonic 3 Voice Cloner") as demo:
    with gr.Row():
        with gr.Column(scale=4):
            gr.Markdown(
                """
                # 📻 Supertonic 3 Local Voice Studio
                Experience **Supertone's Supertonic 3** Text-to-Speech model with custom voice styles running 100% locally on your Mac's CPU.
                No cloud calls, zero external API latency, and studio-grade 44.1kHz audio.
                """
            )
            
    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(
                label="Radio Script / Text Input",
                placeholder="Type what you want the radio host to say...",
                value="Hello audience! <breath> You are listening to a custom version of my voice running entirely on a Mac. <laugh>",
                lines=5
            )
            
            # Interactive visual tips cards using markdown
            gr.HTML(
                """
                <div class="tip-card">
                    <h4 style="margin-top: 0; color: #a78bfa; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                        👤 Using Custom Voices
                    </h4>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; line-height: 1.5; color: #94a3b8;">
                        Supertonic 3 runs fixed presets locally. To use a custom voice:
                        <br/>
                        1. Visit the official <a href="https://supertonic.supertone.ai/voice-builder" target="_blank" style="color: #a78bfa; text-decoration: underline;">Supertonic Voice Builder</a>.
                        <br/>
                        2. Extract and download your voice-style <code>.json</code> embedding file.
                        <br/>
                        3. Select "Use Custom Voice (JSON / Audio)" below and upload that <code>.json</code> file.
                    </p>
                </div>
                """
            )
            
            # Choose between preset voices or custom style JSON
            mode_select = gr.Radio(
                choices=["Use Factory Presets", "Use Custom Voice Style JSON"],
                value="Use Factory Presets",
                label="Voice Source Mode"
            )
            
            # Context-aware inputs based on mode choice
            with gr.Row():
                voice_preset_dropdown = gr.Dropdown(
                    choices=PRESET_VOICES, 
                    value="M1", 
                    label="Preset Selection",
                    visible=True,
                    info="Choose masculine (M) or feminine (F) voice presets"
                )
                lang_select = gr.Dropdown(
                    choices=list(LANGUAGES.keys()), 
                    value="English", 
                    label="Target Language",
                    info="Select target script language"
                )
            
            # File uploader for custom voice style json or reference audio
            custom_json_input = gr.File(
                label="Upload Voice Style (.json) or Audio Reference (.wav, .mp3, .m4a)", 
                file_types=[".json", ".wav", ".mp3", ".m4a", ".ogg", ".flac"],
                type="filepath",
                visible=False
            )
            
            submit_btn = gr.Button("📡 Clone & Broadcast", variant="primary")
            
        with gr.Column(scale=1):
            gr.Markdown("### 🎛️ Audio Receiver")
            audio_output = gr.Audio(
                label="Synthesized Broadcast Output", 
                type="filepath", 
                interactive=False
            )
            
            status_output = gr.Textbox(
                label="System Status Logs", 
                value="System Idle. Ready to synthesize broadcast.", 
                interactive=False,
                lines=5
            )

    # Wire up the dynamic toggle listener
    def toggle_voice_inputs(mode):
        if mode == "Use Custom Voice Style JSON":
            return gr.Dropdown(visible=False), gr.File(visible=True)
        else:
            return gr.Dropdown(visible=True), gr.File(visible=False)

    mode_select.change(
        fn=toggle_voice_inputs,
        inputs=[mode_select],
        outputs=[voice_preset_dropdown, custom_json_input]
    )

    submit_btn.click(
        fn=generate_radio_broadcast,
        inputs=[text_input, mode_select, voice_preset_dropdown, custom_json_input, lang_select],
        outputs=[audio_output, status_output]
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True, theme=theme, css=custom_css, js=js_func)
