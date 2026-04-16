
import os
import base64
import numpy as np
import streamlit as st
from openai import OpenAI
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="El Forjador de Historias",
    page_icon="⚔️",
    layout="centered",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

/* ── Root variables ── */
:root {
    --ink:        #1a1209;
    --parchment:  #f5ead6;
    --parchment2: #ede0c4;
    --gold:       #c9922a;
    --gold-light: #e8b84b;
    --crimson:    #8b1a1a;
    --shadow:     rgba(0,0,0,0.55);
}

/* ── Background ── */
.stApp {
    background: var(--ink);
    background-image:
        radial-gradient(ellipse at 20% 10%, rgba(201,146,42,0.08) 0%, transparent 55%),
        radial-gradient(ellipse at 80% 90%, rgba(139,26,26,0.10) 0%, transparent 55%),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='4' height='4'%3E%3Crect width='4' height='4' fill='%231a1209'/%3E%3Ccircle cx='1' cy='1' r='0.6' fill='%23ffffff08'/%3E%3C/svg%3E");
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 760px; }

/* ── Masthead ── */
.masthead {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    border-bottom: 2px solid var(--gold);
    margin-bottom: 2rem;
    position: relative;
}
.masthead::before, .masthead::after {
    content: '✦';
    color: var(--gold);
    font-size: 1.1rem;
    position: absolute;
    bottom: -0.75rem;
    background: var(--ink);
    padding: 0 0.6rem;
}
.masthead::before { left: 50%; transform: translateX(-50%); }
.masthead::after  { display: none; }

.masthead h1 {
    font-family: 'Cinzel Decorative', serif;
    font-size: clamp(1.6rem, 5vw, 2.6rem);
    font-weight: 900;
    color: var(--gold-light);
    letter-spacing: 0.04em;
    text-shadow: 0 0 30px rgba(201,146,42,0.5), 2px 2px 0 var(--crimson);
    margin: 0 0 0.4rem;
    line-height: 1.2;
}
.masthead p {
    font-family: 'Lora', serif;
    font-style: italic;
    color: #b89a6a;
    font-size: 0.95rem;
    margin: 0;
}

/* ── Section labels ── */
.section-label {
    font-family: 'Cinzel Decorative', serif;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, var(--gold), transparent);
}

/* ── Canvas frame ── */
.canvas-frame {
    border: 2px solid var(--gold);
    border-radius: 4px;
    box-shadow:
        0 0 0 6px rgba(201,146,42,0.08),
        0 0 30px rgba(0,0,0,0.6),
        inset 0 0 20px rgba(201,146,42,0.04);
    overflow: hidden;
    background: #fff;
    margin-bottom: 1.5rem;
}

/* ── Input fields ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: rgba(245,234,214,0.06) !important;
    border: 1px solid rgba(201,146,42,0.35) !important;
    border-radius: 3px !important;
    color: var(--parchment) !important;
    font-family: 'Lora', serif !important;
}
.stTextInput label, .stSelectbox label {
    color: #b89a6a !important;
    font-family: 'Lora', serif !important;
    font-size: 0.85rem !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #120d06 !important;
    border-right: 1px solid rgba(201,146,42,0.2) !important;
}
[data-testid="stSidebar"] * { color: #b89a6a !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family: 'Cinzel Decorative', serif !important;
    color: var(--gold) !important;
}
.stSlider > div > div > div > div { background: var(--gold) !important; }

/* ── Primary button ── */
.stButton > button {
    font-family: 'Cinzel Decorative', serif !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.12em !important;
    background: linear-gradient(135deg, #8b1a1a 0%, #6b1313 100%) !important;
    color: var(--gold-light) !important;
    border: 1px solid var(--gold) !important;
    border-radius: 3px !important;
    padding: 0.65rem 2rem !important;
    text-transform: uppercase !important;
    box-shadow: 0 4px 20px rgba(139,26,26,0.4), inset 0 1px 0 rgba(255,255,255,0.08) !important;
    transition: all 0.25s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #a82020 0%, #8b1a1a 100%) !important;
    box-shadow: 0 6px 30px rgba(139,26,26,0.6), 0 0 15px rgba(201,146,42,0.2) !important;
    transform: translateY(-1px) !important;
}

/* ── Story scroll ── */
.story-scroll {
    background:
        linear-gradient(180deg, rgba(245,234,214,0.97) 0%, rgba(237,224,196,0.97) 100%);
    border: 1px solid #c4a96a;
    border-radius: 2px;
    padding: 2rem 2.2rem;
    margin-top: 1.5rem;
    box-shadow:
        0 0 0 4px rgba(201,146,42,0.12),
        0 12px 40px rgba(0,0,0,0.5),
        inset 0 0 40px rgba(180,150,90,0.15);
    position: relative;
    animation: unfurl 0.6s ease-out;
}
@keyframes unfurl {
    from { opacity: 0; transform: translateY(12px) scaleY(0.97); }
    to   { opacity: 1; transform: translateY(0)  scaleY(1); }
}
.story-scroll::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(to right, transparent, var(--gold), transparent);
}

.story-character-name {
    font-family: 'Cinzel Decorative', serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--crimson);
    margin-bottom: 0.2rem;
    text-shadow: 1px 1px 0 rgba(201,146,42,0.3);
}
.story-body {
    font-family: 'Lora', serif;
    font-size: 0.97rem;
    line-height: 1.85;
    color: #2e1f0e;
    margin-top: 0.8rem;
    white-space: pre-wrap;
}
.story-body::first-letter {
    font-size: 3.2rem;
    font-family: 'Cinzel Decorative', serif;
    font-weight: 900;
    color: var(--crimson);
    float: left;
    line-height: 0.75;
    margin: 0.1rem 0.15rem 0 0;
    text-shadow: 2px 2px 0 rgba(201,146,42,0.4);
}
.story-divider {
    text-align: center;
    color: var(--gold);
    margin: 1rem 0 0;
    font-size: 1.1rem;
    letter-spacing: 0.5rem;
}

/* ── Warning / info ── */
.stWarning, .stInfo {
    border-radius: 3px !important;
    border-left: 3px solid var(--gold) !important;
    background: rgba(201,146,42,0.08) !important;
    color: #b89a6a !important;
    font-family: 'Lora', serif !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--gold) !important; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def build_prompt(name: str, genre: str, tone: str) -> str:
    genre_map = {
        "Fantasía épica": "epic high fantasy",
        "Terror gótico": "gothic horror",
        "Ciencia ficción": "science fiction",
        "Noir / Misterio": "noir mystery",
        "Mitología": "ancient mythology",
    }
    tone_map = {
        "Épico y solemne": "epic and solemn, with grand descriptions",
        "Oscuro y melancólico": "dark and melancholic, with a brooding atmosphere",
        "Misterioso": "mysterious and cryptic, revealing little at a time",
        "Poético": "lyrical and poetic, rich with metaphor",
    }
    return f"""You are a master storyteller and lore-keeper. 
A user has drawn a character sketch. Based on the image, craft a rich character backstory in Spanish.

Character name: {name if name else 'unknown — infer a name from the drawing'}
Genre: {genre_map.get(genre, 'fantasy')}
Tone: {tone_map.get(tone, 'epic and solemne')}

Write the backstory in Spanish with these sections, flowing as a single narrative (do NOT use headers or bullet points):
1. Who they are and what they look like (based on the drawing)
2. Their origin and birthplace
3. A defining tragedy or turning point in their life
4. Their greatest strength and their deepest flaw
5. What they seek — their driving goal or obsession

Keep it between 220–280 words. Make it feel legendary, unforgettable. Begin directly with the story."""


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚔️ El Forjador")
    st.markdown("---")
    stroke_width = st.slider("Grosor del trazo", 1, 25, 5)
    st.markdown("---")
    st.markdown("### Configura tu clave")
    api_key_input = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    st.markdown("---")
    st.markdown(
        "<small style='font-style:italic;'>Dibuja un personaje · Nómbralo · "
        "Elige género y tono · Descubre su historia</small>",
        unsafe_allow_html=True,
    )

# ─── MASTHEAD ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="masthead">
    <h1>⚔️ El Forjador de Historias</h1>
    <p>Dibuja un personaje · Descubre su leyenda</p>
</div>
""", unsafe_allow_html=True)

# ─── DRAWING SECTION ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">✦ Lienzo del personaje</div>', unsafe_allow_html=True)

st.markdown('<div class="canvas-frame">', unsafe_allow_html=True)
canvas_result = st_canvas(
    fill_color="rgba(255,165,0,0.0)",
    stroke_width=stroke_width,
    stroke_color="#1a1209",
    background_color="#f5ead6",
    height=320,
    width=720,
    drawing_mode="freedraw",
    key="canvas",
)
st.markdown('</div>', unsafe_allow_html=True)

# ─── CHARACTER OPTIONS ────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    char_name = st.text_input("Nombre del personaje", placeholder="Deja vacío para que la IA lo invente")
with col2:
    genre = st.selectbox("Género narrativo", [
        "Fantasía épica", "Terror gótico", "Ciencia ficción", "Noir / Misterio", "Mitología"
    ])
with col3:
    tone = st.selectbox("Tono de la historia", [
        "Épico y solemne", "Oscuro y melancólico", "Misterioso", "Poético"
    ])

st.markdown("<br>", unsafe_allow_html=True)

# ─── BUTTON ───────────────────────────────────────────────────────────────────
forge_button = st.button("✦ Forjar la historia ✦", type="primary")

# ─── LOGIC ────────────────────────────────────────────────────────────────────
api_key = api_key_input.strip()

if forge_button:
    if not api_key:
        st.warning("Ingresa tu OpenAI API Key en el panel lateral para continuar.")
    elif canvas_result.image_data is None:
        st.warning("Dibuja un personaje en el lienzo antes de continuar.")
    else:
        with st.spinner("Los pergaminos se despliegan… la historia toma forma…"):
            # Save canvas as image
            img_array = np.array(canvas_result.image_data)
            img = Image.fromarray(img_array.astype("uint8"), "RGBA")
            img.save("character_sketch.png")
            b64_img = encode_image_to_base64("character_sketch.png")

            prompt = build_prompt(char_name, genre, tone)
            client = OpenAI(api_key=api_key)

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{b64_img}"
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=600,
                )
                story = response.choices[0].message.content or ""
                display_name = char_name.strip() if char_name.strip() else "El Desconocido"

                st.markdown(f"""
<div class="story-scroll">
    <div class="story-character-name">{display_name}</div>
    <div style="font-family:'Lora',serif;font-style:italic;font-size:0.8rem;color:#8b6a3a;">
        {genre} · {tone}
    </div>
    <div class="story-body">{story}</div>
    <div class="story-divider">✦ · ✦ · ✦</div>
</div>
""", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Ocurrió un error al invocar la API: {e}")
