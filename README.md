
PostgreSQL Streaming Replication
=========
[![Galaxy](https://img.shields.io/badge/galaxy-samdoran.pgsql_replication-blue.svg?style=flat)](https://galaxy.ansible.com/samdoran/pgsql_replication)
[![Build Status](https://travis-ci.com/samdoran/ansible-role-pgsql-replication.svg?branch=master)](https://travis-ci.com/samdoran/ansible-role-pgsql-replication)

Configure PostgreSQL streaming replication between two or more nodes. This role was developed and tested for use on PostgreSQL for setting up a redundant database backend for [Ansible Tower](https://www.ansible.com/tower). This will not configure advanced clustering but will configure two PostgreSQL nodes in a master/replica configuration.

Each host defined in `pgsqlrep_group_name` will be added to the `pg_hba.conf` on the master node.

This role leverages included with the [Ansible Tower installer](https://releases.ansible.com/ansible-tower/setup/).

Requirements
------------

Ansible Tower installer roles in your `roles_path` as well as a properly configured Ansible Tower inventory file.

Add the replica database node to the Ansible Tower inventory file and define `pgsqlrep_role` for each database host.

```
[tower]
tower1 ansible_connection=local
tower2
tower3

[database]
db-master pgsqlrep_role=master

[database_replica]
db-replica pgsqlrep_role=replica

...

```



Role Variables
--------------

| Name              | Default Value       | Description          |
|-------------------|---------------------|----------------------|
| `pg_port` | `5432` | PostgreSQL port |
| `pgsqlrep_role` | `skip` | `master` or `replica`, which determines which tasks run on the host. |
| `pgsqlrep_user` | `replicator` | User account that will be created and used for replication. |
| `pgsqlrep_password` | `[undefined]` | Password for replication account |
| `pgsqlrep_wal_level` | `hot_standby` | WAL level |
| `pgsqlrep_max_wal_senders` | `groups[pgsqlrep_group_name] | length * 2` | Max number of WAL senders. The minimum needed is two per replica: one for the connection to the master and another for the initial sync. |
| `pgsqlrep_wal_keep_segments` | `100` | Max number of WAL segments. |
| `pgsqlrep_synchronous_commit` | `local` | Set to `on`, `local`, or `off`. Setting to `on` will cause the master to stop accepting writes in the replica goes down. See [documentation](https://www.postgresql.org/docs/9.1/static/runtime-config-wal.html#GUC-SYNCHRONOUS-COMMIT) |
| `pgsqlrep_application_name` | `awx` | Application name used for synchronization. |
| `pgsqlrep_group_name` | `database_replica` | Name of the group that contains the replica database nodes. |
| `pgsqlrep_group_name_master` | `database` | Name of the gorup that contains the master database node. |
| `pgsqlrep_master_address` | `[default IPv4 of the master]` | If you need something other than the default IPv4 address, for exaample, FQDN, define it here. |
| `pgsqlrep_replica_address` | `[default IPv4 of the replica(s)]` | If you need something other than the default IPv4 address, for exaample, FQDN, define it here. |
| `pgsqlrep_postgres_conf_lines` | `[see defaults/main.yml]` | Lines in `postgres.conf` that are set in order to enable streaming replication. |


Dependencies
------------
The following roles from the [Ansible Tower installer](https://releases.ansible.com/ansible-tower/setup/) are required:

  - repos_el
  - postgresql

Example Playbook
----------------

Install this role alongside the roles used by the Ansible Tower installer (bundled or standalone). Then run the example playbook.

**Note:** This example playbook overrides the IP address for the master and replica nodes by getting the last IP from the list of all IPs on the system. This is just an example of how to override this value if the default IP address does not provide the desired IP.

**Note:** If you want to allow _all_ IP addresses to connect to the master node, use `pgsqlrep_replica_address: "{{ groups[pgsqlrep_group_name] | map('extract', hostvars, 'ansible_all_ipv4_addresses') | flatten }}"`.

**Note:** This playbook is not regularly tested and is meant as a guideline only. Use at your own risk.


```yaml
- name: Configure PostgreSQL streaming replication
  hosts: database_replica

  tasks:
    - name: Find recovery.conf
      find:
        paths:
          - /var/lib/pgsql
          - /opt/rh/rh-postgresql10
        recurse: yes
        patterns: recovery.conf
      register: recovery_conf_path

    - name: Remove recovery.conf
      file:
        path: "{{ item.path }}"
        state: absent
      loop: "{{ recovery_conf_path.files }}"

    - name: Add replica to database group
      add_host:
        name: "{{ inventory_hostname }}"
        groups: database
      tags:
        - always

    - import_role:
        name: repos_el

    - import_role:
        name: packages_el
      vars:
        packages_el_install_tower: no
        packages_el_install_postgres: yes

    - import_role:
        name: postgres
      vars:
        postgres_allowed_ipv4: "0.0.0.0/0"
        postgres_allowed_ipv6: "::/0"
        postgres_username: "{{ pg_username }}"
        postgres_password: "{{ pg_password }}"
        postgres_database: "{{ pg_database }}"
        max_postgres_connections: 1024
        postgres_shared_memory_size: "{{ (ansible_memtotal_mb*0.3)|int }}"
        postgres_work_mem: "{{ (ansible_memtotal_mb*0.03)|int }}"
        postgres_maintenance_work_mem: "{{ (ansible_memtotal_mb*0.04)|int }}"
      tags:
        - postgresql_database


- name: Configure PSQL master server
  hosts: database[0]

  vars:
    pgsqlrep_master_address: "{{ hostvars[groups[pgsqlrep_group_name_master][0]]['ansible_facts]['all_ipv4_addresses'][-1] }}"
    pgsqlrep_replica_address: "{{ hostvars[groups[pgsqlrep_group_name][0]]['ansible_facts]['all_ipv4_addresses'][-1] }}"

  tasks:
    - import_role:
        name: samdoran.pgsql_replication


- name: Configure PSQL replica(s)
  hosts: database_replica

  vars:
    pgsqlrep_master_address: "{{ hostvars[groups[pgsqlrep_group_name_master][0]]['ansible_facts']['all_ipv4_addresses'][-1] }}"
    pgsqlrep_replica_address: "{{ hostvars[groups[pgsqlrep_group_name][0]]['ansible_facts']['all_ipv4_addresses'][-1] }}"

  tasks:
    - import_role:
        name: samdoran.pgsql_replication

```

This playbook can be run multiple times. Each time, it erases all the data on the replica node and creates a fresh copy of the database from the master.

If the primary database node goes down, here is a playbook that can be used to fail over to the secondary node.

```yaml
- name: Gather facts
  hosts: all
  become: yes


- name: Failover PostgreSQL
  hosts: database_replica
  become: yes

  vars:
    '9':
      env:
        PATH: /usr/pgsql-{{ pgsql_version }}/bin:{{ ansible_env.PATH }}
        PGDATA: /var/lib/pgsql/{{ pgsql_version }}/data
    '10':
      env:
        PATH: /opt/rh/rh-postgresql10/root/usr/bin:{{ ansible_env.PATH }}
        PGDATA: /var/opt/rh/rh-postgresql10/lib/pgsql/data
        LIBRARY_PATH: /opt/rh/rh-postgresql10/root/usr/lib64
        JAVACONFDIRS: '/etc/opt/rh/rh-postgresql10/java:/etc/java'
        LD_LIBRARY_PATH: /opt/rh/rh-postgresql10/root/usr/lib64
        CPATH: /opt/rh/rh-postgresql10/root/usr/include
        PKG_CONFIG_PATH: /opt/rh/rh-postgresql10/root/usr/lib64/pkgconfig

  tasks:
    - name: Get the current PostgreSQL Version
      import_role:
        name: samdoran.pgsql_replication
        tasks_from: pgsql_version.yml

    - name: Promote secondary PostgreSQL server to primary
      command: pg_ctl promote
      become_user: postgres
      environment: "{{ pgsql_version.split('.')[0]['env']] }}"
      ignore_errors: yes


- name: Update Ansible Tower database configuration
  hosts: tower
  become: yes

  tasks:
    - name: Update Tower postgres.py
      lineinfile:
        dest: /etc/tower/conf.d/postgres.py
        regexp: "^(.*'HOST':)"
        line: "\\1 '{{ hostvars[groups['database_replica'][0]]['ansible_facts']['default_ipv4']['address'] }}',"
        backrefs: yes
      notify: restart tower

  handlers:
    - name: restart tower
      command: ansible-tower-service restart
```

License
-------

Apache 2.0
