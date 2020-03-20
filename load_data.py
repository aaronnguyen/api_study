# since the description of the location has commas.
# will throw off a normal split(",")
# so using standard lib csv to parse
# update1: tried csv and found a null char.
#   will return back to original attempt.
import json

from pymongo import MongoClient


def get_data_from_line(str_line, len_fieldnames):

    # Based on given structure, description can throw off read
    #   so will grab the first elem, and the last few elem.
    #   Then assume whatever is left is the desc and rejoin it all
    lst_dataline = str_line.rstrip().split(",")
    data_list = []
    data_list.append(lst_dataline.pop(0))
    int_num_of_cols_look = len_fieldnames - 1

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

    fileread_csv = open(data_file, "r", newline='')
    header_row = None
    expected_commas = 0
    len_col = 0

    list_fulldata = {}
    error_list = {}

    build_string = ""
    for data_line in fileread_csv:
        if header_row is None:
            header_row = data_line.rstrip().split(",")
            len_col = len(header_row)
            expected_commas = len_col - 1

        else:
            build_string += data_line

            if build_string.count(",") < expected_commas:
                continue
            else:
                lst_rowdata = get_data_from_line(build_string, expected_commas)

                dict_rowdata = {}
                for x in range(0, len_col):
                    dict_rowdata[header_row[x]] = lst_rowdata[x]

                try:
                    dict_rowdata['latitude'] = float(dict_rowdata['latitude'])
                    dict_rowdata['longitude'] = float(
                        dict_rowdata['longitude'])

                    # list_fulldata.append(dict_rowdata)
                    list_fulldata[dict_rowdata["id"]] = dict_rowdata
                except TypeError:
                    error_list[dict_rowdata["id"]] = dict_rowdata

                build_string = ""

    json.dump(list_fulldata, open("data_fulldump.json", "w+"))
