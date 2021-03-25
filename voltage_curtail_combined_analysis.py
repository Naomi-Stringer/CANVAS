# Combines analysis across 24 days of data

#------------------------ Step 0: Import required packages ------------------------
# Import packages required for program
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import matplotlib.ticker as mtick
import calendar
import seaborn as sns; sns.set()
import itertools
from datetime import datetime, timedelta
from time import gmtime, strftime
from collections import OrderedDict

import plotly
import plotly.express as px

from matplotlib import cm
from matplotlib.pyplot import figure
import statsmodels.api as sm
from patsy import dmatrices

import solar_analytics
import util

import matplotlib.pylab as pylab

# Graphing params
# Choose colors here: https://python-graph-gallery.com/100-calling-a-color-with-seaborn/
# Choose params here: https://matplotlib.org/3.1.1/api/matplotlib_configuration_api.html
# Info on the various font. params is available here: https://matplotlib.org/3.1.1/tutorials/introductory/customizing.html
# First set seaborn style:
sns.set_style("whitegrid")
# Then customise: (NOTE grid.alpha is also an option)
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (12, 6.53), # note plot 8 is square and manually sets size below
          'axes.labelsize': 16,
          'axes.titlesize':16,
          'xtick.labelsize':12,
          'ytick.labelsize':12,
          'axes.labelweight':'bold',
          'axes.edgecolor':'gainsboro',
          'grid.color':'gainsboro',
          # 'axes.edgecolor':'whitesmoke',
          # 'grid.color':'whitesmoke',
          #  'grid.alpha':0.5,
          # 'font.family':'serif', ##can use this for times new roman I think
          'legend.edgecolor':'w',
          'text.usetex': False}
pylab.rcParams.update(params)

# For graphing time series
time_fmt = mdates.DateFormatter('%H:%M')

# Below are some things that have weird impacts... rescales the axis labels so that they're wrong.
# plt.rcParams.update({'font.size': 60})
# sns.set(font_scale=1.5)

# import sys
# if sys.version_info[0] < 3:
#     raise Exception("Python 3 or a more recent version is required.")

# Inputs
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
data_date_list = ['2018-01-16', '2018-01-19', '2018-02-02', '2018-02-04', '2018-03-09', '2018-03-31',
                    '2018-04-19', '2018-04-29', '2018-05-13', '2018-05-25', '2018-06-03', '2018-06-27', 
                    '2018-07-10', '2018-07-18', '2018-08-22', '2018-08-25', '2018-09-04', '2018-09-10', 
                    '2018-10-21', '2018-10-26', '2018-11-16', '2018-11-30', '2018-12-23', '2018-12-25']

SUM_STAT_DATA_PATH = 'F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/'
PC_LAT_LON_DATA_FILE_PATH = 'F:/disturbances_analysis/curtail_analysis/copy_DER_disturbance_analysis_for_curtail_data_clean/PostcodesLatLongQGIS.csv'

FIG_V_STRING = '_v7'

SA_INSTALLED_CAPACITY_under_10kW = 844.2
SA_INSTALLED_CAPACITY_10_to_100kW = 246.1
SA_INSTALLED_CAPACITY_TOTAL = SA_INSTALLED_CAPACITY_under_10kW + SA_INSTALLED_CAPACITY_10_to_100kW

FIT_DOLLARS_PER_MWH = 80
SELF_CONSUME_DOLLARS_PER_MWH = 250

# Set this value to 1 to analyse the output of the polyfit analysis (i.e. a better estimate - hopefully! - of
# PV curtail than the straight line method
MAX_CURTAIL_FLAG = 1

# Select the method of PV curtailment estimation for plotting. Options: 'LINEAR_FIT', 'POLYFIT', 'PREFERRED_FIT_METHOD'
CURTAIL_METHOD = 'PREFERRED_FIT_METHOD'

# For plotting example cases
EXAMPLE_DATA_DATE = "2018-10-26"
EXAMPLE_TS_DATA_FILE_PATH = "F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/" + EXAMPLE_DATA_DATE + "_analysis_profiles_polyfit_v4_005sensitivity.csv"
EXAMPLE_END_PTS_METHOD_DATA_FILE_PATH = "F:/05_Solar_Analytics/2019-07-23_dtd_v_curtail_24days/" + EXAMPLE_DATA_DATE + "_analysis_profiles_FULL_DETAIL_v4.csv"
EXAMPLE_SITE_ID = ['1550447108']
LINEAR_FIT_PREFERRED_EXAMPLE_SITE_ID = ['1579656213']
# LINEAR_FIT_PREFERRED_EXAMPLE_SITE_ID_2 = ['1006757091', '1148960611', '86475953', '1775087102', '172441921', '2086445345', '1930975965']
LINEAR_FIT_PREFERRED_EXAMPLE_SITE_ID_2 = ['1775087102']
allowed_residual_band = 0.05 # NOTE - set to 0.05 after some sensitivity testing and eye balling

# Get the colour scheme. Note, same month has same colour for each month
cmap = plt.cm.get_cmap('viridis')
colour_list = [cmap(0.08), cmap(0.17), cmap(0.25), cmap(0.33), cmap(0.42), cmap(0.50), cmap(0.58), cmap(0.67), cmap(0.75), cmap(0.83), cmap(0.92), cmap(1.00)]
colour_list_seasons_24_days = [colour_list[0], colour_list[0],colour_list[0], colour_list[0], colour_list[3], colour_list[3], colour_list[3],  colour_list[3], colour_list[3], colour_list[3], colour_list[8], colour_list[8],colour_list[8], colour_list[8], colour_list[8],colour_list[8], colour_list[11], colour_list[11], colour_list[11], colour_list[11], colour_list[11], colour_list[11], colour_list[0],colour_list[0]]
colour_list_two = [cmap(0.08), cmap(0.08), cmap(0.17), cmap(0.17), cmap(0.25), cmap(0.25), cmap(0.33), cmap(0.33), cmap(0.42), cmap(0.42), cmap(0.50), cmap(0.50), cmap(0.58), cmap(0.58), cmap(0.67), cmap(0.67), cmap(0.75), cmap(0.75), cmap(0.83), cmap(0.83), cmap(0.92), cmap(0.92), cmap(1.00), cmap(1.00)]
colour_list_24_diff_colours = [cmap(0.041666667), cmap(0.083333333), cmap(0.125), cmap(0.166666667), cmap(0.208333333), cmap(0.25), cmap(0.291666667), cmap(0.333333333), cmap(0.375), cmap(0.416666667), cmap(0.458333333), cmap(0.5), cmap(0.541666667), cmap(0.583333333), cmap(0.625), cmap(0.666666667), cmap(0.708333333), cmap(0.75), cmap(0.791666667), cmap(0.833333333), cmap(0.875), cmap(0.916666667), cmap(0.958333333), cmap(1.0)]
# Define some specific colours, note they can be RGB but must be given as a number between 0 and 1. In order to get these floats, divide by 255.
purple = (87/255,30/255,201/255)
pale_pale_purple = (240/255,234/255,252/255)
pale_purple = (179/255,149/255,239/255)
pale_turquoise = (186/255,232/255,225/255)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Open all 24 sum stats
a = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[0] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
b = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[1] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
c = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[2] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
d = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[3] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
e = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[4] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
f = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[5] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
g = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[6] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
h = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[7] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
i = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[8] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
j = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[9] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
k = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[10] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
l = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[11] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
m = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[12] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
n = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[13] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
o = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[14] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
p = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[15] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
q = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[16] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
r = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[17] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
s = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[18] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
t = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[19] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
u = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[20] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
v = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[21] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
w = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[22] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
x = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[23] + "_analysis_sum_stats_polyfit_v4_005sensitivity.csv")
# Add a column containing data date
a['data_date'] = data_date_list[0]
b['data_date'] = data_date_list[1]
c['data_date'] = data_date_list[2]
d['data_date'] = data_date_list[3]
e['data_date'] = data_date_list[4]
f['data_date'] = data_date_list[5]
g['data_date'] = data_date_list[6]
h['data_date'] = data_date_list[7]
i['data_date'] = data_date_list[8]
j['data_date'] = data_date_list[9]
k['data_date'] = data_date_list[10]
l['data_date'] = data_date_list[11]
m['data_date'] = data_date_list[12]
n['data_date'] = data_date_list[13]
o['data_date'] = data_date_list[14]
p['data_date'] = data_date_list[15]
q['data_date'] = data_date_list[16]
r['data_date'] = data_date_list[17]
s['data_date'] = data_date_list[18]
t['data_date'] = data_date_list[19]
u['data_date'] = data_date_list[20]
v['data_date'] = data_date_list[21]
w['data_date'] = data_date_list[22]
x['data_date'] = data_date_list[23]

# Concat
all_days_df = pd.concat([a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x], sort=True)

#------------------------ Add stuff to the all_days_df  ------------------------
# Add month column
all_days_df['month'] = all_days_df['data_date'].str[5:7]
all_days_df['month'] = all_days_df['month'].astype(int)
all_days_df['month_string'] = all_days_df['month'].apply(lambda x: calendar.month_abbr[x])

# Add 'curtail' flag
all_days_df['curtail_flag'] = np.nan
all_days_df.loc[all_days_df['percentage_lost']>=0.0, 'curtail_flag'] = 1

# Add the postcode lat and lon
pc_lat_lon = pd.read_csv(PC_LAT_LON_DATA_FILE_PATH)
all_days_df = all_days_df.merge(pc_lat_lon, left_on='s_postcode', right_on='postcode', how='right')
all_days_df = all_days_df.sort_values(by=['percentage_lost'], ascending=False)

#------------------------ SPLIT INTO TWO DFs ------------------------
# NOTE be careful with this - can either look at JUST the sites reporting curtail (in which case change all 'version 2') or all sites ('version 1')
# Version 1 - set nan values to zero so they are considered when calculating average kWh lost per day per kWac
all_days_df= all_days_df.fillna(0)
all_days_df_incl_zero_curtail_sites = all_days_df.copy()
# Version 2 - drop all of the rows where nan values exist in kWh_lost_per_day_per_kWac so that only curtailed sites are considered in V average etc.
all_days_df_excl_zero_curtail_sites = all_days_df.copy()
all_days_df_excl_zero_curtail_sites = all_days_df_excl_zero_curtail_sites[all_days_df_excl_zero_curtail_sites['gen_loss_est_kWh'] != 0.0]

# NOTE - deliberately doing this before the changes below in order to ensure that the same split occurs each time.
# Approximate zero values can lead to different splits.

#------------------------ Rename columns based on curtail method ------------------------
# to either analyse 1) strainght line fit, 2) polyfit 3) max of the two
# Also have to recalc percentage of sites.
if CURTAIL_METHOD == 'LINEAR_FIT':
    print('Linear fit method selected. No renaming of all_days_df required')
elif CURTAIL_METHOD == 'POLYFIT':
    # INCLUDE Rename existing linear fit columns to be explicitly linear fit
    all_days_df_incl_zero_curtail_sites = all_days_df_incl_zero_curtail_sites.rename(columns = {'gen_loss_est_kWh':'gen_loss_est_kWh_linear_fit',
                                                'percentage_lost':'percentage_lost_linear_fit',
                                                'proportion_of_sites': 'proportion_of_sites_linear_fit'})
    # INCLUDE  Rename polyfit_iter colums to be non explicit - the non explicit columns are printed here.
    all_days_df_incl_zero_curtail_sites = all_days_df_incl_zero_curtail_sites.rename(columns = {'gen_loss_est_kWh_polyfit_iter':'gen_loss_est_kWh',
                                                'percentage_lost_polyfit_iter':'percentage_lost',
                                                'proportion_of_sites_polyfit_iter':'proportion_of_sites'})
    # EXCLUDE
    all_days_df_excl_zero_curtail_sites = all_days_df_excl_zero_curtail_sites.rename(columns = {'gen_loss_est_kWh':'gen_loss_est_kWh_linear_fit',
                                                'percentage_lost':'percentage_lost_linear_fit',
                                                'proportion_of_sites': 'proportion_of_sites_linear_fit'})
    # EXCLUDE Rename polyfit_iter colums to be non explicit - the non explicit columns are printed here.
    all_days_df_excl_zero_curtail_sites = all_days_df_excl_zero_curtail_sites.rename(columns = {'gen_loss_est_kWh_polyfit_iter':'gen_loss_est_kWh',
                                                'percentage_lost_polyfit_iter':'percentage_lost',
                                                'proportion_of_sites_polyfit_iter':'proportion_of_sites'})
elif CURTAIL_METHOD == 'PREFERRED_FIT_METHOD':
    # INCLUDE
    all_days_df_incl_zero_curtail_sites = all_days_df_incl_zero_curtail_sites.rename(columns = {'gen_loss_est_kWh':'gen_loss_est_kWh_linear_fit',
                                                'percentage_lost':'percentage_lost_linear_fit',
                                                'proportion_of_sites':'proportion_of_sites_linear_fit'})
    # INCLUDE
    all_days_df_incl_zero_curtail_sites = all_days_df_incl_zero_curtail_sites.rename(columns = {'gen_loss_est_kWh_preferred':'gen_loss_est_kWh',
                                                'percentage_lost_preferred':'percentage_lost',
                                                'proportion_of_sites_preferred':'proportion_of_sites'})
    # EXCLUDE
    all_days_df_excl_zero_curtail_sites = all_days_df_excl_zero_curtail_sites.rename(columns = {'gen_loss_est_kWh':'gen_loss_est_kWh_linear_fit',
                                                'percentage_lost':'percentage_lost_linear_fit',
                                                'proportion_of_sites':'proportion_of_sites_linear_fit'})
    # EXCLUDE
    all_days_df_excl_zero_curtail_sites = all_days_df_excl_zero_curtail_sites.rename(columns = {'gen_loss_est_kWh_preferred':'gen_loss_est_kWh',
                                                'percentage_lost_preferred':'percentage_lost',
                                                'proportion_of_sites_preferred':'proportion_of_sites'})
else:
    print("ERROR - enter an allowed CURTAIL_METHOD value.")

# Add kWh lost per day per kWac column
all_days_df_incl_zero_curtail_sites['kWh_lost_per_day_per_kWac'] = all_days_df_incl_zero_curtail_sites['gen_loss_est_kWh'] / all_days_df_incl_zero_curtail_sites['first_ac']
all_days_df_excl_zero_curtail_sites['kWh_lost_per_day_per_kWac'] = all_days_df_excl_zero_curtail_sites['gen_loss_est_kWh'] / all_days_df_excl_zero_curtail_sites['first_ac']

#------------------------ Plot 8 ------------------------
# TODO - I do not know why, but sorting before binning changes the number of sites per bin for plot 8. Do plot 8 first.
# Shows the Percentage lost by PV penetration bin, as well as average voltage and site count
# # ---------> Proper way to do this showing all data
# bins = [0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1.0, np.inf]
# bin_labels = ["0-10%","10-15%","15-20%","20-25%","25-30%","30-35%","35-40%","40-45%","45-50%","50-55%","55-60%","60-65%","65-70%","70-75%","75-80%","80-85%","85-90%","90- 95%","95-100%","outside range"]
# # Create bin layers
# all_days_df['pv_penetration_bins'] = pd.cut(all_days_df['pv_penetration'], bins, labels=bin_labels)

# boxplot formatting
boxprops={'color':'grey', 'facecolor':pale_purple, "linestyle":"-" , "linewidth":1} #NOTE for some totally unclear reasons it is important that 'facecolor' comes first. Otherwise it is overwritten. Maybe actually because dict don't keep their order??
whiskerprops = {'color':'grey', "linestyle":"-" , "linewidth":1}
meanprops={"marker":"o","markerfacecolor":"black"}
flierprops={'markerfacecolor':'0.5','markeredgecolor':'1','linestyle':'none','markeredgewidth':'0.5'}
# flierprops = {"marker":"d", "markersize":4}

# ---------> Improper way to do this showing only data I know is there (i.e. >15% and <65% penetration)... based on inital visualisation
bins = [0.150000,0.20000,0.250000,0.30000,0.350000,0.40000,0.450000,0.50000,0.550000,0.60000,0.650000, np.inf]
bin_labels = ["15-20%","20-25%","25-30%","30-35%","35-40%","40-45%","45-50%","50-55%","55-60%","60-65%",">65%"]
printing_bin_labels = ["15-20%","20-25%","25-30%","30-35%","35-40%","40-45%","45-50%","50-55%","55-60%","60-65%"]
# Create bin layers
all_days_df_excl_zero_curtail_sites['pv_penetration_bins'] = pd.cut(all_days_df_excl_zero_curtail_sites['pv_penetration'], bins, labels=bin_labels)
# Get subset of all_days_df_excl_zero_curtail_sites with just the bins we want to print
printing_df = all_days_df_excl_zero_curtail_sites[all_days_df_excl_zero_curtail_sites['pv_penetration_bins'] != ">65%"]
printing_df = printing_df.dropna(subset=['pv_penetration_bins'])

# Add the number of sites as a bar chart over the top, first calculate the numbers required
printing_df_unique_sites = printing_df.drop_duplicates(subset='site_id')
site_count_df = pd.DataFrame({'site_id_count' : printing_df_unique_sites.groupby('pv_penetration_bins')['site_id'].count()})
site_count_df = site_count_df.drop(">65%", axis=0)
# print(site_count_df)
site_count_df['pv_penetration_bins_copy'] = site_count_df.index
# print(site_count_df)

# Create subplots (these will be stacked on top of each other)
fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
fig.set_size_inches(12, 12)
# percentage lost distributions - NOTE for some unknown reason the order of the props items also matter. try not to change them.
sns.boxplot(x='pv_penetration_bins', y='percentage_lost', data=printing_df, showmeans=True, meanprops=meanprops, whiskerprops=whiskerprops, capprops=whiskerprops, boxprops=boxprops, flierprops=flierprops, medianprops=whiskerprops, ax = ax1)
ax1.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax1.set_ylim([-0.05,1.0])
ax1.set_xlim([-0.5,9.5])
ax1.set(ylabel='Percentage lost', xlabel='')
# voltage distributions
sns.boxplot(x='pv_penetration_bins', y='mean_v_all_daylight_hours', data=printing_df, showmeans=True, meanprops=meanprops, whiskerprops=whiskerprops, capprops=whiskerprops, boxprops=boxprops, flierprops=flierprops, medianprops=whiskerprops, ax=ax2)
ax2.set_ylim([230, 260])
ax2.set_xlim([-0.5,9.5])
ax2.set(ylabel='Average voltage (Vrms)', xlabel='')
# Then add values to the plot
sns.barplot(x='pv_penetration_bins_copy', y = 'site_id_count', data = site_count_df, color=pale_purple, ax=ax3)
ax3.set_ylim([-10,300])
ax3.set_xlim([-0.5,9.5])
ax3.set(ylabel='Site count', xlabel='PV penetration by postcode')
for p in ax3.patches:
    height = p.get_height()
    ax3.text(p.get_x()+p.get_width()/2.,
            height + 3,
            '{:1.0f}'.format(height),
            ha="center")
# Plot
plt.show()
# Save figure
# fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'plot_8_penetration_vs_v_and_pv_loss_'+str(CURTAIL_METHOD)+ FIG_V_STRING +'.png', dpi=400, bbox_inches = 'tight', pad_inches = 0)
fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'plot_8_penetration_vs_v_and_pv_loss_'+str(CURTAIL_METHOD)+ FIG_V_STRING +'.pdf', bbox_inches = 'tight', pad_inches = 0.1)

#------------------------ Plot 1 ------------------------
# Make a chart of proportion_of_sites(x) vs percentage_lost (y) with series for each data_date
# plot each day as a line
# TODO - I do not know why, but sorting before binning changes the number of sites per bin for plot 8. Do plot 8 first.
all_days_df_excl_zero_curtail_sites = all_days_df_excl_zero_curtail_sites.sort_values(by=['percentage_lost'])
fig, ax= plt.subplots()
# # Plot
b = util.distribution_plot_1(all_days_df_excl_zero_curtail_sites, data_date_list,ax, colour_list)
# Print
plt.show()
# Save figure
fig.savefig(SUM_STAT_DATA_PATH + 'Images/' + 'plot_1_percentage_gen_lost_distribution_'+str(CURTAIL_METHOD)+ FIG_V_STRING + '.png', dpi=100, bbox_inches = 'tight', pad_inches = 0)

#------------------------ Plot 2 ------------------------
# Distribution for sites in entire data set - i.e. for which there are 24 days of data
# NOTE - use all_days_df rather than 'incl' or 'excl' version because the excl version results in no data,
# whereas the incl version results in lots of zeros on the graph and makes it hard to read.
# UPDATE - we're going to deal with the zeros because it's better not to use the all_days_df if possible. Ambiguity.
# NOTE do not use the [22,23,24] without rethinking the whole updating proportoin of sites thing below.
# list_allowed_num_data_days = [22,23,24]
list_allowed_num_data_days = [24]
# Get the sites with 24 days of data and extract site_id (index) as a list
list_site_ids_all_24d = all_days_df.groupby('site_id')['site_id'].count()
list_site_ids_all_24d = list_site_ids_all_24d[list_site_ids_all_24d.isin(list_allowed_num_data_days)].index.values.tolist()

# filter whole data set for just these 24 d site_ids
all_days_df_repeat_sites = all_days_df_incl_zero_curtail_sites[all_days_df_incl_zero_curtail_sites['site_id'].isin(list_site_ids_all_24d)]
all_days_df_repeat_sites = all_days_df_repeat_sites.sort_values(by=['percentage_lost'], ascending=False)

# Update 'proportion of sites' given there is now a shorter list of sites.
print(len(all_days_df_repeat_sites))
my_list = range(int(len(all_days_df_repeat_sites)/24))
new_list = [(float(x)+float(1))/float(len(all_days_df_repeat_sites)/24) for x in my_list]
# Update the 'proportion of sites' for each data date
for date_now in data_date_list:
    all_days_df_repeat_sites.loc[all_days_df_repeat_sites['data_date'] == date_now, 'proportion_of_sites'] = new_list

# plot each day as a line
fig, ax= plt.subplots()
# Plot
c = util.distribution_plot_1(all_days_df_repeat_sites, data_date_list,ax, colour_list)
fig.savefig(SUM_STAT_DATA_PATH + 'Images/' + 'plot_2_percentage_gen_lost_distribution_sites_with_all_24d_data_'
            +str(CURTAIL_METHOD)+ FIG_V_STRING + '.png', dpi=100, bbox_inches = 'tight', pad_inches = 0)
plt.show()
#------------------------ Plot 6 ------------------------
# Show the number of sites, the number of sites impacted and the proportion of sites impacted
site_count_df = pd.DataFrame({'site_id_count' : all_days_df_excl_zero_curtail_sites.groupby('month')['site_id'].count(),
    'curtail_site_count': all_days_df_excl_zero_curtail_sites.groupby('month')['curtail_flag'].sum()})
site_count_df['proportion_of_sites_curtailed'] = site_count_df['curtail_site_count'] / site_count_df['site_id_count']
site_count_df['month'] = site_count_df.index
# Get month list for fig below
month_list = all_days_df_excl_zero_curtail_sites[['month', 'month_string']].drop_duplicates(subset='month').sort_values(by=['month'])
month_list = month_list['month_string'].tolist()

# Show the spread of percentage lost by date
fig, ax= plt.subplots()
sns.boxplot(x='data_date', y='percentage_lost', data=all_days_df_excl_zero_curtail_sites, palette=colour_list_two,
                 showmeans=True, meanprops={"marker":"o","markerfacecolor":"black"}, order=data_date_list)
ax.set_xticklabels(ax.get_xticklabels(),rotation=90)
# Axis labels
plt.xlabel('Date')
plt.ylabel('Percentage generation lost')
# set y axis to percentage
vals = ax.get_yticks()
ax.set_yticklabels(['{:,.0%}'.format(x) for x in vals])
# Save figure
fig.savefig(SUM_STAT_DATA_PATH + '/Images/plot_6_spread_of_gen_lost_over_dates_'+str(CURTAIL_METHOD)+ FIG_V_STRING +'.png',
            dpi=100, bbox_inches = 'tight', pad_inches = 0)
# Print the figure
plt.show()

# Show by month instead of date
fig, ax= plt.subplots()
sns.boxplot(x='month_string', y='percentage_lost', data=all_days_df_excl_zero_curtail_sites, palette=colour_list,
                 showmeans=True, meanprops={"marker":"o","markerfacecolor":"black"}, order = month_list)
# set y axis to percentage
vals = ax.get_yticks()
ax.set_yticklabels(['{:,.0%}'.format(x) for x in vals])
# Axis labels
plt.xlabel('Month')
plt.ylabel('Percentage generation lost')
# Add second axis with num sites
# ax1 = sns.pointplot(y='proportion_of_sites_curtailed', x='month', data = site_count_df)
# Save figure
fig.savefig(SUM_STAT_DATA_PATH + '/Images/plot_6_spread_of_gen_lost_over_months_'+str(CURTAIL_METHOD)+ FIG_V_STRING + '.png', dpi=100,
            bbox_inches = 'tight', pad_inches = 0)
# plot
plt.show()

print(all_days_df_excl_zero_curtail_sites['mean_v_all_daylight_hours'].mean())
print(all_days_df_excl_zero_curtail_sites['mean_v_all_daylight_hours'].count())
print(all_days_df_excl_zero_curtail_sites['mean_v_all_daylight_hours'].sum())

print(all_days_df_incl_zero_curtail_sites['mean_v_all_daylight_hours'].mean())
print(all_days_df_incl_zero_curtail_sites['mean_v_all_daylight_hours'].count())
print(all_days_df_incl_zero_curtail_sites['mean_v_all_daylight_hours'].sum())

# Show for VOLTAGE by month instead of generation lost
fig, ax= plt.subplots()
sns.boxplot(x='month_string', y='mean_v_all_daylight_hours', data=all_days_df_excl_zero_curtail_sites,
                 palette=colour_list, showmeans=True, meanprops={"marker":"o","markerfacecolor":"black"}, order=month_list)
# Axis labels
plt.xlabel('Month')
plt.ylabel('Voltage (Vrms)')
# Save figure
fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'plot_6_spread_of_v_over_months_'+str(CURTAIL_METHOD)+ FIG_V_STRING +'.png', dpi=100,
            bbox_inches = 'tight', pad_inches = 0)
# Axis limits
ax.set(ylim=(230,260))
# plot
plt.show()

#------------------------ Plot 7 ------------------------
# High level stats and upscaling
# Be VERY careful with this. How you calculate the mean can have a significant impact.
# Checking the other way of getting the average behavior:
print(all_days_df_incl_zero_curtail_sites['kWh_lost_per_day_per_kWac'].mean())
print(all_days_df_incl_zero_curtail_sites['percentage_lost'].mean())

# V1 where all sites are considered
high_level_stats_df_v1 = pd.DataFrame({'sum_ac': all_days_df_incl_zero_curtail_sites.groupby('data_date')['ac'].sum(),
    'sum_first_ac': all_days_df_incl_zero_curtail_sites.groupby('data_date')['first_ac'].sum(),
    'sum_gen_kWh': all_days_df_incl_zero_curtail_sites.groupby('data_date')['gen_kWh'].sum(),
    'sum_gen_loss_est_kWh': all_days_df_incl_zero_curtail_sites.groupby('data_date')['gen_loss_est_kWh'].sum(),
    'mean_percentage_lost': all_days_df_incl_zero_curtail_sites.groupby('data_date')['percentage_lost'].mean(),
    'count_site_id': all_days_df_incl_zero_curtail_sites.groupby('data_date')['site_id'].count(),
    'mean_kWh_lost_per_day_per_kWac': all_days_df_incl_zero_curtail_sites.groupby('data_date')['kWh_lost_per_day_per_kWac'].mean(),
    'mean_mean_v_all_daylight_hours': all_days_df_incl_zero_curtail_sites.groupby('data_date')['mean_v_all_daylight_hours'].mean(),
    'data_date': all_days_df_incl_zero_curtail_sites.groupby('data_date')['data_date'].first()
    })

# V2 where just the curtailed sites are considered
high_level_stats_df_v2 = pd.DataFrame({'sum_ac': all_days_df_excl_zero_curtail_sites.groupby('data_date')['ac'].sum(),
    'sum_first_ac': all_days_df_excl_zero_curtail_sites.groupby('data_date')['first_ac'].sum(),
    'sum_gen_kWh': all_days_df_excl_zero_curtail_sites.groupby('data_date')['gen_kWh'].sum(),
    'sum_gen_loss_est_kWh': all_days_df_excl_zero_curtail_sites.groupby('data_date')['gen_loss_est_kWh'].sum(),
    'mean_percentage_lost': all_days_df_excl_zero_curtail_sites.groupby('data_date')['percentage_lost'].mean(),
    'count_site_id': all_days_df_excl_zero_curtail_sites.groupby('data_date')['site_id'].count(),
    'mean_kWh_lost_per_day_per_kWac': all_days_df_excl_zero_curtail_sites.groupby('data_date')['kWh_lost_per_day_per_kWac'].mean(),
    'mean_mean_v_all_daylight_hours': all_days_df_excl_zero_curtail_sites.groupby('data_date')['mean_v_all_daylight_hours'].mean(),
    'data_date': all_days_df_excl_zero_curtail_sites.groupby('data_date')['data_date'].first()
    })

# Export to csv
high_level_stats_df_v1.to_csv(SUM_STAT_DATA_PATH + 'IMAGES/high_level_stats_df-INCLUDING_zero_curtail_sites_'+str(CURTAIL_METHOD)+ FIG_V_STRING + '.csv')
high_level_stats_df_v2.to_csv(SUM_STAT_DATA_PATH + 'Images/high_level_stats_df-EXCLUDING_zero_curtail_sites_'+str(CURTAIL_METHOD)+ FIG_V_STRING + '.csv')

average_kWh_lost_per_day_per_kWh = high_level_stats_df_v1['mean_kWh_lost_per_day_per_kWac'].mean()
print(average_kWh_lost_per_day_per_kWh)
print(SA_INSTALLED_CAPACITY_TOTAL)
upscaled_gen_lost_est = average_kWh_lost_per_day_per_kWh * SA_INSTALLED_CAPACITY_TOTAL * 365
print(upscaled_gen_lost_est)
lower_bound_financial_impact = upscaled_gen_lost_est * FIT_DOLLARS_PER_MWH
upper_bound_financial_impact = upscaled_gen_lost_est * SELF_CONSUME_DOLLARS_PER_MWH
print(lower_bound_financial_impact)
print(upper_bound_financial_impact)

# Number of sites impacted:
num_sites_impacted_at_least_one_day = len(all_days_df_excl_zero_curtail_sites['site_id'].drop_duplicates().tolist())
print(num_sites_impacted_at_least_one_day)
num_sites_in_data_set_at_least_one_day = len(all_days_df_incl_zero_curtail_sites['site_id'].drop_duplicates().tolist())
print(num_sites_in_data_set_at_least_one_day)



#------------------------ Plot 9 ------------------------
# Scatter plot of average average voltage (x) and average kWh lost per kWac (y) with one data point for each day
# First we want to create the data set grouped by data_date
# One data point per day per site
# Get data
scatter_plot_data = pd.DataFrame({'mean_kWh_lost_per_day_per_kWac': all_days_df_excl_zero_curtail_sites.groupby('data_date')['kWh_lost_per_day_per_kWac'].mean(),
    'mean_mean_v_all_daylight_hours': all_days_df_excl_zero_curtail_sites.groupby('data_date')['mean_v_all_daylight_hours'].mean(),
    'data_date': all_days_df_excl_zero_curtail_sites.groupby('data_date')['data_date'].first()
    })
# Add to chart
fig, ax= plt.subplots()
ax1 = sns.scatterplot(x='mean_v_all_daylight_hours', y='kWh_lost_per_day_per_kWac', data = all_days_df_excl_zero_curtail_sites, hue='data_date', palette=colour_list_seasons_24_days, alpha=0.2, legend=False)
# Average per day
sns.scatterplot(x='mean_mean_v_all_daylight_hours', y='mean_kWh_lost_per_day_per_kWac', data=scatter_plot_data, hue='data_date', palette=colour_list_seasons_24_days, marker='D', edgecolor='black')
# Get legend and make columns
handles, labels = ax1.get_legend_handles_labels()
ax1.legend(handles=handles[1:], labels=labels[1:],ncol=3, title="Date", prop={'size': 12})
# Axis labels
plt.xlabel('Average daily voltage during sunlight hours')
plt.ylabel('Average kWh lost generation '
           '/ day / kWac capacity')
# ax.set_ylim([-0.05,3]) #TODO - sort out y axis for both plots
# ax1.set_ylim([-0.05,3])
plt.show()
# Save
# fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'plot_9_voltage_v_kWh_per_kWac_lost_SEASONS_'+str(CURTAIL_METHOD)+ FIG_V_STRING + '.png', dpi=400, bbox_inches = 'tight', pad_inches = 0)
fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'plot_9_voltage_v_kWh_per_kWac_lost_SEASONS_'+str(CURTAIL_METHOD)+ FIG_V_STRING + '.pdf', bbox_inches = 'tight', pad_inches = 0.1)

#------------------------
# Get r values
#------------------------
# First check voltage versus pv penetration
list1 = all_days_df_excl_zero_curtail_sites['mean_v_all_daylight_hours'].tolist()
list2 = all_days_df_excl_zero_curtail_sites['kWh_lost_per_day_per_kWac'].tolist()
r_value = np.corrcoef(list1,list2)
print(r_value)



#------------------------ Plot 10 ------------------------
# Distribution of impact on customers - only plot impacted customers!
# Get data
distributional_impact_plot_data = pd.DataFrame({'mean_kWh_lost_per_day_per_kWac': all_days_df_excl_zero_curtail_sites.groupby('site_id')['kWh_lost_per_day_per_kWac'].mean(),
    'mean_mean_v_all_daylight_hours': all_days_df_excl_zero_curtail_sites.groupby('site_id')['mean_v_all_daylight_hours'].mean(),
    'ac': all_days_df_excl_zero_curtail_sites.groupby('site_id')['ac'].first(),
    'mean_percentage_lost': all_days_df_excl_zero_curtail_sites.groupby('site_id')['percentage_lost'].mean(),
    'count_data_date': all_days_df_excl_zero_curtail_sites.groupby('site_id')['data_date'].count()
    })
# Copy site_id for plotting
distributional_impact_plot_data['site_id'] = distributional_impact_plot_data.index
# Sort from most impacted to least
distributional_impact_plot_data = distributional_impact_plot_data.sort_values('mean_kWh_lost_per_day_per_kWac', ascending =False)

# Calculate lower and upper bound on p.a. financial impact
distributional_impact_plot_data['lower_bound_fin_impact'] = distributional_impact_plot_data['mean_kWh_lost_per_day_per_kWac'] / 1000.0 * FIT_DOLLARS_PER_MWH * 365
distributional_impact_plot_data['upper_bound_fin_impact'] = distributional_impact_plot_data['mean_kWh_lost_per_day_per_kWac'] / 1000.0 * SELF_CONSUME_DOLLARS_PER_MWH * 365

# Plot in excel
distributional_impact_plot_data.to_csv(SUM_STAT_DATA_PATH + "/Images/distributional_impact_plot_data_"+str(CURTAIL_METHOD)+ FIG_V_STRING + ".csv")

#------------------------ Export data ------------------------
all_days_df_incl_zero_curtail_sites.to_csv(SUM_STAT_DATA_PATH + "all_days_analysis_INCLUDING_zero_curtail_sites_"+str(CURTAIL_METHOD) + FIG_V_STRING + ".csv")
all_days_df_excl_zero_curtail_sites.to_csv(SUM_STAT_DATA_PATH + "all_days_analysis_EXCLUDING_zero_curtail_sites_"+str(CURTAIL_METHOD)+ FIG_V_STRING + ".csv")

# #------------------------ Example plots ------------------------
# #------------------------# #------------------------ # #------------------------
# #------------------------ # #------------------------ # #------------------------
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (12, 6.53), # note plot 8 is square and manually sets size below
         'axes.labelsize': 20,
         'axes.titlesize':20,
         'xtick.labelsize':18,
         'ytick.labelsize':18,
         'axes.labelweight':'bold',
         'axes.edgecolor':'gainsboro',
         'grid.color':'gainsboro',
        #  'grid.alpha':0.5,
        # 'font.family':'serif', ##can use this for times new roman I think
         'legend.edgecolor':'w',
         'text.usetex': False}
pylab.rcParams.update(params)

# Get data
full_eg_data_df = pd.read_csv(EXAMPLE_TS_DATA_FILE_PATH, index_col='t_stamp', parse_dates=True)
full_eg_data_df['clean_cf'] = full_eg_data_df['power_kW'] / full_eg_data_df['ac']

# #------------------------ Example plots - polyfit iter method ------------------------
# Filter for example site
eg_data_df = full_eg_data_df[full_eg_data_df['site_id'].isin(EXAMPLE_SITE_ID)]

# Get list of c_ids
eg_c_id_list = eg_data_df['c_id'].drop_duplicates().tolist()

for c_id in eg_c_id_list:
    # Filter for c_id
    pv_data = eg_data_df[eg_data_df['c_id'] == c_id]
    pv_data['t_stamp_copy'] = pv_data.index
    pv_data['est_cf'] = pv_data['est_cf'].replace({0:np.nan})

    # Plot PV over time (to check)
    fig, ax = plt.subplots()
    ax.plot(pv_data["t_stamp_copy"], pv_data["clean_cf"], '-o', markersize=2, linewidth=1, c=purple, label = 'PV generation')
    ax.plot(pv_data["t_stamp_copy"], pv_data["est_cf"], '-o', markersize=2, linewidth=1, c=colour_list[5], label = 'PV generation loss estimate (linear)')
    ax.fill_between(pv_data["t_stamp_copy"], pv_data["clean_cf"],0, color=purple, alpha=0.6)
    ax.fill_between(pv_data["t_stamp_copy"], pv_data["clean_cf"], pv_data["est_cf"], color=colour_list[5], alpha=0.6)
    # ax1 = ax.twinx()
    # ax1.plot(pv_data["t_stamp_copy"], pv_data["v"], '-o', markersize=4, linewidth=1, c='b')
    plt.xlabel('Time')
    plt.ylabel('Normalised Power (kW/kWac)')
    ax.xaxis.set_major_formatter(time_fmt)
    ax.legend(fontsize=15)
    ax.set(ylim=(-0.05, 1))
    # fig.suptitle(str(c_id), fontsize=16)
    # fig.set_size_inches(6, 4)
    # fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'example_polyfit_iter_method_1'
    #             + FIG_V_STRING + '.png', dpi=400, bbox_inches='tight', pad_inches=0)
    fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'example_polyfit_iter_method_1'
                + FIG_V_STRING + '.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.show()

    # TODO - ******************************** Unfortunately I didn't save the first polyfit attempt so recalc here.
    test = pv_data[pv_data['cf'] > 0]
    x = test['time_in_seconds']
    y = test['cf']
    z = np.polyfit(x, y, 2)

    # Calc the fitted line
    test['polynomial_fit'] = z[0] * test['time_in_seconds'] * test['time_in_seconds'] + \
                             z[1] * test['time_in_seconds'] + z[2]
    # This is calculated for all times (not just non zero) as well for printing / checking
    pv_data['polynomial_fit'] = z[0] * pv_data['time_in_seconds'] * pv_data['time_in_seconds'] + \
                                z[1] * pv_data['time_in_seconds'] + z[2]
    pv_data['curtail_period_temp'] = np.nan
    pv_data.loc[pv_data['est_cf']>0, 'curtail_period_temp'] = 1
    pv_data['polynomial_fit_for_graph_fill'] = pv_data['polynomial_fit'] * pv_data['curtail_period_temp']
    # Get the correlation between my polynomial and the cf data (excluding zeroes) then remove points with
    # 'large' residuals
    # Get line of best fit
    test['ones'] = 1
    A = test[['cf', 'ones']]
    y = test['polynomial_fit']
    m, c = np.linalg.lstsq(A, y)[0]
    test['y_line'] = c + m * test['cf']
    # TODO - ********************************

    # Plot PV and first polyfit over time (to check)
    fig, ax = plt.subplots()
    ax.plot(pv_data["t_stamp_copy"], pv_data["clean_cf"], '-o', markersize=2, linewidth=1, c=purple, label = 'PV generation')
    ax.plot(pv_data["t_stamp_copy"], pv_data["polynomial_fit"], '-o', markersize=2, linewidth=1, c=colour_list[5], label = 'PV generation loss estimate (polyfit 1)')
    ax.fill_between(pv_data["t_stamp_copy"], pv_data["clean_cf"],0, color=purple, alpha=0.6)
    ax.fill_between(pv_data["t_stamp_copy"], pv_data["clean_cf"], pv_data["polynomial_fit_for_graph_fill"], color=colour_list[5], alpha=0.6)
    plt.xlabel('Time')
    plt.ylabel('Normalised Power (kW/kWac)')
    ax.xaxis.set_major_formatter(time_fmt)
    ax.legend(fontsize=15)
    ax.set(ylim=(-0.05, 1))
    # fig.suptitle(str(c_id), fontsize=16)
    # fig.set_size_inches(6, 4)
    fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'example_polyfit_iter_method_2'
                + FIG_V_STRING + '.pdf', bbox_inches='tight', pad_inches=0.1)
    # fig.suptitle(str(c_id), fontsize=16)
    plt.show()

    # Plot cf versus polyfit to see how well they are correlated.
    # Show the line of best fit +/- allowed_residual_band
    test['upper_band'] = test['y_line'] + allowed_residual_band
    test['lower_band'] = test['y_line'] - allowed_residual_band

    fig, ax = plt.subplots()
    ax.plot(test['cf'], test['y_line'], c=colour_list[9], label='Linear fit')
    ax.plot(test['cf'], test['upper_band'], linewidth=1, c=colour_list[5], label='Allowed residual band')
    ax.plot(test['cf'], test['lower_band'], linewidth=1, c=colour_list[5])
    # ax.fill_between(test['cf'], test['lower_band'], test['upper_band'], color=purple, alpha=0.6)
    ax.plot(test["cf"], test["polynomial_fit"], 'o', markersize=3, linewidth=1, c=colour_list[1])
    # ax.fill_between(test['cf'], test['upper_band'], test['lower_band'], color=colour_list[10], alpha=0.6)
    plt.xlabel('Normalised Power (kW/kWac)')
    plt.ylabel('Polynomial fit (polyfit 1)')
    ax.legend(fontsize=15)
    ax.set(ylim=(-0.1, 1), xlim=(-0.1,1))
    fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'example_polyfit_iter_method_3'
                + FIG_V_STRING + '.pdf', bbox_inches='tight', pad_inches=0.1)
    # fig.suptitle(str(c_id), fontsize=16)
    plt.show()

    # Plot PV and new polyfit over time (to check)
    fig, ax = plt.subplots()
    ax.plot(pv_data["t_stamp_copy"], pv_data["clean_cf"], '-o', markersize=2, linewidth=1, c=purple, label = 'PV generation')
    ax.plot(pv_data["t_stamp_copy"], pv_data["est_cf_polyfit_iter"], '-o', markersize=2, linewidth=1,  c=colour_list[5], label = 'PV generation loss estimate (polyfit 2)')
    ax.fill_between(pv_data["t_stamp_copy"], pv_data["clean_cf"],0, color=purple, alpha=0.6)
    ax.fill_between(pv_data["t_stamp_copy"], pv_data["clean_cf"], pv_data["est_cf_polyfit_iter"], color=colour_list[5], alpha=0.6)
    plt.xlabel('Time')
    plt.ylabel('Normalised Power (kW/kWac)')
    ax.xaxis.set_major_formatter(time_fmt)
    ax.legend(fontsize=15)
    ax.set(ylim=(-0.05, 1))
    # fig.suptitle(str(c_id), fontsize=16)
    # fig.set_size_inches(6, 4)
    fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'example_polyfit_iter_method_4'
                + FIG_V_STRING + '.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.show()

# #------------------------ Example plots - linear method preferred ------------------------
# #------------------------ Case where CF exceeds 1 (and CF doesn't exceed 1 for PV gen profile!)
# Filter for example site
eg_data_df = full_eg_data_df[full_eg_data_df['site_id'].isin(LINEAR_FIT_PREFERRED_EXAMPLE_SITE_ID)]

# Get list of c_ids
eg_c_id_list = eg_data_df['c_id'].drop_duplicates().tolist()

for c_id in eg_c_id_list:
    # Filter for c_id
    pv_data = eg_data_df[eg_data_df['c_id'] == c_id]
    pv_data['t_stamp_copy'] = pv_data.index
    pv_data['est_cf'] = pv_data['est_cf'].replace({0:np.nan})

    pv_data['unity_line'] = 1.0

    # Plot PV over time (to check)
    fig, ax = plt.subplots()
    ax.plot(pv_data["t_stamp_copy"], pv_data["clean_cf"], '-o', markersize=2, linewidth=1, c=purple, label = 'PV generation')
    ax.plot(pv_data["t_stamp_copy"], pv_data["est_cf"], '-o', markersize=2, linewidth=1, c=colour_list[5], label = 'PV generation loss estimate (linear)')
    ax.plot(pv_data["t_stamp_copy"], pv_data["est_cf_polyfit_iter"], '-o', markersize=2, linewidth=1, c=colour_list[8],label='PV generation loss estimate (polyfit 2)')
    ax.plot(pv_data['t_stamp_copy'], pv_data['unity_line'], '--', c='black')
    ax.fill_between(pv_data["t_stamp_copy"], pv_data["clean_cf"],0, color=purple, alpha=0.6)
    # ax.fill_between(pv_data["t_stamp_copy"], pv_data["clean_cf"], pv_data["est_cf"], color=colour_list[5], alpha=0.6)
    # ax1 = ax.twinx()
    # ax1.plot(pv_data["t_stamp_copy"], pv_data["v"], '-o', markersize=4, linewidth=1, c='b')
    plt.xlabel('Time')
    plt.ylabel('Normalised Power (kW/kWac)')
    ax.xaxis.set_major_formatter(time_fmt)
    ax.legend(fontsize=15, loc='upper left')
    ax.set(ylim=(-0.05, 1.4))
    # fig.suptitle(str(c_id), fontsize=16)
    # fig.set_size_inches(6, 4)
    fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'example_linear_method_preferred_due_to_CF'
                + FIG_V_STRING + '.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.show()


# #------------------------ Case where total loss estimate is lower for polyfit iter compared with linear
# Filter for example site
eg_data_df = full_eg_data_df[full_eg_data_df['site_id'].isin(LINEAR_FIT_PREFERRED_EXAMPLE_SITE_ID_2)]

# Get list of c_ids
eg_c_id_list = eg_data_df['c_id'].drop_duplicates().tolist()

for c_id in eg_c_id_list:
    # Filter for c_id
    pv_data = eg_data_df[eg_data_df['c_id'] == c_id]
    pv_data['t_stamp_copy'] = pv_data.index
    pv_data['est_cf'] = pv_data['est_cf'].replace({0:np.nan})

    site_id = pv_data['site_id'].iloc[0]

    # Plot PV over time (to check)
    fig, ax = plt.subplots()
    ax.plot(pv_data["t_stamp_copy"], pv_data["clean_cf"], '-o', markersize=2, linewidth=1, c=purple, label = 'PV generation')
    ax.plot(pv_data["t_stamp_copy"], pv_data["est_cf"], '-o', markersize=2, linewidth=1, c=colour_list[5], label = 'PV generation loss estimate (linear)')
    ax.plot(pv_data["t_stamp_copy"], pv_data["est_cf_polyfit_iter"], '-o', markersize=2, linewidth=1, c=colour_list[8],label='PV generation loss estimate (polyfit 2)')
    ax.fill_between(pv_data["t_stamp_copy"], pv_data["clean_cf"],0, color=purple, alpha=0.6)
    # ax.fill_between(pv_data["t_stamp_copy"], pv_data["cf"], pv_data["est_cf"], color=colour_list[5], alpha=0.5)
    # ax1 = ax.twinx()
    # ax1.plot(pv_data["t_stamp_copy"], pv_data["v"], '-o', markersize=4, linewidth=1, c='b')
    plt.xlabel('Time')
    plt.ylabel('Normalised Power (kW/kWac)')
    ax.xaxis.set_major_formatter(time_fmt)
    ax.legend(fontsize=15, loc='upper left')
    ax.set(ylim=(-0.05, 1.4))
    # fig.suptitle('site_id ' + str(site_id) + ' c_id ' + str(c_id), fontsize=16)
    # fig.set_size_inches(6, 4)
    fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'example_linear_method_preferred_due_to_total_PV_losses'
                + FIG_V_STRING + '.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.show()

# #------------------------
# #------------------------ Example plots - lost self consumption ------------------------
# #------------------------
EG_SELF_CONSUM_DATA_FILE_PATH = 'F:/05_Solar_Analytics/pv_lost_analysis_march_2017/'
EG_SELF_CONSUM_DATA_FILE_NAME = 'output_data_site_id_subset_NS_site_25325_v9_DATA_GRAB_polyfit_iter.csv'
self_consum_df = pd.read_csv(EG_SELF_CONSUM_DATA_FILE_PATH + EG_SELF_CONSUM_DATA_FILE_NAME, index_col='t_stamp', parse_dates=True)

# Get stuff to print
self_consum_df['t_stamp_copy'] = self_consum_df.index
self_consum_df['power_kW'] = self_consum_df['cf'] * self_consum_df['ac']
# Get estimated power at times when we need an estimate
self_consum_df['est_power_kW'] = self_consum_df['polyfit_iter'] * self_consum_df['ac']
self_consum_df.loc[self_consum_df['est_cf']==0,'est_power_kW'] = 0
# For printing
self_consum_df['lost_self_consumption'] = pd.concat([self_consum_df['Gross load'], self_consum_df['est_power_kW']], axis=1).min(axis=1)
self_consum_df.loc[self_consum_df['Gross load'] < self_consum_df['power_kW'], 'lost_self_consumption'] = 0
self_consum_df.loc[self_consum_df['est_cf']==0, 'lost_self_consumption'] = 0
# self_consum_df.loc[self_consum_df['power_kW']>0, 'lost_self_consumption'] = 0
# Set zeroes to nan
self_consum_df['est_cf'] = self_consum_df['est_cf'].replace({0:np.nan})
self_consum_df['est_power_kW'] = self_consum_df['est_power_kW'].replace({0:np.nan})
self_consum_df['lost_self_consumption'] = self_consum_df['lost_self_consumption'].replace({0:np.nan})


# Plot PV over time (to check)
fig, ax = plt.subplots()
ax.plot(self_consum_df["t_stamp_copy"], self_consum_df["power_kW"], '-', markersize=2, linewidth=1, c=purple, label = 'PV generation')
ax.plot(self_consum_df["t_stamp_copy"], self_consum_df["est_power_kW"], '-', markersize=2, linewidth=1, c=colour_list[5], label = 'PV generation estimate')
ax.fill_between(self_consum_df["t_stamp_copy"], self_consum_df["power_kW"],0, color=purple, alpha=0.8)
ax.fill_between(self_consum_df["t_stamp_copy"], self_consum_df["power_kW"], self_consum_df["est_power_kW"], color=colour_list[5], alpha=0.6, label='Lost PV export')
ax.plot(self_consum_df["t_stamp_copy"], self_consum_df["Gross load"], '-o', markersize=2, linewidth=1, c='goldenrod', label = 'Behind the meter load')
ax.fill_between(self_consum_df["t_stamp_copy"], self_consum_df["lost_self_consumption"], self_consum_df["power_kW"], color=colour_list[11], alpha=0.6, label='Lost PV self consumption')
# ****Add voltage
ax1 = ax.twinx()
ax1.plot(self_consum_df["t_stamp_copy"], self_consum_df["Voltage"], '-o', markersize=2, linewidth=1, c='lightgrey', label='Voltage', zorder=1)
ax1.set(ylim=(180, 270))
ax1.yaxis.set_ticks(np.arange(180, 270, 15))
ax1.grid(False)
ax1.set_ylabel('Voltage (V)')
ax1.legend(fontsize=15)
# *****
plt.xlabel('Time')
ax.set_ylabel('Power (kW)')
ax.xaxis.set_major_formatter(time_fmt)
ax.legend(fontsize=15)
# *** Bring legend in front of voltage
legend_1 = ax.legend(fontsize=15, loc=2, borderaxespad=1.)
legend_1.remove()
ax1.legend(fontsize=15,loc=1, borderaxespad=1.)
ax1.add_artist(legend_1)
# ***
ax.set(ylim=(-0.05, 6))
fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'example_lost_self_consumption_with_voltage'
            + FIG_V_STRING + '.pdf', bbox_inches='tight', pad_inches=0.1)
plt.show()

# #------------------------
# #------------------------ Example plots - identifying start and end points of curtailment ------------------------
# #------------------------
# Get data
eg_method_df = pd.read_csv(EXAMPLE_END_PTS_METHOD_DATA_FILE_PATH, index_col='t_stamp', parse_dates=True)
eg_method_df['clean_cf'] = eg_method_df['power_kW'] / eg_method_df['ac']

# Filter for example site
eg_data_df = eg_method_df[eg_method_df['site_id'].isin(LINEAR_FIT_PREFERRED_EXAMPLE_SITE_ID)]
c_id = eg_data_df['c_id'].iloc[0]
# Filter for c_id
pv_data = eg_data_df[eg_data_df['c_id'] == c_id]
pv_data['t_stamp_copy'] = pv_data.index

# Get box edges
box_1_edges = pv_data.between_time('08:40','09:10')
box_1_edges = box_1_edges.index.tolist()
# Create rectangle x coordinates
startTime = box_1_edges[0]
endTime = box_1_edges[-1]
# convert to matplotlib date representation
start = mdates.date2num(startTime)
end = mdates.date2num(endTime)
width = end - start

# Get box edges for second example
box_2_edges = pv_data.between_time('15:17','15:45')
box_2_edges = box_2_edges.index.tolist()
# Create rectangle x coordinates
startTime2 = box_2_edges[0]
endTime2 = box_2_edges[-1]
# convert to matplotlib date representation
start2 = mdates.date2num(startTime2)
end2 = mdates.date2num(endTime2)
width2 = end2 - start2

# Firstly, get the total day plot
fig, ax = plt.subplots()
ax.plot(pv_data["t_stamp_copy"], pv_data["clean_cf"], '-o', markersize=2, linewidth=1, c=purple, label = 'PV generation')
ax.fill_between(pv_data["t_stamp_copy"], pv_data["clean_cf"],0, color=purple, alpha=0.5)
# Add call out boxes for examples
rect = Rectangle((start, 0), width, 0.995, linewidth=2,edgecolor='red',facecolor='none', linestyle='-', label='Curtail start and end examples')
ax.add_patch(rect)
rect = Rectangle((start2, 0), width2, 0.995, linewidth=2,edgecolor='red',facecolor='none', linestyle='-')
ax.add_patch(rect)
plt.xlabel('Time')
plt.ylabel('Normalised Power (kW/kWac)')
ax.xaxis.set_major_formatter(time_fmt)
ax.legend(fontsize=15, loc='upper left')
ax.set(ylim=(-0.05, 1.2))
plt.show()
fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'example_get_start_and_end_pts_1'
            + FIG_V_STRING + '.pdf', bbox_inches='tight', pad_inches=0.1)


# #------------------------ Curtail start
# Filter for 8am - 10am
pv_data_AM_curtail_period = pv_data.between_time('08:40','09:10')
# Get possible start points for plotting
pv_data_AM_curtail_period['start_flags_temp'] = pv_data_AM_curtail_period["clean_cf"]*pv_data_AM_curtail_period['start_deriv_flag']
pv_data_AM_curtail_period['start_flags_temp'] = pv_data_AM_curtail_period['start_flags_temp'].replace({0:np.nan})
# Get the actual start points for plotting
pv_data_AM_curtail_period['actual_start_pt_temp'] = pv_data_AM_curtail_period["clean_cf"]*pv_data_AM_curtail_period['start_pts']
pv_data_AM_curtail_period['actual_start_pt_temp'] = pv_data_AM_curtail_period['actual_start_pt_temp'].replace({0:np.nan})
# boundaries on first deriv
pv_data_AM_curtail_period['upper_bound'] = 0.05
pv_data_AM_curtail_period['lower_bound'] = -0.05
pv_data_AM_curtail_period['deriv_start_flags_temp'] = pv_data_AM_curtail_period["cf_first_deriv"]*pv_data_AM_curtail_period['start_deriv_flag']
pv_data_AM_curtail_period['deriv_start_flags_temp'] = pv_data_AM_curtail_period['deriv_start_flags_temp'].replace({0:np.nan})

# Get time stamps for AM annotations
time_stamp_start_df = pv_data.between_time('08:57','08:59')
time_stamp_start_list = time_stamp_start_df.index.tolist()
time_stamp_label_df = pv_data.between_time('09:00','09:01')
time_stamp_label_list = time_stamp_label_df.index.tolist()

# Create subplots (these will be stacked on top of each other)
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.set_size_inches(8, 8.7)
plt.subplots_adjust(hspace = 0.4)
# CF
ax1.plot(pv_data_AM_curtail_period["t_stamp_copy"], pv_data_AM_curtail_period["clean_cf"], '-o', markersize=3, linewidth=1, c=purple, label = 'PV generation')
ax1.plot(pv_data_AM_curtail_period["t_stamp_copy"], pv_data_AM_curtail_period['start_flags_temp'],'D', markersize=5, fillstyle= 'none', markeredgewidth=2, c=colour_list[5], label = 'Possible curtail start points')
ax1.plot(pv_data_AM_curtail_period["t_stamp_copy"], pv_data_AM_curtail_period['actual_start_pt_temp'],'D', markersize=5, fillstyle= 'none', markeredgewidth=2, c='orangered', label = 'Curtail start point')
ax1.fill_between(pv_data_AM_curtail_period["t_stamp_copy"], pv_data_AM_curtail_period["clean_cf"],0, color=purple, alpha=0.5)
ax1.set(ylabel='   Normalised power (kW/kWac)', xlabel='')
ax1.xaxis.set_major_formatter(time_fmt)
ax1.legend(fontsize=15, loc='upper left')
ax1.set(ylim=(-0.05, 1.2))
ax1.annotate('First derivative outside', xy=(time_stamp_start_list[0], 0.67),xytext=(time_stamp_label_list[0], 0.82), fontsize=14)
ax1.annotate('the threshold and prior to', xy=(time_stamp_start_list[0], 0.67),xytext=(time_stamp_label_list[0], 0.72), arrowprops=dict(arrowstyle='-|>', color='black'), fontsize=14)
ax1.annotate('zero value points (Eq. 6)', xy=(time_stamp_start_list[0], 0.67),xytext=(time_stamp_label_list[0], 0.62),fontsize=14)
ax1.annotate('Last non-zero point (Eq. 4)', xy=(time_stamp_start_list[1], 0.22),xytext=(time_stamp_label_list[0], 0.3),arrowprops=dict(arrowstyle='-|>', color='black'),fontsize=14)
# CF deriv
ax2.plot(pv_data_AM_curtail_period["t_stamp_copy"], pv_data_AM_curtail_period["cf_first_deriv"], 'o', markersize=4, linewidth=1, c=purple)

ax2.plot(pv_data_AM_curtail_period['t_stamp_copy'], pv_data_AM_curtail_period['upper_bound'], '--', c='black', label='Derivative threshold')
ax2.plot(pv_data_AM_curtail_period['t_stamp_copy'], pv_data_AM_curtail_period['lower_bound'], '--', c='black')
ax2.plot(pv_data_AM_curtail_period["t_stamp_copy"], pv_data_AM_curtail_period['deriv_start_flags_temp'],'D', markersize=5, fillstyle= 'none', markeredgewidth=2, c=colour_list[5])
ax2.set(ylabel='Normalised power derivative   ', xlabel='Time')
ax2.xaxis.set_major_formatter(time_fmt)
ax2.legend(fontsize=15, loc='upper left')
ax2.set(ylim=(-0.5, 0.5))
# ax2.annotate('The derivative is outside', xy=(time_stamp_start_list[0], -0.45),xytext=(time_stamp_label_list[0], -0.25),arrowprops=dict(facecolor='black', shrink=0.05, width=2),fontsize=14)
# ax2.annotate('bounds and the next point', xy=(time_stamp_start_list[0], -0.45),xytext=(time_stamp_label_list[0], -0.35),fontsize=14)
# set y axis to percentage
vals = ax2.get_yticks()
ax2.set_yticklabels(['{:,.0%}'.format(x) for x in vals])
# Save
plt.tight_layout()
fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'example_get_start_and_end_pts_2'
            + FIG_V_STRING + '.pdf', bbox_inches='tight', pad_inches=0.1)

# #------------------------ Curtail end
# Filter for 8am - 10am
pv_data_PM_curtail_period = pv_data.between_time('15:15','15:45')
# Get end possible end points for plotting
pv_data_PM_curtail_period['end_flags_temp'] = pv_data_PM_curtail_period["clean_cf"]*pv_data_PM_curtail_period['end_deriv_flag']
pv_data_PM_curtail_period['end_flags_temp'] = pv_data_PM_curtail_period['end_flags_temp'].replace({0:np.nan})
# Get the actual end points for plotting
pv_data_PM_curtail_period['actual_end_pt_temp'] = pv_data_PM_curtail_period["clean_cf"]*pv_data_PM_curtail_period['end_pts']
pv_data_PM_curtail_period['actual_end_pt_temp'] = pv_data_PM_curtail_period['actual_end_pt_temp'].replace({0:np.nan})
# boundaries on first deriv
pv_data_PM_curtail_period['upper_bound'] = 0.05
pv_data_PM_curtail_period['lower_bound'] = -0.05
pv_data_PM_curtail_period['deriv_end_flags_temp'] = pv_data_PM_curtail_period["cf_first_deriv"]*pv_data_PM_curtail_period['end_deriv_flag']
pv_data_PM_curtail_period['deriv_end_flags_temp'] = pv_data_PM_curtail_period['deriv_end_flags_temp'].replace({0:np.nan})

# Get time stamps for annotations
time_stamp_end_df = pv_data.between_time('15:31','15:39')
time_stamp_end_list = time_stamp_end_df.index.tolist()
time_stamp_label_df = pv_data.between_time('15:29','15:30')
time_stamp_label_list = time_stamp_label_df.index.tolist()

# Create subplots (these will be stacked on top of each other)
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.set_size_inches(8, 8.7)
plt.subplots_adjust(hspace = 0.4)
# CF
ax1.plot(pv_data_PM_curtail_period["t_stamp_copy"], pv_data_PM_curtail_period["clean_cf"], '-o', markersize=3, linewidth=1, c=purple, label = 'PV generation')
ax1.plot(pv_data_PM_curtail_period["t_stamp_copy"], pv_data_PM_curtail_period['end_flags_temp'],'D', markersize=5, fillstyle= 'none', markeredgewidth=2, c=colour_list[5], label = 'Possible curtail end points')
ax1.plot(pv_data_PM_curtail_period["t_stamp_copy"], pv_data_PM_curtail_period['actual_end_pt_temp'],'D', markersize=5, fillstyle= 'none', markeredgewidth=2, c='orangered', label = 'Curtail end point')
ax1.fill_between(pv_data_PM_curtail_period["t_stamp_copy"], pv_data_PM_curtail_period["clean_cf"],0, color=purple, alpha=0.5)
ax1.set(ylabel='   Normalised power (kW/kWac)', xlabel='')
ax1.xaxis.set_major_formatter(time_fmt)
ax1.legend(fontsize=15, loc='upper left')
ax1.set(ylim=(-0.05, 1.2))
ax1.annotate('First non-zero', xy=(time_stamp_end_list[0], 0.002),xytext=(time_stamp_label_list[0], 0.22),fontsize=14, ha='right')
ax1.annotate('point (Eq. 7) ', xy=(time_stamp_end_list[0], 0.002),xytext=(time_stamp_label_list[0], 0.12),arrowprops=dict(arrowstyle='-|>', color='black'),fontsize=14, ha='right')
ax1.annotate('Last derivative outside', xy=(time_stamp_end_list[3], 0.67),xytext=(time_stamp_end_list[0], 0.5),arrowprops=dict(arrowstyle='-|>', color='black'),fontsize=14, ha='right')
ax1.annotate('the threshold (Eq. 8)   ', xy=(time_stamp_end_list[3], 0.67),xytext=(time_stamp_end_list[0], 0.4),fontsize=14, ha='right')
ax1.annotate('Curtailment end point', xy=(time_stamp_end_list[4], 0.82),xytext=(time_stamp_end_list[4], 1),arrowprops=dict(arrowstyle='-|>', color='black'),fontsize=14, ha='center')
# CF deriv
ax2.plot(pv_data_PM_curtail_period["t_stamp_copy"], pv_data_PM_curtail_period["cf_first_deriv"], 'o', markersize=4, linewidth=1, c=purple)
ax2.plot(pv_data_PM_curtail_period['t_stamp_copy'], pv_data_PM_curtail_period['upper_bound'], '--', c='black', label='Derivative threshold')
ax2.plot(pv_data_PM_curtail_period['t_stamp_copy'], pv_data_PM_curtail_period['lower_bound'], '--', c='black')
ax2.plot(pv_data_PM_curtail_period["t_stamp_copy"], pv_data_PM_curtail_period['deriv_end_flags_temp'],'D', markersize=5, fillstyle= 'none',markeredgewidth=2, c=colour_list[5])
ax2.set(ylabel='Normalised power derivative   ', xlabel='Time')
ax2.xaxis.set_major_formatter(time_fmt)
ax2.legend(fontsize=15, loc='upper left')
ax2.set(ylim=(-0.5, 0.5))
# set y axis to percentage
vals = ax2.get_yticks()
ax2.set_yticklabels(['{:,.0%}'.format(x) for x in vals])
# Save
plt.tight_layout()
fig.savefig(SUM_STAT_DATA_PATH + '/Images/' + 'example_get_start_and_end_pts_3'
            + FIG_V_STRING + '.pdf', bbox_inches='tight', pad_inches=0.1)







# # TODO - EXPERIMENTAL AND UNFINISHED
# #------------------------ Plot 0 ------------------------
# a_ts_df = pd.read_csv(SUM_STAT_DATA_PATH + data_date_list[0] + '_analysis_profiles_v1_all_data.csv', index_col = 't_stamp', parse_dates=True)
# # get list of impacted sites
# a = a[a['percentage_lost']>=0.02]
# a = a[a['percentage_lost']<=0.10]
# site_list_in_a = a['site_id'].drop_duplicates().tolist()
# short_list = site_list_in_a[0:25]
# print(short_list)
#
# # for site in short_list:
# #     temp_df = a_ts_df[a_ts_df['site_id']==site]
# #     temp_df['time_copy'] = temp_df.index
# #     print(temp_df)
# #     # Plot data
# #     fig, ax= plt.subplots()
# #     ax.plot(temp_df["time_copy"], temp_df["cf"], '-o', markersize=4, linewidth=1, c='g')
# #     ax.plot(temp_df["time_copy"], temp_df["est_cf"], '-o', markersize=4, linewidth=1, c='r')
# #     ax1 = ax.twinx()
# #     ax1.plot(temp_df["time_copy"], temp_df["v"], '-o', markersize=4, linewidth=1, c='b')
# #     fig.suptitle(str(site), fontsize=16)
# #     plt.show()
#
# # Extract data for chosen site (131661938)
# a_ts_df = pd.read_csv(SUM_STAT_DATA_PATH + '2018-01-16_analysis_profiles_polyfit_v1_005sensitivity.csv', index_col = 't_stamp', parse_dates=True)
# data_selected_site = a_ts_df[a_ts_df['site_id'] == 157819957]
# data_selected_site.to_csv(SUM_STAT_DATA_PATH + '2018-01-16_site_157819957.csv')
#
# check_site_157819957 = a[a['site_id'] == 157819957]
#
#
# # Extract data for chosen site (131661938)
# x_ts_df = pd.read_csv(SUM_STAT_DATA_PATH + '2018-12-25_analysis_profiles_polyfit_v1_005sensitivity.csv', index_col = 't_stamp', parse_dates=True)
# data_selected_site = x_ts_df[x_ts_df['site_id'] == 1673664627]
# data_selected_site.to_csv(SUM_STAT_DATA_PATH + '2018-12-25_site_1673664627.csv')


#------------------------ Plot 11 - V vs PV penetration ------------------------
# Scatter plot of average average voltage (y) and PV penetration (x) with one data point for each site and for each day

# NOTE - choose whether to filter version_1 or version_2. Ve careful.
filtered_for_high_penetration = all_days_df_excl_zero_curtail_sites[all_days_df_excl_zero_curtail_sites['pv_penetration'] <=1.0]

# First check voltage versus pv penetration
list1 = filtered_for_high_penetration['pv_penetration'].tolist()
list2 = filtered_for_high_penetration['mean_v_all_daylight_hours'].tolist()
r_value = np.corrcoef(list1,list2)
print(r_value)
ax = sns.regplot(x='pv_penetration', y='mean_v_all_daylight_hours', data = filtered_for_high_penetration)
plt.show()

# Then check voltage versus pv loss
list1 = filtered_for_high_penetration['kWh_lost_per_day_per_kWac'].tolist()
list2 = filtered_for_high_penetration['mean_v_all_daylight_hours'].tolist()
r_value = np.corrcoef(list1,list2)
print(r_value)
ax = sns.regplot(x='mean_v_all_daylight_hours', y='kWh_lost_per_day_per_kWac', data = filtered_for_high_penetration)
plt.show()

# Then check penetration versus pv loss
list1 = filtered_for_high_penetration['kWh_lost_per_day_per_kWac'].tolist()
list2 = filtered_for_high_penetration['pv_penetration'].tolist()
r_value = np.corrcoef(list1,list2)
print(r_value)
ax = sns.regplot(x='pv_penetration', y='kWh_lost_per_day_per_kWac', data = filtered_for_high_penetration)
plt.show()

# #------------------------ Plot 12 - mapping curtailment (plotly express) ------------------------
# curtail_by_pc_df = pd.DataFrame({'average_voltage' : all_days_df.groupby('s_postcode')['mean_v_all_daylight_hours'].mean(),
#                                  'average_percentage_curtail': all_days_df.groupby('s_postcode')['percentage_lost'].mean(),
#                                  'lat' : all_days_df.groupby('s_postcode')['lat'].first(),
#                                  'lon' : all_days_df.groupby('s_postcode')['lon'].first(),
#                                  'postcode': all_days_df.groupby('s_postcode')['s_postcode'].first()})
#
# # May need to fill na with zero before plotting.
# curtail_by_pc_df['average_percentage_curtail'] = curtail_by_pc_df['average_percentage_curtail'].fillna(0)
# # px.set_mapbox_access_token(open(".mapbox_token").read())
# fig = px.scatter_mapbox(curtail_by_pc_df, lat='lat', lon='lon', color='average_percentage_curtail')
# fig.update_layout(mapbox_style="open-street-map")
# fig.show()
