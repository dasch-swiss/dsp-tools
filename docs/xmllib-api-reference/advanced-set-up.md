# Advanced Set-Up Options

## Save User Information to CSV

User information, warnings and errors are printed out on the command line.
To save them to a csv file, you can set that up through a `.env` file through the following steps:

- In the directory from where you run your code create a new file called `.env`. 
  If you already have a `.env` file you can add the new line directly.
- Enter the path of the csv file in quotation marks with the variable `WARNING_CSV_SAVEPATH`

Example `.env` file content:

  ```env
  WARNING_CSV_SAVEPATH="my_folder/my_file.csv"
  ```

This file is set-up in append mode, meaning that if you do not delete it after one run, 
the new warnings will be added to the existing file. If the file already exists a row containing `*` is added. 
