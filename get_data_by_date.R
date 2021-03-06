# Takes test month of data and splits it into multiple CSVs based on date

library(dplyr)
library(fasttime)
library(lubridate)

library(ggplot2)
library(plotly)

setwd("F:/CANVAS")
input_data_path <- "F:/05_Solar_Analytics/2021-05-31_CANVAS_Solar_Analytics_data/00_Raw_data_by_month/processed_unsw_202004_data_raw.csv"
output_data_path <- "F:/05_Solar_Analytics/2021-05-31_CANVAS_Solar_Analytics_data/00_Raw_data/"

# Import CSV
df <- read.csv(input_data_path)

# Fix timezones
df <- mutate(df, ts = fastPOSIXct(utc_tstamp, tz="Australia/Brisbane"))

df$date <- as.Date(df$ts, tz="Australia/Brisbane")
df <- df[order(df$ts),]

# Get list of unique data dates
list_data_dates <- c(unique(df$date))

# For each data date, filter the df and send to a csv
for (data_date in list_data_dates){
  # Filter df
  df_temp <- filter(df, date == data_date)
  # Get date as a string for the file name then print to csv
  data_date_name <- as.character(as.Date(data_date,format = "%Y-%m-%d", origin = "1970-01-01"))
  write.csv(df_temp, paste(output_data_path, data_date_name, '.csv', sep=''), row.names=FALSE)
  
}

# Weirdly stopped at 26 Sep - had to run remaining days 'semi manually'
# data_date <- "2019-09-30"
# df_temp <- filter(df, date == data_date)
# # Get date as a string for the file name then print to csv
# data_date_name <- as.character(as.Date(data_date,format = "%Y-%m-%d", origin = "1970-01-01"))
# write.csv(df_temp, paste(output_data_path, data_date_name, '.csv', sep=''), row.names=FALSE)

# Open data single day, filter for first c_id and plot
circuit_check <- read.csv("F:/05_Solar_Analytics/2021-05-24_sample_CANVAS_curtail_data_sept_2019/00_Raw_data/2019-09-03.csv")
circuit <- 923664764
circuit_check <- filter(circuit_check, c_id == circuit)
write.csv(circuit_check, paste(output_data_path, '460511237.csv', sep=''))

  