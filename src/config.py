import os

S3_BUCKET                 	= os.environ.get("S3_BUCKET_NAME")
S3_KEY                    	= os.environ.get("S3_ACCESS_KEY")
S3_SECRET                 	= os.environ.get("S3_SECRET_ACCESS_KEY")
S3_LOCATION               	= 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)


MONGO_USER					= os.environ.get("MONGO_USER")
MONGO_PASSWORD				= os.environ.get("MONGO_PASSWORD")
MONGO_DATABASE				= os.environ.get("MONGO_DATABASE")
MONGO_CONNECTION_URI		= 'mongodb+srv://{}:{}@ymmatheus-cluster-dif6k.mongodb.net/test?retryWrites=true'.format(MONGO_USER, MONGO_PASSWORD)

SECRET_KEY                	= os.urandom(32)
DEBUG                     	= True
PORT                      	= 5000