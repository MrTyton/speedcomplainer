import datetime
import numpy as np
import gnuplotlib as gp
import csv
from os import remove
from optparse import OptionParser


def get_results(date=1):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(date)
    with open("speedresults.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        yester = yesterday.strftime('%Y-%m-%d')
        results = []
        for row in reader:
            if row['Date'] == yester:
                results.append(row)
    return results
        
        
def analysis(data, field):
    if field not in data[0].keys():
        raise Exception("Fieldname not found.")
    datums = [float(x[field]) for x in data]
    return {'min': min(datums), 'max': max(datums), 'mean': "{0:.2f}".format(sum(datums) / len(datums))}
    
def plotter(data, field):
    if field not in data[0].keys():
        raise Exception("Fieldname not found.")
        
    def convert(datum):
        time = datum['Time'].split(":")
        time = float(time[0]) + float(time[1])/60.
        return time
    
    gp.plot((np.array([convert(datum) for datum in data]), np.array([float(x[field]) for x in data]), {'with': 'lines'}), terminal = 'dumb 200, 40', unset = 'grid', ascii=True, output="temp.txt", xlabel="Hour (24)", y2label="Speed (Mb/s)", set="xtics 1")
    with open("temp.txt", "r") as fp:
        print fp.read()
    remove("temp.txt")
    return

def uptime(date=1):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(date)
    with open("pingresults.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        yester = yesterday.strftime('%Y-%m-%d')
        results = []
        for row in reader:
            if row['Date'] == yester:
                results.append(row)
    return results
    
def main(date, plot):
    data = get_results(date)
    for cur in ['Download', 'Upload']:
        anal = analysis(data, cur)
        print "{}:\n\tAverage: {}\n\tMax: {}\n\tMin: {}".format(cur, anal['mean'], anal['max'], anal['min'])
        if plot: plotter(data, cur)
    ping = uptime(date)
    print "Total downtime: {} Minutes\nPercent Uptime: {}%".format(len(ping) - sum([int(x['Success']) for x in ping]), "{0:.2f}".format(float(sum([float(x['Success']) for x in ping])) / float(len(ping)) * 100))
    return
    
if __name__ == "__main__":
    option_parser = OptionParser(usage="usage: %prog [flags]")
    option_parser.add_option('-d', '--date', action='store', dest='date', default=1, type="int", help='How many days back you want to run on the data.')
    option_parser.add_option('-p', '--plot', action='store_true', dest='plot', help='Plot the upload and download speed over the course of the day.')
    (options, args) = option_parser.parse_args()
    main(options.date, options.plot)