print("Script entry point: glaDataCollection.py")

print("Importing time module...")
from time import time
print("Importing load_dotenv from dotenv...")
from dotenv import load_dotenv
print("Importing os and sys modules...")
import os, sys

# setting path in order to be able to import from parent directory
print("Setting up system path for parent directory imports...")
sys.path.append('/info/etu/m2/s2403274/MLOps_Bigdata_Projet/Github-Language-Analysis/')

print("Importing entities from mlProject...")
from src.mlProject.entity import RepositoriesAnalytics, GitHubClient
print("Importing logs from mlProject...")
from src.mlProject.utils.common import log


log("Loading .env file...")
load_dotenv()
log(".env file loaded.")
log("Initializing GitHub client...")
client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
log(f"GitHub client initialized with \n      base_url: {client.base_url}\n      token: {client.token[:4]}****")
log("Loading existing data or initializing new RepositoriesAnalytics...")
analytics = RepositoriesAnalytics.from_csv(folder_path="data", client=client)
log("RepositoriesAnalytics ready.")
queries = [
    "gaming", 
    "machine learning",
    "biology", 
    "cybersecurity", 
    "web development", 
    "data science", 
    "mobile development", 
    "devops", 
    "blockchain", 
    "internet of things",
    "artificial intelligence",
    "cloud computing",
    "virtual reality",
    "quantum computing",
    "computer vision",
    "robotics",
    "natural language processing",
    "nlp",
    "big data",
    "niche",
    "paris",
    "open source",
    "ethics",
    "privacy",
    "education",
    "healthcare",
    "geography",
    "finance",
    "university",
    "music",
    "sports",
    "environment",
    "agriculture"
    "musique",
    "paris",
    "github",
    "hack",
    "bank",
    "bitcoin",
    "self hosting"
]

start = time()
processed_count = 0
# I am saving during the loop to avoid losing data if the process is interrupted
for query in queries:
    # Collect repositories sorted by stars
    log(f"Processing query: {query} sorted by stars")
    current_processed_count = analytics.collect_repository_data_for_search(
        client, 
        query=query, 
        sort="stars",
        n_releases=12,
        logging=True)
    processed_count += current_processed_count
    log(f"Collected {current_processed_count} repositories for query: {query} sorted by stars")
    log("Saving data to CSV...")
    analytics.to_csv("data")
    log("Data saved.")
    
    # Collect repositories sorted by best matches
    log(f"Processing query: {query} sorted by best matches")
    current_processed_count = analytics.collect_repository_data_for_search(
        client, 
        query=query,
        n_releases=12,
        logging=True)
    processed_count += current_processed_count
    log(f"Collected {current_processed_count} repositories for query: {query} sorted by best matches")
    log("Saving data to CSV...")
    analytics.to_csv("data")
    log("Data saved.")
end = time()

hours = int((end - start) // 3600)
minutes = int(((end - start) % 3600) // 60)
log(f"Temps écoulé pour collecter {processed_count} repositories : {hours} heures et {minutes} minutes")