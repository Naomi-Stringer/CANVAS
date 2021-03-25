# Estimates volume of PV generation being curtailed due to over voltage

#------------------------ Step 0: Import required packages ------------------------
# Import packages required for program
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import calendar
import seaborn as sns
import itertools
import datetime
from time import gmtime, strftime

import util

# Inputs
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 24 days for curtail analysis
# DATA_DATE = '2018-01-16'
data_date_list = ["2018-01-16", "2018-01-19", "2018-02-02", "2018-02-04", "2018-03-09", "2018-03-31", 
                    "2018-04-19", "2018-04-29", "2018-05-13", "2018-05-25", "2018-06-03", "2018-06-27", 
                    "2018-07-10", "2018-07-18", "2018-08-22", "2018-08-25", "2018-09-04", "2018-09-10", 
                    "2018-10-21", "2018-10-26", "2018-11-16", "2018-11-30", "2018-12-23", "2018-12-25"]

TS_DATA_FILE_NAME_FULL = "_analysis_profiles_FULL_DETAIL_v4.csv"
TS_DATA_FILE_NAME = "_analysis_profiles_v4.csv"
SUM_STATS_DATA_FILE_NAME = "_analysis_sum_stats_v4.csv"

print(data_date_list)

for DATA_DATE in data_date_list:

    # With external cleaning
    COMBINED_DATA_FILE_PATH = 'F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/' + DATA_DATE + '_cleaned.csv'
    CIRCUIT_DETAILS_FOR_EDITING_FILE_PATH = 'F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/' + DATA_DATE + '_circuit_details_for_editing.csv'

    # Error flags
    ERROR_FLAGS_DATA_PATH = 'Use solar analytics polarity'

    load_list = ['ac_load_net', 'ac_load']
    pv_list = ['pv_site_net', 'pv_site', 'pv_inverter_net']
    load_list_extended = ['ac_load', 'ac_load_net', 'battery_storage', 'load_air_conditioner', 'load_common_area', 'load_ev_charger', 'load_garage', 'load_generator', 'load_hot_water', 'load_hot_water_solar', 'load_kitchen', 'load_laundry', 'load_lighting', 'load_machine', 'load_office', 'load_other', 'load_pool', 'load_powerpoint', 'load_refrigerator', 'load_shed', 'load_spa', 'load_stove', 'load_studio', 'load_subboard', 'load_tenant', 'load_washer']

    # Approx capacity factor value considered to be 'zero', e.g. less than 1% CF is zero.
    CF_ZERO_APPROX = 0.01
    # Approx cf derivative at which considered to be 'ramp'. That is, for at least a 10% change in capacity factor (ABSOLUTE!) expect to be ramping up or down.
    # Note, only applied 'next to' zeros. So should not capture shading effects.
    FIRST_DERIV_FALL_LIMIT = -0.05
    FIRST_DERIV_INCREASE_LIMIT = 0.05
    # For missing data check
    ALLOWED_MISSING_DATA_PERCENTAGE = 0.05
    # Average percentage of capacity at which a system must operate over the course of the day in order to be included in analysis
    VERY_LOW_OUTPUT_AVE_PERCENTAGE_CAPACITY = 0.05

    # Function for getting cumulative count of 0 with resent on 1
    def rcount(a):
        without_reset = (a == 0).cumsum()
        reset_at = (a == 1)
        overcount = np.maximum.accumulate(without_reset * reset_at)
        result = without_reset - overcount
        return result
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Get data
    unaltered_data = pd.read_csv(COMBINED_DATA_FILE_PATH, index_col = 'ts', parse_dates=True )
    # rename energy column
    unaltered_data = unaltered_data.rename(columns = {'e' : 'energy', 'd':'duration', 'sum_ac':'ac'})
    # filter for clean
    unaltered_data = unaltered_data[unaltered_data['clean']=='cleaned']
    # Attempt to fix issues by sorting the index at the beginning
    unaltered_data = unaltered_data.sort_index()
    # Change name to t_stamp
    unaltered_data.index.name = 't_stamp'
    # Add time by seconds from start of the day
    unaltered_data['hrs'] = unaltered_data.index.hour
    unaltered_data['min'] = unaltered_data.index.minute
    unaltered_data['sec'] = unaltered_data.index.second
    unaltered_data['time_in_seconds'] = unaltered_data['hrs'] * 60 * 60 + unaltered_data['min'] * 60 + unaltered_data['sec']

    # Get list of time_intervals
    time_interval_list = unaltered_data['duration'].drop_duplicates().tolist()

    # Check for missing data issues
    # Flag sites with too much missing data (based on threshold), need to also keep the duration
    missing_data_df = pd.DataFrame({'num_data_pts': unaltered_data.groupby('c_id')['energy'].count(), 'duration': unaltered_data.groupby('c_id')['duration'].first()}).reset_index()
    # We now have two possible time intervals: 30s or 60s. 
    # Therefore, we need to run twice?
    for time_interval in time_interval_list:
        # Expected number of time periods
        num_time_periods = 24 * 60 * (60 / time_interval) 
        # Get the minimum number of data points required in order to have enough data (i.e. not lots of missing data)
        missing_data_threshold = num_time_periods * (1 - ALLOWED_MISSING_DATA_PERCENTAGE)
        missing_data_df['missing_data_flag'] = np.nan
        missing_data_df.loc[(missing_data_df['num_data_pts'] <= missing_data_threshold) & missing_data_df['duration']==time_interval , 'missing_data_flag'] = 1.0
    print("The number of c_ids with too much missing data is:")
    print(missing_data_df['missing_data_flag'].sum())
    print("The total number of c_ids is:")
    print(missing_data_df['num_data_pts'].count())
    # Merge information about missing data back onto time series df
    unaltered_data = unaltered_data.reset_index().merge(missing_data_df, on='c_id', how='left').set_index('t_stamp')
    # Filter unaltered data for only sites with sufficient data points
    unaltered_data = unaltered_data[unaltered_data['missing_data_flag'] != 1.0]

    # Filter for PV only
    unaltered_data = unaltered_data[unaltered_data['con_type'].isin(pv_list)]

    # First fix duratoin_x / duration_y problem. Not sure where it is coming from
    # I don't know why, but there is duration_x and duration_y. Drop one and rename the other
    unaltered_data = unaltered_data.drop(['duration_x'], axis=1)
    unaltered_data = unaltered_data.rename(columns={'duration_y': 'duration'})

    # Open _circuit_details_for_editing.csv file for sunrise/set times
    assist_df = pd.read_csv(CIRCUIT_DETAILS_FOR_EDITING_FILE_PATH)

    # Check for PV sites with very low output and remove them
    get_site_ac_df = unaltered_data[['site_id', 'first_ac', 'ac']]
    get_site_ac_df = get_site_ac_df.drop_duplicates(subset='site_id')
    # merge keeping only the site_ids in the time series df. 
    assist_df = assist_df.merge(get_site_ac_df, left_on='site_id', right_on='site_id', how='right')

    # Check whether c_ids operated at less than an average of 5% capacity

    # ******************************************
    # ******************************************
    # ******************************************
    # ******************************************
    # ******************************************
    # Compare using max power output compared with first_ac.
    max_p_df = pd.DataFrame({'max_p_kW': unaltered_data.groupby('c_id')['power_kW'].max(), 'first_ac' : unaltered_data.groupby('c_id')['first_ac'].first()})
    max_p_df['low_output_flag'] = np.nan
    max_p_df.loc[max_p_df['max_p_kW'] < VERY_LOW_OUTPUT_AVE_PERCENTAGE_CAPACITY * max_p_df['first_ac'] , 'low_output_flag'] = 1
    # Copy c_ids to a column (from index)
    max_p_df['c_id'] = max_p_df.index
    print(max_p_df.head())
    # Get list of c_ids to be excluded
    c_ids_to_WITHOUT_low_output = max_p_df[max_p_df['low_output_flag'] != 1]
    c_ids_to_WITHOUT_low_output = c_ids_to_WITHOUT_low_output['c_id'].tolist()
    # print(max_p_df)
    print(len(c_ids_to_WITHOUT_low_output))
    # ******************************************
    # ******************************************
    # ******************************************
    # ******************************************
    # ******************************************

    # Report the number of c_ids dropped.
    print("The number of c_ids excluded due to max output < first_ac * " + str(VERY_LOW_OUTPUT_AVE_PERCENTAGE_CAPACITY)+ ":")
    print(len(max_p_df) - len(c_ids_to_WITHOUT_low_output))
    print("The total number of c_ids remaining is:")
    print(len(max_p_df))

    # Only keep sites that have enough output
    unaltered_data = unaltered_data[unaltered_data['c_id'].isin(c_ids_to_WITHOUT_low_output)]

    # Get assist_df with c_id as index
    assist_df_c_id = assist_df.set_index('c_id')
    print(assist_df_c_id)

    # Get c_id list
    c_id_list = unaltered_data['c_id'].drop_duplicates().tolist()
    # Set up output_df
    output_df = pd.DataFrame()
    output_df.index.name = 't_stamp'

    # Loop
    for c_id in c_id_list:

        # Get data for c_id
        data = unaltered_data[unaltered_data['c_id'] == c_id]

        # Filter for sunshine hours - NOTE must add an hour to sunrise / subtract and hour from sunset since Nick's code did the opposite, but I actually would like correct sunrise/set
        # Sunrise
        sun_rise = assist_df_c_id.loc[c_id,'sunrise']
        sun_rise = pd.to_datetime(sun_rise)
        sun_rise_hour = sun_rise.hour
        sun_rise_min = sun_rise.minute   
        if sun_rise_min <10 :
            sun_rise_min = '0' + str(sun_rise_min)
        else:
            sun_rise_min = str(sun_rise_min)
        sun_rise_for_filter = str(sun_rise_hour + 1) + ':' + sun_rise_min + ':' + str(00)
        # Sunset
        sun_set = assist_df_c_id.loc[c_id,'sunset']
        sun_set = pd.to_datetime(sun_set)
        sun_set_hour = sun_set.hour
        sun_set_min = sun_set.minute
        if sun_set_min <10 :
            sun_set_min = '0' + str(sun_set_min)
        else:
            sun_set_min = str(sun_set_min)   
        sun_set_for_filter = str(sun_set_hour - 1) + ':' + sun_set_min + ':' + str(00)

        print(sun_rise_for_filter)
        print(sun_set_for_filter)
        
        data = data.between_time(sun_rise_for_filter, sun_set_for_filter)

        # Calc CF
        data['unaltered_cf'] = data['power_kW'] / data['ac']
        # Flag approximate zeroes (cf < CF_ZERO_APPROX)
        data['unaltered_zero_flag'] = 0
        data.loc[data['unaltered_cf'] <= CF_ZERO_APPROX, 'unaltered_zero_flag'] = 1
        data['non_zero_flag_count'] = data['unaltered_zero_flag']

        # Remove cases where 'blip' occurs. e.g. above zero but only for a max of 2 time intervals.
        # First, count the non zeros
        a = data['non_zero_flag_count']
        # Now remove from data
        data = data.drop(['non_zero_flag_count'], axis=1)
        # Count non zeros
        result = rcount(a)
        # Add onto data
        data = pd.concat([data,result], axis=1)

        # Copy the unaltered zero flag - we will then remove the 'blips' from it.
        data['zero_flag'] = data['unaltered_zero_flag']

        # Case where single point of 'non zero' before returning to zero
        data.loc[(data['non_zero_flag_count'].shift(-1) == 0) & (data['non_zero_flag_count'] == 1),'zero_flag'] = 1

        # If the non zero flag count in this row is 2 and in the next row is zero, then set zero_flag to 1 (i.e. remove 'blip')
        data.loc[(data['non_zero_flag_count'].shift(-1) == 0) & (data['non_zero_flag_count'] == 2),'zero_flag'] = 1
        data.loc[(data['non_zero_flag_count'].shift(-2) == 0) & (data['non_zero_flag_count'].shift(-1) == 2),'zero_flag'] = 1

        # Set CF to zero where zero flag occurs
        data['cf'] = data['unaltered_cf']
        data.loc[data['zero_flag'] == 1,'cf'] = 0

        # Get first derivative of cf
        data = util.calculate_first_derivative_of_variable(data, 'cf')

        # --------------------------------- Reductions immediately before zero
        # Falling dramatically before zeros
        data['start_deriv_flag'] = 0
        # Just get the first instance of ramp down
        # e.g. Times where zero flag (t+1) = 1, zero flag (t) <>1 and cf_first_deriv < limit
        data.loc[(data['zero_flag'].shift(-1) == 1) & (data['zero_flag'] == 0) & (data['cf_first_deriv'] < FIRST_DERIV_FALL_LIMIT),'start_deriv_flag'] = 1
        # Dealing with 'soft' disconnect
        # Next interval is zero flagged, current value is greater than 'zero' limit
        data.loc[(data['zero_flag'].shift(-1) == 1) & (data['cf'] > CF_ZERO_APPROX),'start_deriv_flag'] = 1

        # Get the next instance of ramp down (well, previous) - repeat four times. Effectively means you can capture periods in which power falls over 5 time intervals (including initial one captured above) 
        data.loc[(data['start_deriv_flag'].shift(-1) == 1) & (data['cf_first_deriv'] < FIRST_DERIV_FALL_LIMIT),'start_deriv_flag'] = 1
        data.loc[(data['start_deriv_flag'].shift(-1) == 1) & (data['cf_first_deriv'] < FIRST_DERIV_FALL_LIMIT),'start_deriv_flag'] = 1
        data.loc[(data['start_deriv_flag'].shift(-1) == 1) & (data['cf_first_deriv'] < FIRST_DERIV_FALL_LIMIT),'start_deriv_flag'] = 1
        data.loc[(data['start_deriv_flag'].shift(-1) == 1) & (data['cf_first_deriv'] < FIRST_DERIV_FALL_LIMIT),'start_deriv_flag'] = 1

        # --------------------------------- Increases immediately after zero
        # Increasing dramatically after zeros
        data['end_deriv_flag'] = 0
        # Just get the first instance of ramp up
        # e.g. Times where zero flag (t) = 1, zero flag (t+1) <>1 and cf_first_deriv > limit
        data.loc[(data['zero_flag'].shift(-1) == 0) & (data['zero_flag'] == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        # Dealing with 'soft' restarts.
        # Previous value was zero flagged, current value is greater than the 'zero' limit
        data.loc[(data['zero_flag'].shift(+1) == 1) & (data['cf'] > CF_ZERO_APPROX),'end_deriv_flag'] = 1

        # Get next instances (x8 as slower ramp up potentially)
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1

        # --------------------------------- Get 'ramp' start and end points
        # Get start points
        data['start_pts'] = 0
        # Case where 'start_derive_flag' is zero in previous interval (t-1), and one in current interval (t)
        data.loc[(data['start_deriv_flag'].shift(+1) == 0) & (data['start_deriv_flag'] == 1),'start_pts'] = 1

        # Get end points
        data['end_pts'] = 0
        # Case where 'end_deriv_flag' is 1 in previous interval (t-1), and 0 in current interval (t)
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['end_deriv_flag'] == 0),'end_pts'] = 1

        # --------------------------------- Add some things to data that we need
        # Check that the first 'start point' occurs before the first 'end point'. If not, then delete the first 'end point'
        # Else in the early hours of the day as the generation goes from zero to non zero it looks like 'soft start'
        # Check three times over (TODO would be better to do this as a while somehow... maybe so that it stops once the first_end_point stops changing?)
        try:
            for i in range(0,3):
                first_end_point = data[data['end_pts']==1]
                first_end_point = first_end_point['time_in_seconds'].iloc[0]
                # Find first start point
                first_start_point = data[data['start_pts']==1]
                first_start_point = first_start_point['time_in_seconds'].iloc[0]
                print(first_end_point)
                print(first_start_point)
                # Check that the first start point occurs after the first end point.
                if first_end_point < first_start_point:
                    data.loc[data['time_in_seconds']==first_end_point, 'end_pts'] = 0
        except:
            print('looks like no start of end points for this site')
            
        # Identify the start and end pt number (so they can be matched to each other)
        data['start_cumsum'] = data['start_pts'].cumsum()
        data['end_cumsum'] = data['end_pts'].cumsum()

        # Get cumulative zeros between 'start' and 'end' pts
        data['count_during_period'] = data['start_pts']
        data.loc[data['end_pts'] == 1,'count_during_period'] =1
        a = data['count_during_period']

        # Copy as a renamed column then remove ^ name from data
        data['start_end_combined'] = data['count_during_period']
        # NOTE - possible issue here? Dropped column but then used later. NO - all good, it's added back on a few
        # lines below using rcount function then merge.
        data = data.drop(['count_during_period'], axis=1)

        # Do count on df 'a' which contains the 'count_during_period' data from a few lines above.
        result = rcount(a)
        data = pd.concat([data,result], axis=1)

        # Flag 'estimate' period (i.e. between start and end pts)
        data['est_period'] = data['start_cumsum'] - data['end_cumsum'] 

        # --------------------------------- get start and end dfs, then get ramp df and merge onto data
        start_df = data[data['start_pts']==1]
        end_df = data[data['end_pts']==1]
        
        # In cases where there are no events, need to 'try'
        try: 
            # Create new ramp_df.
            # NOTE use +2 in the range in order to capture additional end points if the first end point occurs before the first start point. 
            # May make sense to even add a couple.. (i.e. +3 or +4) however this will do for now.
            count_start_pts = start_df['start_cumsum'].max()
            ramp_df = pd.DataFrame(data=range(1,int(count_start_pts+2)), columns=['event_num'])

            # Get data from dfs
            # Keep only cf, time_int and start_cumsum.
            start_df = start_df[['cf', 'time_in_seconds', 'start_cumsum']]
            # Then merge on start_cumsum
            ramp_df = ramp_df.merge(start_df, left_on='event_num', right_on='start_cumsum')
            # Rename columns
            ramp_df = ramp_df.rename(columns = {'cf' : 'start_cf'})
            ramp_df = ramp_df.rename(columns = {'time_in_seconds' : 'start_time_int'})

            # Keep only cf, time)nt and start_cumsum. 
            end_df = end_df[['cf', 'time_in_seconds', 'end_cumsum']]
            # Then merge on start_cumsum
            ramp_df = ramp_df.merge(end_df, left_on='event_num', right_on='end_cumsum')
            # Rename columns
            ramp_df = ramp_df.rename(columns = {'cf' : 'end_cf'})
            ramp_df = ramp_df.rename(columns = {'time_in_seconds' : 'end_time_int'})

            # Check for cases where end time is BEFORE start time for an event. 
            # If this is the case, then delete that end time and shift all end times up by one.
            # Check each event from top to bottom
            num_events = ramp_df['event_num'].max()
            # print(num_events)
            for i in range(0, int(num_events)):
                # print(i)
                # print(ramp_df.loc[i,'end_time_int'])
                # print(ramp_df.loc[i,'start_time_int'])
                if ramp_df.loc[i, 'end_time_int'] < ramp_df.loc[i, 'start_time_int']:
                    ramp_df['end_time_int'] = ramp_df['end_time_int'].shift(-1)

            # Calc the ramp rate
            ramp_df['m'] = (ramp_df['end_cf'] - ramp_df['start_cf']) / (ramp_df['end_time_int'] - ramp_df['start_time_int'])

            # Drop end and start cumsum, then merge onto data
            ramp_df = ramp_df.drop(['end_cumsum', 'start_cumsum'], axis=1)
            zero_row_for_ramp_df = pd.DataFrame(data=[0], columns=['event_num'])
            print(zero_row_for_ramp_df)
            ramp_df = pd.concat([ramp_df, zero_row_for_ramp_df])
            print(ramp_df)

            data = data.reset_index().merge(ramp_df,  left_on='start_cumsum', right_on='event_num').set_index('t_stamp')
            # Calc estimated CF
            data['count_during_period_using_start_time'] = data['est_period'] * (data['time_in_seconds'] - data['start_time_int'])
            data['est_cf'] = data['est_period'] * (data['start_cf'] + data['count_during_period_using_start_time']*data['m'])
            # Add the 'end point'
            data.loc[data['end_pts']==1,'est_cf'] = data['cf']

            # Get est kW and est kWh
            data['est_kW'] = data['est_cf'] * data['ac']
            data['est_kWh'] = data['est_cf'] * data['ac'] * data['duration']/(60*60)

            # Get power lost estimate
            data['gen_loss_est_kWh'] = data['est_kWh'] - (data['power_kW']* data['duration']/(60*60))
            # Issue is that we don't want gen lost to be less than zero!
            data.loc[data['gen_loss_est_kWh'] <0,'gen_loss_est_kWh'] = 0
        except:
            data['no_PV_curtail'] = 1

        # --------------------------------- concat onto output_df
        output_df = pd.concat([output_df, data])

    # Calc gen_kWh for graphing and checking purposes
    output_df['gen_kWh'] = output_df['power_kW'] * output_df['duration']/(60*60)

    # Optional save data to csv
    output_df.to_csv("F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/" + DATA_DATE + TS_DATA_FILE_NAME_FULL)

    # Clean output_df before exporting to csv
    output_df_to_export = output_df[['ac','c_id','cf','clean','con_type','duration','energy','est_cf','est_kW',
                                     'est_kWh','f','first_ac','gen_kWh','gen_loss_est_kWh','Grouping','manufacturer',
                                     'model','power_kW','s_postcode','s_state','site_id','Standard_Version','v',
                                     'zero_flag', 'time_in_seconds']]
    # Optional save data to csv
    output_df_to_export.to_csv("F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/" + DATA_DATE + TS_DATA_FILE_NAME)


    # output_df['t_stamp_copy'] = output_df.index
    # import matplotlib.dates as mdates
    # time_fmt = mdates.DateFormatter('%H:%M')
    # fig, ax = plt.subplots()
    # ax.plot(output_df["t_stamp_copy"], output_df["cf"], '-o', markersize=2, linewidth=1, c='g')
    # ax.plot(output_df["t_stamp_copy"], output_df["est_cf"], '-o', markersize=2, linewidth=1, c='r')
    # # ax1 = ax.twinx()
    # # ax1.plot(pv_data["t_stamp_copy"], pv_data["v"], '-o', markersize=4, linewidth=1, c='b')
    # plt.xlabel('Time')
    # plt.ylabel('Normalised Power (kW/kWac)')
    # ax.xaxis.set_major_formatter(time_fmt)
    # fig.suptitle(str(c_id), fontsize=16)
    # plt.show()


    # --------------------------------- Get summary stats
    # Get site_id list
    site_id_list = unaltered_data['site_id'].drop_duplicates().tolist()
    # Create df to store results
    sum_stats_df = pd.DataFrame(index=site_id_list)

    # Get data of relevance from output_df, summarised by site_id
    meta_df = pd.DataFrame({'power_kW': output_df.groupby('site_id')['power_kW'].sum(),
    'gen_loss_est_kWh': output_df.groupby('site_id')['gen_loss_est_kWh'].sum(),
    'event_num': output_df.groupby('site_id')['event_num'].max(),
    'duration': output_df.groupby('site_id')['duration'].first(),
    's_postcode': output_df.groupby('site_id')['s_postcode'].first(),
    'mean_v_all_daylight_hours': output_df.groupby('site_id')['v'].mean(),
    'first_ac': output_df.groupby('site_id')['first_ac'].first(),
    'ac': output_df.groupby('site_id')['ac'].first(),
    'Standard_Version': output_df.groupby('site_id')['Standard_Version'].first(),
    'Grouping': output_df.groupby('site_id')['Grouping'].first(),
    'model': output_df.groupby('site_id')['model'].first(),
    'manufacturer': output_df.groupby('site_id')['manufacturer'].first()
    })

    # Concat onto results df and name the index
    sum_stats_df = pd.concat([sum_stats_df, meta_df], axis=1)
    sum_stats_df.index.name = 'site_id'

    # Convert generation to kWh
    sum_stats_df['gen_kWh'] = sum_stats_df['power_kW'] * sum_stats_df['duration']/(60*60)
    # sum_stats_df = sum_stats_df.rename(columns = {'power_kW' : 'gen_kWh'})

    # Calc percentage of gen lost
    sum_stats_df['percentage_lost'] = sum_stats_df['gen_loss_est_kWh'].abs() / (sum_stats_df['gen_loss_est_kWh'].abs() + sum_stats_df['gen_kWh'].abs())
    print(sum_stats_df)

    # Get voltage box plot statistics for both curtail times and non curtail times
    curtail_v_df = output_df[output_df['est_period'] == 1]
    all_other_v_df = output_df[output_df['est_period'] != 1]
    # Filter for voltage and site it then get summary stats
    # Curtail times
    curtail_v_df = curtail_v_df[['v','site_id']]
    # rename 'v' to 'curtail_v' in order to see which is which when added to sum_stats_df
    curtail_v_df = curtail_v_df.rename(columns = {'v' : 'v_curtail'})
    curtail_v_box_plot_stats_df = curtail_v_df.groupby('site_id').describe()
    print(curtail_v_box_plot_stats_df)
    # Non curtail times
    all_other_v_df = all_other_v_df[['v','site_id']]
    # rename 'v' to 'other_v' in order to see which is which when added to sum_stats_df
    all_other_v_df = all_other_v_df.rename(columns = {'v' : 'v_all_other'})
    all_other_v_box_plot_stats_df = all_other_v_df.groupby('site_id').describe()
    print(all_other_v_box_plot_stats_df)

    # add box plot stats onto summary stats
    sum_stats_df = pd.concat([sum_stats_df, curtail_v_box_plot_stats_df, all_other_v_box_plot_stats_df], axis=1)

    PC_INSTALLS_DATA_FILE_PATH = 'F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/Postcode_data_for_small-scale installations-SGU-Solar.csv'
    DWELLINGS_DATA_FILE_PATH = 'F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/postcodes_4b8c.csv'

    # Get penetration by postcode
    sum_stats_df = util.get_penetration_by_postcode(PC_INSTALLS_DATA_FILE_PATH, DWELLINGS_DATA_FILE_PATH, sum_stats_df, output_df)

    # Sort and get % of systems
    sum_stats_df = sum_stats_df.sort_values('percentage_lost', ascending =False)

    # Get % of systems
    sum_stats_df['proportion_of_sites'] = range(len(sum_stats_df))
    sum_stats_df['proportion_of_sites'] = (sum_stats_df['proportion_of_sites'] + 1) / len(sum_stats_df)

    # Optional save data to csv
    sum_stats_df.to_csv("F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/" + DATA_DATE + SUM_STATS_DATA_FILE_NAME)