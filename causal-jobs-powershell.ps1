cd 'C:\Program Files\Docker\Docker'
start 'Docker Desktop.exe'
Start-Sleep -Seconds 60
docker start 9ed479c5a42f
cd C:\Users\ggian\Documents\git-repos\causal-jobs
conda activate gmailapi
python load.py
docker stop 9ed479c5a42f
Stop-Process -Name "Docker Desktop"