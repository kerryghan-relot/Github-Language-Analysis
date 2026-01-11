import requests
from datetime import datetime, timedelta
from typing import Any, List, Dict
from time import time, sleep
import copy

class GitHubClient:
    def __init__(self, token: str, base_url: str = "https://api.github.com", hourly_rate_limit: int = 5000):
        # Base attributes
        self.base_url: str = base_url
        self.token: str = token
        self.headers: dict = {
            "Authorization": f"token {self.token}"
        }
        # Rate limiting attributes
        self.last_search_time: float = 0.0
        self.hourly_rate_limit: int = hourly_rate_limit
        # Caching attributes
        self._cached_url: str|None = None
        self._cached_json_result: Any|None = None

    def _get(self, url: str, params: dict|None = None, raw: bool = False, cache: bool = False, **kwargs) -> Any:
        """
        Performs a get request to the provided url and returns the JSON response.
        The header does not need to be provided as it is handled by the class.
        If successful, the response is stored in the last_search attribute.
        It also respects the hourly rate limit set for the client. If the set hourly rate limit is reached, it waits before making the request.
        If raw is True, the raw response object is returned instead of the JSON response. In this case, caching is not performed and the value of cache is ignored.

        Args:
            url (str): the api endpoint to call
            params (dict, optional): query parameters to include in the request. Defaults to None.
            raw (bool, optional): whether to return the raw response object. Defaults to False. If True, caching is ignored.
            cache (bool, optional): whether to cache the response. Defaults to True.

        Returns:
            Dict: the JSON response from the API
        """
        # Check rate limit ("last time request made" + "waiting time between request" - "now")
        sleep(max(0, self.last_search_time + 3600 / self.hourly_rate_limit - time()))

        # Perform the GET request to the GitHub API and raise an error for bad responses
        response: requests.models.Response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        # Parse the JSON response, store it and return it
        self.last_search_time = time()
        if raw:
            return response
        
        json_response: Dict = response.json()
        if cache:
            self._cached_url = response.url
            self._cached_json_result = copy.deepcopy(json_response)
        return json_response
    
    def _get_cached_response(self) -> Any|None:
        """
        Returns the cached JSON response from the last successful API call.

        Returns:
            Any|None: The cached JSON response or None if no request has been made yet
        """
        return copy.deepcopy(self._cached_json_result)
    
    def _get_last_page_number(self, response: requests.models.Response) -> int:
        """
        Extracts the last page number from the Link header of a paginated response.

        Args:
            response (requests.models.Response): The response object from the API call
        Returns:
            int: The last page number, or -1 if not found
        """
        if 'Link' in response.headers:
            for link in response.headers['Link'].split(','):
                if 'rel="last"' in link:
                    last_page_url = link.split(';')[0].strip('<> ')
                    return int(last_page_url.split('page=')[-1].split('&')[0])
        return -1
    
    def get_repository(self, owner: str, repo_name: str, commit_sha: str|None = None, params: dict|None = None, cache: bool = False) -> Dict:
        """
        Retrieves a specific repository from GitHub, eventually at a specific commit SHA.

        Args:
            owner (str): the owner of the repository
            repo_name (str): the name of the repository
            commit_sha (str, optional): the commit SHA to retrieve the repository at. Defaults to None.
            params (dict, optional): query parameters to include in the request. Defaults to None.
            cache (bool, optional): whether to cache the response. Defaults to False.
        Returns:
            Dict: The JSON response containing the repository information
        """
        url: str = f"{self.base_url}/repos/{owner}/{repo_name}"

        if commit_sha:
            url += f"/git/trees/{commit_sha}"

        return self._get(url, params=params, cache=cache)
    
    def get_repositories(self, query: str = "stars:>1000", sort: str|None = "stars", per_page: int = 10, page: int = -1, cache: bool = False) -> List[Dict]:
        """
        Searches for repositories on GitHub based on the provided query.
        If page is -1, it retrieves only all the results from all the pages. Hence, the results will not be cached.

        Args:
            query (str, optional): the search query. Defaults to "stars:>1000".
            sort (str|None, optional): the sort criteria. Defaults to "stars".
            per_page (int, optional): number of results per page. Defaults to 10.
            page (int, optional): the page number to retrieve. Defaults to -1.
            cache (bool, optional): whether to cache the response. Defaults to False.

        Returns:
            List[Dict]: The JSON response containing the search results
        """
        url: str = f"{self.base_url}/search/repositories"

        params: dict = {
            "q": query,
            "sort": sort,
            "order": "desc",
            "per_page": per_page,
            "page": page
        }
        if sort is None:
            params.pop("sort")

        if page == -1:
            all_items: List[Dict] = []

            params["per_page"] = 100
            params["page"] = 1

            raw_response = self._get(url, params=params, raw=True, cache=False)

            # Retrieve the number of pages with an api call
            last_page_number = min(self._get_last_page_number(raw_response), 10)

            all_items.extend(raw_response.json()["items"])

            # Retrieve all other pages since we already processed the first one
            for current_page in range(2, last_page_number + 1):
                repos = self.get_repositories(
                    query=query,
                    sort=sort,
                    per_page=100, # Max per_page value for GitHub API
                    page=current_page,
                    cache=False
                )

                all_items.extend(repos)

            return all_items

        return self._get(url, params=params, cache=cache)["items"]
    
    def get_releases(self, owner: str, repo_name: str, stable_only: bool = True, time_spaced: bool = True, number_of_releases: int = 8, cache: bool = False) -> List[Dict]:
        """
        Retrieves the releases of a specific repository.
        We can select to retrieve only stable releases (non pre-releases and non drafts).
        If time_spaced is True, the releases are spaced over time and only a certain number of releases are returned.

        Args:
            owner (str): the owner of the repository
            repo_name (str): the name of the repository
            stable_only (bool, optional): whether to retrieve only stable releases. Defaults to True.
            time_spaced (bool, optional): whether to space the releases over time. Defaults to True.
            number_of_releases (int, optional): number of releases to retrieve if time_spaced is True. Ignored if time_spaced is False. Defaults to 8.
            cache (bool, optional): whether to cache the response. Defaults to False.

        Returns:
            List[Dict]: The JSON response containing the releases
        """
        url: str = f"{self.base_url}/repos/{owner}/{repo_name}/releases"
        releases: List[Dict] = []

        for page in range(1, 1000):  # Arbitrary limit to avoid infinite loops
            params: dict = {
                "per_page": 100,
                "page": page
            }
            page_releases: List[Dict] = self._get(url, params=params, cache=cache)

            if not page_releases:  # No more releases available
                break

            releases.extend(page_releases)
        
        if stable_only:
            # Filter out pre-releases and drafts using filter()
            releases = list(filter(lambda r: not r.get("prerelease", False) and not r.get("draft", False), releases))

        # Sort releases by published date (or created date)
        releases.sort(key=lambda r: r["published_at"] or r["created_at"])

        if time_spaced and len(releases) > number_of_releases:
            # Convert dates to datetime objects for easier manipulation
            releases_with_dates = []
            for r in releases:
                date_str = r["published_at"] or r["created_at"]
                date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                releases_with_dates.append((r, date_obj))

            # Determine the time span
            target_interval_days = (releases_with_dates[-1][1] - releases_with_dates[0][1]).days / (number_of_releases - 1)

            selected_releases_with_date = [releases_with_dates[0]]

            for i in range(1, number_of_releases - 1):
                target_date = selected_releases_with_date[0][1] + timedelta(days=int(i * target_interval_days))
                
                # Find the release closest to the target date
                closest_release = min(
                    releases_with_dates[1:],
                    key=lambda r: abs((r[1] - target_date).days)
                )
                selected_releases_with_date.append(closest_release)

            selected_releases_with_date.append(releases_with_dates[-1])

            # Ensure to keep only the release data, not the dates. Also ensure no more than the requested number of releases
            releases = [r[0] for r in selected_releases_with_date[:number_of_releases]]
            
        return releases

    def get_file_count_from_tree(self, owner: str, repo_name: str, default_branch: str) -> int:
        """
        Retrieves the number of files via the Git Tree API.
        If owner and repo_name are None, it uses the cached repository from the last API call.
        The call to the Git Tree API is never cached.

        Args:
            owner (str|None, optional): the owner of the repository. Defaults to None.
            repo_name (str|None, optional): the name of the repository. Defaults to None.
        Returns:
            int: The number of files in the repository
        """        
        # Retrieve the Git Tree recursively from the default branch
        tree_data: dict = self.get_repository(
            owner, repo_name, 
            commit_sha=default_branch, 
            params={"recursive": "1"}, 
            cache=False)
            
        # Count only files (not directories)
        file_count = len([item for item in tree_data["tree"] if item["type"] == "blob"])
        
        return file_count
    
    def get_release_count(self, owner: str, repo_name: str) -> int:
        """
        Retrieves the number of releases for a specific repository.

        Args:
            owner (str): the owner of the repository
            repo_name (str): the name of the repository
        Returns:
            int: The number of releases in the repository
        """
        url = f"{self.base_url}/repos/{owner}/{repo_name}/releases"

        response = self._get(url, params={"per_page": 1}, raw=True, cache=False)

        number_of_commits = self._get_last_page_number(response)
        if number_of_commits != -1: return number_of_commits
        
        return len(response.json())
    
    def get_contributor_count(self, owner: str, repo_name: str) -> int:
        """
        Retrieves the number of contributors for a specific repository.

        Args:
            owner (str): the owner of the repository
            repo_name (str): the name of the repository
        Returns:
            int: The number of contributors in the repository
        """
        url = f"{self.base_url}/repos/{owner}/{repo_name}/contributors"

        response = self._get(url, params={"per_page": 1, "anon": "true"}, raw=True, cache=False)

        number_of_commits = self._get_last_page_number(response)
        if number_of_commits != -1: return number_of_commits
        
        return len(response.json())

    def get_commit_count(self, owner: str, repo_name: str) -> int:
        """
        Retrieves the total number commits for a specific repository.

        Args:
            owner (str): the owner of the repository
            repo_name (str): the name of the repository
        Returns:
            int: The total number of commits in the repository
        """
        url = f"{self.base_url}/repos/{owner}/{repo_name}/commits"

        response = self._get(url, params={"per_page": 1}, raw=True, cache=False)

        number_of_commits = self._get_last_page_number(response)
        if number_of_commits != -1: return number_of_commits
        
        return len(response.json())
