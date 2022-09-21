import phonenumbers
import csv

def parse_phones(filepath):

    #Remove duplicateds
    with open(filepath, "r") as infile:
        posts  = csv.DictReader(infile)
        headers = next(posts).keys()

        res = []
        for post in posts:
            if post["phone"] not in [i["phone"] for i in res]:
                    res.append(post)

    #Parse phones
    outpath = filepath.replace('.csv', '_parse.csv')
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
    return outpath

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
