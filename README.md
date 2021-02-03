# Configerus

Dynamic and abstract configuration management

An extendable plugin based configuration system, which allows abstract config
primitives to be loaded from various prioritized sources.  Config from higher
priority source plugins takes precedence over lower priority, with some simple
deep merging.

Configerus makes config easy by:

1. having a simple construction method
2. allowing config to be pulled from a variatey of sources, such as json/yml in
   file paths, or custom dicts
3. using priorities, configerus allows config override, where some sources can
   override others.
4. deep configuration retrieval is easy using "dot" (one.two.three) notation to
   search in config trees

Configerus offers a few tricks for complex use-cases

1. you can apply simple validation (such as jsonschema) on retrieved config
2. you can use a templating syntax to embed config from one source into another
   at the time of retrieval
3. you can use a templating syntax to direct configeraus to replace a string
   file path with the contents of that file. Some files will be unmarshalled
   for the replacement.

Configerus makes advanced config management possible by:

1. allowing you to define your own sources, formatters and validators and inject
   them at run time
2. allowing you to extend using setuptools entrypoints for advanced functionality
   bootstrapping.

## Usage

Configerus has a bit of steep learning curve in its approach and construction
but it easy to use if it is set up correctly.

A cheap and dirty example:

If you have a folder `./config` that has to config files in it:
- settings.yaml
- values.json
```
import configerus
from configerus.contrib.dict import PLUGIN_ID_CONFIGSOURCE_DICT
from configerus.contrib.files import PLUGIN_ID_CONFIGSOURCE_PATH

config = configerus.new_config()
# tell configerus to read files from a path
config.add_source(PLUGIN_ID_CONFIGSOURCE_PATH).set_path('./config')
# add a dynamic dict to configerus, with a 90/100 priority
config.add_source(PLUGIN_ID_CONFIGSOURCE_DICT, priority=90).set_data({
    'values': {
        'one': 'overriden from dict'
    }
})

# load all of the settings
settings = config.load('settings')
user_id = settings.get('user.id') # expects that settings had {user: {id: 'some value'}}

# load some overriding values
values = config.load('values')  # loads the value file, but overrides from the dict
assert values.get('one') == 'overriden from dict'
```
