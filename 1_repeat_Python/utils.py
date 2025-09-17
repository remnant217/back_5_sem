from functools import lru_cache

@lru_cache(maxsize=1000)
def fibonacci(n):
    print(f'Вычисление F({n})')
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(f'Данный код выполняется при импорте модуля {__name__}')

if __name__ == '__main__':
    print('Тестируем функции')
    print(fibonacci(8))
    print(fibonacci(9))