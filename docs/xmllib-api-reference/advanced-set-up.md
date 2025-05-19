# Advanced Set-Up Options

## Save Warnings Output to CSV

User information, warnings and errors are printed out on the command line.
To additionally save them to a CSV file, you can set that up by following the next steps:

- In the directory where you run your code from, create a new file called `.env`. 
  If this file already exists, skip this step and write in the existing file.
- Set `XMLLIB_WARNINGS_CSV_SAVEPATH` to the path of the CSV file

Example `.env` file content:

  ```env
  XMLLIB_WARNINGS_CSV_SAVEPATH="my_folder/my_file.csv"
  ```

This file is set-up in append mode, meaning that if you do not delete it after one run, 
the new warnings will be added to the existing file. If the file already exists a row containing `*` is added. 


## Sorting of Resources and Values in the XML

By default, resources and values are not sorted when creating the XML.
You can configure sorting through the following `.env` variables.

- `XMLLIB_SORT_RESOURCES`: sort resources by resource id
- `XMLLIB_SORT_PROPERTIES`: sort properties by the property name, and the values within the properties

Example `.env` file content:

  ```env
  XMLLIB_SORT_RESOURCES=true
  XMLLIB_SORT_PROPERTIES=true
  ```

If you only want to have either sorted, the keyword can either be omitted or set to `false`.


**Note on the sorting order:**

- The order is determined by the character number in the [Unicode chart](https://www.unicode.org/charts/)
- This means that for example: `B` will come before `a` as capital letters have a lower number than lower case letters
- Numbers are treated as strings, this means that for example: `01` and `1` are treated differently