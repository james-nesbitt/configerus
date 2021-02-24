# Configerus documentation

## Getting to know configerus

Configerus requires some orientation on language and concept used, which is
easier to explain using examples:

### loading config

Usually refers to loading config for a `label` from all sources, and merging it.

Before you have `loaded` the source plugins have probably done very little in
terms of resource consumption, other than perhaps some raw validation.

A label allows a source to compartmentalize top level config, but it is also
there for some plugin realities, such as comparing different files to
non-file sources.

Loading is implemented by the `.load({label})` operation on a config object.
This returns a LoadedConfig object.

### get() values from loaded config

Once a label has been `loaded`, you can `get` values from the config by asking
for a "dot" notation path in the resulting primitive.

Get is implemented by running a `.get({target})` on a loaded config object.

### templating syntaxes

These are effectively regex patterns that tell configerus formatter plugins to
process config before returning it.

In general, templated values where the template matches the entire value are
mutated in type when a replacement is found, but non-full matches perform string
replacements,

Some examples are:

#### Get formatter

a .get() value like "My name is {user.name}" would try to replace the {user.name}
portion with a .get('user.name').  The retrieval can point to other config labels
and can specify a default value if the value isn't found.

If your template portion of a string is the whole string, and the entire value
is replaced with the .get() return, which allows other primitives such as dicts
and lists to be used.

Some examples:

`.get('Pull from another label {other_label:get.target}')`
`.get('specify a default {i.dont.exist?I do exist}')`

#### File formatter

a .get*( value like "[file:path/to/my/file.json]") will actually return the
 contents of the file.json file.  If doing a full match replacement then the
 structured contents of the file replace the whole value, but a partial string
 template will just insert the string contents of the file.

### Validating

You can apply a validation either on the .load() or .get() operations.  This
means that you can use different formatters even on the same config.

validation is plugin based, but usually involves passing in a string identifier
for the validation that the plugin will recognize. If the plugin recognized the
pattern then it will attempt to validate the data, and throw an exception if
invalid content is found.

The `jsonschema` validator plugin expects `jsonschema:arbitrary.config.key`.  It
will retrieve schema from the config object using
`config.load('jsonschema').get('arbitrary.config.key')` and attempt to validate
using the response as a schema.
