import sqlite3

from django.conf import settings


def skill_name(skill_id):
    with sqlite3.connect(settings.EVESTATIC_DB) as db:
        cursor = db.cursor()
        cursor.execute('SELECT typeName FROM invTypes WHERE typeID = ?', (skill_id,))
        result = cursor.fetchone()

    if result is None:
        raise KeyError("type not found")

    return result[0]
