# Advanced Set-Up Options

## Save Output to CSV

User information, warnings and errors are printed out on the command line.
To additionally save them to a CSV file, you can set that up by following the next steps:

- In the directory where you run your code from, create a new file called `.env`. 
  If this file already exists, skip this step and write in the existing file.
- Set `WARNINGS_CSV_SAVEPATH` to the path of the CSV file

Example `.env` file content:

  ```env
  WARNINGS_CSV_SAVEPATH="my_folder/my_file.csv"
  ```

This file is set-up in append mode, meaning that if you do not delete it after one run, 
the new warnings will be added to the existing file. If the file already exists a row containing `*` is added. 
