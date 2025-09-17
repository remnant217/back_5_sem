# принимает список с тратами и возвращает их общую сумму в виде дробного числа
def get_total(expenses) -> float:
    return sum(e.amount for e in expenses)