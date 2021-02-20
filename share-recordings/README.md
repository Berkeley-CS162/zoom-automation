# Share Recordings

This script is intended to fetch Zoom Recording sharing data.
It navigates to the "Recordings" page and clicks "Share..." on each row until it reaches the last page. For each recording sharing modal, it copies the recording's "Sharing Information".

## Usage

**Output**: file of parsed Zoom Recording sharing information (see `parse()`)

## Example

```
python share-recordings.py out.csv
```

## Recommendations

- You may want to turn off recording passcode protection by default in Zoom settings and omit that section in the script
