select client_addr, state, sent_location
write_location, flush_location, replay_location, sync_priority from pg_stat_replication;
