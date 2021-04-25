#!/usr/bin/env python3


from mongodb import MongoCli


def stock_exists(stock):
    try:
        data = mg.lookup_stock(stock)
    except ValueError:
        return False, False
    else:
        return True, data


def main(stock):

    _, data = stock_exists(stock)

    if data:
        print(f"Exists - passing on {stock}")
        pass
    else:
        print(f"DNE - inserting blank for {stock}")
        mg.insert_one_document({'Stock': stock})

if __name__ == "__main__" :

    try:
        for x in [ 'nyse.txt', 'nasdaq.txt' ]:
            file=x
            mg = MongoCli()
            for stock in open(f"../non-app/{file}",'r'):
                main(stock.strip())
    except Exception as e:
        print(e)
        

