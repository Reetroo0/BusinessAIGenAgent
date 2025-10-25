# from config import connection_pool, logger


# # Подключение к БД
# def pgConnect():
#     try:
#         conn = connection_pool.getconn()
#         try:
#             with conn.cursor() as cur:
#                 logger.info("Database connection is OK")
#                 conn.commit()
#         finally:
#             connection_pool.putconn(conn)
#     except Exception as e:
#         logger.error(f"Error connection to database: {e}")