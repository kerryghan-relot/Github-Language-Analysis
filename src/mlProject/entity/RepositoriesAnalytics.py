from collections import defaultdict
from tqdm import notebook
from urllib.parse import quote
import pickle
import os, shutil
from datetime import datetime
from typing import Dict
import pandas as pd

from src.mlProject.entity.GitHubClient import GitHubClient
from src.mlProject.entity.RepositorySummary import RepositorySummary
from src.mlProject.constants.constants import REPOSITORY_FEATURES, SUPPORTED_LANGUAGES
from src.mlProject.utils.common import log

class RepositoriesAnalytics:
    def __init__(self, client: GitHubClient):
        self._client: GitHubClient = client

        self._repos_summary: pd.DataFrame = self._create_empty_repository_statistics_dataframe()
        self._language_matrices: Dict[str, pd.DataFrame] = {}

        self.existing_repositories: set = set()

    def _create_empty_repository_statistics_dataframe(self) -> pd.DataFrame:
        """
        Creates an empty DataFrame with the appropriate columns for RepositoryStatistics.

        Returns:
            pd.DataFrame: An empty DataFrame with RepositoryStatistics columns
        """
        return pd.DataFrame(columns=REPOSITORY_FEATURES)
    
    def __getitem__(self, key: str) -> RepositorySummary:
        """
        Retrieves the RepositoryStatistics for a given repository name.

        Args:
            key (str): The name of the repository

        Returns:
            RepositoryStatistics: The statistics of the repository
        """
        key_stats = self._repos_summary[self._repos_summary["name"] == key]
        return RepositorySummary(**key_stats.iloc[0].to_dict())
    
    def __contains__(self, key: str) -> bool:
        """
        Checks if the repository with the given name exists in the internal DataFrame.

        Args:
            key (str): The name of the repository

        Returns:
            bool: True if the repository exists, False otherwise
        """
        return key in self.existing_repositories
    
    def __delitem__(self, key: str) -> None:
        """
        Deletes the repository with the given name and its language statistics from the internal DataFrames.

        Args:
            key (str): The name of the repository to delete
        """
        if key in self:
            self._repos_summary = self._repos_summary[self._repos_summary["name"] != key]
            del self._language_matrices[key]
            self.existing_repositories.remove(key)

    def to_csv(self, folder_path: str, empty: bool = True) -> None:
        """
        Saves the repository summary DataFrame and the languages DataFrames to CSV files at the specified folder path.

        Args:
            folder_path (str): The folder path to save the CSV files
            empty (bool, optional): Whether to empty the folder if it already exists. Defaults to True.
        """
        # remove the folder if it already exist
        if empty and os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        # Create the folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        # Save repository summary
        summary_path = os.path.join(folder_path, "repositories_summary.csv")
        self._repos_summary.to_csv(summary_path, index=False)

        # Save language matrices
        languages_folder = os.path.join(folder_path, "language_matrices")
        os.makedirs(languages_folder, exist_ok=True)

        # Save each language matrix in its own CSV file
        # They are organized in subfolders by owner
        for full_name, lang_df in self._language_matrices.items():
            owner, repo_name = full_name.split("/")
            repo_folder = os.path.join(languages_folder, owner)
            os.makedirs(repo_folder, exist_ok=True)
            lang_path = os.path.join(repo_folder, f"{repo_name}.csv")
            lang_df.to_csv(lang_path, index=False)

    @classmethod
    def from_csv(cls, folder_path: str, client: GitHubClient) -> "RepositoriesAnalytics":
        """
        Loads the RepositoriesAnalytics object from CSV files at the specified folder path.
        If the folder is empty, returns an empty RepositoriesAnalytics object.

        Args:
            folder_path (str): The folder path to load the CSV files from
            client (GitHubClient): The GitHub client to use for API calls
        Returns:
            RepositoriesAnalytics: The loaded RepositoriesAnalytics object
        """
        instance = cls(client)

        # Return early if folder is empty
        if not os.listdir(folder_path):
            return instance

        # Load repository summary
        summary_path = os.path.join(folder_path, "repositories_summary.csv")
        instance._repos_summary = pd.read_csv(summary_path)

        # Load language matrices
        languages_folder = os.path.join(folder_path, "language_matrices")
        for owner in os.listdir(languages_folder):
            owner_folder = os.path.join(languages_folder, owner)
            if os.path.isdir(owner_folder):
                for repo_file in os.listdir(owner_folder):
                    if repo_file.endswith(".csv"):
                        repo_name = repo_file[:-4]  # Remove .csv extension
                        full_name = f"{owner}/{repo_name}"
                        lang_path = os.path.join(owner_folder, repo_file)
                        instance._language_matrices[full_name] = pd.read_csv(lang_path)

        # Update existing repositories set
        instance.existing_repositories = set(instance._repos_summary["name"].tolist())

        return instance
    
    def to_pickle(self, path: str) -> None:
        """
        Saves the entire object to a pickle file at the specified path.

        Args:
            path (str): The file path to save the pickle
        """
        with open(path, "wb") as f:
            pickle.dump(self, f)

    def _append_repository_summary(self, client: GitHubClient, repo: dict) -> None:
        """
        Appends corresponding RepositoryStatistics to the internal DataFrame.

        Args:
            client (GitHubClient): The GitHub client to use for API calls
            repo (dict): The repository data from GitHub API
        """
        # Retrieve necessary information
        owner, repo_name = repo["owner"]["login"], repo["name"]

        # Get all statistics
        stats = RepositorySummary(
            name=repo["full_name"],
            created_at=datetime.fromisoformat(repo.get("created_at", "")).date(),
            updated_at=datetime.fromisoformat(repo.get("updated_at", "")).date(),
            file_count=client.get_file_count_from_tree(owner=owner, repo_name=repo_name, default_branch=repo["default_branch"]),
            release_count=client.get_release_count(owner=owner, repo_name=repo_name),
            size=repo["size"],
            star_count=repo["stargazers_count"],
            fork_count=repo["forks_count"],
            contributor_count=client.get_contributor_count(owner=owner, repo_name=repo_name),
            commit_count=client.get_commit_count(owner=owner, repo_name=repo_name),
            issue_count=client.get_issue_count(owner=owner, repo_name=repo_name),
            topics=repo.get("topics", [])
        )

        # Update the dataframe in place
        self._repos_summary.loc[len(self._repos_summary)] = pd.Series(stats.__dict__)

    def _add_language_matrix(self, client: GitHubClient, repo: dict, n_releases: int) -> bool:
        """
        Appends the language statistics DataFrame to the internal dictionary for a given repository.

        Args:
            client (GitHubClient): The GitHub client to use for API calls
            repo (dict): The repository data from GitHub API
            n_releases (int): The number of releases to process
        Returns:
            bool: True if at least one release was processed, False otherwise
        """
        # Retrieve necessary information
        owner, repo_name, full_name = repo["owner"]["login"], repo["name"], repo["full_name"]

        # Get n_releases time-spaced stable releases
        releases = client.get_releases(owner, repo_name, stable_only=True, time_spaced=True, number_of_releases=n_releases)

        if not releases:
            return False

        # Process each release to compute the percentage of each language
        for release in releases:
            # URL-encode the tag name to handle special characters like '#', '?', '/', etc.
            tag_name = quote(release['tag_name'], safe='')
            
            # Retrieve the Git Tree recursively from the release tag
            tree_data = client.get_repository(
                owner, 
                repo_name, 
                commit_sha=tag_name, 
                params={"recursive": "1"}, 
                cache=False
            )['tree']

            # Compute file sizes per language
            file_sizes = defaultdict(int)
            for file_info in filter(lambda f: f['type'] == 'blob', tree_data):
                file_extension = os.path.splitext(file_info['path'])[1]
                file_size = file_info['size']

                if file_extension not in SUPPORTED_LANGUAGES:
                    continue

                file_sizes[file_extension] += file_size

            # Normalize file sizes
            total_size = sum(file_sizes.values())
            for ext in file_sizes: 
                file_sizes[ext] /= total_size
                file_sizes[ext] = round(file_sizes[ext], 4)

            # Create a temporary dict to include the date
            temp_dict = dict(file_sizes)
            temp_dict['date'] = datetime.fromisoformat(release.get('published_at', release.get('created_at', ''))).date()

            # Create the dataframe if not existing
            if full_name not in self._language_matrices:
                self._language_matrices[full_name] = pd.DataFrame(columns=['date']+list(SUPPORTED_LANGUAGES))

            # Effectively add the row to the DataFrame
            num_rows = len(self._language_matrices[full_name])
            self._language_matrices[full_name].loc[num_rows] = temp_dict

            # Replace NaN with 0
            self._language_matrices[full_name].fillna(0, inplace=True)

        return True

    def collect_repository_data_for_search(self, client: GitHubClient, query: str, sort: str|None = None, update: bool = False, max_repositories: int = 1000, n_releases: int = 12, logging: bool = False) -> int:
        """
        Collects repository data for repositories matching the search query.

        Args:
            client (GitHubClient): The GitHub client to use for API calls
            query (str): The search query to find repositories
            sort (str|None): The sort criteria for the search results. Defaults to None.
            update (bool, optional): Whether to update existing repositories. Defaults to False.
            max_repositories (int, optional): Maximum number of repositories to process. Defaults to 1000.
            n_releases (int, optional): Number of releases to process for language statistics. Defaults to 12.
            logging (bool, optional): Whether to log progress messages. Defaults to False.
        Returns:
            int: The number of processed repositories
        """

        repositories = client.search_repositories(query=query, sort=sort, page=-1)

        processed_repo = 0

        for repo in notebook.tqdm(repositories[:max_repositories], desc=f"Processing {query}"):
            # Skip if already exists and not updating
            if repo["full_name"] in self and not update:
                if logging: log(f"Repository {repo['full_name']} already exists. Skipping.", level="INFO")
                continue
            # If updating, remove existing entry
            if update:
                del self[repo["full_name"]]

            # Compute and store language matrix
            any_release = self._add_language_matrix(client, repo, n_releases)
                
            # Skip if no release found
            if not any_release:
                if logging: log(f"Repository {repo['full_name']} has no releases. Skipping.", level="WARN")
                continue
            
            # Get and append repository summary to the internal DataFrame
            self._append_repository_summary(client, repo)

            # Update the set of existing repositories
            self.existing_repositories.add(repo["full_name"])
            if logging: log(f"Repository {repo['full_name']} processed successfully.", level="INFO")

            processed_repo += 1

        # Return the actual number of processed repositories
        return processed_repo


    def repositories_summary(self) -> pd.DataFrame:
        """
        Returns the internal DataFrame containing the repository statistics.

        Returns:
            pd.DataFrame: DataFrame containing the repository statistics
        """
        return self._repos_summary
