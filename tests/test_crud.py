import json
import os
import subprocess
import sys
import tempfile

from pyorm import ORM, load_config


SCHEMA = {
    "users": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "email": "TEXT NOT NULL",
        "age": "INT NOT NULL",
    }
}


def run_pyorm_init(workdir):
    subprocess.run(
        [sys.executable, "-m", "pyorm.cli", "--init", "1"],
        cwd=workdir,
        check=True,
    )


def test_init_creates_config_file():
    with tempfile.TemporaryDirectory() as tmp:
        run_pyorm_init(tmp)

        config_path = os.path.join(tmp, ".pyorm")
        assert os.path.exists(config_path), ".pyorm config file was not created"

        with open(config_path) as f:
            raw = json.load(f)
        assert "SALT" in raw and "PASSWORD" in raw

        cnf = load_config(config_path)
        assert isinstance(cnf["SALT"], bytes) and len(cnf["SALT"]) == 16
        assert isinstance(cnf["PASSWORD"], bytes) and len(cnf["PASSWORD"]) > 0


def test_crud_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        run_pyorm_init(tmp)
        cnf = load_config(os.path.join(tmp, ".pyorm"))
        db_path = os.path.join(tmp, "users.db")

        orm = ORM(db_path, cnf["PASSWORD"], cnf["SALT"], SCHEMA)
        users = orm.model("users")
        assert users is not None

        alice_id = users.insert({"name": "Alice", "email": "alice@example.com", "age": 30})
        bob_id = users.insert({"name": "Bob", "email": "bob@example.com", "age": 42})
        assert alice_id == 1 and bob_id == 2

        rows = users.find()
        assert len(rows) == 2

        updated = users.update({"id": alice_id}, {"age": 31})
        assert updated == 1

        alice = users.first({"id": alice_id})
        assert alice[1] == "Alice" and alice[3] == 31

        deleted = users.delete({"id": bob_id})
        assert deleted == 1
        assert len(users.find()) == 1

        orm.save()
        assert os.path.exists(db_path), "encrypted db file was not written"


def test_persistence_across_instances():
    with tempfile.TemporaryDirectory() as tmp:
        run_pyorm_init(tmp)
        cnf = load_config(os.path.join(tmp, ".pyorm"))
        db_path = os.path.join(tmp, "persist.db")

        ORM.__models__ = {}
        orm = ORM(db_path, cnf["PASSWORD"], cnf["SALT"], SCHEMA)
        orm.model("users").insert({"name": "Carol", "email": "carol@example.com", "age": 25})
        orm.save()

        ORM.__models__ = {}
        orm2 = ORM(db_path, cnf["PASSWORD"], cnf["SALT"], SCHEMA)
        rows = orm2.model("users").find()
        assert len(rows) == 1
        assert rows[0][1] == "Carol"


if __name__ == "__main__":
    test_init_creates_config_file()
    print("init test: ok")
    test_crud_roundtrip()
    print("crud test: ok")
    test_persistence_across_instances()
    print("persistence test: ok")
