import billing
from orders import place

if __name__ == "__main__":
    place(30)
    print(billing.ledger)
