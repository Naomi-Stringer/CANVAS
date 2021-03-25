# Util module
# List of useful functions


# Import required things
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
from matplotlib.patches import Rectangle
import calendar
import seaborn as sns; sns.set()
import itertools
import datetime
from time import gmtime, strftime
from matplotlib import cm


def distribution_plot_1(all_days_df, data_date_list, ax, colour_list):
    # Used to look like this: ax.plot(a['proportion_of_sites'], a['percentage_lost'], 'o-', markersize=4, linewidth=1, label=data_date_list[0], c=colour_list[0])
    # Have generalised so as to pass it all_days_df instead of 'a', 'b' etc.
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[0]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[0]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label=data_date_list[0], c=colour_list[0])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[1]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[1]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label=data_date_list[1], c=colour_list[0])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[2]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[2]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[2], c=colour_list[1])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[3]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[3]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[3], c=colour_list[1])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[4]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[4]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[4], c=colour_list[2])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[5]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[5]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[5], c=colour_list[2])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[6]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[6]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[6], c=colour_list[3])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[7]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[7]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[7], c=colour_list[3])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[8]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[8]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[8], c=colour_list[4])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[9]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[9]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[9], c=colour_list[4])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[10]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[10]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[10], c=colour_list[5])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[11]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[11]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[11], c=colour_list[5])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[12]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[12]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[12], c=colour_list[6])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[13]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[13]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[13], c=colour_list[6])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[14]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[14]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[14], c=colour_list[7])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[15]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[15]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[15], c=colour_list[7])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[16]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[16]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[16], c=colour_list[8])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[17]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[17]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[17], c=colour_list[8])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[18]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[18]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[18], c=colour_list[9])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[19]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[19]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[19], c=colour_list[9])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[20]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[20]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[20], c=colour_list[10])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[21]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[21]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[21], c=colour_list[10])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[22]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[22]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[22], c=colour_list[11])
    ax.plot(all_days_df[all_days_df['data_date'] == data_date_list[23]]['proportion_of_sites'], all_days_df[all_days_df['data_date'] == data_date_list[23]]['percentage_lost'], 'o-', markersize=3, linewidth=0.5, label= data_date_list[23], c=colour_list[11])

    # # get average by data date and plot on top in black
    # all_days_df_average = pd.DataFrame(all_days_df.groupby('site_id')['percentage_lost'].mean(),columns=['percentage_lost'])
    # all_days_df_average = all_days_df_average.sort_values('percentage_lost', ascending =False)
    # # Get % of systems
    # all_days_df_average['proportion_of_sites'] = range(len(all_days_df_average))
    # all_days_df_average['proportion_of_sites'] = (all_days_df_average['proportion_of_sites'] + 1) / len(all_days_df_average)
    # print(all_days_df_average)
    # # Add to plot
    # ax.plot(all_days_df_average['proportion_of_sites'], all_days_df_average['percentage_lost'], 'o-', markersize=4, linewidth=1, label= 'Average percentage lost by site', c='black')

    # Show worst case line
    rect = Rectangle((-0.05, -0.05), 0.1, 0.21, linewidth=1, edgecolor='black', facecolor='none', linestyle='--',zorder=25)
    ax.add_patch(rect)
    # get legend
    legend = ax.legend()
    plt.legend(ncol=3, title="Date", prop={'size': 12})
    # set y axis to percentage
    # vals = ax.get_yticks()
    # ax.set_yticklabels(['{:,.0%}'.format(x) for x in vals])
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    # set x axis as percentage
    # vals = ax.get_xticks()
    # ax.set_xticklabels(['{:,.0%}'.format(x) for x in vals])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1))
    # Axis labels
    plt.xlabel('Proportion of sites (all sites)')
    plt.ylabel('Estimated generation curtailed')
    # Axis limits
    # ax.set(ylim=(-0.0001, 0.7))
