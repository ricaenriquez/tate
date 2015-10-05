__author__ = 'rme38'

from pandas import *
options.mode.chained_assignment = None
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_style("white")

df_year_known_small = read_csv('tate_years.csv')
# years = np.arange(1875,2025)
# g = sns.factorplot('acquisitionYear',data=df_year_known_small,hue='acquisition',col='acquisition',
#                    x_order=years,kind="bar",margin_titles=True,sharey=False,palette=sns.color_palette("hls",4))
# g.set_ylabels(label="Pieces of Art Acquired")
# g.set_xlabels(label='Acquisition Year')
# g.set_xticklabels(step=25)
# sns.plt.show()
# h = sns.FacetGrid(df_year_known_small,col='acquisition',hue='acquisition',margin_titles=True,
#                   xlim=(1823, 2013),ylim=(1545, 2013),palette=sns.color_palette("hls", 4))
# h.map(plt.scatter,'acquisitionYear','year',s=25,alpha=.25)
# for ax in h.axes.flat:
#     ax.plot((1823,2013),(1823,2013),c=".2",ls="--")
# h.set_xlabels(label='Acquisition Year')
# h.set_ylabels(label="Year of 'Completion'")
# h.set_titles(['Accepted','Bequeathed','Presented','Purchased'])
# sns.plt.show()

df_post_1950_cut = read_csv('tate_artists_birth.csv')
# grouped=DataFrame({'pieces': df_post_1950_cut.groupby(["Year Artwork 'Completed'",'Artist Birth Country']).size()}).reset_index()
# grouped_rect=grouped.pivot('Artist Birth Country',"Year Artwork 'Completed'",'pieces')
# grouped_rect=grouped_rect.fillna(0)
# sns.heatmap(grouped_rect, yticklabels=['Unknown','Africa','Asia','North America','Oceania','South America'])
# plt.show()
