from app import db
from app.base.models import Poem

def createPoems():
    for ind in range(5):
        poem = Poem(**{"body":"test number "+str(ind)})
        db.session.add(poem)

    db.session.commit()

    return None

if __name__ == "__main__":
    createPoems()