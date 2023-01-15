#!/bin/bash
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/y8q1v8m0
docker build -t codefresh-package-parser:1.3.0 ./codefresh-package-parser/
docker tag codefresh-package-parser:1.3.0 public.ecr.aws/y8q1v8m0/codefresh-package-parser:1.3.0
docker tag codefresh-package-parser:1.3.0 public.ecr.aws/y8q1v8m0/codefresh-package-parser:latest
docker push public.ecr.aws/y8q1v8m0/codefresh-package-parser:latest
docker push public.ecr.aws/y8q1v8m0/codefresh-package-parser:1.3.0
