# redis sessions

# redis expire will be set according to cookie age too
SESSION_COOKIE_AGE = 3600 * 24 * 14  # 14 days

SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 1,
    # 'password': '',  # password can be set here
    'prefix': 'bcm_session',
    'socket_timeout': 3
}
