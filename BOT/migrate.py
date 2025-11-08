import psycopg2
from config import logger

#DSN = "host=localhost user=postgres password=4268 dbname=aigovnodb port=54321 sslmode=disable"
DSN = "host=localhost port=54321 dbname=aigovnodb user=postgres password=4268 sslmode=disable"

def create_tables():
    try:
        with psycopg2.connect(DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE user_data (
                        id SERIAL PRIMARY KEY,     
                        tg_id BIGINT UNIQUE NOT NULL,    
                        name TEXT NOT NULL,            
                        age INT CHECK (age >= 0),       
                        education TEXT,                
                        skills TEXT[] DEFAULT '{}',     
                        experience TEXT,               
                        target_position TEXT            
                    );
                """)
                connection.commit()
                logger.info("Все таблицы успешно созданы.")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    create_tables()