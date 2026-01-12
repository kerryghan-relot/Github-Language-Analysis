# This is the exhaustive list of features we want to collect for each repository
# They will be stored in the RepositorySummary entity. 
# On disk they are saved in a CSV file with these exact column names.
REPOSITORY_FEATURES = [
    "name", 
    "created_at", 
    "updated_at",
    "file_count", 
    "release_count", 
    "size", 
    "star_count", 
    "fork_count", 
    "contributor_count", 
    "commit_count",
    "issue_count",
    "topics"
]


# List of supported programming languages by their file extensions
# This list will be the columns of the language matrix dataframes
SUPPORTED_LANGUAGES = {
    # Web (JavaScript, TypeScript, markup, styling)
    ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".scss", ".vue",
    # Systems & low-level (C, C++, Rust, Go, Assembly)
    ".c", ".h", ".cpp", ".cc", ".hpp", ".rs", ".go", ".asm", ".s",
    # JVM (Java, Kotlin, Scala)
    ".java", ".kt", ".scala",
    # Microsoft / .NET (C#, VB, F#)
    ".cs", ".vb", ".fs",
    # Scripting (Python, Ruby, PHP, Perl, Lua)
    ".py", ".rb", ".php", ".pl", ".lua",
    # Shell & command-line
    ".sh", ".bat", ".cmd", ".ps1",
    # Functional (Haskell, Elixir)
    ".hs", ".ex",
    # Mobile (Swift, Dart, Objective-C)
    ".swift", ".dart", ".m",
    # Data & science (R, Julia, SQL)
    ".r", ".jl", ".sql",
    # Legacy (COBOL, Fortran, Pascal)
    ".cob", ".cbl", ".f90", ".f95", ".f", ".pas",
}