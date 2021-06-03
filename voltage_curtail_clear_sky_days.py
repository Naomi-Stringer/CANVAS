# Gets PV curtailment estimate using a polynomial fit method with an iterative step to remove 'outliers'
# (only really useful for clear sky days! Otherwise the straight line approximation is preferable!!)
# See write up of method for key limitations and next steps

#------------------------ Step 0: Import required packages ------------------------
# Import packages required for program
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import seaborn as sns; sns.set()
# For graphing time series
time_fmt = mdates.DateFormatter('%H:%M')

# Inputs
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
data_date_list = ["2019-09-01", "2019-09-02", "2019-09-03", "2019-09-04", "2019-09-05", "2019-09-06",
                  "2019-09-07", "2019-09-08", "2019-09-09", "2019-09-10", "2019-09-11", "2019-09-12",
                  "2019-09-13", "2019-09-14", "2019-09-15", "2019-09-16", "2019-09-17", "2019-09-18",
                  "2019-09-19", "2019-09-20", "2019-09-21", "2019-09-22", "2019-09-23", "2019-09-24",
                  "2019-09-25", "2019-09-26", "2019-09-27", "2019-09-28", "2019-09-29", "2019-09-30",
                    "2019-07-02","2019-07-03","2019-07-04","2019-07-05", #"2019-07-01",
                    "2019-07-06","2019-07-07","2019-07-08","2019-07-09","2019-07-10",
                    "2019-07-11","2019-07-12","2019-07-13","2019-07-14","2019-07-15",
                    "2019-07-16","2019-07-17","2019-07-18","2019-07-19","2019-07-20",
                    "2019-07-21","2019-07-22","2019-07-23","2019-07-24","2019-07-25",
                    "2019-07-26","2019-07-27","2019-07-28","2019-07-29","2019-07-30",
                    "2019-07-31","2019-08-02","2019-08-03","2019-08-04", #"2019-08-01",
                    "2019-08-05","2019-08-06","2019-08-07","2019-08-08","2019-08-09",
                    "2019-08-10","2019-08-11","2019-08-12","2019-08-13","2019-08-14",
                    "2019-08-15","2019-08-16","2019-08-17","2019-08-18","2019-08-19",
                    "2019-08-20","2019-08-21","2019-08-22","2019-08-23","2019-08-24",
                    "2019-08-25","2019-08-26","2019-08-27","2019-08-28","2019-08-29",#removed september!
                    "2019-08-30","2019-08-31","2019-10-02","2019-10-03", #"2019-10-01",
                    "2019-10-04","2019-10-05","2019-10-06","2019-10-07","2019-10-08",
                    "2019-10-09","2019-10-10","2019-10-11","2019-10-12","2019-10-13",
                    "2019-10-14","2019-10-15","2019-10-16","2019-10-17","2019-10-18",
                    "2019-10-19","2019-10-20","2019-10-21","2019-10-22","2019-10-23",
                    "2019-10-24","2019-10-25","2019-10-26","2019-10-27","2019-10-28",
                    "2019-10-29","2019-10-30","2019-10-31","2019-11-02", #"2019-11-01",
                    "2019-11-03","2019-11-04","2019-11-05","2019-11-06","2019-11-07",
                    "2019-11-08","2019-11-09","2019-11-10","2019-11-11","2019-11-12",
                    "2019-11-13","2019-11-14","2019-11-15","2019-11-16","2019-11-17",
                    "2019-11-18","2019-11-19","2019-11-20","2019-11-21","2019-11-22",
                    "2019-11-23","2019-11-24","2019-11-25","2019-11-26","2019-11-27",
                    "2019-11-28","2019-11-29","2019-11-30","2019-12-02", #"2019-12-01",
                    "2019-12-03","2019-12-04","2019-12-05","2019-12-06","2019-12-07",
                    "2019-12-08","2019-12-09","2019-12-10","2019-12-11","2019-12-12",
                    "2019-12-13","2019-12-14","2019-12-15","2019-12-16","2019-12-17",
                    "2019-12-18","2019-12-19","2019-12-20","2019-12-21","2019-12-22",
                    "2019-12-23","2019-12-24","2019-12-25","2019-12-26","2019-12-27",
                    "2019-12-28","2019-12-29","2019-12-30","2019-12-31", #"2020-01-01",
                    "2020-01-02","2020-01-03","2020-01-04","2020-01-05","2020-01-06",
                    "2020-01-07","2020-01-08","2020-01-09","2020-01-10","2020-01-11",
                    "2020-01-12","2020-01-13","2020-01-14","2020-01-15","2020-01-16",
                    "2020-01-17","2020-01-18","2020-01-19","2020-01-20","2020-01-21",
                    "2020-01-22","2020-01-23","2020-01-24","2020-01-25","2020-01-26",
                    "2020-01-27","2020-01-28","2020-01-29","2020-01-30","2020-01-31",
                    "2020-02-02","2020-02-03","2020-02-04","2020-02-05", #"2020-02-01",
                    "2020-02-06","2020-02-07","2020-02-08","2020-02-09","2020-02-10",
                    "2020-02-11","2020-02-12","2020-02-13","2020-02-14","2020-02-15",
                    "2020-02-16","2020-02-17","2020-02-18","2020-02-19","2020-02-20",
                    "2020-02-21","2020-02-22","2020-02-23","2020-02-24","2020-02-25",
                    "2020-02-26","2020-02-27","2020-02-28","2020-02-29",# "2020-03-01",
                    "2020-03-02","2020-03-03","2020-03-04","2020-03-05","2020-03-06",
                    "2020-03-07","2020-03-08","2020-03-09","2020-03-10","2020-03-11",
                    "2020-03-12","2020-03-13","2020-03-14","2020-03-15","2020-03-16",
                    "2020-03-17","2020-03-18","2020-03-19","2020-03-20","2020-03-21",
                    "2020-03-22","2020-03-23","2020-03-24","2020-03-25","2020-03-26",
                    "2020-03-27","2020-03-28","2020-03-29","2020-03-30","2020-03-31",
                    "2020-04-02","2020-04-03","2020-04-04","2020-04-05", #"2020-04-01",
                    "2020-04-06","2020-04-07","2020-04-08","2020-04-09","2020-04-10",
                    "2020-04-11","2020-04-12","2020-04-13","2020-04-14","2020-04-15",
                    "2020-04-16","2020-04-17","2020-04-18","2020-04-19","2020-04-20",
                    "2020-04-21","2020-04-22","2020-04-23","2020-04-24","2020-04-25",
                    "2020-04-26","2020-04-27","2020-04-28","2020-04-29","2020-04-30"]


# Data files are located here:
INPUT_DATA_FILE_PATH = 'F:/05_Solar_Analytics/2021-05-31_CANVAS_Solar_Analytics_data/02_Curtail_output/'
OUTPUT_FILE_PATH = "F:/05_Solar_Analytics/2021-05-31_CANVAS_Solar_Analytics_data/03_Polyfit_output/"

# File names are here:
TS_DATA_FILE_PATH = '_analysis_profiles_v4.csv'
SUM_STATS_DATA_FILE_PATH = "_analysis_sum_stats_v4.csv"
OUTPUT_PROFILES = "_analysis_profiles_polyfit_v4.csv"
OUTPUT_SUM_STATS = "_analysis_sum_stats_polyfit_v4.csv"

# File path for clear sky days csv
CLEAR_SKY_DAYS_FILE_PATH = 'F:/CANVAS/clear_sky_days_01-2019_07-2020_manual.csv'

# This value is used to remove data points when calculating the polynomial.
# The first polynomial uses all non zero cf values.
# Then the straight line correlation between polyfit and actual cf is calculated and residuals found for each cf
# Data points with residuals greater than or less than the allowed residual band are removed and
# the polynomial fit is recalculated using this smaller subset of points: 'polyfit_iter'
allowed_residual_band = 0.05 # NOTE - set to 0.05 after some sensitivity testing and eye balling
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

for data_date in data_date_list:
    # Load PV profiles
    data_df = pd.read_csv(INPUT_DATA_FILE_PATH + data_date + TS_DATA_FILE_PATH, index_col = 't_stamp', parse_dates=True)
    # Load clear sky days CSV and flag NON clear sky days in data_df
    clear_sky_days_df = pd.read_csv(CLEAR_SKY_DAYS_FILE_PATH)
    clear_sky_days_list = clear_sky_days_df['clear_sky_days'].astype(str).tolist()
    if data_date in clear_sky_days_list:
        data_df['non_clear_sky_day_flag'] = 0
    else:
        data_df['non_clear_sky_day_flag'] = 1

    # Get list of c_ids
    c_id_list = data_df['c_id'].drop_duplicates().tolist()
    # Set up output_df
    output_df = pd.DataFrame()
    output_df.index.name = 't_stamp'
    counter = 0

    for c_id in c_id_list:
        perc_complete = counter / len(c_id_list)
        print(perc_complete)
        counter += 1

        # Filter for c_id
        pv_data = data_df[data_df['c_id'] == c_id]
        pv_data['t_stamp_copy'] = pv_data.index

        # First get time in seconds for polyfit
        pv_data['hrs'] = pv_data.index.hour
        pv_data['min'] = pv_data.index.minute
        pv_data['sec'] = pv_data.index.second
        pv_data['time_in_seconds'] = pv_data['hrs'] * 60 * 60 + pv_data['min'] * 60 + pv_data['sec']

        # Try applying a 2nd order polynomial **to non-zero cf points only**
        # Needs to be 'try' because if there are ONLY zero points then error b/c we pass an empty df to polyfit function
        try:
            test = pv_data[pv_data['cf']>0]
            x = test['time_in_seconds']
            y = test['cf']
            z = np.polyfit(x,y,2)

            # Calc the fitted line
            test['polynomial_fit'] = z[0]*test['time_in_seconds']*test['time_in_seconds'] + \
                                            z[1]*test['time_in_seconds'] + z[2]
            # This is calculated for all times (not just non zero) as well for printing / checking
            pv_data['polynomial_fit'] = z[0]*pv_data['time_in_seconds']*pv_data['time_in_seconds'] + \
                                            z[1]*pv_data['time_in_seconds'] + z[2]

            # Get the correlation between my polynomial and the cf data (excluding zeroes) then remove points with
            # 'large' residuals
            # Get line of best fit
            test['ones'] = 1
            A = test[['cf', 'ones']]
            y = test['polynomial_fit']
            m,c = np.linalg.lstsq(A,y)[0]
            test['y_line'] = c + m*test['cf']

            # Remove data points where the residual is +/- allowed_residual_band from the line of best fit
            # (in an attempt to improve our correlation)
            test['residuals'] = test['polynomial_fit'] - test['y_line']
            test_filtered = test[test['residuals'].abs() <= allowed_residual_band]

            # Use this filtered curve to get a new polyfit
            x = test_filtered['time_in_seconds']
            y = test_filtered['cf']
            z = np.polyfit(x,y,2)

            test_filtered['polynomial_fit'] = z[0]*test_filtered['time_in_seconds']*test_filtered['time_in_seconds'] + \
                                              z[1]*test_filtered['time_in_seconds'] + z[2]
            pv_data['polyfit_iter'] = z[0]*pv_data['time_in_seconds']*pv_data['time_in_seconds'] + \
                                            z[1]*pv_data['time_in_seconds'] + z[2]
            # Where there is est_cf (i.e. it's identified as a period of curtailment and so we have a straight line
            # estimate) then use est_cf_polyfit_iter
            pv_data['est_cf_polyfit_iter'] = np.nan
            pv_data.loc[pv_data['est_cf']>0, 'est_cf_polyfit_iter'] = pv_data['polyfit_iter']

            # Just keep the polyfit_iter for the periods where there was already a straight line estimate as above
            pv_data = pv_data.drop(['polynomial_fit'], axis=1)

            # Get est kW and est kWh
            pv_data['est_kW_polyfit_iter'] = pv_data['est_cf_polyfit_iter'] * pv_data['ac']
            pv_data['est_kWh_polyfit_iter'] = pv_data['est_cf_polyfit_iter'] * \
                                              pv_data['ac'] * pv_data['duration'] / (60 * 60)
            # Get power lost estimate
            pv_data['gen_loss_est_kWh_polyfit_iter'] = pv_data['est_kWh_polyfit_iter'] - pv_data['gen_kWh']
            # Issue is that we don't want gen lost to be less than zero!
            pv_data.loc[pv_data['gen_loss_est_kWh_polyfit_iter'] < 0, 'gen_loss_est_kWh_polyfit_iter'] = 0

        except:
            print('Error somewhere in the polyfit process for c_id ' + str(c_id))

        # --------------------------------- concat onto output_df
        output_df = pd.concat([output_df, pv_data])

    # *********************************** CHECKS and identify 'preferred' method ***********************************
    # Check on polyfit giving large cfs (>=1) --> allowed if the cf for that c_id is already large
    # For each c_id get max polyfit and max cf
    cf_max_check = pd.DataFrame({'cf_max' : output_df.groupby('c_id')['cf'].max(),
                                 'polyfit_iter_cf_max' : output_df.groupby('c_id')['est_cf_polyfit_iter'].max(),
                                 'site_id' : output_df.groupby('c_id')['site_id'].first()})
    # Find cases where straight line and polyfit iter methods return cf >= 1
    cf_max_check['straight_line_max_greater_or_equal_1'] = np.nan
    cf_max_check.loc[cf_max_check['cf_max'] >= 1, 'straight_line_max_greater_or_equal_1'] = 1
    cf_max_check['polyfit_iter_max_greater_or_equal_1'] = np.nan
    cf_max_check.loc[cf_max_check['polyfit_iter_cf_max'] >= 1, 'polyfit_iter_max_greater_or_equal_1'] = 1
    # Flag cases where straight line method must be used. i.e. the polyfit iter cf max is  >= 1, but straight line cf max is not.
    cf_max_check = cf_max_check.fillna(0)
    cf_max_check['must_use_straight_line_method_due_to_cf_max'] = cf_max_check['polyfit_iter_max_greater_or_equal_1'] - cf_max_check['straight_line_max_greater_or_equal_1']
    cf_max_check.loc[cf_max_check['must_use_straight_line_method_due_to_cf_max'] < 0, 'must_use_straight_line_method_due_to_cf_max'] = 0
    # Get new df by site_id in order to merge onto output_df
    cf_max_check_by_site_id = pd.DataFrame({'must_use_straight_line_method_due_to_cf_max' : cf_max_check.groupby('site_id')['must_use_straight_line_method_due_to_cf_max'].max()})

    # Check whether the straight line or polyfit iter gives a larger total generation lost.
    # We want to take the larger of the two.
    gen_loss_total_check = pd.DataFrame({'straight_line_gen_loss_total' : output_df.groupby('site_id')['gen_loss_est_kWh'].sum(),
                                         'polyfit_iter_gen_loss_total' : output_df.groupby('site_id')['gen_loss_est_kWh_polyfit_iter'].sum()})
    gen_loss_total_check['must_use_straight_line_method_due_to_gen_loss_total'] = np.nan
    gen_loss_total_check.loc[gen_loss_total_check['straight_line_gen_loss_total'] > gen_loss_total_check['polyfit_iter_gen_loss_total'], 'must_use_straight_line_method_due_to_gen_loss_total'] = 1
    gen_loss_total_check = gen_loss_total_check.fillna(0)
    gen_loss_total_check = gen_loss_total_check[['must_use_straight_line_method_due_to_gen_loss_total']]

    # Merge both checks back onto output_df and create a single column: use straight line estimate over polyfit iter? Y/N
    output_df = output_df.merge(cf_max_check_by_site_id, left_on='site_id', right_index=True, how='left')
    output_df = output_df.merge(gen_loss_total_check, left_on='site_id', right_index=True, how='left')
    # Get flag if either conditions are true
    # OR if not a clear sky day
    output_df['use_straight_line_method_flag'] = output_df['must_use_straight_line_method_due_to_gen_loss_total'] + output_df['must_use_straight_line_method_due_to_cf_max'] + output_df['non_clear_sky_day_flag']
    output_df.loc[output_df['use_straight_line_method_flag'] > 1, 'use_straight_line_method_flag'] = 1
    output_df['use_polyfit_iter_method_flag'] = 1 - output_df['use_straight_line_method_flag']

    # Set the preferred est_cf_preferred etc to the polyfit method, unless the straight line flag is present,
    # in which case use the straight line method
    output_df['est_cf_preferred'] = (output_df['est_cf_polyfit_iter'] * output_df['use_polyfit_iter_method_flag']) + (output_df['est_cf'] * output_df['use_straight_line_method_flag'])
    output_df['est_kW_preferred'] = (output_df['est_kW_polyfit_iter'] * output_df['use_polyfit_iter_method_flag']) + (output_df['est_kW'] * output_df['use_straight_line_method_flag'])
    output_df['est_kWh_preferred'] = (output_df['est_kWh_polyfit_iter'] * output_df['use_polyfit_iter_method_flag']) + (output_df['est_kWh'] * output_df['use_straight_line_method_flag'])
    output_df['gen_loss_est_kWh_preferred'] = (output_df['gen_loss_est_kWh_polyfit_iter'] * output_df['use_polyfit_iter_method_flag']) + (output_df['gen_loss_est_kWh'] * output_df['use_straight_line_method_flag'])

    # Optional save data to csv
    output_df.to_csv(OUTPUT_FILE_PATH + data_date + OUTPUT_PROFILES)

    # --------------------------------- Summary stuff
    # Calc the new generation lost amount by site and also get the max for checking that polyfit doesn't go above 1
    # Also add the reason for selecting polyfit or linear estimate
    new_gen_lost = pd.DataFrame({ 'gen_loss_est_kWh_polyfit_iter' : output_df.groupby('site_id')['gen_loss_est_kWh_polyfit_iter'].sum(),
                                  'gen_loss_est_kWh_preferred' : output_df.groupby('site_id')['gen_loss_est_kWh_preferred'].sum(),
                                  'linear_method_preferred' : output_df.groupby('site_id')['use_straight_line_method_flag'].max(),
                                  'polyfit_method_preferred' : output_df.groupby('site_id')['use_polyfit_iter_method_flag'].max()})

    # Open previous sum stats
    sum_stats_df = pd.read_csv(INPUT_DATA_FILE_PATH + data_date + SUM_STATS_DATA_FILE_PATH)

    # Append on the new gen lost
    sum_stats_df = sum_stats_df.merge(new_gen_lost, left_on='site_id', right_index=True)

    # Calc percentage of gen lost using polyfit iter and preferred
    sum_stats_df['percentage_lost_polyfit_iter'] = sum_stats_df['gen_loss_est_kWh_polyfit_iter'].abs() / (sum_stats_df['gen_loss_est_kWh_polyfit_iter'].abs() + sum_stats_df['gen_kWh'].abs())
    sum_stats_df['percentage_lost_preferred'] = sum_stats_df['gen_loss_est_kWh_preferred'].abs() / (sum_stats_df['gen_loss_est_kWh_preferred'].abs() + sum_stats_df['gen_kWh'].abs())

    # Get proportion of sites for graphing using polyfit iter and preferred
    sum_stats_df = sum_stats_df.sort_values('percentage_lost_polyfit_iter', ascending =False)
    sum_stats_df['proportion_of_sites_polyfit_iter'] = range(len(sum_stats_df))
    sum_stats_df['proportion_of_sites_polyfit_iter'] = (sum_stats_df['proportion_of_sites_polyfit_iter'] + 1) / len(sum_stats_df)
    # Preferred
    sum_stats_df = sum_stats_df.sort_values('percentage_lost_preferred', ascending =False)
    sum_stats_df['proportion_of_sites_preferred'] = range(len(sum_stats_df))
    sum_stats_df['proportion_of_sites_preferred'] = (sum_stats_df['proportion_of_sites_preferred'] + 1) / len(sum_stats_df)

    # Save summary statistics to  csv
    sum_stats_df.to_csv(OUTPUT_FILE_PATH + data_date + OUTPUT_SUM_STATS)