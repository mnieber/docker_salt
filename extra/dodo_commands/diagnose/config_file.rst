Dodo Configuration
==================

The configuration for the Salt Dodo Commands environment is stored in {{ '${/ROOT/res_dir}/config.yaml' | dodo_expand(link=True) }}.

You can print the configuration in 2 ways:

- (unexpanded): `cat $(dodo which --config)`
- (expanded):   `dodo print-config`

Extra salt dodo commands are configured in {{ '/ROOT/command_path/1' | dodo_expand(key=True) }}. To see the list of all available commands run: `dodo`.
