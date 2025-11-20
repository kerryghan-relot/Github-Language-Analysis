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

### 3. Install the required dependencies:
Once you have created and activated your virtual environment (either pip or conda), run:
```bash
pip install -r requirements.txt
```
