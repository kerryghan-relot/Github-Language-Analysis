print("Hello, World!\n")

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
log(f"Initializing GitHub client with token {os.getenv('GITHUB_TOKEN')[:6]}****...")
client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
log(f"GitHub client initialized with \n      base_url: {client.base_url}\n      token: {client.token[:4]}****")

log("")
log("--------------------------------")
log("Everything is set up correctly!")