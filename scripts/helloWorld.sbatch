#!/bin/bash
#
# SBATCH wrapper to launch scripts/glaDataCollection.py and notify on completion.
# SLURM Script for GitHub data collection
#
# Usage:
#   `sbatch scripts/helloWorld.sbatch`
#
# Slurm directives:
# - single node, 5 CPUs, 30 GB RAM, 5 minutes, email notifications

#SBATCH --job-name=hello_world_test
#SBATCH --output=/info/etu/m2/s2403274/MLOps_Bigdata_Projet/Github-Language-Analysis/logs/helloWorld_%j.log
#SBATCH --error=/info/etu/m2/s2403274/MLOps_Bigdata_Projet/Github-Language-Analysis/logs/helloWorld_%j.err
#SBATCH --time=00:05:00
#SBATCH --mem=30G
#SBATCH --cpus-per-task=5
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kerryghan.relot.etudiant@pm.me

echo "📈 Github Language Analysis - Hello World (SLURM)"
echo "=========================================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "Start time: $(date)"
echo ""

# Déterminer la racine du projet
# SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="/info/etu/m2/s2403274/MLOps_Bigdata_Projet/Github-Language-Analysis"

cd "$PROJECT_ROOT" || {
    echo "❌ Impossible de se placer à la racine du projet"
    exit 1
}

# Créer le dossier de logs avec chemin absolu
mkdir -p "$PROJECT_ROOT/logs"


# Lancer la collecte via le script collect_github_data.sh
echo "🚀 Lancement du helloWorld..."
echo "⏱️  Durée maximale: 5 minutes"
echo "⏱️  Début: $(date)"
echo ""

# Exécuter le script de collecte
source ~/miniconda3/etc/profile.d/conda.sh
conda activate superman

# Setting variable to launch python script
PYTHON=~/miniconda3/envs/superman/bin/python
SCRIPT=$PROJECT_ROOT/scripts/helloWorld.py

${PYTHON} "${SCRIPT}"

EXIT_CODE=$?

# Résumé final
echo ""
echo "=========================================================="
echo "📊 Fin du helloWorld"
echo "⏱️  Fin: $(date)"
echo "Exit code: $EXIT_CODE"
echo ""

echo ""
echo "🎉 Job SLURM terminé!"
echo "💡 Consultez les logs dans: logs/helloWorld_${SLURM_JOB_ID}.out"

exit $EXIT_CODE