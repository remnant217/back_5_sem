products_db: list[dict] = [
    # {'id': 1, 'title': 'Ноутбук', 'price': 79990, 'stock': 5},
    # {'id': 2, 'title': 'Клавиатура', 'price': 2990, 'stock': 12},
    # {'id': 3, 'title': 'Наушники', 'price': 1990, 'stock': 10}
]

next_id = max((p['id'] for p in products_db), default=0) + 1
print(next_id)