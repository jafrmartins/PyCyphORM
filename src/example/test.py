from pyorm import load_config, ORM

cnf = load_config(".pyorm")

orm = ORM("hello.db", cnf["PASSWORD"], cnf["SALT"], {
    "test": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "window_title": "TEXT NOT NULL",
        "application_name": "TEXT NOT NULL",
        "machine_name": "TEXT NOT NULL",
        "desktop_scheenshot": "TEXT NOT NULL",
        "epoch": "INT NOT NULL"
    }
})

m = orm.model("test")
if m:

    id = m.insert({
        "window_title": "TEXT NOT NULL",
        "application_name": "TEXT NOT NULL",
        "machine_name": "TEXT NOT NULL",
        "desktop_scheenshot": "TEXT NOT NULL",
        "epoch": 19999
    })

    print(id)

    m.update({ "id": id }, { "window_title": "TEXT NOT NULL UPDATED", })
    all = m.find()
    print(all)
    one = m.first({ "id": id })
    print(one)

orm.save()
