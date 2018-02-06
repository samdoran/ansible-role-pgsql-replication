Failover playbook Usage:

Edit the inventory files as needed.

ansible-playbook -i inventory_cluster failover.yml --e pg_version=<version>
