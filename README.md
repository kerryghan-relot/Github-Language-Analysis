# Github-Language-Analysis

MLOps project to retrieve Github's repositories and analyse their language usage over time.

## Structure explanation

The `template.py` is used to create the basic structure of the project. You can modify and expand upon it as needed for your analysis.

The `requirements.txt` file lists all the Python packages required to run the project.

The `setup.py` file is used for packaging and distributing the project. It is especially useful in our case to use the project like any other installed package.

## How to use

### 1. Clone the repository:
```bash
git clone https://github.com/kerryghan-relot/Github-Language-Analysis.git
cd Github-Language-Analysis
```
Or use your favorite tool/IDE to clone the repository.
<br>
If you want to modify the project structure, you can run the `template.py` script:
```bash
python template.py
```

### 2. Create and activate a virtual environment:
You can use either `pip` or `conda` to create a virtual environment.
<br>
If you decide to use `pip`, run:
```bash
python -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`
```
If you prefer `conda`, run:
```bash
conda create --name myenv python=3.13
conda activate myenv
```
You can also simply choose to use uv (that's the prefered method), simply run:
```bash
uv sync
```
it will automatically use the pyproject.toml and uv.lock files to generate your environnement.

### 3. Install the required dependencies:
Once you have created and activated your virtual environment (either pip or conda), run:
```bash
pip install -r requirements.txt
```

### 4. Exploring with demos
Once your environnement is setup properly, you can explore demos in the `./demo/` folder to discover all the capabilities of the project.

### 5. Scripting
You can also automate the data retrieval via the scripts provided. the `helloWorld` scripts serves just as a test. The `dataCollector.sbatch` and `glaDataCollection.py` are used to actually retrieve data from the API.

Note that in order for you to be able to run the script, you must get an API key and put it in the `.env` file at the root of the project. It should at least contain the following line:
```
GITHUB_TOKEN=ghp_***** # Replace with you actual API key
```