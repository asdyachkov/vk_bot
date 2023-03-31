from dvhb_hybrid.amodels import Model

from .models import User as DjangoGame

class Game(Model):
    table = Model.get_table_from_django(DjangoGame)
