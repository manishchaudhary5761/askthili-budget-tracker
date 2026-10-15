"""A simple terminal-based expense logger."""

def add(ledger, amount, category, note=""):
    ledger.append({
        "amount": amount,
        "category": category,
        "note": note
    })


def balance(ledger):
    total = 0
    for entry in ledger:
        total += entry["amount"]
    return total


def show(ledger):
    for number, entry in enumerate(ledger, start=1):
        print(
            f"{number:>3}  {entry['amount']:>10.2f}  "
            f"{entry['category']:<12} {entry['note']}"
        )
    print(f"     {'balance':>10}  {balance(ledger):>10.2f}")


def main():
    ledger = []
    print("commands: add <amount> <category> [note] | list | balance | quit")
    print("income is positive, an expense is negative")

    while True:
        try:
            line = input().strip()
        except EOFError:
            break

        if line == "":
            continue

        words = line.split()
        command = words[0]

        if command == "add" and len(words) >= 3:
            add(ledger, float(words[1]), words[2], " ".join(words[3:]))
        elif command == "list":
            show(ledger)
        elif command == "balance":
            print(balance(ledger))
        elif command == "quit":
            break
        else:
            print("sorry, I don't understand that")


if __name__ == "__main__":
    main()
