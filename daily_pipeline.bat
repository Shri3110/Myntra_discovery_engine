@echo off
echo ======================================================= >> "c:\Myntra discovery engine\pipeline_automation.log"
echo [%date% %time%] Starting automated daily pipeline... >> "c:\Myntra discovery engine\pipeline_automation.log"
cd "c:\Myntra discovery engine\phase_5_testing"
python run_pipeline.py >> "c:\Myntra discovery engine\pipeline_automation.log" 2>&1
echo [%date% %time%] Pipeline completed. >> "c:\Myntra discovery engine\pipeline_automation.log"
echo ======================================================= >> "c:\Myntra discovery engine\pipeline_automation.log"
