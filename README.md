# gitlab-personal-access-token

Ensure PAT is present in gitlab database. This tool is mainly used when you need to automate gitlab installation and configuration afterwards. Normally you need to generate the access token via the web UI. With this tool, you can inject your own Personal access token directly into Gitlab database.

## Getting started

`API_KEY` value must be exactly 20 characters long

Example used in Ansible task:

```yaml
- name: Create Gitlab PAT for admin
  community.kubernetes.k8s:
    definition:
      apiVersion: batch/v1
      kind: Job
      metadata:
        name: gitlab-create-admin-pat
        namespace: default
      spec:
        ttlSecondsAfterFinished: 300
        template:
          spec:
            containers:
            - name: main
              image: cinaq/gitlab-personal-access-token:v0.1.0
              env:
              - name: PG_HOST
                value: gitlab-postgresql
              - name: PG_PORT
                value: "5432"
              - name: PG_DBNAME
                value: gitlabhq_production
              - name: PG_USERNAME
                value: gitlab
              - name: PG_PASSWORD
                value: "{{ gitlab_postgresql_password.resources[0].data['postgresql-password'] | b64decode }}"
              - name: USER_ID
                value: "1"
              - name: API_KEY
                value: "{{ gitlab_admin_api_key }}"
              - name: DB_KEY_BASE
                value: "{{ gitlab_rails_secrets.production.db_key_base }}"
              imagePullPolicy: Always
            restartPolicy: OnFailure
    wait: yes
    wait_timeout: 300
    wait_condition:
      type: Complete
      status: True

```

## License

MIT License