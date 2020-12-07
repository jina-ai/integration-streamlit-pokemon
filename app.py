__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import streamlit as st
from PIL import Image
from util import Getter, Defaults, Renderer, Encoder
from streamlit_drawable_canvas import st_canvas

# App state setup
# app_state = st.experimental_get_query_params()
# app_state = {k: v[0] if isinstance(v, list) else v for k, v in app_state.items()} # fetch the first item in each query string as we don't have multiple values for each query string key in this example

logo_html = """
<center>
<strong>Search Pokemon with</strong><br>
<img src='https://raw.githubusercontent.com/jina-ai/jina/master/.github/logo-only.gif' width=300 style='margin-bottom: 2em'>
<p>
Upload an image or draw a Pokemon, and Jina's neural search framework will use AI to find the closest match!
<p>
    </center>
"""

media_option = ["image", "draw"]
st.markdown(logo_html, unsafe_allow_html=True)
st.sidebar.title("Options")

# media_default = media_option.index(app_state["media"]) if "media" in app_state else 1
media = st.sidebar.selectbox(label="Search by", options=[i.capitalize() for i in media_option])

# app_state["media"] = media.lower()
# st.experimental_set_query_params(**app_state)

# endpoint_default = app_state["endpoint"] if "endpoint" in app_state else Defaults.endpoint
# endpoint = Defaults.endpoint
# app_state["endpoint"] = endpoint
# st.experimental_set_query_params(**app_state)

# top_k_default = int(app_state["top_k"]) if "top_k" in app_state else 10
top_k = st.sidebar.slider("Show me this many results", min_value=1, max_value=20, value=10)
# app_state["top_k"] = top_k
# st.experimental_set_query_params(**app_state)

if media == "Text":
    query_default = app_state["q"] if "q" in app_state else Defaults.text_query
    query = st.text_input("What do you wish to search?", value=Defaults.text_query)
    app_state["q"] = query
    st.experimental_set_query_params(**app_state)
elif media == "Image":
    query = st.file_uploader("File")
elif media == "Draw":
    st.sidebar.header("Drawing Options")
    stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
    stroke_color = st.sidebar.color_picker("Stroke color hex: ")
    bg_color = st.sidebar.color_picker("Background color hex: ", "#ffffff")
    bg_image = st.sidebar.file_uploader("Background image:", type=["png", "jpg"])
    drawing_mode = st.sidebar.selectbox(
        "Drawing tool:", ("freedraw", "line", "rect", "circle", "transform")
    )

    data = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="" if bg_image else bg_color,
        background_image=Image.open(bg_image) if bg_image else None,
        update_streamlit=True,
        width=400,
        height=400,
        drawing_mode=drawing_mode,
        key="canvas",
    )

st.sidebar.markdown('#### Advanced options')
endpoint = st.sidebar.text_input("Endpoint", value=Defaults.endpoint)

if st.button("Search"):
    if media == "Text":
        results = Getter.text(query=query, top_k=top_k, endpoint=endpoint)
        content = results
        st.markdown(Renderer.text(content))
    elif media == "Image" or media == "Draw":
        if media == "Image":
            encoded_query = Encoder.img_base64(query.read())
        elif media == "Draw":
            encoded_query = Encoder.canvas_to_base64(data)
        results = Getter.images(endpoint=endpoint, query=encoded_query, top_k=top_k)
        html = Renderer.images(results)
        st.write(html, unsafe_allow_html=True)
    st.balloons()

st.markdown(Defaults.jina_text, unsafe_allow_html=True)
