import csv

batch_size = 5000  # Размер каждой "партии"
batch_num = 1  # Счетчик для имен файлов

with open('delcarts.csv', 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    header = next(csvreader)  # Пропускаем заголовок CSV
    rows = []
    for row in csvreader:
        rows.append(row)
        if len(rows) == batch_size:
            filename = f'out{batch_num}.txt'
            with open(filename, 'w') as outfile:
                cardnums = ",\n".join([r[0] for r in rows])
                outfile.write(f'update loyalty_cards set deleted = 1 where id in (\n{cardnums}\n);')
            batch_num += 1
            rows = []
    if len(rows) > 0:
        filename = f'out{batch_num}.txt'
        with open(filename, 'w') as outfile:
            cardnums = ",\n".join([r[0] for r in rows])
            outfile.write(f'update loyalty_cards set deleted = 1 where id in (\n{cardnums}\n);')
