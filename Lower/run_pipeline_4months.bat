@echo off
REM ============================================================
REM run_pipeline_4months.bat
REM Reruns the ENTIRE taxi analytics pipeline against all four
REM combined months (Jan-Apr 2026) instead of just January.
REM
REM THE ONLY REAL CHANGE vs. the original January-only run is the
REM -input path on the CLEANING job below: it now points at the
REM whole raw/CSV FOLDER instead of one filename. Hadoop Streaming
REM automatically treats every file in that folder as input, so
REM fhv_tripdata_2026-01/02/03/04.csv are all combined for free.
REM No mapper/reducer .py file needs to change for this.
REM ============================================================

REM ---- EDIT THESE TWO PATHS IF YOUR SETUP DIFFERS -------------
set HADOOP_JAR="C:\hadoop\share\hadoop\tools\lib\hadoop-streaming-3.4.3.jar"
set SCRIPTS="C:\Users\user\Desktop\Bigdata\Project\Lower"
REM --------------------------------------------------------------

REM This is the ONE line that combines the 4 months: a folder,
REM not a single filename. All 4 CSVs are already on HDFS.
set RAW_INPUT=/taxi_project/input/raw/CSV

echo ================================================================
echo Step 0: Clearing old outputs (Hadoop refuses to overwrite output dirs)
echo ================================================================
hdfs dfs -rm -r -f /taxi_project/input/cleaned
hdfs dfs -rm -r -f /taxi_project/output/hourly
hdfs dfs -rm -r -f /taxi_project/output/daily
hdfs dfs -rm -r -f /taxi_project/output/locations
hdfs dfs -rm -r -f /taxi_project/output/locations_topn
hdfs dfs -rm -r -f /taxi_project/output/routes
hdfs dfs -rm -r -f /taxi_project/output/routes_top20
hdfs dfs -rm -r -f /taxi_project/output/duration
hdfs dfs -rm -r -f /taxi_project/output/anomalies

echo ================================================================
echo Step 1: Cleaning job -- INPUT IS NOW THE FOLDER (all 4 months)
echo ================================================================
hadoop jar %HADOOP_JAR% ^
  -input %RAW_INPUT% ^
  -output /taxi_project/input/cleaned ^
  -mapper "python mapper_cleaning.py" ^
  -reducer "python reducer_cleaning.py" ^
  -file %SCRIPTS%\mapper_cleaning.py ^
  -file %SCRIPTS%\reducer_cleaning.py
if errorlevel 1 goto :error

echo ================================================================
echo Step 2: Hourly demand
echo ================================================================
hadoop jar %HADOOP_JAR% ^
  -input /taxi_project/input/cleaned ^
  -output /taxi_project/output/hourly ^
  -mapper "python mapper_hourly.py" ^
  -reducer "python reducer_hourly.py" ^
  -file %SCRIPTS%\mapper_hourly.py ^
  -file %SCRIPTS%\reducer_hourly.py
if errorlevel 1 goto :error

echo ================================================================
echo Step 3: Daily demand
echo ================================================================
hadoop jar %HADOOP_JAR% ^
  -input /taxi_project/input/cleaned ^
  -output /taxi_project/output/daily ^
  -mapper "python mapper_daily.py" ^
  -reducer "python reducer_daily.py" ^
  -file %SCRIPTS%\mapper_daily.py ^
  -file %SCRIPTS%\reducer_daily.py
if errorlevel 1 goto :error

echo ================================================================
echo Step 4: Pickup zone ranking -- Job 1 (counts)
echo ================================================================
hadoop jar %HADOOP_JAR% ^
  -input /taxi_project/input/cleaned ^
  -output /taxi_project/output/locations ^
  -mapper "python mapper_location.py" ^
  -reducer "python reducer_location.py" ^
  -file %SCRIPTS%\mapper_location.py ^
  -file %SCRIPTS%\reducer_location.py
if errorlevel 1 goto :error

echo ================================================================
echo Step 5: Pickup zone ranking -- Job 2 (Top/Bottom 10)
echo ================================================================
hadoop jar %HADOOP_JAR% ^
  -input /taxi_project/output/locations ^
  -output /taxi_project/output/locations_topn ^
  -mapper "python mapper_topn.py" ^
  -reducer "python reducer_topn.py" ^
  -file %SCRIPTS%\mapper_topn.py ^
  -file %SCRIPTS%\reducer_topn.py
if errorlevel 1 goto :error

echo ================================================================
echo Step 6: Route ranking -- Job 1 (counts)
echo ================================================================
hadoop jar %HADOOP_JAR% ^
  -input /taxi_project/input/cleaned ^
  -output /taxi_project/output/routes ^
  -mapper "python mapper_route.py" ^
  -reducer "python reducer_route.py" ^
  -file %SCRIPTS%\mapper_route.py ^
  -file %SCRIPTS%\reducer_route.py
if errorlevel 1 goto :error

echo ================================================================
echo Step 7: Route ranking -- Job 2 (Top 20) -- mapper_topn.py reused
echo ================================================================
hadoop jar %HADOOP_JAR% ^
  -input /taxi_project/output/routes ^
  -output /taxi_project/output/routes_top20 ^
  -mapper "python mapper_topn.py" ^
  -reducer "python reducer_route_topn.py" ^
  -file %SCRIPTS%\mapper_topn.py ^
  -file %SCRIPTS%\reducer_route_topn.py
if errorlevel 1 goto :error

echo ================================================================
echo Step 8: Trip duration analysis
echo ================================================================
hadoop jar %HADOOP_JAR% ^
  -input /taxi_project/input/cleaned ^
  -output /taxi_project/output/duration ^
  -mapper "python mapper_duration.py" ^
  -reducer "python reducer_duration.py" ^
  -file %SCRIPTS%\mapper_duration.py ^
  -file %SCRIPTS%\reducer_duration.py
if errorlevel 1 goto :error

echo ================================================================
echo Step 9: Anomaly detection
echo ================================================================
hadoop jar %HADOOP_JAR% ^
  -input /taxi_project/input/cleaned ^
  -output /taxi_project/output/anomalies ^
  -mapper "python mapper_anomaly.py" ^
  -reducer "python reducer_anomaly.py" ^
  -file %SCRIPTS%\mapper_anomaly.py ^
  -file %SCRIPTS%\reducer_anomaly.py
if errorlevel 1 goto :error

echo ================================================================
echo Step 10: Pull every output part-00000 back to local disk
echo ================================================================
set RESULTS=C:\Users\user\Desktop\Bigdata\Results
del /q %RESULTS%\daily.tsv 2>nul
del /q %RESULTS%\locations.tsv 2>nul
del /q %RESULTS%\locations_topn.tsv 2>nul
del /q %RESULTS%\routes.tsv 2>nul
del /q %RESULTS%\routes_top20.tsv 2>nul
del /q %RESULTS%\duration.tsv 2>nul
del /q %RESULTS%\anomalies.tsv 2>nul
del /q %RESULTS%\hourly.tsv 2>nul

hdfs dfs -get /taxi_project/output/hourly/part-00000 %RESULTS%\hourly.tsv
hdfs dfs -get /taxi_project/output/daily/part-00000 %RESULTS%\daily.tsv
hdfs dfs -get /taxi_project/output/locations/part-00000 %RESULTS%\locations.tsv
hdfs dfs -get /taxi_project/output/locations_topn/part-00000 %RESULTS%\locations_topn.tsv
hdfs dfs -get /taxi_project/output/routes/part-00000 %RESULTS%\routes.tsv
hdfs dfs -get /taxi_project/output/routes_top20/part-00000 %RESULTS%\routes_top20.tsv
hdfs dfs -get /taxi_project/output/duration/part-00000 %RESULTS%\duration.tsv
hdfs dfs -get /taxi_project/output/anomalies/part-00000 %RESULTS%\anomalies.tsv

echo ================================================================
echo DONE. All 4 months combined and reprocessed. Results in %RESULTS%
echo ================================================================
goto :eof

:error
echo.
echo *** A job failed (see above). Fix the error, then rerun this script. ***
exit /b 1
