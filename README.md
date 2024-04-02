# akamai-tf-tools

Script to export akamai properties in bulk.


| | |
|--|:--|
| Author:                   | Shohei Tanaka(@xcir) |
| Date:                     | - |
| Version:                  | trunk |
| Manual section:           | 7 |

# Require

- docker
- ~/.edgerc([Akamai credential file](https://techdocs.akamai.com/developer/docs/set-up-authentication-credentials))

# How to use

[see.](https://labs.gree.jp/blog/?p=22991)

# Commands

## akamai-docker.sh

run `akamai/shell`

## get_property.sh [property name] [property ver(option)]

Can only be executed in `akamai/shell`.
Exports the specified property.
save path is props/`ctr_contractID`/`grp_groupID`/`[property name]`/

## get_all_property.py

Can only be executed in `akamai/shell`.
Exports all property.
save path is props/`ctr_contractID`/`grp_groupID`/`[property name]`/

## maintenance.py -f -x

Can only be executed in `akamai/shell`.
Export, update, and delete properties.

- -f
  - If tfstate is present, attempt to reacquire the property.
- -x
  - Execute the export, update, and delete.

# License

Except for the sample-template/ folder, all other folders are BSD-2-Clause licensed.

sample-template/ is based on [akamai/examples-terraform](https://github.com/akamai/examples-terraform).
