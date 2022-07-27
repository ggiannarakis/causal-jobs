cd 'C:\Program Files\Docker\Docker'
start 'Docker Desktop.exe'
Start-Sleep -Seconds 45
docker start 9ed479c5a42f
cd C:\Users\ggian\Documents\git-repos\causal-jobs
conda activate gmailapi
python Analysis.ipynb
jupyter nbconvert Analysis.ipynb --to html --no-input --no-prompt
docker stop 9ed479c5a42f
git add --all
git commit -m "latest report"
git push