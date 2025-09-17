from pydantic import BaseModel

class Game(BaseModel):
    name: str
    year_release: int
    rating: float

game_1 = Game(name={'Half-Life 2'}, year_release=2004, rating=90)
game_2 = Game(name='Death Stranding', year_release=2019, rating='86')
game_3 = Game(name='Metro 2033', year_release=2010, rating=77.2)
game_4 = Game(name='Heroes of Might and Magic V', year_release=2006, rating=77.12)



