# CANVAS
(Curtailment and Network Voltage Analysis Study)

Currently, this repository contains code for cleaning then analysing Solar Analytics data to estimate PV curtailment due to over voltage tripping.
It requires 30s or 60s data from individual PV sites in the Solar Analytics format.

## 1. Data cleaning

Executed in R for consistency with disturbances analysis of Solar Analytics data undertaken by Nick Gorman and Taru Veijalainen.
See scripts:
* clean_for_curtail_analysis_NS.R
* data_cleaning_functions.R
* data_manipulation_functions.R

## 2.  Estimating curtailed PV generation (straight line method)

Executed in Python. Requires the output from step 1. Uses simple mathematical expressions and user-specified thresholds to identify periods of curtailment (near zero operation). Then draws a straight line between the start and end of the curtailment period and estimates the curtailed generation. See scripts:

* voltage_curtail.py
* util.py


## 3. Estimating curtailed PV generation *on clear sky days* (iterative polyfit method)

Executed in python. Requires the output from step 2. **Requires clear sky days to generate sensible outputs.**
Iteratively fits a polynomial to the PV profile to estimate clear sky output. Then estimates curtailed generation. See script:

* voltage_curtail_clear_sky_days.py

## 4. Plotting findings

Executed in python. Requires the output from stpe 3. Plots various findings including some parts of the method (refer to paper). See scripts:

* voltage_curtail_combined_analyis.py
* util.py
