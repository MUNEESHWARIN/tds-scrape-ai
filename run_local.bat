
@echo off
echo Starting TDS Virtual TA...

echo Installing dependencies...
pip install -r requirements.txt

echo Running scraper...
python scraper.py

echo Starting Flask app...
echo API will be available at: http://localhost:5000
python app.py

pause