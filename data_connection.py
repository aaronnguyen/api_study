"""
Created a data connection object to make it easier to reimplement without
affecting the main api app code.

Originally started to implement a mongodb connector out of curiousity but
spent more time debugging the connection and decided to do a simulated
data implementation instead.
"""
import json
import sys
import os


class dataconn(object):

    def __init__(self, csv_file=None, json_quickload=None):

        # Let us simulate persistence
        self.DATASET = {}
        persistent_path = "data_fulldump.json"
        if os.path.exists(persistent_path):
            self.DATASET = json.load(open(persistent_path, "r"))

        # TODO: Implement a way to digest errors,
        # currently just a placeholder to store the data.
        self.error_list = {}

        if csv_file is not None:
            self._csv_parse(csv_file)

    def write_data_row(self, dict_rowdata):
        """
        #### Input:

        - Dictionary data row

        #### Desc:

        To depict writing data into a database.
        If the id exists, what should we do? Update or return collision error?
        Went ahead with collision error.
        """
        if dict_rowdata["id"] in self.DATASET:
            self.error_list[dict_rowdata["id"]] = dict_rowdata
            self.error_list[dict_rowdata["id"]]["error"] = "doc_id collision"
        else:
            self.DATASET[dict_rowdata["id"]] = dict_rowdata

        # TODO: Implement proper data verification to reduce junk data.
        if "id" not in dict_rowdata:
            return False, "Missing Fields"
        return True, dict_rowdata["id"]

    def commit(self):
        # Primitive approach, but just write new to file to "save"
        json.dump(self.DATASET, open("data_fulldump.json", "w+"))

    def get_data_row_iter(self):
        """
        TODO: Implement a real iterator instead of creating a new data struct

        #### Output:

        - Should return an iterator, so it can just go through all the rows.
        """
        list_alldata = []
        for row_id in self.DATASET:
            row = self.DATASET[row_id]
            list_alldata.append(row)
        return list_alldata

    def get_data_row_by_id(self, id):
        # If we need to search a real DB by document ID, do it here.
        return self.DATASET[id]

    def _get_data_from_line(self, str_line, len_fieldnames):
        """
        #### Input:

        - The string we will parse
        - Length of fields

        #### Output:

        - List of values

        #### Description:

        Since the description of the location has commas. Will throw off a
        normal split(","). Using standard lib csv to parse will fail because
        description includes new lines. (I might be doing something wrong here)
        So had to build manual line parser. by reading the lines one by one.

        Should be a better way to determine if name string is complete.
        What we know, a string with special char are wrapped in double quotes.
        Could determine position of double quotes.
        """

        # Name can throw off the split function. So grab the first element and
        # iterate backwards.  Assume whatever is left as the Name as rejoin.
        lst_dataline = str_line.rstrip().split(",")
        data_list = []
        data_list.append(lst_dataline.pop(0))
        int_num_of_cols_look = len_fieldnames - 1

        list_data_hold = []
        for x in range(int_num_of_cols_look):
            list_data_hold.append(lst_dataline.pop(-1))

        # Whatever is left should be the "name".
        # TODO: better optimization, this is just quick and dirty.
        list_data_hold.append(",".join(lst_dataline))

        # Because we were working backwards, we need to reverse the list.
        data_list.extend(reversed(list_data_hold))

        return data_list

    def _csv_parse(self, csv_file_path):
        """
        #### Input:

        - CSV file path

        #### Desc:

        Just parse the CSV file line by line and write to the simulated
        DATASET variable in the object.
        """

        fileread_csv = open(csv_file_path, "r", newline='')
        header_row = None
        expected_commas = 0
        len_col = 0

        build_string = ""
        for data_line in fileread_csv:

            # Assume the first row is the header row. will get col's names
            if header_row is None:
                header_row = data_line.rstrip().split(",")
                len_col = len(header_row)
                expected_commas = len_col - 1

            else:
                # Make an assumption data lines can span multiple lines
                build_string += data_line

                # If we are short on expected commas, then the request will
                # fail due to not enough info.
                if build_string.count(",") < expected_commas:
                    continue
                else:
                    # Will pass if we have enough column values to work with.
                    lst_rowdata = self._get_data_from_line(
                        build_string, expected_commas)

                    dict_rowdata = {}
                    for x in range(0, len_col):
                        dict_rowdata[header_row[x]] = lst_rowdata[x]

                    # Try to convert to lat and long, required fields.
                    # If they fail, then save error row and we can use that
                    # to send an error message.
                    try:
                        dict_rowdata['latitude'] = float(
                            dict_rowdata['latitude'])
                        dict_rowdata['longitude'] = float(
                            dict_rowdata['longitude'])

                        self.write_data_row(dict_rowdata)
                    except ValueError:
                        self.error_list[dict_rowdata["id"]] = dict_rowdata
                        self.error_list[dict_rowdata["id"]]["error"] = (
                            "lat long float conv error")

                    # Assuming we have to build each string before processing,
                    # so reinitialize it as empty.
                    build_string = ""


if __name__ == "__main__":

    # E.G.: python3 data_connection.py AB_NYC_2019.csv
    data_file = sys.argv[1]
    dbc = dataconn(csv_file=data_file)

    # Dump it into json for quick loading using the json.load()
    dbc.commit()
