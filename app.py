
import json
import re

import streamlit as st
from ollama import chat

MODEL = "qwen2.5:3b"

st.set_page_config(
    page_title="TouchGrass AI",
    page_icon="🌱",
    layout="centered",
)

st.title("🌱 TouchGrass AI")
st.caption("AI that gets you away from AI.")
st.write(
    "Generate a small outdoor adventure, complete your missions, "
    "and earn your TouchGrass score."
)

# Store generated adventure and progress across Streamlit reruns.
if "adventure" not in st.session_state:
    st.session_state.adventure = None

if "completed" not in st.session_state:
    st.session_state.completed = []

if "outdoor_mode" not in st.session_state:
    st.session_state.outdoor_mode = False


def create_adventure(time_available, environment, difficulty, interest):
    prompt = f"""
You are TouchGrass AI, a safe outdoor adventure planner.

Create a short outdoor adventure using these preferences:
- Time available: {time_available}
- Environment: {environment}
- Difficulty: {difficulty}
- Interests: {interest or "nature exploration"}

Return ONLY valid JSON in this exact structure:
{{
  "title": "A short adventure title",
  "intro": "One short encouraging sentence",
  "missions": [
    "First mission",
    "Second mission",
    "Third mission",
    "Fourth mission"
  ],
  "final_challenge": "One final challenge"
}}

Rules:
- Exactly four missions.
- Every mission must be possible outdoors.
- No expensive equipment.
- Make missions safe, accessible, and respectful of wildlife.
- Do not ask users to eat, touch, or collect unknown plants,
  disturb animals, trespass, or enter unsafe areas.
- Adapt missions to the selected environment and time.
- Keep each mission concise.
"""

    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        format="json",
        options={"temperature": 0.8},
    )

    content = response["message"]["content"]
    data = json.loads(content)

    missions = data.get("missions", [])
    if not isinstance(missions, list) or len(missions) != 4:
        raise ValueError("The AI did not return exactly four missions.")

    if not all(isinstance(mission, str) and mission.strip()
               for mission in missions):
        raise ValueError("One or more missions were empty.")

    final_challenge = data.get("final_challenge", "")
    if not isinstance(final_challenge, str) or not final_challenge.strip():
        raise ValueError("The final challenge was missing.")

    return {
        "title": str(data.get("title", "Your Outdoor Adventure")),
        "intro": str(data.get("intro", "Take a breath and explore.")),
        "missions": missions,
        "final_challenge": final_challenge,
    }


if not st.session_state.outdoor_mode:
    st.subheader("Plan your adventure")

    with st.form("adventure_form"):
        time_available = st.selectbox(
            "⏱️ How much time do you have?",
            ["10 minutes", "20 minutes", "30 minutes", "1 hour"],
        )

        environment = st.selectbox(
            "🌳 Where are you going?",
            [
                "Park",
                "Garden",
                "Neighborhood",
                "Forest or trail",
                "Beach",
                "Any safe outdoor place",
            ],
        )

        difficulty = st.select_slider(
            "🎯 Difficulty",
            options=["Easy", "Medium", "Adventure"],
        )

        interest = st.text_input(
            "✨ What interests you?",
            placeholder="Birds, plants, photography, clouds...",
        )

        generate = st.form_submit_button("🌱 Create My Adventure")

    if generate:
        try:
            with st.spinner("Your local AI is planning your adventure..."):
                adventure = create_adventure(
                    time_available,
                    environment,
                    difficulty,
                    interest,
                )

            st.session_state.adventure = adventure
            st.session_state.completed = []
            st.session_state.outdoor_mode = False
            st.success("Adventure created!")
        except Exception as error:
            st.error(
                "I couldn't generate an adventure. Check that Ollama "
                "is running and the model is installed."
            )
            st.caption(f"Technical details: {error}")

adventure = st.session_state.adventure

if adventure:
    st.divider()
    st.header(f"🌿 {adventure['title']}")
    st.write(adventure["intro"])

    if not st.session_state.outdoor_mode:
        st.subheader("Your missions")

        for index, mission in enumerate(adventure["missions"]):
            key = f"mission_{index}"
            checked = st.checkbox(
                mission,
                value=index in st.session_state.completed,
                key=key,
            )

            if checked and index not in st.session_state.completed:
                st.session_state.completed.append(index)
            elif not checked and index in st.session_state.completed:
                st.session_state.completed.remove(index)

        final_checked = st.checkbox(
            f"🏁 Final challenge: {adventure['final_challenge']}",
            value=4 in st.session_state.completed,
            key="final_mission",
        )

        if final_checked and 4 not in st.session_state.completed:
            st.session_state.completed.append(4)
        elif not final_checked and 4 in st.session_state.completed:
            st.session_state.completed.remove(4)

        completed_count = len(st.session_state.completed)
        score = completed_count * 20

        st.divider()
        st.subheader("🌱 TOUCHGRASS SCORE")
        st.metric("Your score", f"{score} / 100")
        st.progress(score / 100)

        if score == 100:
            st.success("Amazing! You completed every mission. 🌳")
        elif score >= 60:
            st.info("Nice work! You spent time exploring outdoors.")
        elif score > 0:
            st.info("Good start! Every outdoor moment counts.")
        else:
            st.caption("Complete a mission to start earning points.")

        st.button(
            "🌳 Go Outside Mode",
            on_click=lambda: st.session_state.update(outdoor_mode=True),
            type="primary",
        )

        if st.button("🔄 Start a new adventure"):
            st.session_state.adventure = None
            st.session_state.completed = []
            st.session_state.outdoor_mode = False
            st.rerun()

    else:
        st.title("🌳 TIME TO GO OUTSIDE")
        st.subheader("Put your phone away and enjoy the real world.")
        st.write(f"**Your mission:** {adventure['missions'][0]}")
        st.write(f"**Final challenge:** {adventure['final_challenge']}")
        st.info(
            "Head to a safe outdoor place. You can return when you're "
            "ready to mark your missions complete."
        )

        if st.button("I'm back — track my missions"):
            st.session_state.outdoor_mode = False
            st.rerun()

st.divider()
st.caption(
    "Local AI powered by Ollama and Qwen2.5. "
    "Stay safe, respect nature, and follow local rules."
)
