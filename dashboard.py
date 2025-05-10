import streamlit as st
import requests

API_URL = "https://carsmoviesinventoryproject-production.up.railway.app/api/v1/carsmovies?page=0&size=5&sort=carMovieYear,desc"

def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        # Assuming the data is in a key like 'content' or directly a list
        # Adjust based on actual API response structure
        if isinstance(data, dict) and "content" in data:
            return data["content"]
        elif isinstance(data, list):
            return data
        else:
            return []
    except requests.RequestException as e:
        st.error(f"Error fetching data from API: {e}")
        return []

def main():
    st.title("Cars Movies Dashboard")
    st.write("Fetching data from API...")

    data = fetch_data()

    if data:
        # Display data in a table with selected columns
        filtered_data = [
            {
                "id": item.get("id", ""),
                "carMovieName": item.get("carMovieName", ""),
                "carMovieYear": item.get("carMovieYear", ""),
                "duration": item.get("duration", "")
            }
            for item in data
        ]
        st.table(filtered_data)
    else:
        st.write("No data available.")

if __name__ == "__main__":
    main()
