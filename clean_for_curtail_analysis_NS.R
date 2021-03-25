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
# source("aggregate_functions.R")
# source("upscale_function.R")
source("data_cleaning_functions.R")
# source("normalised_power_function.R")
# source("response_categorisation_function.R")
# source("distance_from_event.R")
# source("documentation.R")
# source("ideal_response_functions.R")

# Adding a for loop to do analysis for all 24 days of data
# data_date_list <- c("2018-01-16", "2018-01-19", "2018-02-02", "2018-02-04", "2018-03-09", "2018-03-31", 
#                     "2018-04-19", "2018-04-29", "2018-05-13", "2018-05-25", "2018-06-03", "2018-06-27", 
#                     "2018-07-10", "2018-07-18", "2018-08-22", "2018-08-25", "2018-09-04", "2018-09-10", 
#                     "2018-10-21", "2018-10-26", "2018-11-16", "2018-11-30", "2018-12-23", "2018-12-25")

data_date_list <- c("2018-12-25")

for (data_date in data_date_list){
  
  # Get input from GUI
  #data_date = "2018-12-25"
  time_series_file <- paste("F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/", data_date, ".csv", sep='')
  circuit_details_file <- "F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/circuit_details.csv"
  site_details_file <- "F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/site_details_renamed.csv"
  # #25th August data
  # time_series_file <- paste("F:/05_Solar_Analytics/2018-09-12_solar_analytics_transfer_to_aemo/2018-05-25_sa_qld_fault_aemo.csv", sep='')
  # circuit_details_file <- "F:/05_Solar_Analytics/2018-09-12_solar_analytics_transfer_to_aemo/circuit_details.csv"
  # site_details_file <- "F:/05_Solar_Analytics/2018-09-12_solar_analytics_transfer_to_aemo/sites_details.csv"
  #   region <- reactive({input$region})
  duration <- c("5","30","60")
  
  # This is the event that runs when the "Load data" button on the GUI is
  # Clicked. 
  duration_options <- c("5", "30", "60")
  ts_data <- read.csv(file=time_series_file, header=TRUE, stringsAsFactors = FALSE)

  # Data from CSV is assumed to need processing.
  if ('utc_tstamp' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("utc_tstamp"), c("ts"))}
  if ('t_stamp' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("t_stamp"), c("ts"))}
  if ('voltage' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("voltage"), c("v"))}
  if ('vrms' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("vrms"), c("v"))}
  if ('voltage_max' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("voltage_max"), c("v"))}
  if ('frequency' %in% colnames(ts_data)) {ts_data <- setnames(ts_data, c("frequency"), c("f"))}
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
  if ('State' %in% colnames(sd_data)) {sd_data <- setnames(sd_data, c("State"), c("s_state"))}
  if ('ac_rating_w'%in% colnames(sd_data)) {sd_data <- mutate(sd_data, ac_rating_w = ac_rating_w/1000)}
  if ('ac_rating_w'%in% colnames(sd_data)) {sd_data <- setnames(sd_data, c("ac_rating_w"), c("ac"))}
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
  combined_data <- select(combined_data, c_id, ts, v, f, d, site_id, e, con_type, s_state, s_postcode, 
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
  combined_data_clean_site_details <- select(combined_data_clean_site_details, c_id, ts, v, f, d, site_id, e, con_type, s_state, s_postcode, 
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
  combined_data_after_clean <- select(combined_data_after_clean, c_id, ts, v, f, d, site_id, e, con_type,
                                      s_state, s_postcode, Standard_Version, Grouping, polarity, first_ac,
                                      power_kW, reactive_power, clean, manufacturer, model, sum_ac, time_offset)
  combined_data <- rbind(combined_data, combined_data_after_clean)
  remove(combined_data_after_clean)
  
  print('yay')
  
  # Export csv
  path_out = "F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/"
  write.csv(combined_data, paste(path_out,data_date,'_cleaned_TEST_20_July_2020.csv',sep = ''), row.names=FALSE)
  
  # Also export circuit_details_for_editing which contains helpful stuff like energy_day and sunrise/sunset times
  write.csv(circuit_details_for_editing, paste(path_out, data_date, '_circuit_details_for_editing_cleaned_TEST_20_July_2020.csv', sep=""), row.names=FALSE)
    
}