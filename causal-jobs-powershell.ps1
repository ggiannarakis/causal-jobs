Start-Transcript 'C:\Users\ggian\Documents\git-repos\causal-jobs\daily_job_log.txt' -Append
cd 'C:\Program Files\Docker\Docker'
start 'Docker Desktop.exe'
Start-Sleep -Seconds 60
docker start 9ed479c5a42f
cd C:\Users\ggian\Documents\git-repos\causal-jobs
conda activate gmailapi
python load.py
python send_email.py
docker stop 9ed479c5a42f
Stop-Process -Name "Docker Desktop"
Stop-Transcript