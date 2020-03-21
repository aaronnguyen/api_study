import json

# from pymongo import MongoClient


# # TODO: flesh this out for usage.
# def load_mongo(dict_rowdata):

#     username = "mongoroot"
#     password = "mongorootpassword"
#     client = MongoClient('mongodb://%s:%s@localhost:27017/%s' % (
#         username, password, 'rentalproperties'))
#     mdb_rental = client.db.rentalproperties

#     r_id = mdb_rental.insert_one(dict_rowdata).inserted_id
#     return r_id
class dataconn(object):

    def __init__(self, csv_file=None, json_quickload=None):

        self.DATASET = {}
        self.error_list = {}

        # take json as priority since it is quicker
        if json_quickload is not None:
            self.DATASET = json.load(open(json_quickload, "r"))
        elif csv_file is not None:
            self._csv_parse(csv_file)

    def write_data_row(self, data_row):
        pass

    def get_data_row_iter(self):
        list_alldata = []
        for row_id in self.DATASET:
            row = self.DATASET[row_id]
            list_alldata.append(row)
        return list_alldata

    def get_data_row_by_id(self, id):
        return self.DATASET[id]

    # since the description of the location has commas.
    # will throw off a normal split(",")
    # so using standard lib csv to parse
    # update1: tried csv and found a null char.
    #   will return back to original attempt.
    def _get_data_from_line(self, str_line, len_fieldnames):

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
        #   should be a better way to determine if name string is complete.
        # What we know, a string with special chars
        #   are wrapped in double quotes.
        # could determine position of double quotes.
        # TODO: better optimization, this is just quick and dirty.
        list_data_hold.append(",".join(lst_dataline))

        # Because we were working backwards, we need to reverse the list.
        data_list.extend(reversed(list_data_hold))

        return data_list

    def _csv_parse(self, csv_file_path):

        fileread_csv = open(csv_file_path, "r", newline='')
        header_row = None
        expected_commas = 0
        len_col = 0

        build_string = ""
        for data_line in fileread_csv:

            # assume the first row is the header row. will get col's names
            if header_row is None:
                header_row = data_line.rstrip().split(",")
                len_col = len(header_row)
                expected_commas = len_col - 1

            else:
                # make an assumption data lines can span multiple lines
                build_string += data_line

                # if we are short on expected commas, then the request will
                #   fail due to not enough info.
                if build_string.count(",") < expected_commas:
                    continue
                else:
                    # will pass if we have enough column values to work with.
                    lst_rowdata = self.get_data_from_line(
                        build_string, expected_commas)

                    dict_rowdata = {}
                    for x in range(0, len_col):
                        dict_rowdata[header_row[x]] = lst_rowdata[x]

                    # try to convert to lat and long, required fields.
                    # if they fail, then save error row and we cna use that
                    #   to report back to submitter or to server.
                    try:
                        dict_rowdata['latitude'] = float(
                            dict_rowdata['latitude'])
                        dict_rowdata['longitude'] = float(
                            dict_rowdata['longitude'])

                        self.DATASET[dict_rowdata["id"]] = dict_rowdata
                    except TypeError:
                        self.error_list[dict_rowdata["id"]] = dict_rowdata

                    build_string = ""


if __name__ == "__main__":

    data_file = "AB_NYC_2019.csv"
    dbc = dataconn(csv_file=data_file)

    # primitive approach, but process the data once and just dump it all into.
    json.dump(dbc.DATASET, open("data_fulldump.json", "w+"))
