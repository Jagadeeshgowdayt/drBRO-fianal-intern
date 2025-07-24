import requests
from bs4 import BeautifulSoup
from telegraph import Telegraph

# Set up Telegraph account
telegraph = Telegraph()
telegraph.create_account(short_name="MovieBot")

def search(query):
    """
    Search for movies on IMDb and return results posted to Telegraph.
    """
    url = f"https://www.imdb.com/find?q={query}&s=tt&ttype=ft&ref_=fn_ft"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all search result sections
        result_sections = soup.find_all("div", class_="find-result-item")
        if not result_sections:
            return None

        content = ""
        for section in result_sections[:10]: # Limit to top 10 results
            link_tag = section.find("a")
            if not link_tag:
                continue
                
            title = link_tag.text.strip()
            year_tag = section.find("ul", class_="ipc-metadata-list-summary-item__details")
            year = year_tag.text.strip() if year_tag else "N/A"
            
            poster_tag = section.find("img", class_="ipc-image")
            poster_url = poster_tag['src'] if poster_tag else ""

            content += f"<img src='{poster_url}'><br><b><a href='https://www.imdb.com{link_tag['href']}'>{title}</a> - {year}</b><br>"

        if not content:
            return None

        # Create a Telegraph page
        page = telegraph.create_page(
            title=f"IMDb Search Results for '{query}'",
            html_content=content
        )
        return f"https://telegra.ph/{page['path']}"

    except requests.RequestException as e:
        print(f"Error during IMDb search request: {e}")
        return None
    except Exception as e:
        print(f"An error occurred in search: {e}")
        return None


def top():
    """
    Scrape the top-rated 250 movies from IMDb.
    Returns a list of movie dictionaries.
    """
    try:
        headers = {'Accept-Language': 'en-US,en;q=0.5'}
        response = requests.get("https://www.imdb.com/chart/top/", headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        movies_list = []
        movie_items = soup.select("li.ipc-metadata-list-summary-item")

        for item in movie_items:
            title_tag = item.select_one("h3.ipc-title__text")
            # Example: "1. The Shawshank Redemption" -> "The Shawshank Redemption"
            title = ". ".join(title_tag.text.split(". ")[1:]) if title_tag else "N/A"

            poster_tag = item.select_one("img.ipc-image")
            poster = poster_tag['src'] if poster_tag else ""

            rating_tag = item.select_one("span.ipc-rating-star")
            rating = rating_tag.text.split()[0] if rating_tag else "N/A"
            
            metadata_div = item.select_one("div.ipc-title-metadata-item")
            year = metadata_div.text.split()[0] if metadata_div else "N/A"

            movies_list.append({
                'title': title,
                'year': year,
                'rating': rating,
                'image': poster,
            })
        
        return movies_list

    except requests.RequestException as e:
        print(f"Error fetching top movies page: {e}")
        return []
    except Exception as e:
        print(f"An error occurred in top(): {e}")
        return []

