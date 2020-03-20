# since the description of the location has commas.
# will throw off a normal split(",")
# so using standard lib csv to parse
# update1: tried csv and found a null char.
#   will return back to original attempt.
from pymongo import MongoClient


def get_data_from_line(str_line):
    # Based on given structure, description can throw off read
    #   so will grab the first elem, and the last few elem.
    #   Then assume whatever is left is the desc and rejoin it all
    lst_dataline = str_line.split(",")
    data_list = []

    data_list.append(lst_dataline.pop(0))
    int_num_of_cols_look = len(fieldnames) - 2

    list_data_hold = []
    for x in range(int_num_of_cols_look):
        list_data_hold.append(lst_dataline.pop(-1))
    # Whatever is left should be the description.
    list_data_hold.append(",".join(lst_dataline))

    data_list.extend(reversed(list_data_hold))

    return data_list


def load_mongo(dict_rowdata):

    username = "mongoroot"
    password = "mongorootpassword"
    client = MongoClient('mongodb://%s:%s@localhost:27017/%s' % (
        username, password, 'rentalproperties'))
    mdb_rental = client.db.rentalproperties

    r_id = mdb_rental.insert_one(dict_rowdata).inserted_id
    return r_id


if __name__ == "__main__":

    error_rows = []
    data_file = "AB_NYC_2019.csv"
    limit = 200

    fileread_csv = open(data_file, "r", newline='')
    fieldnames = None

    list_fulldata = []

    for raw_str_line in fileread_csv:
        # print(str_line)
        str_line = raw_str_line.rstrip()
        limit -= 1

        if fieldnames is None:
            # Making an assumption that no columns have a comma char in it.
            fieldnames = str_line.split(",")
            len_fieldnames = len(fieldnames)
        else:
            error = False

            # [footnote1]
            try:
                list_rowdata = get_data_from_line(str_line)
            except IndexError as ie:
                if "pop from empty list" in str(ie):
                    error_rows.append(str_line)
                    error = True
                else:
                    raise

            if len_fieldnames != len(list_rowdata):
                if error is False:
                    error_rows.append(str_line)
                    error = True

            else:
                dict_rowdata = {}
                for x in range(0, len_fieldnames):
                    dict_rowdata[fieldnames[x]] = list_rowdata[x]

                # mongo_id = load_mongo(dict_rowdata)
                list_fulldata.append(dict_rowdata)

        if limit == 0:
            break

    import json
    json.dump(list_fulldata, open("data_limiteddump.json", "w+"))

# [footnote1] TODO: figure out why it fails
#   Pretty sure because there is an empty line we are not considering.
#   If i get around to it, then I will figure out why.