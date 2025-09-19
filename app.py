from __future__ import annotations
import pickle
import re
from dataclasses import dataclass, field
import os

import streamlit as st


st.markdown('<meta name="robots" content="noindex, nofollow">',unsafe_allow_html=True)


hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


@dataclass
class SchoolClass:
    name: str
    block: str
    course_id: tuple[int, int] | None
    location: str
    event: dict = field(compare=False, repr=False) # for future proofing

    @classmethod
    def parse_event(cls, event: dict) -> SchoolClass | None:
        if event_summary := event.get('summary', None):
            event_summary = event_summary.strip()
        else:
            return None # not a class if no summary, probably hidden event("busy")
        if "Advisor check in" in event_summary or event_summary in blacklist:
            return None
    
        block_match = re.search(r"\(([^)]+)\)\s*$", event_summary)
        if not block_match:
            return None # not a class
        block = block_match.group(1)
        name = event_summary[:block_match.start()].strip()

        course_id = re.search(r"\b(\d{1,3})-([1-9])\b", name) # might only be 3 digits for first number
        if course_id:
            name = name[:course_id.start()-2].strip() # -2 to remove dash
            course_id = (int(course_id.group(1)), int(course_id.group(2)))

        location = event.get('location', None)
        if location:
            location = location.split(',')[0] # get just the classroom number
        else:
            return None # Not a class ?
        return cls(name, block, course_id, location, event)
    
    def __repr__(self):
        return f"name={self.name}, block={self.block}, course_id={self.course_id}, location={self.location}"

    def __hash__(self):
        return hash((self.name, self.block, self.course_id, self.location))


with open('classes.pkl', 'rb') as f:
    classes = pickle.load(f)

# blocks = ("A", "B", "C", "D", "E", "F", "G", "H", "ADV")

st.set_page_config(
    page_title="FS Class Rosters",
    page_icon="favicon.ico",
)

st.title("Friends Seminary Class Roster Viewer")

selected_block = None

selected_class = st.selectbox(
    "Choose a class:",
    {c.name for c in classes.keys()},   # list of strings
    index=None,      # start empty
    placeholder="Type to search…"
)


if selected_class:
    selected_block = st.segmented_control(
        "Select a block:",
        sorted({c.block for c in classes if c.name == selected_class})
    )

if selected_block and selected_class:
    for sc, students in classes.items():
        if sc.name == selected_class and sc.block == selected_block:
            course_str = f"{sc.course_id[0]}-{sc.course_id[1]}" if type(sc.course_id) is tuple else "N/A"
            st.subheader(f"{sc.name} — Block {sc.block}")
            st.caption(f"Course ID: {course_str}, Location: {sc.location}")

            for first, last, email in sorted(students, key=lambda x: (x[1], x[0])):
                st.write(f"**{first} {last}** — {email}")




# if selected_class:
#     st.session_state.blocks = {c.block for c in classes if c.name == selected_class}


# if selected_block:
#     st.session_state.classes = {c for c in classes if c.block == selected_block}
