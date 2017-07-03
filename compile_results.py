import datetime
import numpy as np
import gnuplotlib as gp
import csv


def get_results():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(1)
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
    gp.plot((np.array(range(len(data))), np.array([float(x[field]) for x in data]), {'with': 'lines'}), terminal = 'dumb 200, 40', unset = 'grid')
    return

def uptime():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(1)
    with open("pingresults.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        yester = yesterday.strftime('%Y-%m-%d')
        results = []
        for row in reader:
            if row['Date'] == yester:
                results.append(row)
    return results
    
def main():
    data = get_results()
    for cur in ['Download', 'Upload']:
        anal = analysis(data, cur)
        print "{}:\n\tAverage: {}\n\tMax: {}\n\tMin: {}".format(cur, anal['mean'], anal['max'], anal['min'])
        plotter(data, cur)
    ping = uptime()
    print "Total downtime: {} Minutes\nPercent Uptime: {}%".format(len(ping) - sum([int(x['Success']) for x in ping]), "{0:.2f}".format(float(sum([float(x['Success']) for x in ping])) / float(len(ping)) * 100))
    return
    
if __name__ == "__main__":
    main()