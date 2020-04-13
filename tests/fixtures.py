import os
from dataclasses import dataclass

import pytest
from app import create_app
from models import db


@pytest.fixture(scope='session')
def setup_test_app():
    app = create_app()
    app.app_context().push()
    file_path = os.path.abspath(os.getcwd())

    test_db = f"sqlite:///{file_path}/test_db.sqlite"
    app.config["SQLALCHEMY_DATABASE_URI"] = test_db
    db.init_app(app)
    db.create_all(app=app)

    with app.test_client() as client:
        yield client, db

    os.remove(f"{file_path}/test_db.sqlite")  # this is teardown


@pytest.fixture(scope='module')
def location_dict():
    loc_dict = dict(longitude=-73.5673,
                    latitude=45.5017,
                    postcode='H2S 3C3')

    yield loc_dict


@pytest.fixture(scope="session")
def test_db(setup_test_app):
    _, db = setup_test_app

    yield db


@pytest.fixture(scope="session")
def test_client(setup_test_app):
    client, _ = setup_test_app

    yield client


@pytest.fixture(scope='session')
def example_forecast():
    pass


@dataclass
class TestLocation:
    postcode: str
    city: str
    lon: float
    lat: float


test_locations = [TestLocation(postcode='BS6 7ER',
                               city='Bristol',
                               lat=51.45,
                               lon=-2.58),
                  TestLocation(postcode='H2S 3C2',
                               city='Montreal',
                               lat=45.5,
                               lon=-73.6)]