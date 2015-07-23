import os
import pprint
import re
from tqdm import *
import xlsxwriter

if __name__ == "__main__":

    p = pprint.PrettyPrinter()

    column_names = ['Key', 'Constraint', 'Data Type', 'Default', 'Description']


    # change to directory with table definition files

    username = os.environ.get("USERNAME")
    
    os.chdir(os.path.join('C:\\', 'users', username, 'Desktop', 'ddl'))


    # get a list of all the files in the directory
    
    filelist = os.listdir()
    

    ddl = {}


    # iterate through each of the table definition files

    for outputfile in tqdm(filelist):

##        print(outputfile)

        with open(outputfile, 'r') as file:

            for line in file:

                if re.match("^CREATE.*\sTABLE\s", line):

                    # if there is a '.' in the line, parse schema.table from line
                    
                    if re.match("\.", line):

                        structure = re.match("^\s*CREATE.*\sTABLE\s((?P<schema>.+?(?=\.))\.)?(?P<table>.+?(?=(\.|\s|$|\()))", line)

                        schema = structure.group('schema')
                        table = structure.group('table')


                    # parse the schema from the file name, and the table from the CREATE TABLE line
                    
                    else:
                        
                        structure = re.match("^(?P<schema>.+(?=\..+\.sql))", outputfile)

                        schema = structure.group('schema')
                        
                        structure = re.match("^CREATE.*\sTABLE\s\"?(?P<table>.+?(?=(\.|\s|$|\(|\")))", line)
##                        print(line)

##                        if schema == 'dbsnmp':
##                            print(line)
##
##                        if schema == 'dbsnmp':
##                            print("parsing table / schema from line")

                        table = structure.group('table')


                    # if the schema does not already exist in our data dictionary, create it
                    if not ddl.get(schema):
                        ddl[schema] = {}

                    # if the table does not already exist in our data dictionary, create it
                    if not ddl[schema].get(table):
                        ddl[schema][table] = []


                    line = next(file)

                    if re.match("^\(", line):
 
                        # until we reach a close parenthesis, read each line and parse out column names and attributes
                        while True:

                            line = next(file)

                            if re.match("^\)", line) or "PRIMARY KEY" in line:
                                break
                            
                            definition = re.match("^\s*(?P<column>\S+)\s+(?P<datatype>.+?(?=($|,$|\s+NOT NULL|\s+DEFAULT)))(\s+DEFAULT\s(?P<default>(\'.+\'|.+?)(?=(,$|\s+NOT NULL))))?(\s+(?P<constraint>NOT NULL)(?=(,$|\s+)))?", line)

##                            if schema == 'dbsnmp':
##                                print(schema)
##                                print(table)
##                                print(definition.groupdict())

##                            print(definition.groupdict())

                            ddl[schema][table].append(definition.groupdict())

                elif re.match("^ALTER TABLE", line):

                    if "." in line:

                        structure = re.match("^\s*ALTER TABLE ((?P<schema>.+?(?=\.))\.)?(?P<table>.+?(?=(\.|\s|$|\()))", line)

                        schema = structure.group('schema')
                        table = structure.group('table')


                    # parse the schema from the file name, and the table from the CREATE TABLE line
                    
                    else:
                        
                        structure = re.match("^(?P<schema>.+(?=\..+\.sql))", outputfile)

                        schema = structure.group('schema')

                        structure = re.match("^\s*ALTER TABLE \"?(?P<table>.+?(?=(\.|\s|$|\(|\")))", line)

                        table = structure.group('table')

                    # if the schema does not already exist in our data dictionary, create it
                    if not ddl.get(schema):
                        ddl[schema] = {}

                    # if the table does not already exist in our data dictionary, create it
                    if not ddl[schema].get(table):
                        ddl[schema][table] = []

                    while True:

                        line = next(file)

                        if "PRIMARY KEY" in line:

                            line = next(file)

                            constraints = re.match("\s*\((?P<primary_keys>.+?(?=\)))", line)

                            primary_keys = constraints.group('primary_keys')

                            while " " in primary_keys:

                                primary_keys = primary_keys.replace(" ", "")

                            primary_keys = primary_keys.split(",")

                            for field in ddl[schema][table]:

                                if field.get('column') in primary_keys:

                                    field['key'] = 'PRIMARY KEY'

                            if ";" in line:
                                break

                        elif "FOREIGN KEY" in line:

                            constraints = re.match("\s*FOREIGN KEY\s*\((?P<foreign_key>.+?(?=\)))", line)

                            foreign_key = constraints.group('foreign_key')

                            line = next(file)

                            description = re.match("\s*REFERENCES\s(?P<foreign_reference>.+(?=$))", line)

                            for field in ddl[schema][table]:

                                if foreign_key == field.get('column'):

                                    field['key'] = 'FOREIGN KEY'
                                    field['description'] = "References {}".format(description.group('foreign_reference'))

                            if ";" in line:
                                break
                            

                        if ";" in line:
                            break

        file.close()

##    p.pprint(ddl)

    print("{} files read. Now creating output files...".format(len(filelist)))
    print()

    if not os.path.exists('Data Definitions'):
        os.makedirs('Data Definitions')
    os.chdir('Data Definitions')

    for schema in tqdm(ddl):

        workbook = xlsxwriter.Workbook('{}.xlsx'.format(schema.upper()))

        worksheet = workbook.add_worksheet()

        pagebreaks = []

        columnwidth = 0
        keywidth = 3
        constraintwidth = 10
        datatypewidth = 9
        defaultwidth = 7
        descriptionwidth = 11
        

        # each output file starts at the first row
        row = 0

        # start output at the first column
        col = 0

        for table in sorted(ddl[schema]):

            # start writing the field details at the first column of the next row
            col = 0
            
            # write the header row
            worksheet.write(row, col, table, workbook.add_format({'bold': True, 'align': 'left', 'bottom': 2}))

            col += 1

            for header in (column_names):

                worksheet.write(row, col, header, workbook.add_format({'bold': True, 'align': 'center', 'bottom': 2}))

                col += 1

                        
            row += 1

            for field in ddl[schema][table]:

                # start writing the field details at the first column of the next row
                col = 0

                worksheet.write(row, col, field.get('column'), workbook.add_format({'bottom': 7, 'left': 7, 'right': 7}))

                if field.get('column') and len(field.get('column')) > columnwidth:
                    columnwidth = len(field.get('column'))
                    
                col += 1

                worksheet.write(row, col, field.get('key'), workbook.add_format({'bottom': 7, 'left': 7, 'right': 7}))

                if field.get('key') and len(field.get('key')) > keywidth:
                    keywidth = len(field.get('key'))
                    
                col += 1

                worksheet.write(row, col, field.get('constraint'), workbook.add_format({'bottom': 7, 'left': 7, 'right': 7}))

                if field.get('constraint') and len(field.get('constraint')) > constraintwidth:
                    constraintwidth = len(field.get('constraint'))
                    
                col += 1

                worksheet.write(row, col, field.get('datatype'), workbook.add_format({'bottom': 7, 'left': 7, 'right': 7}))

                if field.get('datatype') and len(field.get('datatype')) > datatypewidth:
                    datatypewidth = len(field.get('datatype'))
                    
                col += 1

                worksheet.write(row, col, field.get('default'), workbook.add_format({'bottom': 7, 'left': 7, 'right': 7}))

                if field.get('default') and len(field.get('default')) > defaultwidth:
                    defaultwidth = len(field.get('default'))
                    
                col += 1

                worksheet.write(row, col, field.get('description'), workbook.add_format({'bottom': 7, 'left': 7, 'right': 7}))

                if field.get('description') and len(field.get('description')) > descriptionwidth:
                    descriptionwidth = len(field.get('description'))
                    
                row += 1

            row += 3
            pagebreaks.append(row)

        worksheet.set_header('&LSchema: {}'.format(schema.upper()))
        worksheet.set_footer('&RPage &P of &N')
        worksheet.set_h_pagebreaks(pagebreaks)
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)


        worksheet.set_column(0, 0, columnwidth * 1.1)
        worksheet.set_column(1, 1, keywidth * 1.1)
        worksheet.set_column(2, 2, constraintwidth * 1.1)
        worksheet.set_column(3, 3, datatypewidth * 1.1)
        worksheet.set_column(4, 4, defaultwidth * 1.1)
        worksheet.set_column(5, 5, descriptionwidth * 1.1)
        
        workbook.close()
