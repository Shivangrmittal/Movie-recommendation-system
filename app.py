import streamlit as st
import pickle
import pandas as pd
import requests

from PIL import Image, ImageDraw, ImageFont

def add_text_to_image(image_path, text):
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Fixed large bold font
    font_size = img.width // 10
    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # --- TEXT WRAPPING ---
    max_width = img.width * 0.8
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = bbox[2] - bbox[0]

        if test_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    # --- CALCULATE TOTAL HEIGHT ---
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])

    total_text_height = sum(line_heights) + (len(lines) - 1) * 10  # spacing

    # --- START POSITION (centered) ---
    y = (img.height - total_text_height) // 2

    # --- DRAW EACH LINE ---
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]

        x = (img.width - text_width) // 2

        draw.text((x, y), line, font=font, fill="black")

        y += line_heights[i] + 10  # line spacing

    return img

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movie = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie.append(movies.iloc[i[0]].title)
    return recommended_movie

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl','rb'))

st.title('Movie Recommendation System')

selected_movie_name = st.selectbox(
    'Your favourite movie?',
    movies['title'].values)

poster_path = "poster.png"  

if st.button('Recommend'):
    names = recommend(selected_movie_name)

    col1, col2, col3, col4, col5 = st.columns(5)

    cols = [col1, col2, col3, col4, col5]

    for i in range(5):
        with cols[i]:
            img = add_text_to_image(poster_path, names[i])
            st.image(img, use_container_width=True)
