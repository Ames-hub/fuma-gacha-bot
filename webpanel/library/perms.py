from fastapi import HTTPException, Request
from library.database import DB_PATH
from library.auth import authbook
from functools import wraps
from enum import IntFlag
import sqlite3

class permissions(IntFlag):
    DELETE_USERS        = 1 << 0
    ADD_USERS           = 1 << 1
    MODIFY_PERMISSIONS  = 1 << 2
    VIEW_LOGS           = 1 << 3
    VIEW_BUGS           = 1 << 4
    RESOLVE_BUGS        = 1 << 5
    VIEW_FEEDBACK       = 1 << 6
    MANAGE_CARDS        = 1 << 7
    MANAGE_COMMANDS     = 1 << 8
    ADMIN               = 1 << 31

def _get_permissions(username: str) -> int | None:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT permissions_int FROM authbook WHERE username=?",
            (username,)
        )
        row = cur.fetchone()
    return row[0] if row else None

class user:
    def __init__(self, username: str):
        self.username = username

    def has_permission(self, permission: permissions) -> bool:
        perms = _get_permissions(self.username)
        if perms is None:
            return False
        if perms & permission.ADMIN:
            return True
        return (perms & permission) != 0

    def add_permission(self, permission: permissions):
        """Grant a specific permission to a user."""
        perms = _get_permissions(self.username)
        perms |= permission
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE authbook SET permissions_int=? WHERE username=?", (perms, self.username))
            conn.commit()
        return True

    def remove_permission(self, permission: permissions):
        """Revoke a specific permission from a user."""
        perms = _get_permissions(self.username)
        perms &= ~permission
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE authbook SET permissions_int=? WHERE username=?", (perms, self.username))
            conn.commit()
        return True