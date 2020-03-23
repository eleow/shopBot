import csv

WHATIS_SOURCE = 'SystemCode/Fulfillment/data/glossary_cleaned.csv'
whatis_list = []

with open(WHATIS_SOURCE, mode='r', encoding="utf-8-sig") as infile:
    reader = csv.reader(infile)
    for row in reader:

        whatis_list.append(row[0].strip().lower() + '\n')

        # Expand synonyms / Copy description and source
        if (row[3] != ''):
            synonyms = row[3].split(',')
            for s in synonyms:
                whatis_list.append(s.strip().lower() + '\n')

print(whatis_list)
with open('entity_whatis_term_NEW.txt', 'w+') as f:
    f.writelines(whatis_list)
