from htbuilder.units import rem # type: ignore
from htbuilder import div, styles # type: ignore
from elasticsearch import Elasticsearch # type: ignore
from dotenv import load_dotenv # type: ignore
import base64, os, re
import streamlit as st # type: ignore


st.set_page_config(page_title="Homework 2", layout="wide")

DEBUG_MODE = st.query_params.get("debug", "false").lower() == "true"

SUGGESTIONS = {
    "📜 Arthur’s 1882 veto": (
        "Why did President Chester A. Arthur veto the Chinese Exclusion Act of 1882?"
    ),
    "🕊️ LBJ–North Vietnam talks": (
        "What announcement did President Lyndon B. Johnson make regarding communication with North Vietnam"
    ),
    "⚖️ \"The world must be made safe for democracy\"": (
        "\"The world must be made safe for democracy\""
    ),
        "🦠 Donald Trump Coronavirus": (
        "Donald Trump coronavirus speech"
    )
}

INDEX_NAME = "main_index"
load_dotenv(dotenv_path="elastic-start-local/.env")
ES_URL = os.getenv("ES_LOCAL_URL")
PASSWD = os.getenv("ES_LOCAL_PASSWORD")
USR = "elastic"

es = Elasticsearch(ES_URL, basic_auth=(USR,PASSWD), request_timeout=30)

try:
    with open("img/es_logo.png", "rb") as f:
        data = base64.b64encode(f.read()).decode()
    html_logo = f"""
    <div style="font-size:5rem; line-height:1;">
        <img src="data:image/png;base64,{data}" width="80">
    </div>
    """
    if hasattr(st, "html"):
        st.html(html_logo)
    else:
        st.markdown(html_logo, unsafe_allow_html=True)
except Exception:
    pass

title_row = st.container()
with title_row:
    st.title("Search with ElasticSearch", anchor=False)

with st.sidebar:
    st.header("Search Settings")

    selected_field = st.segmented_control(
        "Search Fields",
        options=["all", "title", "content"],
        default="all",
    )

    st.divider()

    selected_size = st.slider(
        "Risultati per pagina",
        min_value=5,
        max_value=50,
        value=10,
        step=5,
    )

    DEBUG_MODE = st.toggle(
        "Debug",
        value=DEBUG_MODE,
        help="Mostra la query e dettagli tecnici",
    )
    
if "query_text" not in st.session_state:
    st.session_state["query_text"] = ""

def _apply_suggestion():
    sel = st.session_state.get("examples_sel")
    if sel:
        st.session_state["query_text"] = SUGGESTIONS[sel]
        st.session_state["examples_sel"] = None

with st.container():
    user_msg = st.chat_input("Search for something...", key="initial_question")

    st.pills(
        label="Examples",
        label_visibility="collapsed",
        options=list(SUGGESTIONS.keys()),
        key="examples_sel",        
        on_change=_apply_suggestion
    )

q = user_msg or st.session_state.get("query_text", "")

if q:
    q = q.strip()
    if not q:
        st.info("Scrivi qualcosa nella query…")
    else:
        st.write(f"Ricerca per: `{q}`")

        m = re.fullmatch(r'"(.+?)"', q)
        is_phrase = m is not None
        phrase = m.group(1) if is_phrase else None

        if selected_field == "all":
            mm = {
                "query": phrase if is_phrase else q,
                "fields": ["title", "content"],
            }
            if is_phrase:
                mm["type"] = "phrase"
            body = {
                "query": {"multi_match": mm},
                "highlight": {
                    "pre_tags": ["<mark>"], "post_tags": ["</mark>"],
                    "fields": {
                        "title": {},
                        "content": {"fragment_size": 160, "number_of_fragments": 2},
                    },
                },
            }
        else:
            field = selected_field
            match_clause = {"match_phrase" if is_phrase else "match": {field: phrase if is_phrase else q}}
            body = {
                "query": match_clause,
                "highlight": {
                    "pre_tags": ["<mark>"], "post_tags": ["</mark>"],
                    "fields": {field: {"fragment_size": 160, "number_of_fragments": 3}},
                },
            }

        if DEBUG_MODE:
            with st.expander("Query (debug)"):
                import json
                st.code(json.dumps(body, indent=2, ensure_ascii=False), language="json")

        try:
            res = es.search(index=INDEX_NAME, body=body, size=selected_size)
        except Exception as e:
            st.error(f"Errore in ricerca: {e}")
            st.stop()

        hits = res.get("hits", {}).get("hits", [])
        total = res.get("hits", {}).get("total", {}).get("value", 0)
        st.subheader(f"Results: {total}")

        if not hits:
            st.write("Nessun risultato.")
        else:
            for h in hits[:selected_size]:
                source = h.get("_source", {}) or {}
                title = source.get("title") or "(senza titolo)"
                score = h.get("_score", 0.0)
                hl = h.get("highlight", {}) or {}

                with st.container(border=True):
                    st.markdown(f"### {title}")
                    st.caption(f"• score: {score:.3f}")

                    content_frags = hl.get("content", [])

                    if content_frags:
                        sn = '<br>'.join(content_frags[:1]) 
                        st.markdown(sn[:200], unsafe_allow_html=True)
                    else:
                        txt = (source.get("content") or "")[:200]
                        if txt:
                            st.write(txt + ("…" if len(txt) == 200 else ""))
                        else:
                            st.write("_Nessun estratto disponibile_")