import boto3, botocore, hashlib
from config import S3_KEY, S3_SECRET, S3_BUCKET, S3_LOCATION

s3 = boto3.client("s3", aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file_to_s3(file, bucket_name):

	'''
		Uploads picture to S3 bucket. hashes the file and uses it as the name, 
			avoiding multiple pictures hosted
	
		returns the url of hosted image to populate the database
	'''

	try:
		
		filename = str(hashlib.sha256(file.read()).hexdigest())+'.'+file.filename.split(".")[1] 
		file.seek(0)
		s3.upload_fileobj(file, bucket_name,  filename  )

	except Exception as e:
		print("Something Happened: ", e)
		return e

	return "{}{}".format(S3_LOCATION,  filename   )
