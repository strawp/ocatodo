# ocatodo

Download your last Ocado shopping list as a todo.txt list

## Why

Ocado stopped giving you a printout of your shopping list to tick off items from, which sucked. This script logs into your account and downloads your last shopping list, outputting it in `todo.txt` format.

## Usage

```
python ocatodo.py -u mysername@example.com -p mypassw0rd >> ~/Dropbox/todo/todo.txt
```

## Dependencies

`argparse`, `requests`


