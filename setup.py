import setuptools

with open('README.md','r',encoding="utf-8") as f:
    long_description=f.read()


__version__= "0.0.0"

REPO_NAME='Github-Language-Analysis'
AUTHOR_USER_NAME="Kerryghan Relot, Lucas Schmitt"
SRC_REPO = "mlProject"
AUTHOR_EMAIL="kerryghan.relot.etu@univ-lemans.fr, lucas.schmitt.etu@univ-lemans.fr"

setuptools.setup(
    name=SRC_REPO,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="MLOps project to retrieve Github's repositories and analyse their language usage over time.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/kerryghan-relot/Github-Language-Analysis/",
    project_urls={
        "Bug Tracker": "https://github.com/kerryghan-relot/Github-Language-Analysis/issues",
        "Source": "https://github.com/kerryghan-relot/Github-Language-Analysis"
    },
    package_dir={"":"src"},
    packages=setuptools.find_packages(where='src')
)