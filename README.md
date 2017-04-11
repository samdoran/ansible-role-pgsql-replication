PostgreSQL Streaming Replication
=========

Configure PostgreSQL streaming replication between two nodes. This was primarily developed and tested for use on PostgreSQL 9.4 for setting up a redundant database backend for [Ansible Tower](https://www.ansible.com/tower).

Requirements
------------



Role Variables
--------------

| Name              | Default Value       | Description          |
|-------------------|---------------------|----------------------|
| `` | `` |  |


Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

    - hosts: all
      roles:
         - postgresql
         - postgresql_replication

License
-------

MIT
