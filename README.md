# Project Deutzia: Creating a Audit Trail on a DynamoDB table using S3,CloudTrail Data Events, Lambda, CloudWatch Logs with Event Subscription Filters, Glue and Athena

This is a demo project on cretaing an Audit Trail of a DynamoDB table. All the data events are stored in a S3 bucket and CloudWatch Log Group and enabling viewing the data using Athena.

## Description

This sample project demonstrate creating a audit trail of a DynamoDB table using CloudTrail data events. The data event API calls are logged into a S3 bucket and CloudWatch Log Group. Using Subescription Filter, the events are pushed to a Kinesis Data Stream, which invokes a Lambda and formats the required attributes and saved them to a S3 bucket. A Glue Crawler runs every 10 mins and checks for any schema change. The audit table can be queried using Athena.

![Project Deutzia - Design Diagram](https://subhamay-projects-repository-us-east-1.s3.amazonaws.com/0090-deutzia/deutzia-architecture-diagram.png?)


## Getting Started

### Dependencies

* Create a Customer Managed KMS Key in the region where you want to create the stack..
* Modify the KMS Key Policy to let the IAM user encrypt / decrypt using any resource using the created KMS Key.

### Installing

* Clone the repository.
* Create a S3 bucket and make it public.
* Create the folders - deutzia/cft/nested-stacks, deutzia/cft/cross-stacks, deutzia/code
* Upload the following YAML templates to deutzia/cft/nested-stacks
    * athena-stack.yaml  
    * cloudwatch-log-stack.yaml 
    * glue-crawler-stack.yaml    
    * kinesis-stack.yaml     
    * s3-stack.yaml
    * cloudtrail-stack.yaml    
    * dynamodb-stack.yaml   
    * iam-role-stack.yaml   
    * lambda-function-stack.yaml 
    * sqs-stack.yaml
* Upload the following YAML templates to deutzia/cft/cross-stacks
    * custom-resource-lambda-stack.yaml
* Upload the following YAML templates to deutzia/cft/
    * deutzia-root-stack.yaml
* Zip and Upload the Python file  to deutzia/cft/code
* Create the cross-stack using the template custom-resource-lambda-stack.yaml by using the S3 url and pass the appropriate parameters.
* Create the entire using by using the root stack template custom-resource-lambda-stack.yaml by providing the required parameters and the s3 cross stack name created in the previous step.

### Executing program

* Create, Delete or Update an item in the DynamoDB table.
* After around 15 mins, query the Athena table to check the audit trail.
## Help

Post message in my blog (https://blog.subhamay.com)


## Authors

Contributors names and contact info

Subhamay Bhattacharyya  - [subhamay.aws@gmail.com](https://blog.subhamay.com)

## Version History

* 0.1
    * Initial Release


## License

This project is licensed under Subhamay Bhattacharyya. All Rights Reserved.

## Acknowledgments

Inspiration, code snippets, etc.
* [Stephane Maarek ](https://www.linkedin.com/in/stephanemaarek/)
* [Neal Davis](https://www.linkedin.com/in/nealkdavis/)
* [Adrian Cantrill](https://www.linkedin.com/in/adriancantrill/)
