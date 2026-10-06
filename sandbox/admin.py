"""Správcovské příkazy: python -m sandbox.admin delete <jméno>."""

import sys

from . import auth, engine


def delete_user(name: str) -> int:
    key = auth.normalize_username(name)
    for user in (auth.SandboxUser(r["username"], r["uid"])
                 for r in auth._load_users().values()):
        if auth.normalize_username(user.username) == key:
            engine.stop(user)
            auth.delete_account(user)
            print(f"Účet '{user.username}' byl smazán.")
            return 0
    print(f"Účet '{name}' neexistuje.")
    return 1


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "delete":
        sys.exit(delete_user(sys.argv[2]))
    print("Použití: python -m sandbox.admin delete <jméno>")
    sys.exit(2)
