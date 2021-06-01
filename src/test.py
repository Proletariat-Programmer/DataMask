import csv


with open(f'static/analysis_result/2/SRR385938.tsv/tables/cluster.tsv', "r+") as file:
     rd = csv.reader(file, delimiter="\t", quotechar='"')
     for item in rd:
        print(item)

