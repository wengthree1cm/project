import sqlite3

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trial_data (
            drug_name TEXT,
            sponsor TEXT,
            trial_sites INTEGER,
            enrollment INTEGER,
            start_date TEXT,
            completion_date TEXT,
            source_file TEXT,
            update_time TEXT,
            PRIMARY KEY (drug_name, start_date)
        )
    ''')
    conn.commit()
    conn.close()

def insert_or_update_drug(data, db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 检查是否已有这条记录（按 drug_name + start_date）
    c.execute("SELECT * FROM trial_data WHERE drug_name=? AND start_date=?", 
              (data["drug_name"], data["start_date"]))
    row = c.fetchone()

    if row:
        # 更新
        for key in data:
            c.execute(f'''
                UPDATE trial_data SET {key}=? 
                WHERE drug_name=? AND start_date=?
            ''', (data[key], data["drug_name"], data["start_date"]))
    else:
        # 插入新记录
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = list(data.values())
        c.execute(f'''
            INSERT INTO trial_data ({fields}) VALUES ({placeholders})
        ''', values)

    conn.commit()
    conn.close()
