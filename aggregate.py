#!/usr/bin/env python
import glob
import json


def consolidate(pattern):
    sparse = {}
    consolidated = []
    outfilename = '{}.json'.format(pattern)
    for file in glob.glob("{}*.json".format(pattern)):
        print(file)
        with open(file) as jsonfile:
            data = json.load(jsonfile)
            for i, serie in enumerate(data):
                if not i in sparse:
                    sparse[i] = {}
                for point in serie:
                    timestamp = point['date']
                    sparse[i][timestamp] = point['value']

    for i in sparse:
        newlist = []
        for date in sorted(sparse[i].keys()):
            newlist.append(dict(date=date, value=sparse[i][date]))
        consolidated.append(newlist)

    with open(outfilename,'w') as outfile:
        print('output in {}'.format(outfilename))
        json.dump(consolidated,outfile)


if __name__ == '__main__':
    consolidate('monthly')
    consolidate('weekly')
