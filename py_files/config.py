import os

USER_DATA_PATH = os.path.abspath(os.path.join(os.getcwd(), '..', 'user_data'))
os.makedirs(USER_DATA_PATH, exist_ok=True)
USER_PATH = os.path.join(USER_DATA_PATH, 'users')
os.makedirs(USER_PATH, exist_ok=True)


