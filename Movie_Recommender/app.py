import pickle
import streamlit as st
import requests
from streamlit_lottie import st_lottie
import json

def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    overview = data.get('overview', 'No overview available')
    rating = data.get('vote_average', 'N/A')
    genre = ", ".join([g['name'] for g in data.get('genres', [])])
    
    full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750.png?text=No+Image"
    return full_path, overview, rating, genre

def recommend(movie):
    if movie not in movies['title'].values:
        return [], [], [], [], []
    
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movie_names, posters, overviews, ratings, genres = [], [], [], [], []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        poster, overview, rating, genre = fetch_movie_details(movie_id)
        posters.append(poster)
        recommended_movie_names.append(movies.iloc[i[0]].title)
        overviews.append(overview)
        ratings.append(rating)
        genres.append(genre)
    
    return recommended_movie_names, posters, overviews, ratings, genres

# Streamlit UI
st.set_page_config(page_title='Movie Recommender', layout='wide', initial_sidebar_state='expanded')

# Load Lottie Animations
welcome_animation = load_lottie_url("https://assets3.lottiefiles.com/packages/lf20_welcome_dog.json")
finding_animation = load_lottie_url("https://assets4.lottiefiles.com/packages/lf20_searching_dog.json")
success_animation = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_happy_dog.json")

# Add Dark Gradient Video Background
st.markdown(
    """
    <style>
        @keyframes gradientBG {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        .stApp {
            background: linear-gradient(270deg, #000000, #1B1B1B, #2C2C2C, #000000);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('🎬 Movie Recommender System')

if welcome_animation:
    st_lottie(welcome_animation, height=200)

movies = pickle.load(open('Pickle/movie_list.pkl', 'rb'))
similarity = pickle.load(open('Pickle/similarity.pkl', 'rb'))

# Sidebar
st.sidebar.header('🔍 Search for a Movie')
movie_list = movies['title'].values
selected_movie = st.sidebar.selectbox("Type or select a movie", movie_list)

if st.sidebar.button('🎥 Get Recommendations'):
    if finding_animation:
        st_lottie(finding_animation, height=200)
    
    names, posters, overviews, ratings, genres = recommend(selected_movie)
    if names:
        if success_animation:
            st_lottie(success_animation, height=200)
        
        st.subheader(f"📌 Movies similar to **{selected_movie}**")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        for i, col in enumerate([col1, col2, col3, col4, col5]):
            with col:
                st.image(posters[i], use_container_width=True)
                st.markdown(f"### 🎞 {names[i]}")
                st.markdown(f"⭐ **{ratings[i]}** | 🎭 *{genres[i]}*")
                st.caption(overviews[i][:100] + '...')
                
                # Add a small hover effect using markdown
                st.markdown("<style>img:hover {transform: scale(1.05); transition: 0.3s ease-in-out;}</style>", unsafe_allow_html=True)
    else:
        st.error("⚠️ No recommendations found. Try another movie.")
