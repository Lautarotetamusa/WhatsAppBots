import phonenumbers
import json
import csv

#Para convertir un json que sale de airbyte en un csv que pueda usar
def json2csv(filepath):
    with open(filepath, "r") as jsonfile:
        posts = json.load(jsonfile)

    outpath = filepath.replace('.json', '_parse.csv')
    print(outpath)
    with open(outpath, "w") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(posts[0]["_airbyte_data"].keys())
        for post in posts:
            csv_writer.writerow(post["_airbyte_data"].values())

def parse_phones(file):

    #Remove duplicateds
    with open(file.path, "r") as infile:
        posts  = csv.DictReader(infile)
        headers = next(posts).keys()

        res = []
        for post in posts:
            if post["phone"] not in [i["phone"] for i in res]:
                    res.append(post)

    #Parse phones
    outpath = file.path.replace('.csv', '_parse.csv')
    with open(outpath, "w") as outfile:
        outcsv = csv.writer(outfile)
        outcsv.writerow(headers)
        for post in res:
            try:
                number = phonenumbers.parse(post["phone"], "MX")
                parse_number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL)
                post["phone"] = "521"+parse_number.replace(" ","")

                outcsv.writerow(post.values())
            except Exception as e:
                print("Wrong", post["phone"])
    return file.name.replace('.csv', '_parse.csv')

def remove_duplicateds(filepath):
    with open(filepath) as infile:
        res = []
        posts  = csv.DictReader(infile)

        len = 0
        for post in posts:
            len += 1
            if post["phone"] not in [i["phone"] for i in res]:
                res.append(post)

        print(len)
        print(len(res))

if __name__ == '__main__':
    file = "../media/posts/inmuebles24.csv"
    parse_phones(file)
