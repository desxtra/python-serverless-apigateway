
# Serverless lambda, api, terraform

A simple python app to test lambda and apigateway


## Deployment

To deploy this app into aws run:

```bash
  git clone https://github.com/desxtra/python-serverless-apigateway.git
```
```bash
  cd python-serverless-apigateway
```
```bash
  cd terraform
```
```bash
  terraform init
```
```bash
  terraform apply
```
## Environment Variables

To run this project, you will need to add the following environment variables to your terraform.tfvars file

`aws_region  = "your_region"`

`db_username = "your_user"`

`db_password = "your_db_password"`

`db_name     = "your_db_name"`

