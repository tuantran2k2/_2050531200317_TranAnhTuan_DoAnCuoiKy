
# ====================== DATA PATH_CV  ======================
DATAS_PATH = "./files"

from urllib.parse import quote_plus

password = quote_plus("tuandenk56")
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://root:{password}@127.0.0.1:3306/chatbot_cv"


#JWT login:
JWT  = "5878fe66-08ed-4e52-afee-86a16f1eb030"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 100000000



#STMP gửi mã đăng ký từ gmail
SECRET_KEY = "54d66538-9654-4b34-9f62-7465b3a8ce54"
JWT_REFRESH_KEY = "7b75afc6-dda1-4a9f-a9c4-71c7504d5a29"
SECRET_KEY = "54d66538-9654-4b34-9f62-7465b3a8ce54"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "khnh113a@gmail.com"
SMTP_PASSWORD = "mjkd poba rymf bhav"
VERIFICATION_TIMEOUT = 10


COLLECTION  = "jobs_collection"


AWS_BUCKET_NAME = "doancuoiky"
AWS_ACCESS_KEY_ID="AKIA2GOKAYY6JHWZNJMG"
AWS_SECRET_ACCESS_KEY="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"
AWS_DEFAULT_REGION="us-west-2"

