import csv

if __name__ == "__main__":
    with open('output.csv', mode='w') as output_file:
        output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output_writer.writerow(['A', 'B', 'C'])
        output_writer.writerow(['D', 'E', 'F'])