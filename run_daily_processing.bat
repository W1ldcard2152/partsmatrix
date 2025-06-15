@echo off 
echo Running daily consensus processing... 
python manage.py process_consensus_fitments --new-data-only 
python manage.py consensus_quality_analysis --export-json --output-dir ./daily_reports 
echo Daily processing complete! 
pause 
