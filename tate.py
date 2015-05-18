__author__ = 'Rica Enriquez'

from pandas import *
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_style("white")
from incf.countryutils import transformations

# Suppress SettingWithCopyWarning
options.mode.chained_assignment = None

#Open artists data
df_artists = read_csv('artist_data.csv', skipinitialspace=True, low_memory=False)

# Columns to use in artwork data set
art_vars = ['artist', 'artistId', 'title', 'creditLine', 'year', 'acquisitionYear']

#Open artwork data
df_artwork = read_csv('artwork_data.csv', skipinitialspace=True, na_values=['no date'], usecols=art_vars, low_memory=False)

# Only use the pieces of work with a credit line.
df_art_credit = df_artwork[df_artwork.creditLine.notnull()]

# Divide the acquisition methods into keywords that are usually the first word
df_art_credit['acquisition'] = df_art_credit.apply(lambda row: (row.creditLine.split()[0].lower()),axis=1)

# Meaning of acquisition methods:
# presented - shown, but not owned by the museum
# purchased - bought directly by the museum
# bequeathed - given to the museum as part of a will
# accepted - given to the museum in exchange for tax
# commissioned - by the museum
# transferred - from another museum
# gift - from someone
# exchanged - from an artist
# partial - purchase/gift
# uncovered - after remounting

# Clean up some pieces that have keywords that are the same as another category
df_art_credit.acquisition = df_art_credit.acquisition.replace({'given': 'gift', 'offered': 'accepted',
                                                               '[uncovered': 'uncovered', 'acquired': 'partial'})

# The first word artist is for Artist Rooms. They all fall in either presented or acquired jointly.
def find_acquisition(entry):
    if 'presented' in entry.lower():
        return 'presented'
    elif 'acquired' in entry.lower():
        return 'acquired jointly'

df_art_credit.acquisition[df_art_credit['acquisition'] == 'artist'] = \
    df_art_credit[df_art_credit['acquisition'] == 'artist'].apply(lambda row: (find_acquisition(row.creditLine)), axis=1)

# Will look at time trends, so take out nulls/clean up - look at year created and acquisiton year
df_year_known = df_art_credit[df_art_credit.year.notnull()]
df_year_known.year = df_year_known.year.replace({'c.1997-9': '1998'})
df_year_known.year = df_year_known.year.astype(np.int64)

# Just look at these categories for now since most pieces are acquired through these methods
df_year_known_small = df_year_known[(df_year_known.acquisition == 'accepted') |
                                    (df_year_known.acquisition == 'bequeathed') |
                                    (df_year_known.acquisition == 'presented') |
                                    (df_year_known.acquisition == 'purchased')]
df_year_known_small = df_year_known_small[df_year_known_small.year <= df_year_known_small.acquisitionYear].reset_index()
df_year_known_small.acquisitionYear = df_year_known_small.acquisitionYear.astype(np.int64)

def find_presented(entry):
    if ('presented by the artist' in entry.lower()) | ('and the artist' in entry.lower()) \
            | ("artist's estate" in entry.lower()) | ('estate of the artist' in entry.lower()):
        return 'Artist'
    elif ('society' in entry.lower()) | ('fund' in entry.lower()) | ('foundation' in entry.lower()) | ('loan' in entry.lower()) \
            | ('subscribers' in entry.lower()) | ('bequest' in entry.lower()) | ('committee' in entry.lower()) \
            | ('patrons' in entry.lower()) | ('members' in entry.lower()) | ('university' in entry.lower()) \
            | ('institute' in entry.lower()) | ('museum' in entry.lower()) | ('gallery' in entry.lower()) \
            | ('galleries' in entry.lower()) | ('council' in entry.lower()) | ('federation' in entry.lower()) \
            | ('ministry' in entry.lower()) | ('association' in entry.lower()) | ('trust' in entry.lower()) \
            | ('friends' in entry.lower()) | ('collection' in entry.lower()) | ('galerie' in entry.lower()):
        return 'Groups'
    elif ('anonymous' in entry.lower()) | ('private collector' in entry.lower()) | ('by' not in entry.lower()):
        return 'Anonymous'
    else:
        # print entry
        return 'Named Individuals'
df_year_known_small['Artist Presented'] = 1
df_year_known_small['Artist Presented'] = df_year_known_small[df_year_known_small.acquisition == 'presented'].\
    apply(lambda row: find_presented(row.creditLine), axis=1)

# Plot after 1856 because there were 37,403 Turner paintings accepted that year, which shrinks the bar plot for accepted
# Plot number pieces per year for each method
years = np.arange(1875,2025)
g = sns.factorplot('acquisitionYear', data=df_year_known_small, hue='acquisition', col='acquisition',
                   x_order=years, kind="bar", margin_titles=True, sharey=False, palette=sns.color_palette("hls", 4))
g.set_ylabels(label="Pieces of Art Acquired")
g.set_xlabels(label='Acquisition Year')
g.set_xticklabels(step=25)
sns.plt.show()

presented_1975_artists = df_year_known[(df_year_known.acquisition == 'presented') & (df_year_known.acquisitionYear == 1975)]['artist'].unique()
print 'Number of unique artists purchased in 1997 was', len(presented_1975_artists)
pieces_1975 = len(df_year_known[(df_year_known['acquisitionYear'] == 1975) & (df_year_known["acquisition"] == 'presented')])
max_pieces = 0
print 'Artists whose pieces were presented in 1975 that had the most pieces, # pieces, and percent of total pieces presented that year'
for artist in presented_1975_artists:
    pieces = len(df_year_known[(df_year_known['artist'] == artist) &
                     (df_year_known['acquisitionYear'] == 1975) & (df_year_known["acquisition"] == 'presented')])
    if pieces > max_pieces:
        max_pieces = pieces
        print artist, max_pieces, float(max_pieces)/float(pieces_1975)*100.

purchased_1997_artists = df_year_known[(df_year_known.acquisition == 'purchased') & (df_year_known.acquisitionYear == 1997)]['artist'].unique()
print 'Number of unique artists purchased in 1997 was', len(purchased_1997_artists)
pieces_1997 = len(df_year_known[(df_year_known['acquisitionYear'] == 1997) & (df_year_known["acquisition"] == 'purchased')])
max_pieces = 0
print 'Artists whose pieces were purchased in 1997 that had the most pieces, # pieces, and percent of total pieces presented that year'
for artist in purchased_1997_artists:
    pieces = len(df_year_known[(df_year_known['artist'] == artist) &
                     (df_year_known['acquisitionYear'] == 1997) & (df_year_known["acquisition"] == 'purchased')])
    if pieces > max_pieces:
        max_pieces = pieces
        print artist, max_pieces, float(max_pieces)/float(pieces_1997)*100.

# Plot relation of acquisition year and year art piece completed
h = sns.FacetGrid(df_year_known_small, col='acquisition', hue='acquisition', margin_titles=True,
                  xlim=(1823, 2013), ylim=(1545, 2013), palette=sns.color_palette("hls", 4), legend_out=True)
h.map(plt.scatter, 'acquisitionYear', 'year', s=25, alpha=.25)
for ax in h.axes.flat:
    ax.plot((1823, 2013), (1823, 2013), c=".2", ls="--")
h.set_xlabels(label='Acquisition Year')
h.set_ylabels(label="Year of 'Completion'")
h.set_titles(['Accepted', 'Bequeathed', 'Presented', 'Purchased'])
sns.plt.show()

# Plot types of donors pieces were presented
df_year_known_small_presented = df_year_known_small[df_year_known_small['acquisition'] == 'presented']
# h = sns.lmplot('acquisitionYear', 'year', df_year_known_small_presented, 'Artist Presented', fit_reg=False, s=25, alpha=.25)
h = sns.FacetGrid(df_year_known_small_presented, col='Artist Presented', hue='Artist Presented', margin_titles=True,
                  xlim=(1823, 2013), ylim=(1545, 2013), palette=sns.color_palette("hls", 4), legend_out=False)
h.map(plt.scatter, 'acquisitionYear', 'year', s=25, alpha=.25)
for ax in h.axes.flat:
    ax.plot((1823, 2013), (1823, 2013), c=".2", ls="--")
h.set_xlabels(label='Acquisition Year')
h.set_ylabels(label="Year of 'Completion'")
h.set_titles('Presented Pieces by Presenter Type')
sns.plt.show()

# If year of acquisition is the same year of completion plot donor type
df_year_known_small_presented_same = df_year_known_small_presented[df_year_known_small_presented['acquisitionYear']
                                                                   == df_year_known_small_presented['year']]

h = sns.barplot(x='Artist Presented', data=df_year_known_small_presented_same, ci=None, palette=sns.color_palette("hls", 4), hline=.1)
# h.set_xlabels(label='Presenter Type')
# h.set_ylabels(label="Number of Pieces")
# h.set_titles('Presented Pieces by Presenter Type')
sns.plt.show()


df_groups = df_year_known_small_presented_same[df_year_known_small_presented_same['Artist Presented'] == 'Groups']
groups = df_groups.creditLine.unique()

def find_group(entry):
    if 'Chantrey Bequest' in entry:
        return 'Chantrey Bequest'
    elif 'Contemporary Art Society' in entry:
        return 'Contemporary Art Society'
    elif 'Institute of Contemporary Prints' in entry:
        return 'Institute of Contemporary Prints'
    elif 'Tate' in entry:
        return 'Tate Patrons/Friends'

df_groups['Groups'] = df_groups.apply(lambda row: find_group(row.creditLine), axis=1)
h=sns.barplot(x='Groups', data=df_groups, ci=None, palette=sns.color_palette("hls", 4), hline=.1)
# h.set_xlabels(label='Presenter Group Type')
# h.set_ylabels(label="Number of Pieces")
sns.plt.show()





# See which countries/continents artists came from for each year
def replace_country(entry):
    if entry == 'Unknown':
        return 'Unknown'
    if ('United Kingdom' in entry) | ('Braintree' in entry) | ('Egremont' in entry) | ('Kensington' in entry) | \
        ('Liverpool' in entry) | ('London' in entry) | ('Canterbury' in entry) | ('Plymouth' in entry) | \
        ('Epsom' in entry) | ('Wimbledon' in entry) | ('Blackheath' in entry) | ('Bermondsey' in entry) | \
        ('Douglas' in entry) | ('Melmerby' in entry) | ('Isle of Man' in entry) | ('Stoke on Trent' in entry) | \
        ('Beckington' in entry) | ('Edinburgh' in entry) | ('Hertfordshire' in entry) | ('Bristol' in entry) | \
        ('Rochdale' in entry) | ('Montserra' in entry) | ('Saint H\xc3\xa9lier' in entry):
        return 'United Kingdom of Great Britain & Northern Ireland'
    if ('United States' in entry) | ('Staten Island' in entry):
        return 'United States of America'
    if ('Polska' in entry) | ('Schlesien' in entry) | ('Niederschlesien' in entry):
        return 'Poland'
    if "Yisra'el" in entry:
        return 'Israel'
    if "Deutschland" in entry:
        return 'Germany'
    if 'Italia' in entry:
        return 'Italy'
    if 'Argentina' in entry:
        return 'Argentina'
    if ('Schweiz' in entry) | ('Solothurn' in entry):
        return 'Switzerland'
    if 'Suomi' in entry:
        return 'Finland'
    if 'Zhonghua' in entry:
        return 'China'
    if ('France' in entry) | ('Auteuil' in entry) | ('Charlieu' in entry):
        return 'France'
    if 'T\xc3\xbcrkiye' in entry:
        return 'Turkey'
    if 'Iraq' in entry:
        return 'Iraq'
    if 'Belgi\xc3\xab' in entry:
        return 'Belgium'
    if 'Rossiya' in entry:
        return 'Russian Federation'
    if 'Malaysia' in entry:
        return 'Malaysia'
    if 'Portugal' in entry:
        return 'Portugal'
    if 'Nederland' in entry:
        return 'Netherlands'
    if 'M\xc3\xa9xico' in entry:
        return 'Mexico'
    if 'Espa\xc3\xb1a' in entry:
        return 'Spain'
    if 'Brasil' in entry:
        return 'Brazil'
    if 'Ukrayina' in entry:
        return 'Ukraine'
    if 'Per\xc3\xba' in entry:
        return 'Peru'
    if 'Pakistan' in entry:
        return 'Pakistan'
    if 'Nihon' in entry:
        return 'Japan'
    if '\xc3\x8eran' in entry:
        return 'Iran'
    if 'Venezuela' in entry:
        return 'Venezuela'
    if 'Viet Nam' in entry:
        return 'Vietnam'
    if 'Rom\xc3\xa2nia' in entry:
        return 'Romania'
    if ('Australia' in entry) | ('Perth' in entry):
        return 'Australia'
    if "Al-Jaza'ir" in entry:
        return 'Algeria'
    if 'Canada' in entry:
        return 'Canada'
    if ('Sverige' in entry) | ('Stockholm' in entry):
        return 'Sweden'
    if '\xc3\x89ire' in entry:
        return 'Ireland'
    if 'New Zealand' in entry:
        return 'New Zealand'
    if 'Zambia' in entry:
        return 'Zambia'
    if 'Guyana' in entry:
        return 'Guyana'
    if 'Prathet Thai' in entry:
        return 'Thailand'
    if ('Beograd' in entry) | ('Novi Sad' in entry) | ('\xc5\xa0id' in entry):
        return 'Serbia'
    if ('Brno' in entry) | ('Cesk\xc3\xa1 Republika' in entry):
        return  'Czech Republic'
    if '\xc3\x96sterreich' in entry:
        return 'Austria'
    if 'South Africa' in entry:
        return 'South Africa'
    if 'Uganda' in entry:
        return 'Uganda'
    if 'Norge' in entry:
        return 'Norway'
    if 'Bharat' in entry:
        return 'India'
    if 'Bosna i Hercegovina' in entry:
        return 'Bosnia and Herzegovina'
    if 'Slovenija' in entry:
        return 'Slovenia'
    if 'Cuba' in entry:
        return 'Cuba'
    if 'Colombia' in entry:
        return 'Colombia'
    if 'Latvija' in entry:
        return 'Latvia'
    if 'Bulgaria' in entry:
        return 'Bulgaria'
    if 'Belarus' in entry:
        return 'Belarus'
    if 'Danmark' in entry:
        return 'Denmark'
    if 'Chile' in entry:
        return 'Chile'
    if 'Cameroun' in entry:
        return 'Cameroon'
    if "Al-Lubnan" in entry:
        return 'Lebanon'
    if 'Misr'in entry:
        return 'Egypt'
    if 'Makedonija' in entry:
        return 'Macedonia'
    if 'As-Sudan' in entry:
        return 'Sudan'
    if 'Eesti' in entry:
        return 'Estonia'
    if 'Slovensk\xc3\xa1 Republika' in entry:
        return 'Slovakia (Slovak Republic)'
    if 'B\xc3\xa9nin' in entry:
        return 'Benin'
    if 'Hrvatska' in entry:
        return 'Croatia'
    if 'Bahamas' in entry:
        return 'Bahamas'
    if 'Indonesia' in entry:
        return 'Indonesia'
    if 'Tanzania' in entry:
        return 'Tanzania'
    if 'Bangladesh' in entry:
        return 'Bangladesh'
    if 'Tunis' in entry:
        return 'Tunisia'
    if 'Magyarorsz\xc3\xa1g' in entry:
        return "Hungary"
    if 'Moldova' in entry:
        return 'Moldova'
    if 'Mauritius' in entry:
        return 'Mauritius'
    if ("Taehan Min'guk" in entry) | ("Choson Minjujuui In'min Konghwaguk" in entry):
        return 'Korea'
    if "Suriyah" in entry:
        return 'Syrian Arab Republic'
    if '\xc3\x8dsland' in entry:
        return 'Iceland'
    if 'Pilipinas' in entry:
        return 'Philippines'
    if 'Jamaica' in entry:
        return 'Jamaica'
    if 'Kenya' in entry:
        return 'Kenya'
    if 'Malta' in entry:
        return 'Malta'
    if 'Panam\xc3\xa1' in entry:
        return 'Panama'
    if 'Nicaragua' in entry:
        return 'Nicaragua'
    if 'Sri Lanka' in entry:
        return 'Sri Lanka'
    if 'Lietuva' in entry:
        return 'Lithuania'
    if 'Luxembourg' in entry:
        return 'Luxembourg'
    if 'Chung-hua Min-kuo' in entry:
        return 'Taiwan'
    if 'Lao' in entry:
        return "Lao People's Democratic Republic"
    if 'Shqip\xc3\xabria' in entry:
        return 'Albania'
    if 'Ell\xc3\xa1s' in entry:
        return 'Greece'
    if 'Charlotte Amalie' in entry:
        return 'United States Virgin Islands'
    return entry

def find_continent(country):
    if country == 'Unknown':
        return 'Unknown'
    else:
        return transformations.cn_to_ctn(country)

df_artists[df_artists.placeOfBirth.isnull()] = 'Unknown'

# Make new columns of country and continents from placeOfBirth Data
df_artists['country'] = df_artists.apply(lambda x: (replace_country(x.placeOfBirth)), axis=1)
df_artists['continent'] = df_artists.apply(lambda x: (find_continent(x.country)), axis=1)

def get_continent(artistId):
        return np.array_str(df_artists['continent'][df_artists['id'] == artistId].values)[2:-2]

# Let's focus on pieces after 1950!
df_post_1950 = df_year_known_small[(df_year_known_small.year >= 1950)]

# Match the continent each artist came from with each piece of artwork
df_post_1950['Artist Birth Continent'] = df_post_1950.apply(lambda x: (get_continent(x.artistId)), axis=1)

# Let's focus on pieces not in Europe!
df_post_1950_cut = df_post_1950[(df_post_1950['Artist Birth Continent'] != 'Europe')].reset_index()
df_post_1950_cut["Year Artwork 'Completed'"] = df_post_1950_cut['year']



print (df_post_1950_cut.groupby(["Year Artwork 'Completed'"]).size().sum())

grouped = DataFrame({'pieces': df_post_1950_cut.groupby(["Year Artwork 'Completed'", 'Artist Birth Continent']).size()
                               /(df_post_1950_cut.groupby(["Year Artwork 'Completed'"]).size())*100.}).reset_index()
grouped_rect = grouped.pivot('Artist Birth Continent', "Year Artwork 'Completed'", 'pieces')
grouped_rect = grouped_rect.fillna(0)
h = sns.heatmap(grouped_rect, yticklabels=['Unknown', 'Africa', 'Asia', 'North America', 'Oceania', 'South America'])
plt.show()

# Look to see which artists were hot in Asia and South America
SA_artists = df_post_1950_cut[(df_post_1950_cut['Artist Birth Continent'] == 'South America') &
                     (df_post_1950_cut["Year Artwork 'Completed'"] == 1976)].artist.unique()

print "South American Artists with work completed in 1976, number of pieces, and [acquisition year]"
for artist in SA_artists:
    print artist, len(df_post_1950_cut[(df_post_1950_cut['artist'] == artist) &
                     (df_post_1950_cut["Year Artwork 'Completed'"] == 1976)]),\
        df_post_1950_cut[(df_post_1950_cut['artist'] == artist) &
                         (df_post_1950_cut["Year Artwork 'Completed'"] == 1976)]['acquisitionYear'].unique()


Asian_artists = df_post_1950_cut[(df_post_1950_cut['Artist Birth Continent'] == 'Asia') &
                                 (df_post_1950_cut["Year Artwork 'Completed'"] == 2007)].artist.unique()

print "Asian Artists with work completed in 2007, number of pieces, and [acquisition year]"
for artist in Asian_artists:
        print artist, len(df_post_1950_cut[(df_post_1950_cut['artist'] == artist) &
                     (df_post_1950_cut["Year Artwork 'Completed'"] == 2007)]),\
        df_post_1950_cut[(df_post_1950_cut['artist'] == artist) &
                         (df_post_1950_cut["Year Artwork 'Completed'"] == 2007)]['acquisitionYear'].unique()

Asian_artists = df_post_1950_cut[(df_post_1950_cut['Artist Birth Continent'] == 'Asia') &
                                 (df_post_1950_cut["Year Artwork 'Completed'"] == 2011)].artist.unique()

print "Asian Artists with work completed in 2011, number of pieces, and [acquisition year]"
for artist in Asian_artists:
        print artist, len(df_post_1950_cut[(df_post_1950_cut['artist'] == artist) &
                     (df_post_1950_cut["Year Artwork 'Completed'"] == 2011)]),\
        df_post_1950_cut[(df_post_1950_cut['artist'] == artist) &
                         (df_post_1950_cut["Year Artwork 'Completed'"] == 2011)]['acquisitionYear'].unique()


Asian_artists = df_post_1950_cut[(df_post_1950_cut['Artist Birth Continent'] == 'Asia') &
                                 (df_post_1950_cut["Year Artwork 'Completed'"] == 2012)].artist.unique()

print "Asian Artists with work completed in 2012, number of pieces, and [acquisition year]"
for artist in Asian_artists:
        print artist, len(df_post_1950_cut[(df_post_1950_cut['artist'] == artist) &
                     (df_post_1950_cut["Year Artwork 'Completed'"] == 2012)]),\
        df_post_1950_cut[(df_post_1950_cut['artist'] == artist) &
                         (df_post_1950_cut["Year Artwork 'Completed'"] == 2012)]['acquisitionYear'].unique()
