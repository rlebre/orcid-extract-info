# orcid-extract-info
Script to extract personal information and publications of a given ORCID

Note: Script will run a small server to receive access_token from ORCID API. Sometimes, ORCID API do not process the request. If it happens, just press Ctrl+C and run the script again.

## Building


```
pip install -r requirements.txt
```


## Run
```
$ python orcid-extract-data.py -h
usage: orcid-extract-data.py [-h] (-id ID | -i INPUTFILE)
                             [-s path/to/directory] [-o path/to/file.json]
                             [-csv path/to/file.csv]

Script that reads records from OrcID and outputs to a json file

optional arguments:
  -h, --help            show this help message and exit
  -id ID, --id ID       Provide the OrcID desired
  -i INPUTFILE, --inputfile INPUTFILE
                        Provide a file containing a list of the OrcIDs desired
                        (one per line)
  -s path/to/directory, --save_requests path/to/directory
                        Folder where to save the intermidiate request files
  -o path/to/file.json, --output path/to/file.json
                        JSON File where to save the simplified model. Default:
                        (current path)/export.json
  -csv path/to/file.csv, --output_csv path/to/file.csv
                        CSV File where to save the exported data. Default:
                        (current path)/export.csv

```

## Example
```
$ python orcid-extract-data.py -i input_ids -o new.json -s save_resquests
Starting...
Getting access token
Getting data
getting:  0000-0002-9164-0016
Identified 127 works
getting:  0000-0003-1176-552X
Identified 33 works

DONE!
Exported JSON:  new.json
Exported CSV:   export.csv

```