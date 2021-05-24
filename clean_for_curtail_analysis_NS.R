##COPY of Rshiny app adapted for data cleaning only
#library (shiny)
library(shinyTime)
library(shinyWidgets)
library(shinyalert)
library(plotly)
library(feather)
library(lubridate)
library(dplyr)
library(tidyr)
library(data.table)
library(shinycssloaders)
library(shinyFiles)
library(shinyjs)
library(stringr)
library(fasttime)
library(DT)
library(suncalc)
library(ggmap)
library(measurements)
library(assertthat)
library(geosphere)
library(swfscMisc)
library(padr)
source("data_manipulation_functions.R")
source("data_cleaning_functions.R")

setwd("F:/CANVAS")

# Adding a for loop to do analysis for data
data_date_list <- c("2019-09-01", "2019-09-02", "2019-09-03", "2019-09-04", "2019-09-05", "2019-09-06",
                    "2019-09-07", "2019-09-08", "2019-09-09", "2019-09-10", "2019-09-11", "2019-09-12",
                    "2019-09-13", "2019-09-14", "2019-09-15", "2019-09-16", "2019-09-17", "2019-09-18",
                    "2019-09-19", "2019-09-20", "2019-09-21", "2019-09-22", "2019-09-23", "2019-09-24",
                    "2019-09-25", "2019-09-26", "2019-09-27", "2019-09-28", "2019-09-29", "2019-09-30")
# For testing
data_date_list <- c("2019-09-18")

for (data_date in data_date_list){
  
  # Get input from GUI
  time_series_file <- paste("F:/05_Solar_Analytics/2021-05-24_sample_CANVAS_curtail_data_sept_2019/00_Raw_data/", data_date, ".csv", sep='')
  circuit_details_file <- "F:/05_Solar_Analytics/2021-05-24_sample_CANVAS_curtail_data_sept_2019/00_Raw_data/unsw_20190701_circuit_details.csv"
  site_details_file <- "F:/05_Solar_Analytics/2021-05-24_sample_CANVAS_curtail_data_sept_2019/00_Raw_data/unsw_20190701_site_details.csv"
  duration <- c("5","30","60")
  
  # This is the event that runs when the "Load data" button on the GUI is
  # Clicked. 
  duration_options <- c("5", "30", "60")
  ts_data <- read.csv(file=time_series_file, header=TRUE, stringsAsFactors = FALSE)
  
  # Drop ts and date columns (added when separating the data into individual date files)
  ts_data <- select(ts_data, c_id, utc_tstamp, energy, power, reactive_power, voltage, duration)

  # Data from CSV is assumed to need processing.
  if ('utc_tstamp' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("utc_tstamp"), c("ts"))}
  if ('t_stamp' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("t_stamp"), c("ts"))}
  if ('voltage' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("voltage"), c("v"))}
  if ('vrms' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("vrms"), c("v"))}
  if ('voltage_max' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("voltage_max"), c("v"))}
  if ('reactive_power' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("reactive_power"), c("reactive_power"))}
  if ('energy' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("energy"), c("e"))}
  if ('duration' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("duration"), c("d"))}
  time_series_data <- ts_data
  time_series_data <- time_series_data %>% distinct(c_id, ts, .keep_all=TRUE)
  time_series_data <- mutate(time_series_data, c_id = as.character(c_id))
  time_series_data <- process_raw_time_series_data(time_series_data)
  # Filter for duration
  duration_sample_sizes <- get_duration_sample_counts(time_series_data, duration_options)
  time_series_data <- filter(time_series_data, d==duration)
  
  # The circuit details file requires no processing and is small so always 
  # load from CSV.
  circuit_details <- read.csv(file=circuit_details_file, header=TRUE, stringsAsFactors = FALSE)
  circuit_details <- select(circuit_details, c_id, site_id, con_type, polarity)
  circuit_details <- circuit_details %>% mutate(site_id = as.character(site_id))
  circuit_details <- circuit_details %>% mutate(c_id = as.character(c_id))
  
  # Load site details data.
  sd_data <- read.csv(file=site_details_file, header=TRUE, stringsAsFactors = FALSE)
  # Add s_state column to avoid errors
  sd_data$s_state <- "SA"
  if ('State' %in% colnames(sd_data)) {sd_data <- setnames(sd_data, c("State"), c("s_state"))}
  if ('ac_cap_w'%in% colnames(sd_data)) {sd_data <- mutate(sd_data, ac_cap_w = ac_cap_w/1000)}
  if ('ac_cap_w'%in% colnames(sd_data)) {sd_data <- setnames(sd_data, c("ac_cap_w"), c("ac"))}
  if ('dc_cap_w' %in% colnames(sd_data)) {sd_data <- mutate(sd_data, dc_cap_w = dc_cap_w/1000)}
  if ('dc_cap_w' %in% colnames(sd_data)) {sd_data <- setnames(sd_data, c("dc_cap_w"), c("dc"))}
  if ('AC.Rating.kW.' %in% colnames(sd_data)) {sd_data <- setnames(sd_data, c("AC.Rating.kW."), c("ac"))}
  if ('DC.Rating.kW.' %in% colnames(sd_data)) {sd_data <- mutate(sd_data, DC.Rating.kW.=DC.Rating.kW.*1000)}
  if ('DC.Rating.kW.' %in% colnames(sd_data)) {sd_data <- setnames(sd_data, c("DC.Rating.kW."), c("dc"))}
  if ('inverter_manufacturer' %in% colnames(sd_data)) {
      sd_data <- setnames(sd_data, c("inverter_manufacturer"), c("manufacturer"))
  }
  if ('inverter_model' %in% colnames(sd_data)) {sd_data <- setnames(sd_data, c("inverter_model"), c("model"))}
  site_details_raw <- sd_data
  site_details_raw <- site_details_raw %>% mutate(site_id = as.character(site_id))
  # Older site details proided the day of installation not just the month. We 
  # change the name of the column to match the new format which is just by 
  # month but keep the original info regarding the date.
  if("pv_install_date" %in% colnames(site_details_raw)){
      site_details_raw <- setnames(site_details_raw, c("pv_install_date"),
                      c("pv_installation_year_month"))
  }
  # Data from CSV is assumed to need processing.
  site_details <- process_raw_site_details(site_details_raw)
  
  # Load postcode lat and long data
  postcode_data_file <- "PostcodesLatLongQGIS.csv"
  postcode_data <- read.csv(file=postcode_data_file, header=TRUE, stringsAsFactors = FALSE)
  postcode_data <- process_postcode_data(postcode_data)
        
  # Perform data, processing and combine data table into a single data frame
  combined_data <- combine_data_tables(time_series_data, circuit_details, site_details)
  # Get the number of sites at this stage. Note, this should be the same as for completely uncleaned data.
  
  combined_data <- combined_data %>% mutate(clean="raw")
  combined_data <- select(combined_data, c_id, ts, v, d, site_id, e, con_type, s_state, s_postcode, 
                          Standard_Version, Grouping, polarity, first_ac,power_kW, reactive_power, clean, manufacturer, model, 
                          sum_ac, time_offset)
        
  # Clean site details data
  site_details_cleaned <- site_details_data_cleaning(combined_data, site_details_raw)
  site_details_cleaned <- site_details_cleaned[order(site_details_cleaned$site_id),]
  # Next make sure the site_details are processed before trying to do the clean. Need first_ac in kW (not W)
  site_details_cleaned_processed <- process_raw_site_details(site_details_cleaned)
  # Also need to get a new version of combined_data as an input to clean_connection_types to ensure the first_ac is in kW (not W)
  combined_data_clean_site_details <- combine_data_tables(time_series_data, circuit_details, site_details_cleaned_processed)
  combined_data_clean_site_details <- combined_data_clean_site_details %>% mutate(clean="raw")
  combined_data_clean_site_details <- select(combined_data_clean_site_details, c_id, ts, v, d, site_id, e, con_type, s_state, s_postcode, 
                          Standard_Version, Grouping, polarity, first_ac,power_kW, reactive_power, clean, manufacturer, model, 
                          sum_ac, time_offset)
  # Clean circuit details file
  circuit_details_for_editing <- clean_connection_types(combined_data_clean_site_details, circuit_details, postcode_data)
  
  # Add cleaned data to display data for main tab
  combined_data_after_clean <- combine_data_tables(time_series_data, circuit_details_for_editing, 
                                                      site_details_cleaned_processed)
  remove(time_series_data)
  combined_data <- filter(combined_data, clean=="raw")
  combined_data_after_clean <- combined_data_after_clean %>% mutate(clean="cleaned")
  combined_data_after_clean <- select(combined_data_after_clean, c_id, ts, v, d, site_id, e, con_type,
                                      s_state, s_postcode, Standard_Version, Grouping, polarity, first_ac,
                                      power_kW, reactive_power, clean, manufacturer, model, sum_ac, time_offset)
  combined_data <- rbind(combined_data, combined_data_after_clean)
  remove(combined_data_after_clean)
  
  print('yay')
  
  # Export csv
  path_out = "F:/05_Solar_Analytics/2021-05-24_sample_CANVAS_curtail_data_sept_2019/01_Cleaned_data/"
  write.csv(combined_data, paste(path_out,data_date,'_cleaned.csv',sep = ''), row.names=FALSE)
  
  # Also export circuit_details_for_editing which contains helpful stuff like energy_day and sunrise/sunset times
  write.csv(circuit_details_for_editing, paste(path_out, data_date, '_circuit_details_for_editing_cleaned.csv', sep=""), row.names=FALSE)
    
}