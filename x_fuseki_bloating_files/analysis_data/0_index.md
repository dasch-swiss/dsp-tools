# Notes

Notes to the files

- comparison_different_values_run1.csv
  - Identical values on each resource (validate is switched off)
  - Each value 13 times per resource so that it is identical with the resource that has every type once
  - Content of all the text values is identical
  - Decimal and integer are single digit size
- comparison_different_values_run2.csv
  - Same as run 1
- comparison_different_values_very_large_int_value.csv
  - 10 Values starting at: 1'000'000'000'000
  - to see if the size of the integer has an influence
- comparison_hard_ware_mac_book.csv
  - To compare if the hard-ware (Cheesgrater vs. Macbook) has an influence
  - It does not
- increasing_num_larger_int_value.csv
  - Int value starting at 1, to ensure that the large size of int value is correct
  - It is the identical int value files used in increasing_num_run1
- increasing_num_run1.csv
  - Increasing the number of values or resources
  - Int value is increasing starting at 1
  - default long text size is 20'000 characters
- increasing_num_small_int_value.csv
  - All the int values are identical, namely 1
  - This is the first try to check if the size of the value has an influence
- same_file_upload_no_reset.csv
  - The file where the resource has every value type once with 10'000 resources was uploaded 10 times
  - The stack was not restarted
  - This is to investigate if the initial DB size has an influence
- triple_count_comparison.csv
  - Comparing the number of triples generated per value type
  - This is to see if the triple number has a correlation
- triple_count_comparison_5000_res.csv
  - Comparing the number of triples generated per value type
  - Content of the values is identical for all 13 usages.
  - Int is 1
  - decimal is 1.1
- 
