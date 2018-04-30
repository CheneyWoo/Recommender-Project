import download_and_write

series_url_list = []
with open("hot_series.txt", 'r') as f:
    for line in f.readlines():
        if line.startswith('h'):
            series_url_list.append(line.strip())

#print(series_url_list[21])
download_and_write.write_first_row()
counter1 = 0
counter2 = 0

for series in series_url_list:
    counter2 += download_and_write.Page(series).num_of_product
    counter1 += 1
    print("第%d个系列下载完毕"%counter1)
print("累计下载了%d个系列，%d个单品"%(counter1,counter2))