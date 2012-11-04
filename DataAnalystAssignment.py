import sqlite3 
import sys
import csv
import os
import argparse
from datetime import datetime

class ConnToSQLite:
    """Establish conn, create cursor, qry, and close SQLite."""
    def establish_conn_sqlite(self, database_file):
        try:
            conn = sqlite3.connect(database_file)
        except sqlite3.Error, e:
            sys.exit("Could not connect to the database")
        return conn
    def create_cursor(self, conn):
        cursor = conn.cursor()
        return cursor
    def sql_qry(self, cursor, qry_string):
        cursor.execute(qry_string)
        data = cursor.fetchall()
        return data
    def close_conn(self, conn):
        conn.close()

class CsvOps:
    """Create file obj, create csv writer, writelines, close csv."""
    def open_csv(self, filename):
        file_obj = open(filename, 'wb')
        return file_obj
    def csv_writer(self, csv_file_obj):
        csv_writer = csv.writer(csv_file_obj)
        return csv_writer
    def write_line_csv(self, csv_writer, line_to_write):
        csv_writer.writerow(line_to_write)
    def close_csv(self, file_to_close):
        file_to_close.close()

class DateTasks:
    """Check length of year, get date format for strptime, evaluate"""
    #I noticed a date with 3 digits, so I wrote code to trap errors with len(years) not equal to 2 or 4
    def check_year_length(self, date_str):
        year_length = 0
        for char in reversed(date_str):
            if char != '/' and char != '-':
                year_length += 1
            else:
                return year_length
    def get_date_format(self, date_str, year_length):
        """Assign datetime attributes based on delimeter type and
           length of year.
        """
        #My understanding is that sqlite date and time methods will not work on dates not stored in ISO8061
        #Perhaps dateutil module would work well here...something I can look into in the future
        #I elected to convert dates stored as strings via the strptime method in the datetime module
        #I made the assumptions:  delimeters always are / or -, and month, day, year is the order
        if year_length == 4 and '/' in date_str:
            date_format = '%m/%d/%Y'
        elif year_length == 4 and '-' in date_str:
            date_format = '%m-%d-%Y'
        elif year_length == 2 and '/' in date_str:
            date_format = '%m/%d/%y'
        elif year_length == 2 and '-' in date_str:
            date_format = '%m-%d-%y'
        return date_format
    def evaluate_and_writeline(self, date_field, date_format, records, eval_datetime, csv_o=None, csv_writer=None, args=None, err_log=None):
        """Convert date string to datetime and evaluate...write lines to stdout or csv and error_log depending on default mode or filename mode
        """
        try:
            converted_date = datetime.strptime(date_field, date_format)
            if converted_date > eval_datetime:
                if args:
                    csv_o.write_line_csv(csv_writer, records)
                else:
                    for e in records: print e,
                    print '\n'
        except ValueError as detail:
            if err_log:
                print >> sys.stderr, datetime.now(), 'Error:', detail, records
                err_log.write(str(datetime.now()) + ' Error: ' + str(detail) + ' ' )
                for e in records:
                    err_log.write(e + ' ')
                err_log.write(' processing next record\n')
            else:
                print >> sys.stderr, datetime.now(), 'Error:', detail, records, '\n'

def process_without_filename(date_tsk, data, eval_datetime):
    """Processes in default mode: calls evaluate_and_writeline and writes to stdout
    """
    for records in data:
        year_length = date_tsk.check_year_length(records[1])
        if year_length == 3 or year_length > 4:
            print >> sys.stderr, datetime.now(), "Error: lengh of year: ", records
        else:
            date_format = date_tsk.get_date_format(records[1], year_length)
            date_tsk.evaluate_and_writeline(records[1], date_format, records, eval_datetime)

def process_with_filename(date_tsk, con_sql, conn, data, eval_datetime, csv_o, csv_writer, args, error_log_file, results_file):
    """Processes in optional mode with filename: writes to csv with filename argument and logs errors in errors.txt in
    current directory.  
    """
    for records in data:
        year_length = date_tsk.check_year_length(records[1])
        if year_length == 3 or year_length > 4:
            error_log_file.write(str(datetime.now()) + ' Error: lengh of year: ')
            for e in records:
                error_log_file.write(e + ' ')
            error_log_file.write(' processing next record\n')
            print >> sys.stderr, datetime.now(), " Error: lengh of year: ", records
        else:
            date_format = date_tsk.get_date_format(records[1], year_length)
            date_tsk.evaluate_and_writeline(records[1], date_format, records, eval_datetime, csv_o, csv_writer, args, error_log_file)

def main():
    parser = argparse.ArgumentParser(description="""Establish conn to example.db, qry data tbl for kit_type=abbott, results < 1000, and records dated > Jan, 1, 2000, output to csv and errorlog in current working directory...default prints to stdout.""")
    parser.add_argument('-f', '--filename', help='filename for output to csv: default = results to stdout')
    args = parser.parse_args()
    con_sql = ConnToSQLite()
    csv_o = CsvOps()
    date_tsk = DateTasks()
    conn = con_sql.establish_conn_sqlite('example.db')
    cursor = con_sql.create_cursor(conn)
    qry_string = """SELECT patient_id, date, kit_type, result FROM data WHERE kit_type = 'abbott' AND CAST(result AS REAL) <= 1000"""
    data = con_sql.sql_qry(cursor, qry_string)
    eval_datetime = datetime(2000, 01, 01)
    if not args.filename:
        process_without_filename(date_tsk, data, eval_datetime)
    else:
        results_file = os.getcwd() + '/' + args.filename + '.csv' 
        results_file = csv_o.open_csv(results_file)
        error_log_file = open(os.getcwd() + '/' + 'errors.txt', 'w')
        csv_writer = csv_o.csv_writer(results_file)
        headers = ('patient_id','date','kit_type','result')
        csv_o.write_line_csv(csv_writer, headers)
        process_with_filename(date_tsk, con_sql, conn, data, eval_datetime, csv_o, csv_writer, args, error_log_file, results_file)
        con_sql.close_conn(conn)
        csv_o.close_csv(results_file)
        error_log_file.close()
    
if __name__ == '__main__':
    main()

#I noticed a value in the results field with a letter in it instead of a digit: i.e. 10o ...a script to identify these instances may be prudent
#Thanks for checking out my code....look forward to the interview on Tuesday!
