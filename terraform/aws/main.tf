resource "aws_instance" "example" {
  ami           = "ami-b70554c8"
  // See https://aws.amazon.com/ec2/instance-types/
  instance_type = "t2.micro"

  subnet_id     = "subnet-565bc86c"

  key_name      = "remote3-key"
  vpc_security_group_ids = [
    "sg-cc5241a9"
  ]
}
