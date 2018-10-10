# ocatodo

Download your last Ocado shopping list as a todo.txt list

## Why

Ocado stopped giving you a printout of your shopping list to tick off items from, which sucked. This script logs into your account and downloads your last shopping list, outputting it in (todo.txt)[http://todotxt.org/] format.

## Usage

```
python ocatodo.py -u mysername@example.com -p mypassw0rd >> ~/Dropbox/todo/todo.txt
```

I recommend managing your todo.txt with something like (Simpletask)[https://play.google.com/store/apps/details?id=nl.mpcjanssen.todotxtholo&hl=en_GB]

## Dependencies

`argparse`, `requests`


