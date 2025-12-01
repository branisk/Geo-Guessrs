source /workspace/miniconda/etc/profile.d/conda.sh
conda activate geoguessr
python -m ipykernel install --user --name geoguessr --display-name "Python (geoguessr)"
jupyter kernelspec list
git config --global credential.helper store
