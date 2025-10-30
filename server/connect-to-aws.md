Deploy on EC2 Instance (manual)

Launch an EC2 instance (Amazon Linux or Ubuntu).

Install Node.js, Git, and PM2:

sudo apt update
sudo apt install -y nodejs npm git
sudo npm install -g pm2


Clone your repo:

git clone <your-github-repo-url>
cd <repo-name>
npm install

nano .env
change the database url in the format 

and make the database created to be publically accessable

DATABASE_URL="postgresql://<username>:<password>@<host>:<port>/<database>?schema=public"

change username to your username
change password to your password
change host to your endpoint
change port to 5432
change database to your database name


Start your app with PM2:

then npx prisma generate
and then  npx prisma migrate dev

Allow inbound traffic on port 5000 in your EC2 Security Group.

⚙️ Step 3: Connect RDS and EC2

Go to RDS → Databases → Connectivity & Security

In “VPC security groups”, add the EC2 security group as an inbound rule:

Type: PostgreSQL
Port: 5432
Source: EC2 security group


✅ This lets your EC2 backend communicate with RDS.



Invoke-WebRequest -Uri "http://yourip:5000/api/auth/register" -Method POST -ContentType "application/json" -Body '{"email":"test1@example.com","password":"password123","name":"Test User"}'




