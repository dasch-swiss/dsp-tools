# Advanced Set-Up Options

## Save Output to CSV

User information, warnings and errors are printed out on the command line.
To additionally save them to a CSV file, you can set that up through a `.env` file through the following steps:

- In the directory from where you run your code, create a new file called `.env`. 
  If this file already exists, continue with the next step. 
- Set `WARNING_CSV_SAVEPATH` to the path of the CSV file

Example `.env` file content:

  ```env
  WARNING_CSV_SAVEPATH="my_folder/my_file.csv"
  ```

This file is set-up in append mode, meaning that if you do not delete it after one run, 
the new warnings will be added to the existing file. If the file already exists a row containing `*` is added. 
