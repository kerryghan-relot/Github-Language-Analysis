# GitHub Language Analysis

## Description du projet

Le but de ce projet est de faire une analyse et prédiction de la popularité des langages de programmation que l'on retrouve sur GitHub.


## Données récupérées

Nous avons récupéré les pourcentages de chaque langages pour chaque repository et pour jusqu'à 12 releases par repository si disponible.

Nous avons d'abord stocké ces données dans des fichiers csv. Nous avions un fichier csv par repository où les colonnes sont les langages de programmation et les lignes sont les releases récupérées.

Nous avons ensuite concaténé les fichiers csv en un seul afin de faciliter l'analyse.

Nous avons également un second fichier csv plus général qui stocke des informations et statistiques sur chaque repository (un repository par ligne).

Les langages de programmation récupérés sont les suivants :
```python
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
```
Nous avons volontairement exclus tous types de fichiers textes tels que les fichiers de configurations, markdown, textes bruts, logs, etc…


## Outils utilisés

Nous pensions tout d'abord utiliser Microsoft Azure avec PowerBI pour la visualisation de données. Cependant nous avons rencontré des difficultés techniques qui nous en ont empêché. Aussi, nous avons reçu un email nous indiquant que nos crédits étaient expirés.
C'est pourquoi nous nous sommes tourné vers une solution auto-herbergée et open-source. Nous avons loué un VPS chez OVH et installé Apache Superset dessus.


## Model utilisé

Pour le model utilisé, nous avons utilisé le modèle de prédiction et modélisation de série temporelle fournit par Meta dans sa librairie `Prophet`.