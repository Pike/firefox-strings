import argparse
from collections import defaultdict
import json


if __name__=='__main__':
    p = argparse.ArgumentParser()
    p.add_argument('in_data')
    args = p.parse_args()
    with open(args.in_data) as infile:
        data = json.load(infile)

    yearly_w = defaultdict(lambda: defaultdict(int))
    yearly_s = defaultdict(lambda: defaultdict(int))
    monthly_wt = defaultdict(lambda: defaultdict(int))
    monthly_st = defaultdict(lambda: defaultdict(int))
    
    for item in data:
        d_w = yearly_w[item['year']]
        d_s = yearly_s[item['year']]
        for f, file_data in item['updates'].items():
            cat = 'browser'
            if 'mobile/' in f:
                cat = 'mobile'
            elif 'devtools/' in f:
                cat = 'devtools'
            d_w[cat] += file_data['words']
            d_s[cat] += file_data['strings']
        d_wt = monthly_wt[(item['year'], item['month'])]
        d_st = monthly_st[(item['year'], item['month'])]
        for f, file_data in item['totals'].items():
            cat = 'browser'
            if 'mobile/' in f:
                cat = 'mobile'
            elif 'devtools/' in f:
                cat = 'devtools'
            d_wt[cat] += file_data['words']
            d_st[cat] += file_data['strings']

    # find max for totals in a year
    yearly_wt = defaultdict(lambda: defaultdict(int))
    yearly_st = defaultdict(lambda: defaultdict(int))
    for (year, month), d in monthly_wt.items():
        for cat, cnt in d.items():
            yearly_wt[year][cat] = max(yearly_wt[year][cat], cnt)
    for (year, month), d in monthly_st.items():
        for cat, cnt in d.items():
            yearly_st[year][cat] = max(yearly_st[year][cat], cnt)

    print "Year\tbrowser\tmobile\tdevtools"
    for year, d in sorted(yearly_w.items()):
        print "\t".join([str(year), str(d.get('browser', '')), str(d.get('mobile', '')), str(d.get('devtools', ''))])

    print

    print "Year\tbrowser\tmobile\tdevtools"
    for year, d in sorted(yearly_s.items()):
        print "\t".join([str(year), str(d.get('browser', '')), str(d.get('mobile', '')), str(d.get('devtools', ''))])

    print

    print "Year\tbrowser\tmobile\tdevtools"
    for year, d in sorted(yearly_wt.items()):
        print "\t".join([str(year), str(d.get('browser', '')), str(d.get('mobile', '')), str(d.get('devtools', ''))])

    print

    print "Year\tbrowser\tmobile\tdevtools"
    for year, d in sorted(yearly_st.items()):
        print "\t".join([str(year), str(d.get('browser', '')), str(d.get('mobile', '')), str(d.get('devtools', ''))])
