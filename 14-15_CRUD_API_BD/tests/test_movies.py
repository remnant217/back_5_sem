import pytest

# тестирование фильтрации
@pytest.mark.parametrize(
    'params, expected_titles',
    [
        ({}, {'Интерстеллар', 'Гладиатор', 'Форрест Гамп', 'Унесенные призраками', 'Шрэк', 'Престиж', 'Тайна Коко'}),
        ({'year_min': 2010}, {'Интерстеллар', 'Тайна Коко'}),
        ({'year_max': 2001}, {'Гладиатор', 'Форрест Гамп', 'Унесенные призраками', 'Шрэк'}),
        ({'min_rating': 8.2}, {'Интерстеллар', 'Гладиатор'}),
        ({'year_min': 2000, 'year_max': 2006, 'min_rating': 7.8}, {'Гладиатор', 'Унесенные призраками'})
    ]
)
def test_movies_filters(client, params, expected_titles):
    response = client.get('/movies', params=params)
    assert response.status_code == 200
    assert {movie['title'] for movie in response.json()} == expected_titles

# тестирование сортировки и пагинации
def test_order_and_pagination(client):
    response = client.get('/movies', params={'order_by': '123', 'limit': 7})
    assert response.status_code == 200
    titles = [movie['title'] for movie in response.json()]
    assert titles == [
        'Гладиатор',
        'Интерстеллар',
        'Форрест Гамп',
        'Унесенные призраками',
        'Тайна Коко',
        'Шрэк',
        'Престиж'
    ]

    response_1 = client.get('/movies', params={'order_by': 'title', 'limit': 2, 'offset': 0})
    response_2 = client.get('/movies', params={'order_by': 'title', 'limit': 2, 'offset': 2})
    assert [movie['title'] for movie in response_1.json()] == ['Гладиатор', 'Интерстеллар']
    assert [movie['title'] for movie in response_2.json()] == ['Престиж', 'Тайна Коко']

# тестирование CRUD-операций
def test_crud(client):
    # тестируем create
    data = {'title': 'Дюна', 'genre': 'Научная фантастика', 'rating': 7.7, 'year': 2021}
    response = client.post('/movies', json=data)
    assert response.status_code in (200, 201)
    created_movie = response.json()
    movie_id = created_movie['id']

    # тестируем patch
    response = client.patch(f'/movies/{movie_id}', json={'rating': 7.0})
    assert response.status_code == 200
    assert response.json()['rating'] == 7.0

    # тестируем read
    response = client.get(f'/movies/{movie_id}')
    assert response.status_code == 200
    assert response.json()['year'] == 2021

    # тестируем delete
    response = client.delete(f'/movies/{movie_id}')
    assert response.status_code in (200, 204)

    # тестируем read удаленного фильма
    response = client.get(f'/movies/{movie_id}')
    assert response.status_code == 404