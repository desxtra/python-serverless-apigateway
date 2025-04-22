provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "http_methods_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "http-methods-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.http_methods_vpc.id
  
  tags = {
    Name = "http-methods-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public_subnet_1" {
  vpc_id                  = aws_vpc.http_methods_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "http-methods-public-subnet-1"
  }
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id                  = aws_vpc.http_methods_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "http-methods-public-subnet-2"
  }
}

# Private Subnets
resource "aws_subnet" "private_subnet_1" {
  vpc_id                  = aws_vpc.http_methods_vpc.id
  cidr_block              = "10.0.3.0/24"
  availability_zone       = "${var.aws_region}a"
  
  tags = {
    Name = "http-methods-private-subnet-1"
  }
}

resource "aws_subnet" "private_subnet_2" {
  vpc_id                  = aws_vpc.http_methods_vpc.id
  cidr_block              = "10.0.4.0/24"
  availability_zone       = "${var.aws_region}b"
  
  tags = {
    Name = "http-methods-private-subnet-2"
  }
}

# Route Table for Public Subnets
resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.http_methods_vpc.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  
  tags = {
    Name = "http-methods-public-route-table"
  }
}

# Route Table Association for Public Subnets
resource "aws_route_table_association" "public_1_association" {
  subnet_id      = aws_subnet.public_subnet_1.id
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_route_table_association" "public_2_association" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.public_route_table.id
}

# NAT Gateway for Private Subnets
resource "aws_eip" "nat_eip" {
  domain = "vpc"
  
  tags = {
    Name = "http-methods-nat-eip"
  }
}

resource "aws_nat_gateway" "nat_gateway" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_subnet_1.id
  
  tags = {
    Name = "http-methods-nat-gateway"
  }
}

# Route Table for Private Subnets
resource "aws_route_table" "private_route_table" {
  vpc_id = aws_vpc.http_methods_vpc.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gateway.id
  }
  
  tags = {
    Name = "http-methods-private-route-table"
  }
}

# Route Table Association for Private Subnets
resource "aws_route_table_association" "private_1_association" {
  subnet_id      = aws_subnet.private_subnet_1.id
  route_table_id = aws_route_table.private_route_table.id
}

resource "aws_route_table_association" "private_2_association" {
  subnet_id      = aws_subnet.private_subnet_2.id
  route_table_id = aws_route_table.private_route_table.id
}

# Security Group for RDS
resource "aws_security_group" "rds_sg" {
  name        = "http-methods-rds-sg"
  description = "Security group for RDS MySQL instance"
  vpc_id      = aws_vpc.http_methods_vpc.id
  
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]  # Allow MySQL connections from within the VPC
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "http-methods-rds-sg"
  }
}

# Security Group for Lambda
resource "aws_security_group" "lambda_sg" {
  name        = "http-methods-lambda-sg"
  description = "Security group for Lambda functions"
  vpc_id      = aws_vpc.http_methods_vpc.id
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "http-methods-lambda-sg"
  }
}

# DB Subnet Group
resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "http-methods-rds-subnet-group"
  subnet_ids = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]
  
  tags = {
    Name = "http-methods-rds-subnet-group"
  }
}

# RDS MySQL Instance
resource "aws_db_instance" "http_methods_db" {
  identifier             = "http-methods-db"
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_type           = "gp2"
  username               = var.db_username
  password               = var.db_password
  db_name                = var.db_name
  parameter_group_name   = "default.mysql8.0"
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot    = true
  publicly_accessible    = false
  
  tags = {
    Name = "http-methods-db"
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "http-methods-lambda-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attach policies to the Lambda role
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Outputs
output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.http_methods_vpc.id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
}

output "lambda_security_group_id" {
  description = "ID of the Lambda security group"
  value       = aws_security_group.lambda_sg.id
}

output "rds_endpoint" {
  description = "Endpoint of the RDS instance"
  value       = aws_db_instance.http_methods_db.endpoint
}

output "lambda_role_arn" {
  description = "ARN of the Lambda IAM role"
  value       = aws_iam_role.lambda_role.arn
}

output "rds_username" {
  description = "Username for the RDS instance"
  value       = var.db_username
  sensitive   = true
}

output "rds_password" {
  description = "Password for the RDS instance"
  value       = var.db_password
  sensitive   = true
}

output "rds_database_name" {
  description = "Database name for the RDS instance"
  value       = var.db_name
}