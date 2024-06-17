from decouple import config

class Config:
    SECRET_KEY=config('SECRET_KEY')

class DevelomentConfig(Config):
    DEBUG=True

config={
    'development' : DevelomentConfig
}