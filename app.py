import random
from datetime import date, timedelta
import streamlit as st

st.set_page_config(page_title="TouchGrass AI", page_icon="🌿", layout="wide")

# ---------- Visual design ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
.stApp {background:#f4faf5;color:#183d2b;font-family:'DM Sans',sans-serif}
.block-container {max-width:1160px;padding-top:1.4rem;padding-bottom:3rem}
h1,h2,h3 {font-family:'Manrope',sans-serif;color:#183d2b}
div[data-testid="stMetric"] {background:#fff;border:1px solid #dfece1;border-radius:16px;padding:13px}
div.stButton>button {border-radius:12px;min-height:40px;font-weight:700;border:1px solid #cde2d1}
div.stButton>button[kind="primary"] {background:#17764b;color:#fff;border-color:#17764b}
.hero {background:linear-gradient(120deg,#dff4e5,#f8f3dc);border:1px solid #d9ebdc;border-radius:24px;padding:26px;margin:12px 0 18px}
.eyebrow {font-size:12px;letter-spacing:1.5px;font-weight:800;color:#238152}
.hero h1 {font-size:42px;line-height:1.12;margin:8px 0}
.hero p,.muted {color:#526f5c}
.card {background:#fff;border:1px solid #dfebdf;border-radius:18px;padding:17px;margin-bottom:10px}
.small {color:#67806e;font-size:13px}
</style>
""", unsafe_allow_html=True)

# ---------- Session state ----------
initial_state = {
    "daily_goal": 30,
    "outdoor_minutes": 0,
    "points": 0,
    "daily_missions_done": set(),
    "journal_checks": set(),
    "game_missions_done": set(),
    "game_card_indices": {},
    "adventure_plan": None,
    "weekly_targets": {},
}
for state_key, default_value in initial_state.items():
    if state_key not in st.session_state:
        st.session_state[state_key] = default_value

today = date.today()
today_id = today.isoformat()

DAILY_MISSIONS = [
    ("☀️", "Step outside for 10 minutes", 10, "A short reset counts."),
    ("🌿", "Notice 5 things in nature", 10, "Observe; leave plants and wildlife undisturbed."),
    ("🚶", "Walk without scrolling", 15, "Keep your phone away except for safety."),
    ("🧘", "Take 10 slow breaths outdoors", 5, "Choose a safe, comfortable spot."),
    ("🫶", "Invite someone for a short walk", 15, "A tiny walk together is enough."),
    ("🌳", "Visit a nearby green space", 20, "Pick a safe, accessible place."),
]

GAMES = {
    "🌼 Nature Bingo": {
        "description": "A mini scavenger hunt. Observe, don’t pick or disturb anything.",
        "cards": [
            ("Find 3 shades of green", "Look for light, medium, and dark green."),
            ("Spot a leaf-shaped shadow", "Notice the shape without touching the plant."),
            ("Find something heart-shaped", "It could be a leaf, cloud, or pattern."),
            ("Hear 3 outdoor sounds", "Pause and listen for a full minute."),
            ("Find a repeating pattern", "Look at bark, petals, pavement, or clouds."),
        ],
    },
    "📸 Photo Quest": {
        "description": "Make a tiny visual story. You can sketch instead of taking photos.",
        "cards": [
            ("Capture a tiny detail", "Find something you might usually walk past."),
            ("Photograph a shadow", "Look for a surprising shape."),
            ("Create a nature colour palette", "Find three colours that work together."),
            ("Make a 3-photo story", "Beginning, middle, end—your mini adventure."),
            ("Find an interesting texture", "Photograph it without damaging anything."),
        ],
    },
    "🧑‍🤝‍🧑 Friend Group Quest": {
        "description": "Playful group challenges that are kind and low-pressure.",
        "cards": [
            ("Invent a ridiculous team name", "Everyone gets one vote."),
            ("Take turns leading for 2 minutes", "The leader chooses a safe direction."),
            ("Narrate nature like a documentary", "Give a 10-second dramatic commentary."),
            ("Spot five things others missed", "Share what you noticed."),
            ("Create a group memory", "Take a photo or describe the moment."),
        ],
    },
    "🔎 Nature Detective": {
        "description": "Use your senses to investigate your surroundings.",
        "cards": [
            ("Listen for three sounds", "Only pause somewhere safe, away from traffic."),
            ("Watch how wind moves things", "Notice leaves, grass, or clouds."),
            ("Find two repeating patterns", "Look for lines, spirals, or symmetry."),
            ("Observe one spot for a minute", "What changed? What stayed the same?"),
            ("Predict the weather from clues", "Compare your guess with the sky."),
        ],
    },
    "💬 Walk & Wonder": {
        "description": "Conversation starters for friends and family. Anyone can pass.",
        "cards": [
            ("What tiny thing made you happy lately?", "Take turns sharing; listening counts."),
            ("What would this place sound like as music?", "Invent a soundtrack together."),
            ("Share a favourite shared memory", "Keep it light and comfortable."),
            ("What would your ideal slow Sunday look like?", "Dream up a low-pressure plan."),
            ("What would you like to learn outdoors?", "Pick one thing to try together."),
        ],
    },
}

JOURNAL_ITEMS = [
    ("🌤️", "I went outside for at least 5 minutes"),
    ("🚶", "I moved or walked away from my desk/bed"),
    ("🌿", "I noticed something in nature"),
    ("📵", "I spent one outdoor moment without scrolling"),
    ("🫶", "I shared a real-world moment with someone (or myself)"),
]

def log_activity(minutes: int, points: int) -> None:
    st.session_state.outdoor_minutes += minutes
    st.session_state.points += points

def safe_progress(value: int, target: int) -> float:
    return min(max(value / max(target, 1), 0.0), 1.0)

# ---------- Navigation ----------
st.markdown('<div class="eyebrow">TOUCHGRASS AI · REAL PLACES, REAL PEOPLE</div>', unsafe_allow_html=True)
home_tab, play_tab, journey_tab, planner_tab = st.tabs(
    ["🏡 Home", "🎉 Play Together", "📈 My Journey", "🗺️ Adventure Planner"]
)

# ---------- Home ----------
with home_tab:
    st.markdown(
        '<div class="hero"><div class="eyebrow">A LITTLE LESS SCREEN TIME</div>'
        '<h1>Go outside.<br>Come back happier. 🌿</h1>'
        '<p>Your daily outdoor missions, fun group games, and a simple way to track your progress. '
        'Start with just five minutes.</p></div>',
        unsafe_allow_html=True,
    )
    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric("🎯 Daily target", f"{st.session_state.daily_goal} min")
    metric_b.metric("🌳 Outside today", f"{st.session_state.outdoor_minutes} min")
    metric_c.metric("⭐ Total points", st.session_state.points)
    st.progress(
        safe_progress(st.session_state.outdoor_minutes, st.session_state.daily_goal),
        text=f"Daily goal: {min(st.session_state.outdoor_minutes, st.session_state.daily_goal)} / {st.session_state.daily_goal} minutes",
    )

    st.markdown("## 🌱 Today's missions")
    st.caption("Complete a mission in real life, then mark it done to earn points.")
    for index, (emoji, title, minutes, tip) in enumerate(DAILY_MISSIONS):
        mission_id = f"{today_id}:daily:{index}"
        col_icon, col_text, col_action = st.columns([0.6, 4.8, 1.4])
        col_icon.markdown(f"## {emoji}")
        col_text.markdown(f"**{title}**")
        col_text.caption(f"{minutes} min · {tip}")
        if mission_id in st.session_state.daily_missions_done:
            col_action.button("Completed ✓", key=f"daily_done_{index}", disabled=True, use_container_width=True)
        elif col_action.button("Mark done", key=f"daily_do_{index}", type="primary", use_container_width=True):
            st.session_state.daily_missions_done.add(mission_id)
            log_activity(minutes, 10)
            st.toast(f"+10 points · {minutes} outdoor minutes 🌱")
            st.rerun()
        st.divider()

    st.markdown("## ✨ Pick your next vibe")
    card_a, card_b, card_c = st.columns(3)
    with card_a:
        st.markdown('<div class="card"><h3>🎉 Play together</h3><p class="small">Bingo, photo quests, group missions, and conversation cards.</p></div>', unsafe_allow_html=True)
    with card_b:
        st.markdown('<div class="card"><h3>📈 Build your habit</h3><p class="small">A 100-point checklist, outdoor goals, and weekly targets.</p></div>', unsafe_allow_html=True)
    with card_c:
        st.markdown('<div class="card"><h3>🗺️ Plan an outing</h3><p class="small">A mini plan based on your time, budget, and mood.</p></div>', unsafe_allow_html=True)

# ---------- Play Together ----------
with play_tab:
    st.markdown("## 🎉 Play Together")
    st.write("Choose a deck, read a mission, then put the phone away and do it together.")
    selected_game = st.selectbox("Choose your game", list(GAMES.keys()))
    selected_data = GAMES[selected_game]
    st.markdown(
        f'<div class="card"><h3>{selected_game}</h3><p class="small">{selected_data["description"]}</p></div>',
        unsafe_allow_html=True,
    )

    if selected_game not in st.session_state.game_card_indices:
        st.session_state.game_card_indices[selected_game] = random.randrange(len(selected_data["cards"]))
    card_index = st.session_state.game_card_indices[selected_game]
    prompt_title, prompt_detail = selected_data["cards"][card_index]

    st.markdown(
        f'<div class="hero"><div class="eyebrow">MISSION CARD {card_index + 1} OF {len(selected_data["cards"])}</div>'
        f'<h2>{prompt_title}</h2><p>{prompt_detail}</p>'
        '<p>🌱 Complete it at your own pace. You can skip any prompt.</p></div>',
        unsafe_allow_html=True,
    )

    action_a, action_b = st.columns(2)
    with action_a:
        if st.button("🔀 Shuffle a new mission", type="primary", use_container_width=True):
            possible_indices = [i for i in range(len(selected_data["cards"])) if i != card_index]
            st.session_state.game_card_indices[selected_game] = random.choice(possible_indices)
            st.rerun()

    game_done_id = f"{today_id}:game:{selected_game}:{card_index}"
    with action_b:
        if game_done_id in st.session_state.game_missions_done:
            st.button("Mission completed ✓", disabled=True, use_container_width=True)
        elif st.button("✅ We did it! +20 points", use_container_width=True):
            st.session_state.game_missions_done.add(game_done_id)
            log_activity(10, 20)
            st.toast("Nice! +20 points and 10 outdoor minutes 🌱")
            st.rerun()

    st.markdown("### 🏅 Group scorecard")
    games_done_today = sum(1 for item in st.session_state.game_missions_done if item.startswith(f"{today_id}:"))
    st.metric("Game missions completed today", games_done_today)
    st.progress(safe_progress(games_done_today, 5), text=f"{min(games_done_today, 5)} / 5 missions toward today's mini milestone")
    st.info("Safety first: stay somewhere familiar and safe, respect nature and others, and keep a phone available for emergencies.")

# ---------- My Journey ----------
with journey_tab:
    st.markdown("## 📈 My Journey")
    st.write("Your daily wellbeing checklist is out of 100 points. Each checked box adds 20.")
    st.session_state.daily_goal = st.slider(
        "Daily outdoor minutes goal", min_value=10, max_value=120, step=5,
        value=int(st.session_state.daily_goal), key="daily_goal_slider",
    )

    st.markdown("### Today's 100-point checklist")
    for index, (emoji, label) in enumerate(JOURNAL_ITEMS):
        item_id = f"{today_id}:journal:{index}"
        widget_key = f"journal_checkbox_{today_id}_{index}"
        currently_checked = item_id in st.session_state.journal_checks
        new_checked = st.checkbox(
            f"{emoji} {label}  ·  +20 points",
            value=currently_checked,
            key=widget_key,
        )
        if new_checked and item_id not in st.session_state.journal_checks:
            st.session_state.journal_checks.add(item_id)
            st.session_state.points += 20
        elif not new_checked and item_id in st.session_state.journal_checks:
            st.session_state.journal_checks.remove(item_id)
            st.session_state.points = max(0, st.session_state.points - 20)

    score = sum(20 for index in range(len(JOURNAL_ITEMS)) if f"{today_id}:journal:{index}" in st.session_state.journal_checks)
    st.markdown("---")
    score_a, score_b, score_c = st.columns(3)
    score_a.metric("Today's score", f"{score}/100")
    score_b.metric("Outdoor time", f"{st.session_state.outdoor_minutes} min")
    score_c.metric("Total points", st.session_state.points)
    st.progress(score / 100, text=f"{score}% of today's checklist complete")
    if score == 100:
        st.success("🌟 100/100! You showed up for yourself today.")
        st.balloons()
    elif score >= 60:
        st.success("You're building momentum. One more small step if it feels good.")
    else:
        st.caption("Every checkbox is worth 20 points. Start with the easiest one.")

    st.markdown("### 🗓️ Your 7-day outdoor targets")
    st.caption("Set realistic minutes targets. These are flexible plans, not pressure.")
    for day_offset in range(7):
        target_date = today + timedelta(days=day_offset)
        target_id = target_date.isoformat()
        default_target = 30 if day_offset < 3 else 20
        saved_target = st.session_state.weekly_targets.get(target_id, default_target)
        day_col, target_col = st.columns([1.5, 3])
        day_col.markdown(f"**{target_date.strftime('%A')}**" + (" · Today" if day_offset == 0 else ""))
        chosen_target = target_col.select_slider(
            f"{target_date.strftime('%a %d')} target",
            options=[5, 10, 15, 20, 30, 45, 60, 90],
            value=saved_target,
            key=f"week_target_{target_id}",
            label_visibility="collapsed",
        )
        st.session_state.weekly_targets[target_id] = chosen_target

    st.markdown("### 💚 Recent wins")
    st.write(f"🌱 {len(st.session_state.daily_missions_done)} daily missions checked off this session.")
    st.write(f"🎉 {len(st.session_state.game_missions_done)} game cards completed this session.")
    st.caption("This prototype keeps progress for the current app session. Permanent saved history can be added later.")

# ---------- Adventure Planner ----------
with planner_tab:
    st.markdown("## 🗺️ Plan a mini-adventure")
    st.write("Build an easy outing around your time, budget, and mood.")
    with st.form("adventure_planner_form"):
        when = st.selectbox("When do you want to go?", ["Today", "This weekend", "Next week"])
        duration = st.selectbox("Time available", ["15 minutes", "30 minutes", "1 hour", "2+ hours"])
        budget = st.selectbox("Budget", ["Free", "Under ₹100", "Under ₹300"])
        company = st.selectbox("Who's coming?", ["Solo", "Friends", "Family", "Partner"])
        energy = st.select_slider("Energy level", options=["Low-key", "Medium", "High-energy"], value="Medium")
        vibes = st.multiselect("What sounds fun?", ["Nature", "Walking", "Photography", "Games", "Quiet time", "Picnic"], default=["Nature", "Walking"])
        area = st.text_input("Optional area or place", placeholder="Nearby park, lake, garden…")
        submitted = st.form_submit_button("Create my plan ✨", type="primary", use_container_width=True)

    if submitted:
        mapping = {
            "Nature": ("🔎", "Nature detective", "Notice patterns, clouds, and sounds without disturbing wildlife."),
            "Walking": ("🚶", "Curiosity walk", "Choose a safe route and notice one new thing every few minutes."),
            "Photography": ("📸", "Tiny photo story", "Capture a colour, a pattern, and a shadow."),
            "Games": ("🎯", "Nature bingo", "Find five natural details; observe, don't pick."),
            "Quiet time": ("🍃", "Five-minute reset", "Sit somewhere safe and notice breeze, light, and sounds."),
            "Picnic": ("🧺", "Simple snack break", "Bring water and take all rubbish home."),
        }
        missions = [mapping[vibe] for vibe in vibes if vibe in mapping]
        if not missions:
            missions = [("🌿", "Gentle outdoor break", "Walk or sit somewhere safe and public.")]
        st.session_state.adventure_plan = {
            "when": when, "duration": duration, "budget": budget, "company": company,
            "energy": energy, "area": area, "missions": missions,
        }

    if st.session_state.adventure_plan:
        plan_data = st.session_state.adventure_plan
        st.markdown("---")
        st.markdown(f"### 🌄 Your plan · {plan_data['duration']} · {plan_data['budget']}")
        details = f"{plan_data['when']} · {plan_data['company']} · {plan_data['energy']} energy"
        if plan_data["area"].strip():
            details += f" · {plan_data['area'].strip()}"
        st.caption(details)
        for index, (emoji, title, description) in enumerate(plan_data["missions"], start=1):
            st.markdown(
                f'<div class="card"><b>{emoji} Mission {index}: {title}</b>'
                f'<p class="small">{description}</p></div>',
                unsafe_allow_html=True,
            )
        st.markdown("**Before you leave**")
        pack_a, pack_b, pack_c = st.columns(3)
        pack_a.checkbox("Bring water", key="pack_water")
        pack_b.checkbox("Wear comfy shoes", key="pack_shoes")
        pack_c.checkbox("Leave no litter", key="pack_litter")
        plan_text = (
            f"TouchGrass Adventure\nWhen: {plan_data['when']}\nTime: {plan_data['duration']}\n"
            f"Budget: {plan_data['budget']}\nCompany: {plan_data['company']}\n\n"
        )
        plan_text += "\n".join(
            f"{index}. {title}: {description}"
            for index, (_, title, description) in enumerate(plan_data["missions"], start=1)
        )
        st.download_button(
            "⬇️ Download my adventure", data=plan_text,
            file_name="touchgrass-adventure.txt", mime="text/plain",
        )

st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#68816e;font-size:12px">'
    '🌿 TouchGrass AI · Small steps. Bigger days.</div>',
    unsafe_allow_html=True,
)
