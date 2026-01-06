import sqlite3

def conectar():
    return sqlite3.connect("caixa.db", check_same_thread=False)

def criar_tabela():
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            cliente TEXT,
            valor REAL,
            forma TEXT,
            comprovante TEXT
        )
    """)
    conn.commit()
    conn.close()
