import os
import re
import xlsxwriter

if __name__ == "__main__":

    column_names = ['Primary Key', 'Null?', 'Data Type', 'Default', 'Description']


    # change to directory with table definition files

    username = os.environ.get("USERNAME")
    
    os.chdir(os.path.join('C:\\', 'users', username, 'Desktop', 'ddl'))


    # get a list of all the files in the directory
    
    filelist = os.listdir()


    schema = None


    # iterate through each of the table definition files

    for file in filelist:


        # extract the schema name and table name from the file name
        
        structure = re.match("(?P<schema>^[^\.]+)\.(?P<table>[^\.]+)", file)


        # if it's a new schema, close the current schema output file and start a new one
        
        if structure.group('schema') != schema:

            if schema:

                worksheet.set_header('&LSchema: {}'.format(schema))
                worksheet.set_h_pagebreaks(pagebreaks)
                worksheet.set_landscape()
                worksheet.fit_to_pages(1, 0)
                
                worksheet.set_column(0, 0, field_columnwidth)
                
                workbook.close()

            schema = structure.group('schema')

            workbook = xlsxwriter.Workbook('{}.xlsx'.format(schema))

            worksheet = workbook.add_worksheet()

            pagebreaks = []

            # each output file starts at the first row
            row = 0

            table_columnwidth = 0
            field_columnwidth = 0
            

        table = structure.group('table')


        # open the table definition file

        with open(file, 'r') as table_ddl:

            print("Opening {}...".format(file))
            print()


            # start output at the first column
            col = 0


            # write the header row

            worksheet.write(row, col, table, workbook.add_format({'bold': True, 'align': 'left', 'bottom': 2}))

            if len(table) > field_columnwidth:
                field_columnwidth = len(table)

            col += 1
            
            for header in (column_names):

                worksheet.write(row, col, header, workbook.add_format({'bold': True, 'align': 'center', 'bottom': 2}))

                col += 1
                
  
            # add pagebreak after each set of header rows
            if row > 0:
                pagebreaks.append(row)


            # start writing the field details at the first column of the next row
            col = 0            
            row += 1


            # write the field details            
            worksheet.write(row, col, table)

            if len(table) > field_columnwidth:
                field_columnwidth = len(table)

            # move on to the next row after writing all the details about a field
            row += 1
            

            row += 3

        table_ddl.close()
        print("{} closed.".format(file))
        
        print()
        print("====================")
        print()

    worksheet.set_header('&LSchema: {}'.format(schema))
    worksheet.set_h_pagebreaks(pagebreaks)
    worksheet.set_landscape()
    worksheet.fit_to_pages(1, 0)

    # increase the table and field widths by 10% when sizing columns
    worksheet.set_column(0, 0, field_columnwidth * 1.1)
    
    workbook.close()
