@echo off
setlocal enabledelayedexpansion

set "SCRIPTS=plot_1_stacked_bars.py plot_2_queue.py plot_3_throught.py plot_4_certifycate.py plot_5.py"

for %%S in (%SCRIPTS%) do (
    echo(
    echo === Running %%S ===
    python "%%S"
    if errorlevel 1 (
        echo *** Script %%S failed with exit code !errorlevel! ***
        exit /b !errorlevel!
    )
)

echo(
echo All plot scripts completed successfully.
exit /b 0
