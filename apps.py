import pickle
import streamlit as st
import requests
import time

# Load data outside the function (assuming they're small)
with open('movie_list.pkl', 'rb') as f:
    movies = pickle.load(f)

with open('similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)

# Fetch the poster for the movie using the movie ID
def fetch_poster(movie_id):
    api_key = "8265bd1679663a7ea12ac168da84d2e8"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    for attempt in range(5):  # Retry mechanism to handle intermittent issues
        try:
            response = requests.get(url, verify=False, timeout=10)
            response.raise_for_status()  # Check if the response is successful
            poster_path = response.json().get('poster_path')

            if poster_path:
                return f"https://image.tmdb.org/t/p/w500/{poster_path}"
            else:
                return None  # No poster found, return None
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)  # Wait before retrying in case of failure

    return None  # Return None if all attempts fail


# Recommendation logic
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:  # Get the top 5 recommendations (excluding the first, which is the movie itself)
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)
        # Add a placeholder image if no poster is found
        recommended_movie_posters.append(poster_url if poster_url else 'https://via.placeholder.com/500')
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters


# Streamlit App UI
st.header('Movie Recommender System')
movie_name = st.selectbox('Enter the name of the movie you liked:', movies['title'].values)

if st.button('Recommend'):
    recommended_movies, recommended_posters = recommend(movie_name)
    st.subheader('Recommended Movies:')
    col1, col2, col3 = st.columns(3)
    for i in range(len(recommended_movies)):
        with col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3:
            st.image(recommended_posters[i])
            st.write(recommended_movies[i])