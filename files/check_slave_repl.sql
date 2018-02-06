select now() - pg_last_xact_replay_timestamp() AS replication_delay;
