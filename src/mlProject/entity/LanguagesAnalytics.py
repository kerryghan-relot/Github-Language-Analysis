from copy import deepcopy
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from math import ceil
import numpy as np
from pandas.io.formats.style import Styler
from prophet import Prophet

from src.mlProject.entity import GitHubClient, RepositoriesAnalytics
from src.mlProject.constants import SUPPORTED_LANGUAGES

class LanguagesAnalytics:
    def __init__(self, client: GitHubClient, folder_path: str = "data"):
        self.repositories_analytics: RepositoriesAnalytics = RepositoriesAnalytics.from_csv(folder_path, client=client)
        self.merged_df: pd.DataFrame = pd.DataFrame()
        self._supported_languages: set = SUPPORTED_LANGUAGES


    def merge_and_clean_language_data(self) -> pd.DataFrame:
        """
        Merge and clean language data from repositories into a single DataFrame.
        The resulting DataFrame will have a 'name' column for the repository name, a 'date' column for the date of the data, and columns for each supported language with the percentage of files in that language.
        The 'name' column will be the first column in the DataFrame, followed by the 'date' column and then the language columns.
        The 'date' column will be converted to datetime format for easier analysis.

        Returns:
            pd.DataFrame: A cleaned DataFrame with merged language data.
        """
        self.merged_df: pd.DataFrame = pd.DataFrame()

        # Merge language matrices for all repositories
        for name in self.repositories_analytics.existing_repositories:
            df = self.repositories_analytics._language_matrices[name]
            df["name"] = name
            self.merged_df = pd.concat([self.merged_df, df], ignore_index=True)

        # Reorder columns to have 'name' first
        cols = ['name', 'date', *self._supported_languages]
        self.merged_df = self.merged_df[cols]

        # Convert 'date' column to datetime
        self.merged_df['date'] = pd.to_datetime(self.merged_df['date'])

        return self.merged_df

    def clean_repositories_without_supported_languages(self) -> dict:
        """
        Remove repositories that do not use any of the supported languages.
        The function identifies releases that have zero usage for all supported languages and removes them from the merged DataFrame.
        The instance variable `merged_df` is updated to reflect the cleaned data.
        It also calculates and returns information about the cleaning process, including counts and percentages of removed releases and repositories.

        Returns:
            dict: Information about the cleaning process, including counts and percentages of removed releases and repositories.
        """
        info: dict[str, int | float] = {
            "total_releases": len(self.merged_df),
            "total_repositories": len(self.merged_df['name'].unique()),
        }

        # Filter columns corresponding to supported languages
        filtered_df = self.merged_df[[*self._supported_languages]]

        # Identify repositories with no usage of supported languages
        repos_without_supported_languages = filtered_df.index[(filtered_df == 0).all(axis=1)]

        # Remove repositories that do not use any supported languages
        self.merged_df = self.merged_df.drop(index=repos_without_supported_languages)

        info["total_releases_after_cleaning"] = len(self.merged_df)
        info["total_repositories_after_cleaning"] = len(self.merged_df['name'].unique())
        info["removed_releases"] = info["total_releases"] - info["total_releases_after_cleaning"]
        info["removed_repositories"] = info["total_repositories"] - info["total_repositories_after_cleaning"]
        info["percentage_removed_releases"] = (info["removed_releases"] / info["total_releases"]) * 100
        info["percentage_removed_repositories"] = (info["removed_repositories"] / info["total_repositories"]) * 100
        info["repositories_with_12_or_more_releases"] = len(self.merged_df['name'].value_counts().where(lambda x: x >= 12).dropna())
        info["percentage_repositories_with_12_or_more_releases"] = (info["repositories_with_12_or_more_releases"] / info["total_repositories_after_cleaning"]) * 100

        return info

    def get_language_usage_summary(self) -> pd.DataFrame:
        """
        Calculate the percentage of repositories using each supported language and the average percentage of files in each language across all repositories.
        Column names signification:
            'language_extensions' : Programming languages extensions (e.g., .py for Python, .js for JavaScript, etc.). It represents the programming language used in the repositories being analyzed.
            'repository_count' : Number of repositories that contain files in that language.
            'language_usage_percentage' : Proportion of repositories that contain at least one file in that language. It means "X% of repositories uses that language.".
            'average_file_percentage' : Average percentage of files in that language across all repositories. It means "On average, a repository has X% of its files in that language.".
            'has_100_percent_repos' : Indicates whether there are any repositories that are 100% written in that language (i.e., all files in the repository are of that language).

        Returns:
            pd.DataFrame: A DataFrame summarizing language usage statistics.
        """
        # Calculate the percentage of repositories using each supported language
        language_usage_values = [
            (language, (self.merged_df[language] > 0).sum(), (self.merged_df[language] > 0).sum() / len(self.merged_df), (self.merged_df[language] == 1).any())
            for language in self._supported_languages
        ]
        language_usage_df = pd.DataFrame(
            language_usage_values,
            columns=["language_extensions", "repository_count", "language_usage_percentage", "has_100_percent_repos"]
        )

        # Calculate the average percentage of files in each language across all repositories
        average_file_percentage_df = pd.DataFrame(
            self.merged_df.describe().loc["mean"].reset_index()
        )
        average_file_percentage_df = average_file_percentage_df.rename(
            columns={"index": "language_extensions", "mean": "average_file_percentage"}
        )

        # Merge the two DataFrames on the 'language_extensions' column
        languages_summary = average_file_percentage_df.merge(language_usage_df, on="language_extensions")
        # Sort the merged DataFrame by the number of repositories using each language in descending order
        languages_summary = languages_summary.sort_values(by="repository_count", ascending=False)
        # Reset the index to ensure a clean, sequential index after sorting
        languages_summary = languages_summary.reset_index(drop=True)
        # Reorder columns for better readability
        languages_summary = languages_summary[["language_extensions", "repository_count", "language_usage_percentage", "average_file_percentage", "has_100_percent_repos"]]

        # Display the final DataFrame
        return languages_summary


    def display_language_usage_summary(self) -> Styler:
        """
        Format the language usage summary DataFrame for better readability.

        Args:
            languages_summary (Styler): The Styled DataFrame summarizing language usage statistics.
        """
        languages_summary: pd.DataFrame = self.get_language_usage_summary()

        return languages_summary.style.format({
            "average_file_percentage": "{:.4f} %",
            "language_usage_percentage": "{:.4f} %"
        }).relabel_index(["Language",
            "Number of Repositories",
            "Usage Percentage",
            "Average File Percentage",
            "Has 100% Repositories"
        ], axis=1).set_caption("Summary of Supported Languages Usage in Repositories")


    def save_language_usage_summary(self, filename: str = "data/language_usage_summary.csv") -> None:
        """
        Save the language usage summary DataFrame to a CSV file.

        Args:
            filename (str): The name of the CSV file to save the summary to. Default is "data/language_usage_summary.csv".

        Returns:
            None: Saves the DataFrame to a CSV file.
        """
        languages_summary: pd.DataFrame = self.get_language_usage_summary()

        languages_summary.to_csv(filename, index=False)

    def save_merged_language_matrix(self, filename: str = "data/merged_language_matrix.csv") -> None:
        """
        Save the merged language matrix DataFrame to a CSV file.

        Args:
            filename (str): The name of the CSV file to save the merged language matrix to. Default is "data/merged_language_matrix.csv".

        Returns:
            None: Saves the DataFrame to a CSV file.
        """
        self.merged_df.to_csv(filename, index=False)

    def plot_language_correlation_matrix(self, separating_lines: bool = True) -> None:
        """
        Build and display a correlation matrix heatmap for the usage of supported languages in repositories.
        Only the lower triangle of the correlation matrix is displayed to avoid redundancy, as the matrix is symmetric.
        The languages extensions are sorted alphabetically in the correlation matrix for better readability.

        Args:
            separating_lines (bool): Whether to include separating lines between the cells in the heatmap. Default is True.

        Returns:
            None: Displays a heatmap of the correlation matrix.
        """
        # Build a correlation matrix to see if there are languages that are often used together in the same repositories
        correlation_matrix = self.merged_df[sorted(self._supported_languages)].corr()

        # Display the correlation matrix as a heatmap, but only plot the lower triangle to avoid redundancy
        plt.figure(figsize=(14, 12))
        sns.heatmap(
            correlation_matrix,
            cmap="coolwarm",
            linewidths=0.5 * separating_lines,
            mask=np.triu(np.ones_like(correlation_matrix, dtype=bool)),
        )
        plt.title("Correlation Matrix of Supported Languages Usage in Repositories")
        plt.tick_params(axis='x', rotation=60)
        plt.show()

    def plot_language_percentage(self) -> None:
        """
        Plots a bar chart showing the percentage of releases using each language, sorted in descending order.
        It represents how many releases have at least one file in that language.

        Also plots a bar chart showing the average file percentage per language, sorted in descending order.
        It represents how much of the codebase is written in that language on average across all repositories.

        Returns:
            None: Displays the bar chart.
        """
        languages_summary: pd.DataFrame = self.get_language_usage_summary()

        fig, axes = plt.subplots(2, 1, figsize=(12, 10))

        # Bar chart for percentage of releases using each language
        sns.barplot(
            x="language_extensions",
            y="language_usage_percentage",
            data=languages_summary.sort_values(by="language_usage_percentage", ascending=False),
            palette="viridis",
            hue="language_extensions",
            legend=False,
            ax=axes[0]
        )
        axes[0].set_title("Percentage of Releases Using Each Language")
        axes[0].set_xlabel("Language Extensions")
        axes[0].set_ylabel("Percentage of Releases")
        axes[0].tick_params(axis='x', rotation=45)

        # Bar chart for average file percentage per language
        sns.barplot(
            x="language_extensions",
            y="average_file_percentage",
            data=languages_summary.sort_values(by="average_file_percentage", ascending=False),
            palette="hot",
            hue="language_extensions",
            legend=False,
            ax=axes[1]
        )
        axes[1].set_title("Average File Percentage per Language")
        axes[1].set_xlabel("Language Extensions")
        axes[1].set_ylabel("File Percentage")
        axes[1].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.show()

    def plot_language_evolution(self, language_extension: str | list[str], errorbar: str | None = "ci", start_date: str | None = None, end_date: str | None = None, interval: str = "M"):
        """
        Plots the evolution of the percentage of files in the specified language(s) across all repositories over time.

        Args:
            df (pd.DataFrame): The DataFrame containing the merged language matrix with a 'date' column and language extension columns.
            language_extension (str | list[str]): The language extension(s) to plot (e.g., ".py" for Python). Can be a single string or a list of strings for multiple languages.
            errorbar (str | None): The type of error bars to display. Options are "ci" for confidence interval, "sd" for standard deviation, or None for no error bars. Default is "ci".
            start_date (str | None): The start date for filtering the data (inclusive). Should be in a format recognized by pd.to_datetime (e.g., "2023-01-01"). Default is None (no filtering).
            end_date (str | None): The end date for filtering the data (inclusive). Should be in a format recognized by pd.to_datetime (e.g., "2023-12-31"). Default is None (no filtering).
            interval (str): The time interval for grouping the data. Options are : "D" for daily, "W" for weekly, "M" for monthly, "Q" for quarterly, "Y" for yearly, etc. Default is "M" (monthly).
        """
        if isinstance(language_extension, str):
            language_extension = [language_extension]

        # Check if the all the language extensions are supported
        if not set(language_extension).issubset(self._supported_languages):
            print(f"Language extension(s) {', '.join(set(language_extension) - self._supported_languages)} is(are) not supported.")
            return

        if start_date is not None:
            self.merged_df = self.merged_df[self.merged_df['date'] >= pd.to_datetime(start_date)]
        if end_date is not None:
            self.merged_df = self.merged_df[self.merged_df['date'] <= pd.to_datetime(end_date)]

        # Group the merged_df by date and calculate the average percentage of files in the specified language for each date
        evolution_df = self.merged_df.groupby('date')[language_extension].mean().reset_index()

        evolution_df['date'] = pd.to_datetime(evolution_df['date']).dt.to_period(interval).dt.to_timestamp()

        # Plot the evolution of the percentage of files in the specified language over time
        plt.figure(figsize=(12, 6))
        for lang in language_extension:
            sns.lineplot(x='date', y=lang, data=evolution_df, marker='o', label=lang, errorbar=errorbar)
        plt.title(f"Evolution of Average Percentage of Files in {language_extension} Over Time")
        plt.xlabel("Date")
        plt.ylabel("Average Percentage of Files")
        plt.xticks(rotation=45)
        plt.grid()
        plt.legend()
        plt.show()

    def plot_releases_per_interval(self, interval="Q"):
        """
        Plots the number of releases per specified time interval.

        Parameters:
            merged_df (pd.DataFrame): DataFrame containing a 'date' column.
            interval (str): Time interval for grouping (e.g., 'Q' for quarterly, 'Y' for yearly).
        """
        releases_per_interval = self.merged_df['date'].dt.to_period(interval).value_counts().sort_index()

        interval_names = {
            "D": "day",
            "W": "week",
            "M": "month",
            "Q": "quarter",
            "Y": "year"
        }

        plt.figure(figsize=(10, 6))
        sns.barplot(x=releases_per_interval.index, y=releases_per_interval.values)
        plt.title(f"Number of Releases per {interval_names.get(interval, interval)}")
        plt.xlabel(f"{interval_names.get(interval, interval)}")
        plt.ylabel("Number of Releases")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()

    def predict_language_evolution(self, language_extension: str, future_periods: int = 12, interval: str = "M"):
        """
        Predicts the future evolution of the percentage of files in a specified language using a simple linear regression model.

        Parameters:
            language_extension (str): The language extension to predict (e.g., ".py" for Python).
            future_periods (int): The number of future periods to predict. Default is 12.
            interval (str): The time interval for grouping the data. Options are : "D" for daily, "W" for weekly, "M" for monthly, "Q" for quarterly, "Y" for yearly, etc. Default is "M" (monthly).
        """
        evolution_df = deepcopy(self.merged_df)

        evolution_df['date'] = pd.to_datetime(evolution_df['date']).dt.to_period(interval).dt.to_timestamp()

        evolution_df = evolution_df.groupby('date')[[language_extension]].sum().reset_index()

        model = Prophet()
        # Prophet requires the columns to be named 'ds' for the date and 'y' for the value to predict
        model.fit(evolution_df.rename(columns={'date': 'ds', language_extension: 'y'}))

        future = model.make_future_dataframe(periods=future_periods, freq=interval)

        return model.predict(future)

    def plot_language_evolution_prediction(self, language_extension: str, future_periods: int = 12, interval: str = "M", ax: plt.Axes | None = None):
        """
        Plots the predicted future evolution of the percentage of files in a specified language.

        Parameters:
            language_extension (str): The language extension to predict (e.g., ".py" for Python).
            future_periods (int): The number of future periods to predict. Default is 12.
            interval (str): The time interval for grouping the data. Options are : "D" for daily, "W" for weekly, "M" for monthly, "Q" for quarterly, "Y" for yearly, etc. Default is "M" (monthly).
        """
        evolution_df = deepcopy(self.merged_df)

        evolution_df['date'] = pd.to_datetime(evolution_df['date']).dt.to_period(interval).dt.to_timestamp()

        evolution_df = evolution_df.groupby('date')[[language_extension]].sum().reset_index()

        model = Prophet()
        # Prophet requires the columns to be named 'ds' for the date and 'y' for the value to predict
        model.fit(evolution_df.rename(columns={'date': 'ds', language_extension: 'y'}))

        future = model.make_future_dataframe(periods=future_periods, freq=interval)

        forecast = model.predict(future)

        figure = model.plot(forecast, include_legend=True, ax=ax)

        return figure

    def plot_all_languages_predictions(self, future_periods: int = 12, interval: str = "M"):
        """
        Plots the predicted future evolution of the percentage of files in all supported languages.

        Parameters:
            future_periods (int): The number of future periods to predict. Default is 12.
            interval (str): The time interval for grouping the data. Options are : "D" for daily, "W" for weekly, "M" for monthly, "Q" for quarterly, "Y" for yearly, etc. Default is "M" (monthly).
        """

        langs = list(self._supported_languages)
        n = len(langs)
        sqrt_n = ceil(n**0.5)
        nrows = sqrt_n if n > sqrt_n * (sqrt_n - 1) else sqrt_n - 1
        ncols = sqrt_n

        fig, axes = plt.subplots(nrows, ncols, figsize=(ncols*10, nrows*6))

        for i in range(nrows):
            for j in range(ncols):
                if i*ncols + j >= n:
                    # Do not display the empty subplots
                    axes[i][j].axis('off')
                    continue
                lang = langs[i*ncols + j]
                self.plot_language_evolution_prediction(lang, future_periods=future_periods, interval=interval, ax=axes[i][j])
                axes[i][j].set_title(f"Evolution of {lang} language usage over time with Prophet")

        return fig

