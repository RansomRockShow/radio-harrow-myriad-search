"""Radio Harrow Myriad Music Search – Streamlit edition."""
from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import streamlit as st

HERE = Path(__file__).resolve().parent
COLUMNS = ["MediaId", "Title", "Artists", "SecondaryCategory", "Intro", "Extro", "FirstReleaseYear", "Ending"]
EXPORT_COLUMNS = ["Id", "ItemTitle", "ArtistName1", "Description1"] + [""] * 14

st.set_page_config(page_title="Radio Harrow Myriad Search", page_icon="📻", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1200px;}
h1 {color: #bf302d;}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Loading the Myriad catalogue…")
def load_catalogue():
    # Keep IDs and duration strings as supplied by Myriad.
    data = pd.read_csv(HERE / "Myriad Data.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    for name in COLUMNS:
        if name not in data.columns:
            data[name] = ""
    return data[COLUMNS].reset_index(drop=True)

def export_csv(pad):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\\r\\n")
    writer.writerow(EXPORT_COLUMNS)
    for item in pad:
        writer.writerow([item["MediaId"], item["Title"], item["Artists"], ""] + [""] * 14)
    return output.getvalue().encode("utf-8-sig")

if "pad" not in st.session_state:
    st.session_state.pad = []
if "artist" not in st.session_state:
    st.session_state.artist = ""
if "song" not in st.session_state:
    st.session_state.song = ""

top1, top2 = st.columns([1, 4], vertical_alignment="center")
with top1:
    st.image(str(HERE / "Radio Harrow Logo.png"), use_container_width=True)
with top2:
    st.title("Myriad Music Search")
    date_file = HERE / "Myriad Extract Date.txt"
    date_text = date_file.read_text(encoding="utf-8-sig").strip() if date_file.exists() else "Not recorded"
    st.caption(f"Radio Harrow • Catalogue extract: {date_text}")

try:
    catalogue = load_catalogue()
except Exception as exc:
    st.error(f"Cannot load the Myriad catalogue: {exc}")
    st.stop()

st.subheader("Search the music library")
artist_col, song_col = st.columns(2)
with artist_col:
    artist = st.text_input("Artist contains", key="artist", placeholder="e.g. Beatles")
with song_col:
    song = st.text_input("Song title contains", key="song", placeholder="e.g. Yesterday")

results = catalogue
if artist.strip():
    results = results[results["Artists"].str.contains(artist.strip(), case=False, regex=False, na=False)]
if song.strip():
    results = results[results["Title"].str.contains(song.strip(), case=False, regex=False, na=False)]
results = results.reset_index(drop=True)
st.caption(f"{len(results):,} matching tracks • {len(catalogue):,} records in the catalogue")

if len(results) > 0:
    # Native Streamlit row selection. Selections do not change the Pad List until Add is pressed.
    display = results.rename(columns={
        "Artists": "Artist", "Title": "Song", "Extro": "Duration",
        "FirstReleaseYear": "Year", "MediaId": "Media ID",
        "SecondaryCategory": "Category"
    })
    event = st.dataframe(
        display[["Artist", "Song", "Duration", "Year", "Media ID", "Category", "Intro", "Ending"]],
        hide_index=True, use_container_width=True, height=310,
        selection_mode="single-row", on_select="rerun", key="search_grid",
    )
    selected_indices = event.selection.rows
    selected = results.iloc[selected_indices[0]].to_dict() if selected_indices else None
    left, right = st.columns([1, 1])
    with left:
        if st.button("➕ Add selected track to Pad List", type="primary", disabled=selected is None):
            if any(str(x["MediaId"]) == str(selected["MediaId"]) for x in st.session_state.pad):
                st.warning("This track is already in the Pad List.")
            else:
                st.session_state.pad.append({k: str(selected[k]) for k in COLUMNS})
                st.rerun()
    with right:
        st.write("**Copy selected track:**")
        if selected is not None:
            # st.code includes a native browser Copy-to-clipboard control.
            st.code(f'{selected["Artists"]} – {selected["Title"]} – {selected["Extro"]}', language=None)
        else:
            st.caption("Select a row to reveal its copyable details.")
else:
    st.info("No matching tracks. Try a different search.")

st.divider()
st.subheader(f"Pad List ({len(st.session_state.pad)} tracks)")
if st.session_state.pad:
    pad_df = pd.DataFrame(st.session_state.pad)
    pad_df.insert(0, "No.", range(1, len(pad_df) + 1))
    st.dataframe(
        pad_df.rename(columns={"MediaId":"Media ID","Title":"Song","Artists":"Artist","Extro":"Duration"})[
            ["No.", "Media ID", "Artist", "Song", "Duration"]
        ], hide_index=True, use_container_width=True, height=min(320, 75 + 35 * len(pad_df))
    )
    options = list(range(len(st.session_state.pad)))
    def label(i):
        item = st.session_state.pad[i]
        return f'{i+1}. {item["Artists"]} – {item["Title"]}'
    choice = st.selectbox("Track to remove or move", options, format_func=label)
    b1,b2,b3,b4 = st.columns(4)
    with b1:
        if st.button("Remove track"):
            st.session_state.pad.pop(choice)
            st.rerun()
    with b2:
        if st.button("Move up", disabled=choice == 0):
            p=st.session_state.pad
            p[choice-1],p[choice]=p[choice],p[choice-1]
            st.rerun()
    with b3:
        if st.button("Move down", disabled=choice == len(options)-1):
            p=st.session_state.pad
            p[choice+1],p[choice]=p[choice],p[choice+1]
            st.rerun()
    with b4:
        if st.button("Clear Pad List"):
            st.session_state.pad=[]
            st.rerun()
    st.download_button(
        "⬇️ Download Myriad Pad List CSV",
        data=export_csv(st.session_state.pad),
        file_name="Myriad Pad List.csv",
        mime="text/csv",
        type="primary",
    )
else:
    st.info("Your Pad List is empty. Select a search result and add it above.")

st.caption("Each presenter has a separate Pad List for their browser session. No changes are made to the shared catalogue.")
