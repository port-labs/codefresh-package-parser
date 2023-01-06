# Port Codefresh package parser workflow template

This repository contains:

- The code for a docker image that can be used during an ArgoCD Workflow (or Codefresh workflow) to parse package/library entities and send them to Port;
- A Workflow template definition that can be used with the docker image;
- The required service account, role and role binding definitions required to use the workflow template;
- An example secret definition to provide a `CLIENT_ID` and `CLIENT_SECRET` to use the workflow template;
- An example secret definition to provide a `token` to use the workflow template;
- Usage examples of the Workflow template as part of the ArgoCD workflow process.

The docker image is hosted and managed by Port, there is no need to build and host it yourself.

Use the provided examples to integrate Port with your existing ArgoCD and Codefresh CI process.

# Installation and usage

- Copy and commit the [packageParserWorkflowTemplate.yml](./packageParserWorkflowTemplate.yml) file to your Codefresh git source;
- Add the required service account, cluster role and role binding to your codefresh runtime namespace by using the command: `kubectl apply -f rbac.yml -n YOUR_NAMESPACE`;
- Add a secret to your cluster containing your `PORT_CLIENT_ID` and `PORT_CLIENT_SECRET` after encoding them in base64;
- Add a secret to your cluster containing your `token` after encoding them in base64;
- Use the `package-parser` template as shown in the [examples](./examples/).

# Available templates

## package-parser

The `package-parser` template gets the credentials required to clone a bitbucket repo and the path to a packages definition file and then creates the matching package entities in Port.

### Inputs

- `REPO_URL` - URL of the bitbucket repo to clone
- `GIT_TOKEN_SECRET` - name of the secret to get the bitbucket access token from;
- `GIT_TOKEN_SECRET_KEY` - key in the secret where the base64 encoded token is stored (default :`token`);
- `PORT_CREDENTIALS_SECRET` - name of the secret to get the `CLIENT_ID` and `CLIENT_SECRET` from (default: `port-credentials`);
- `PORT_CLIENT_ID_KEY` - key in the secret where the base64 encoded `PORT_CLIENT_ID` is stored (default: `PORT_CLIENT_ID`);
- `PORT_CLIENT_SECRET_KEY` - key in the secret where the base64 encoded `PORT_CLIENT_SECRET` is stored (default `PORT_CLIENT_SECRET`);
- `PACKAGE_MANAGER` - the package manager type to use as a parsing template for the input files, available values are: `C_SHARP`, `NPM`, `JAVA`;
- `PACKAGES_FILE_FILTER` - file filter to match package files by, for example: `*.csproj`;
- `INTERNAL_PACKAGE_FILTERS` - a comma delimited string to mark internal packages (packages whose name matches the filter will be marked as internal), for example: "port,json".

### Outputs

- `PARSED_PACKAGES_ARRAY` - array containing the identifiers of all of the package release versions created by the workflow template;

### Example usage

```yaml
- name: parse-and-report-packages
  templateRef:
    name: port-package-parser
    template: package-parser
  arguments:
    parameters:
      - name: REPO_URL
        value: bitbucket.org/port-labs/package-reporting-demo.git
      - name: GIT_TOKEN_SECRET
        value: bitbucket-access-token
      - name: PORT_CREDENTIALS_SECRET
        value: port-credentials
      - name: PORT_CLIENT_ID_KEY
        value: PORT_CLIENT_ID
      - name: PORT_CLIENT_SECRET_KEY
        value: PORT_CLIENT_SECRET
      - name: PACKAGE_MANAGER
        value: C_SHARP
      - name: PACKAGES_FILE_FILTER
        value: "*.csproj"
      - name: INTERNAL_PACKAGE_FILTERS
        value: "port,json"
```

To access the workflow outputs, use `{{workflow.outputs.parameters.PARSED_PACKAGES_ARRAY}}`
