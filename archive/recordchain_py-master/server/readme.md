
generate the server using the jumpscale tools,

## requirements


# jumpscale 93

make sure jumpscale 9.3 has been installed [see here](https://github.com/Jumpscale/core9)

# go-raml

```bash
js9 'j.tools.prefab.local.runtimes.golang.goraml()'
```

# the api specs

get the code for the specs
```bash
js9_code get --url "https://github.com/rivine/recordchain"
```

## to generate

- go in this dir, call generate_reset.sh if you want to reset as well (careful) otherwise generate.sh


