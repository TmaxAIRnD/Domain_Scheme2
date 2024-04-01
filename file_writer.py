from dataclasses import asdict, fields
import csv

def save_to_csv(filename, data, model):
    fieldnames = [field.name for field in fields(model)]
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow(asdict(item))
