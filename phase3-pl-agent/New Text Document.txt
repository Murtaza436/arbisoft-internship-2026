import streamlit as st
import pandas as pd

from src.agent import run_agent
from src.memory import SessionMemory
from src.tools.rag_tool import search_historical_stats_df


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Premier League Research Assistant",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #777;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .comparison-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
    }

    .stButton > button {
        width: 100%;
        border-radius: 8px;
        min-height: 45px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION MEMORY
# ============================================================

if "memory" not in st.session_state:
    st.session_state.memory = SessionMemory()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ⚽ PL Research Assistant")

    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "Dashboard",
            "Head-to-Head",
            "Player Comparison",
            "Historical Comparison",
            "Interactive Chat",
        ],
        index=[
            "Dashboard",
            "Head-to-Head",
            "Player Comparison",
            "Historical Comparison",
            "Interactive Chat",
        ].index(st.session_state.page),
    )

    st.session_state.page = page

    st.markdown("---")

    st.markdown(
        """
        ### Available Analysis

        🔴 Current Premier League data

        📚 Historical statistics

        ⚔️ Team comparisons

        👤 Player comparisons

        🏆 Historical seasons

        💬 Interactive research chat
        """
    )


# ============================================================
# HELPER: RUN AGENT
# ============================================================

def ask_agent(question):
    """
    Send a question through the existing Week 8 agent.
    """

    with st.spinner("Researching..."):

        try:
            answer = run_agent(
                question,
                st.session_state.memory,
            )

            return answer

        except Exception as e:
            return f"Error while running the agent: {e}"


# ============================================================
# HELPER: DISPLAY DATA
# ============================================================

def display_result(result):

    if isinstance(result, pd.DataFrame):

        if result.empty:
            st.warning("No data found.")
        else:
            st.dataframe(
                result,
                use_container_width=True,
                hide_index=True,
            )

    elif isinstance(result, dict):

        if "career" in result:

            st.markdown("### Career Summary")

            st.dataframe(
                result["career"],
                use_container_width=True,
                hide_index=True,
            )

        if "season" in result:

            st.markdown("### Season Breakdown")

            st.dataframe(
                result["season"],
                use_container_width=True,
                hide_index=True,
            )

    else:

        st.markdown(result)


# ============================================================
# DASHBOARD
# ============================================================

if st.session_state.page == "Dashboard":

    st.markdown(
        '<div class="main-title">⚽ Premier League Research Assistant</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        "Explore current Premier League data, historical statistics, "
        "team comparisons, player comparisons and football history."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Quick Comparisons</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### ⚔️ Team Head-to-Head")

        if st.button("Liverpool vs Manchester City"):
            st.session_state.page = "Head-to-Head"
            st.session_state.h2h_question = (
                "Compare Liverpool and Manchester City historically."
            )
            st.rerun()

        if st.button("Arsenal vs Chelsea"):
            st.session_state.page = "Head-to-Head"
            st.session_state.h2h_question = (
                "Compare Arsenal and Chelsea historically."
            )
            st.rerun()

    with col2:

        st.markdown("### 👤 Player Comparison")

        if st.button("Mohamed Salah vs Erling Haaland"):
            st.session_state.page = "Player Comparison"
            st.session_state.player_question = (
                "Compare Mohamed Salah and Erling Haaland "
                "using their historical Premier League statistics."
            )
            st.rerun()

        st.markdown("### 🏆 Historical Comparison")

        if st.button("Leicester 2015/16 vs Liverpool 2019/20"):
            st.session_state.page = "Historical Comparison"
            st.session_state.history_question = (
                "Compare Leicester City's 2015/16 Premier League "
                "season with Liverpool's 2019/20 Premier League season."
            )
            st.rerun()

    st.markdown("---")

    st.markdown("### 💬 Ask the Research Assistant")

    question = st.text_input(
        "Enter a Premier League question",
        placeholder=(
            "e.g. Who had more Premier League goals, "
            "Salah or Haaland?"
        ),
    )

    if st.button("Research Question") and question:

        answer = ask_agent(question)

        st.markdown("### Answer")

        st.markdown(answer)


# ============================================================
# HEAD-TO-HEAD
# ============================================================

elif st.session_state.page == "Head-to-Head":

    st.markdown(
        '<div class="main-title">⚔️ Head-to-Head Comparison</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "Compare two Premier League clubs using your historical match database."
    )

    teams = [
        "Arsenal",
        "Chelsea",
        "Liverpool",
        "Manchester City",
        "Manchester United",
        "Tottenham",
        "Everton",
        "Aston Villa",
        "Newcastle United",
        "Leicester City",
        "West Ham United",
        "Brighton Hove Albion",
        "Crystal Palace",
        "Wolverhampton",
        "Nottingham Forest",
        "Fulham",
        "AFC Bournemouth",
        "Burnley",
    ]

    col1, col2 = st.columns(2)

    with col1:
        team1 = st.selectbox(
            "Team 1",
            teams,
            index=teams.index("Liverpool"),
        )

    with col2:
        team2 = st.selectbox(
            "Team 2",
            teams,
            index=teams.index("Manchester City"),
        )

    if st.button("Compare Teams"):

        question = (
            f"Compare the historical Premier League record "
            f"of {team1} and {team2}. "
            f"Show their meetings, scores, seasons and winners "
            f"in a table."
        )

        result = search_historical_stats_df(
            f"{team1} {team2}",
            n_results=100,
        )

        st.markdown(
            f"### {team1} vs {team2}"
        )

        display_result(result)


# ============================================================
# PLAYER COMPARISON
# ============================================================

elif st.session_state.page == "Player Comparison":

    st.markdown(
        '<div class="main-title">👤 Player Comparison</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "Compare Premier League players using your historical statistics database."
    )

    col1, col2 = st.columns(2)

    with col1:

        player1 = st.text_input(
            "Player 1",
            value="Mohamed Salah",
        )

    with col2:

        player2 = st.text_input(
            "Player 2",
            value="Erling Haaland",
        )

    if st.button("Compare Players"):

        q1 = search_historical_stats_df(
            player1,
            n_results=500,
        )

        q2 = search_historical_stats_df(
            player2,
            n_results=500,
        )

        st.markdown(
            f"### {player1} vs {player2}"
        )

        if isinstance(q1, dict) and isinstance(q2, dict):

            career1 = q1["career"].iloc[0]
            career2 = q2["career"].iloc[0]

            comparison = pd.DataFrame(
                {
                    "Statistic": [
                        "Games",
                        "Minutes",
                        "Goals",
                        "Assists",
                        "Yellow Cards",
                        "Red Cards",
                    ],
                    player1: [
                        career1["Games"],
                        career1["Minutes"],
                        career1["Goals"],
                        career1["Assists"],
                        career1["Yellow Cards"],
                        career1["Red Cards"],
                    ],
                    player2: [
                        career2["Games"],
                        career2["Minutes"],
                        career2["Goals"],
                        career2["Assists"],
                        career2["Yellow Cards"],
                        career2["Red Cards"],
                    ],
                }
            )

            st.dataframe(
                comparison,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.error(
                "One or both players could not be found."
            )


# ============================================================
# HISTORICAL COMPARISON
# ============================================================

elif st.session_state.page == "Historical Comparison":

    st.markdown(
        '<div class="main-title">🏆 Historical Season Comparison</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "Compare important Premier League seasons and historical achievements."
    )

    comparison = st.selectbox(
        "Choose comparison",
        [
            "Leicester City 2015/16 vs Liverpool 2019/20",
            "Custom historical comparison",
        ],
    )

    if comparison == "Leicester City 2015/16 vs Liverpool 2019/20":

        if st.button("Compare Seasons"):

            leicester = ask_agent(
                "Give me the Premier League statistics "
                "for Leicester City during the 2015/16 season."
            )

            liverpool = ask_agent(
                "Give me the Premier League statistics "
                "for Liverpool during the 2019/20 season."
            )

            st.markdown(
                "### Leicester City 2015/16 vs Liverpool 2019/20"
            )

            st.markdown("#### Leicester City 2015/16")

            st.markdown(leicester)

            st.markdown("#### Liverpool 2019/20")

            st.markdown(liverpool)

    else:

        st.info(
            "Use the Interactive Chat for custom historical comparisons."
        )


# ============================================================
# INTERACTIVE CHAT
# ============================================================

elif st.session_state.page == "Interactive Chat":

    st.markdown(
        '<div class="main-title">💬 Interactive Premier League Chat</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "Ask questions about Premier League history, players, teams, "
        "results, standings and comparisons."
    )

    # Display previous messages

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    question = st.chat_input(
        "Ask a Premier League question..."
    )

    if question:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            answer = ask_agent(question)

            st.markdown(answer)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )