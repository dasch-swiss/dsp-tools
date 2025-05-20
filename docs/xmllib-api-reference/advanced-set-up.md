# Advanced Set-Up Options

## Using an `.env` File

The advanced set-up options are configured through an `.env` file.
This file should lie in the directory where you run your code from.

If you already have an `.env` file you can add the new variables to the existing file.

Please note that if a parameter is omitted it has the same meaning as setting it to `false`.

Oftentimes, `.env` files are used to store sensitive parameters, such as passwords.
Therefore, it is best practice to add it to your `.gitignore` file if it is not already.


## Save Warnings Output to CSV

User information, warnings and errors are printed out on the command line.
To additionally save them to a CSV file, set `XMLLIB_WARNINGS_CSV_SAVEPATH` to the path of the CSV file.

Example `.env` file content:

  ```env
  XMLLIB_WARNINGS_CSV_SAVEPATH="my_folder/my_file.csv"
  ```

This file is set-up in append mode, meaning that if you do not delete it after one run, 
the new warnings will be added to the existing file. If the file already exists a row containing `*` is added. 


## Configurations for the Resulting XML File

### Sorting of Resources and Values in the XML

By default, resources and values are not sorted when creating the XML.
You can configure sorting through the following `.env` variables.

- `XMLLIB_SORT_RESOURCES`: sort resources by resource id
- `XMLLIB_SORT_PROPERTIES`: sort properties by the property name, and the values within the properties

Example `.env` file content:

  ```env
  XMLLIB_SORT_RESOURCES=true
  XMLLIB_SORT_PROPERTIES=true
  ```

If you want to enable only one of these sortings, the other can either be omitted or set to `false`.


**Note on the sorting order:**

- The order is determined by the character number in the [Unicode chart](https://www.unicode.org/charts/).
- This means that for example: `B` will come before `a`, as capital letters have a lower number than lower case letters.
- Numbers are treated as strings. This means that for example `01` and `1` are treated differently.

### Authorship Reference IDs

By default, authorship IDs are generated using a UUID.
If the references should be consistent across all runs, then this `.env` variable can be set.
When this variable is set, the authorships are sorted alphabetically and the IDs will start at 1.

Example `.env` file content:

  ```env
  XMLLIB_AUTHORSHIP_ID_WITH_INTEGERS=true
  ```
