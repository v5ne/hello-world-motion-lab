import html
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Hello World Motion Lab", page_icon="✨", layout="wide")

st.title("✨ Hello World Motion Lab")
st.caption("A tiny app for experimenting with names, fonts, colors, and motion.")

with st.sidebar:
    st.header("Controls")
    name = st.text_input("Enter your name", value="Hello World", max_chars=80)
    font_family = st.selectbox(
        "Font type",
        ["Arial", "Courier New", "Georgia", "Times New Roman", "Verdana", "Trebuchet MS", "Impact"],
    )
    font_size = st.slider("Font size", min_value=20, max_value=100, value=48, step=2)
    background = st.selectbox(
        "Background",
        ["Light", "Dark", "Sky", "Sunset", "Forest", "Lavender", "Ocean"],
    )
    name_mode = st.selectbox("Name display mode", ["Centered", "Ticker Tape", "Repeated"])
    effect = st.selectbox(
        "Dynamic action",
        ["None", "Rain", "Snow", "Hail", "Wind Gust", "Confetti", "Tornado"],
    )
    speed = st.slider("Animation speed", min_value=1, max_value=10, value=5,
                      help="Higher values move the effect faster.")
    text_color = st.selectbox("Name color", ["Auto", "White", "Black", "Yellow", "Pink", "Cyan"])

backgrounds = {
    "Light": ("#f8fafc", "#172033"),
    "Dark": ("#10131c", "#ffffff"),
    "Sky": ("linear-gradient(135deg, #dff5ff, #91d7f5)", "#10304a"),
    "Sunset": ("linear-gradient(135deg, #ffb36b, #e879a9, #7b6de0)", "#ffffff"),
    "Forest": ("linear-gradient(135deg, #163d32, #4b8b62)", "#ffffff"),
    "Lavender": ("linear-gradient(135deg, #f0e7ff, #c4b5fd)", "#30204a"),
    "Ocean": ("linear-gradient(135deg, #064e7a, #18a6b8)", "#ffffff"),
}
bg, default_text = backgrounds[background]
colors = {
    "Auto": default_text,
    "White": "#ffffff",
    "Black": "#111111",
    "Yellow": "#ffe66d",
    "Pink": "#ff5fa2",
    "Cyan": "#67e8f9",
}
safe_name = html.escape(name or "Hello World")
safe_font = font_family.replace("'", "").replace('"', "")
name_color = colors[text_color]

# Build the name display using escaped user input.
if name_mode == "Repeated":
    name_markup = "<div class='repeated'>" + "<span>" + safe_name + "</span>" * 5 + "</div>"
elif name_mode == "Ticker Tape":
    name_markup = f"<div class='ticker'><span>{safe_name}&nbsp;&nbsp;&nbsp;✦&nbsp;&nbsp;&nbsp;{safe_name}&nbsp;&nbsp;&nbsp;✦&nbsp;&nbsp;&nbsp;</span></div>"
else:
    name_markup = f"<div class='center-name'>{safe_name}</div>"

effect_class = {
    "None": "none",
    "Rain": "rain",
    "Snow": "snow",
    "Hail": "hail",
    "Wind Gust": "wind",
    "Confetti": "confetti",
    "Tornado": "tornado",
}[effect]

# Motion is animated by CSS in the embedded component, so it loops smoothly
# without repeatedly rerunning the entire Streamlit script.
html_doc = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
.scene {{
  position: relative; width: 100%; height: 600px; overflow: hidden;
  border-radius: 18px; background: {bg}; color: {name_color};
  font-family: "{safe_font}", sans-serif;
}}
.name-layer {{
  position: absolute; inset: 0; z-index: 3; display: flex;
  align-items: center; justify-content: center; padding: 24px;
  font-size: {font_size}px; font-weight: 700; text-align: center;
  overflow: hidden; overflow-wrap: anywhere; text-shadow: 0 2px 10px #0002;
}}
.center-name {{ max-width: 100%; }}
.repeated {{ display: flex; flex-direction: column; gap: 12px; align-items: center; }}
.repeated span {{ line-height: 1.05; }}
.ticker {{ white-space: nowrap; width: 100%; overflow: hidden; }}
.ticker span {{ display: inline-block; padding-left: 100%; animation: ticker {max(5, 22 - speed * 1.5)}s linear infinite; }}
@keyframes ticker {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-100%); }} }}
.particle {{
  position: absolute; top: -12%; left: var(--x); font-size: var(--size);
  opacity: var(--opacity, .85); animation: fall var(--duration) linear infinite;
  animation-delay: var(--delay); z-index: 1; pointer-events: none;
}}
@keyframes fall {{ 0% {{ transform: translate3d(0,-10%,0) rotate(0deg); }} 100% {{ transform: translate3d(var(--drift, 0px),720px,0) rotate(360deg); }} }}
.wind-line {{
  position: absolute; left: -45%; top: var(--y); height: 3px; width: var(--w);
  border-radius: 99px; background: currentColor; opacity: .35;
  animation: gust var(--duration) ease-in-out infinite; animation-delay: var(--delay);
}}
@keyframes gust {{ 0% {{ transform: translateX(0) scaleX(.6); opacity: 0; }} 20% {{ opacity: .45; }} 100% {{ transform: translateX(190%) scaleX(1.2); opacity: 0; }} }}
.tornado-swirl {{
  position: absolute; left: 50%; top: 50%; width: var(--w); height: var(--h);
  border: 3px solid currentColor; border-left-color: transparent; border-bottom-color: transparent;
  border-radius: 50%; opacity: .45; transform: translate(-50%,-50%);
  animation: swirl var(--duration) linear infinite; animation-delay: var(--delay);
}}
@keyframes swirl {{ from {{ transform: translate(-50%,-50%) rotate(0deg) scaleX(1); }} to {{ transform: translate(-50%,-50%) rotate(360deg) scaleX(.45); }} }}
.effect-label {{ position:absolute; z-index:2; bottom:14px; right:16px; font: 12px Arial,sans-serif; opacity:.65; }}
</style>
</head>
<body>
<div class="scene">
  <div class="effects {effect_class}" aria-hidden="true">
"""

symbols = {
    "Rain": ("💧", 45),
    "Snow": ("❄️", 38),
    "Hail": ("🧊", 32),
    "Confetti": ("🎉", 42),
}
if effect in symbols:
    symbol, count = symbols[effect]
    particles = []
    for i in range(count):
        x = (i * 37 + 11) % 100
        size = 10 + ((i * 13) % 19)
        duration = max(2.0, (13 - speed) * 0.55 + ((i * 7) % 30) / 10)
        delay = -(((i * 11) % 35) / 10)
        drift = ((i * 19) % 121) - 60
        particles.append(
            f"<span class='particle' style='--x:{x}%;--size:{size}px;--duration:{duration:.1f}s;"
            f"--delay:{delay:.1f}s;--drift:{drift}px'>{symbol}</span>"
        )
    html_doc += "".join(particles)
elif effect == "Wind Gust":
    gusts = []
    for i in range(14):
        gusts.append(
            f"<span class='wind-line' style='--y:{5 + (i * 7) % 90}%;--w:{70 + (i * 23) % 180}px;"
            f"--duration:{max(1.2, 6 - speed * .4 + (i % 4) * .3):.1f}s;--delay:{-(i % 7) * .6:.1f}s'></span>"
        )
    html_doc += "".join(gusts)
elif effect == "Tornado":
    swirls = []
    for i in range(12):
        swirls.append(
            f"<span class='tornado-swirl' style='--w:{90 + i * 20}px;--h:{35 + i * 12}px;"
            f"--duration:{max(1.5, 8 - speed * .5 + i * .12):.1f}s;--delay:{-i * .25:.1f}s'></span>"
        )
    html_doc += "".join(swirls)

html_doc += f"""
  </div>
  <div class="name-layer">{name_markup}</div>
  <div class="effect-label">{effect if effect != "None" else "Ready to say hello!"}</div>
</div>
</body>
</html>
"""

components.html(html_doc, height=620, scrolling=False)

st.caption("Tip: change the controls in the sidebar to try different looks and animations.")
