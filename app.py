import io

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.style as style
import pandas as pd
import seaborn as sns
from flask import Flask, render_template, Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

style.use('seaborn-pastel')
sns.set_style('whitegrid')
sns.set_context('paper')
matplotlib.use('Agg')

# Initialising flask app
app = Flask(__name__)


# Home Route
@app.route('/')
def index():
    return render_template('index.html')


# Recommendation code logic starts from here
# importing the data
chicago = pd.read_csv('static/Chicago-DivvyBikes.csv',
                      parse_dates=['starttime', 'stoptime'],
                      dtype={'usertype': 'category',
                             'gender': 'category'})

# sorting the data according to the need for customer-types distribution
data = chicago.sort_values(by='starttime')
data = data.reset_index()


# Route for customer-type distribution analysis
@app.route('/customer-type-distribution')
def plot_png_customer_type():
    fig = create_figure_customer_type()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')


def create_figure_customer_type():
    fig, ax = plt.subplots(figsize=(8, 8))

    group_user = data.groupby('usertype').size()
    group_user.plot(kind='bar', title='Distribution of user types', rot=45)

    return fig


# Route for finding gender distribution analysis
@app.route('/gender-distribution')
def plot_png_gender_distribution():
    fig = create_figure_gender_distribution()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')


def create_figure_gender_distribution():
    fig, ax = plt.subplots(figsize=(8, 8))

    group_gender = data.groupby('gender').size()
    group_gender.plot(kind='bar', title='Distribution of genders', rot=45, color=['pink', 'lightblue'])

    return fig


# Route for finding Age group distribution analysis
# Changing the data according to required format
data = data.sort_values(by='birthyear')


@app.route('/age-distribution')
def plot_png_age_distribution():
    fig = create_figure_age_distribution()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')


def create_figure_age_distribution():
    fig, ax = plt.subplots(figsize=(12, 8))

    group_by_birth_year = data.groupby('birthyear').size()
    group_by_birth_year.plot(kind='bar', title='Distribution of birth years')

    return fig


# Route for Date-Time Distribution analysis
data = data.set_index('starttime')


@app.route('/date-time-distribution')
def plot_png_date_time_distribution():
    fig = create_figure_date_time_distribution()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')


def create_figure_date_time_distribution():
    fig, ax = plt.subplots(figsize=(14, 10))

    plt.subplot(2, 2, 1)
    data.groupby(data.index.month)['tripduration'].count().plot.bar(
        title='Distribution of # trips by month', rot=0)
    plt.xlabel('Month')
    plt.ylabel('# trips')

    plt.subplot(2, 2, 2)
    data.groupby(data.index.day)['tripduration'].count().plot.bar(
        title='Distribution of # trips by day', rot=0)
    plt.xlabel('Day')
    plt.ylabel('# trips')

    ax = plt.subplot(2, 2, 3)
    data.groupby(data.index.weekday)['tripduration'].count().plot.bar(
        title='Distribution of # trips by day of the week', rot=0)
    plt.xlabel('Day of the week')
    plt.ylabel('# trips')
    ax.set_xticklabels(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    plt.subplot(2, 2, 4)
    data.groupby(data.index.hour)['tripduration'].count().plot.bar(
        title='Distribution of # trips by hour', rot=0)
    plt.xlabel('Hour')
    plt.ylabel('# trips')

    return fig


# Route for Most used and least used station analysis
# This logic finds out bike stations with their usage and ranks them according to their usage
most_used_start_station = chicago.groupby('from_station_name').count()['trip_id'].reset_index()
most_used_start_station.rename(columns={'trip_id': 'rides_booked', 'from_station_name': 'station_name'}, inplace=True)

top_10_stations = most_used_start_station.sort_values('rides_booked', ascending=False)[:10]
bottom_10_stations = most_used_start_station.sort_values('rides_booked')[:10]


@app.route('/most-used-distribution')
def plot_png_most_used_distribution():
    fig = create_figure_most_used_distribution()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')


def create_figure_most_used_distribution():
    fig, ax = plt.subplots(figsize=(12, 8))

    sns.barplot(data=top_10_stations, x='station_name', y='rides_booked', palette=sns.color_palette("crest", n_colors=len(top_10_stations) + 4), ax=ax)

    plt.title("Most Popular Divvy Bike Stations in Chicago")
    plt.xlabel("Station Names")
    plt.ylabel('Number of Trips Originating from Station')

    ax.set_xticklabels(ax.get_xticklabels(), rotation=10, horizontalalignment='right')
    ax.bar_label(ax.containers[0])

    plt.show()

    return fig


@app.route('/least-used-distribution')
def plot_png_least_used_distribution():
    fig = create_figure_least_used_distribution()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')


def create_figure_least_used_distribution():
    fig, ax = plt.subplots(figsize=(12, 8))

    sns.barplot(data=bottom_10_stations, x='station_name', y='rides_booked', palette=sns.color_palette("crest", n_colors=len(top_10_stations) + 4), ax=ax)

    plt.title("Least Popular Divvy Bike Stations in Chicago")
    plt.xlabel("Station Names")
    plt.ylabel('Number of Trips Originating from Station')

    ax.set_xticklabels(ax.get_xticklabels(), rotation=10, horizontalalignment='right')
    ax.bar_label(ax.containers[0])

    plt.show()

    return fig


if __name__ == '__main__':
    app.run(debug=True)
