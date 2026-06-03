import sqlite3


class BancoDeDados:
    def __init__(self, nome_banco: str = 'materiais.db'):

        try:
            self.conn = sqlite3.connect(nome_banco)
            self.cur = self.conn.cursor()


            self.cur.execute("PRAGMA foreign_keys = ON;")


            self._inicializar_esquema()

        except sqlite3.Error as e:
            raise Exception(f"Erro crítico ao conectar no banco de dados: {e}")

    def _inicializar_esquema(self) -> None:

        try:
            self.cur.execute('''
            CREATE TABLE IF NOT EXISTS monitor (
                id_monitor INTEGER PRIMARY KEY AUTOINCREMENT, 
                nome TEXT NOT NULL
            )
            ''')

            self.cur.execute('''
            CREATE TABLE IF NOT EXISTS material (
                id_material INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                quantidade_material INT,
                observacoes TEXT             
            )    
            ''')

            self.cur.execute('''
            CREATE TABLE IF NOT EXISTS entrada (
                id_entrada INTEGER PRIMARY KEY AUTOINCREMENT,
                entrada DATE,
                quantidade_entrada INT,
                id_material INT,
                FOREIGN KEY (id_material)
                    REFERENCES material(id_material)
            )
            ''')

            self.cur.execute('''
            CREATE TABLE IF NOT EXISTS danos (
                id_danos INTEGER PRIMARY KEY AUTOINCREMENT,
                data_danos DATE,
                quantidade_danos INT,
                id_material INT,
                FOREIGN KEY (id_material)
                    REFERENCES material(id_material)
            )
            ''')

            # --- GATILHOS (TRIGGERS) ---
            self.cur.execute('''
            CREATE TRIGGER IF NOT EXISTS atualiza_material_entrada
            AFTER INSERT ON entrada
            BEGIN
                UPDATE material 
                SET quantidade_material = quantidade_material + NEW.quantidade_entrada
                WHERE id_material = NEW.id_material;
            END;
            ''')

            self.cur.execute('''
            CREATE TRIGGER IF NOT EXISTS atualiza_material_danos
            AFTER INSERT ON danos
            BEGIN
                UPDATE material 
                SET quantidade_material = quantidade_material - NEW.quantidade_danos
                WHERE id_material = NEW.id_material;
            END;
            ''')

            self.cur.execute('''
            CREATE TRIGGER IF NOT EXISTS devolve_material_danos
            AFTER DELETE ON danos
            BEGIN
                UPDATE material 
                SET quantidade_material = quantidade_material + OLD.quantidade_danos 
                WHERE id_material = OLD.id_material;
            END;
            ''')

            self.cur.execute('''
            CREATE TRIGGER IF NOT EXISTS reverte_material_entrada
            AFTER DELETE ON entrada
            BEGIN                                           
                UPDATE material 
                SET quantidade_material = quantidade_material - OLD.quantidade_entrada 
                WHERE id_material = OLD.id_material;
            END;
            ''')

            self.conn.commit()

        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro ao criar esquema do banco: {e}")


    # UTILIDADE

    def fechar_conexao(self) -> None:
        """Fecha a conexão com o banco de dados de forma segura."""
        if self.conn:
            self.conn.close()


    # CADASTRAR (CREATE)

    def criar_monitor(self, nome: str) -> bool:
        try:
            self.cur.execute("INSERT INTO monitor (nome) VALUES (?)", (nome,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro ao criar monitor: {e}")

    def criar_material(self, nome: str, quantidade_material: int, observacoes: str = "") -> bool:
        try:
            self.cur.execute(
                "INSERT INTO material (nome, quantidade_material, observacoes) VALUES (?, ?, ?)",
                (nome, quantidade_material, observacoes)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro ao criar material: {e}")

    def criar_entrada(self, data_entrada: str, quantidade_entrada: int, id_material: int) -> bool:
        try:
            self.cur.execute(
                "INSERT INTO entrada (entrada, quantidade_entrada, id_material) VALUES (?, ?, ?)",
                (data_entrada, quantidade_entrada, id_material)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro ao registrar entrada: {e}")

    def criar_danos(self, data_danos: str, quantidade_danos: int, id_material: int) -> bool:
        try:
            self.cur.execute(
                "INSERT INTO danos (data_danos, quantidade_danos, id_material) VALUES (?,?,?)",
                (data_danos, quantidade_danos, id_material)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro ao registrar danos/perdas: {e}")


    # LER / LISTAR (READ)

    def listar_monitores(self) -> list:
        try:
            self.cur.execute("SELECT * FROM monitor")
            return self.cur.fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Erro ao listar monitores: {e}")

    def listar_materiais(self) -> list:
        try:
            self.cur.execute("SELECT * FROM material")
            return self.cur.fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Erro ao listar materiais: {e}")

    def listar_entradas(self) -> list:
        try:
            self.cur.execute("SELECT * FROM entrada")
            return self.cur.fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Erro ao listar entradas: {e}")

    def listar_danos(self) -> list:
        try:
            self.cur.execute("SELECT * FROM danos")
            return self.cur.fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Erro ao listar danos: {e}")


    # ATUALIZAR (UPDATE)

    def atualizar_monitor(self, id_monitor: int, nome: str) -> bool:
        try:
            self.cur.execute("UPDATE monitor SET nome = ? WHERE id_monitor = ?", (nome, id_monitor))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro ao atualizar monitor: {e}")

    def atualizar_material(self, id_material: int, nome: str, quantidade: int, observacoes: str) -> bool:
        try:
            self.cur.execute('''
                UPDATE material 
                SET nome = ?, quantidade_material = ?, observacoes = ? 
                WHERE id_material = ?
            ''', (nome, quantidade, observacoes, id_material))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro ao atualizar material: {e}")

    def atualizar_entrada(self, id_entrada: int, quantidade_entrada: int) -> bool:
        try:
            self.cur.execute(
                "UPDATE entrada SET quantidade_entrada = ? WHERE id_entrada = ?",
                (quantidade_entrada, id_entrada)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro ao atualizar entrada: {e}")

    def atualizar_danos(self, id_danos: int, quantidade_danos: int) -> bool:
        try:
            self.cur.execute(
                "UPDATE danos SET quantidade_danos = ? WHERE id_danos = ?",
                (quantidade_danos, id_danos)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro ao atualizar danos: {e}")


    # DELETAR

    def deletar_monitor(self, id_monitor: int) -> bool:
        try:
            self.cur.execute("DELETE FROM monitor WHERE id_monitor = ?", (id_monitor,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro ao deletar monitor: {e}")

    def deletar_material(self, id_material: int) -> bool:
        try:
            self.cur.execute("DELETE FROM material WHERE id_material = ?", (id_material,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro ao deletar material: {e}")

    def cancelar_entrada(self, id_entrada: int) -> bool:
        try:
            self.cur.execute("DELETE FROM entrada WHERE id_entrada = ?", (id_entrada,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro ao cancelar entrada: {e}")

    def cancelar_danos(self, id_danos: int) -> bool:
        try:
            self.cur.execute("DELETE FROM danos WHERE id_danos = ?", (id_danos,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Erro ao cancelar dano: {e}")