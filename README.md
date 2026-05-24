# PyCyphORM

A simple in-memory encrypted ORM for SQLite3.

The database lives in memory while in use and is persisted to disk as a gzipped,
Fernet-encrypted blob. Keys are derived from a password and salt with PBKDF2-HMAC-SHA256.

## Install

```bash
pip install PyCyphORM
```

## CLI

Generate a `.pyorm` config (random salt + password) in the current directory:

```bash
pyorm --init 1
```

Decrypt an encrypted database file to `<file>.decoded.db`:

```bash
pyorm --decrypt path/to/db
```

## Library usage

```python
from pyorm import ORM, load_config

cnf = load_config(".pyorm")

orm = ORM("users.db", cnf["PASSWORD"], cnf["SALT"], {
    "users": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "email": "TEXT NOT NULL",
        "age": "INT NOT NULL",
    }
})

users = orm.model("users")
users.insert({"name": "Alice", "email": "alice@example.com", "age": 30})
users.update({"name": "Alice"}, {"age": 31})
print(users.find())
print(users.first({"name": "Alice"}))
users.delete({"name": "Alice"})

orm.save()
```

`orm.save()` writes the encrypted snapshot back to disk. Without it, changes
remain in memory only.

## License

MIT
