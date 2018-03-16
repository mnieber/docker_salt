The salt docker image
=====================

The Salt Dodo Commands project contains a docker image with the Salt deployment tool. This allows you to run salt-ssh and deploy software to a remote server. The docker file for this salt image is {{ '${/DOCKER/images/base/build_dir}/Dockerfile' | dodo_expand(link=True) }}. The other docker image parameters are given in {{ '/DOCKER/images/base' | dodo_expand(key=True) }}

Building the salt image
-----------------------

.. code-block:: bash

    $(dodo activate salt)
    dodo dockerbuild base

Deploying to a docker image with salt
-------------------------------------

We will first look at deploying to a docker image, which is possible by:

- running a sshd service in a docker container.
- deploying to the container over ssh
- committing the docker container to a new docker image

Note that the docker container must have `sshd` installed for this to work.

Suppose you have some salt sources in `~/projects/foo/src/salt`. To deploy the `"prod"` variant to a `foo:base` docker image:

.. code-block:: bash

    # first start the ssh-agent service
    dodo salt-ssh-agent start
    # then deploy with
    dodo salt-deploy --src ~/projects/foo/src/salt --docker-image foo:base prod

This will:

- start a docker container called `sshd_on_foo_base`.
- find the value of ({{ '/SSH/key_name' | dodo_expand(key=True) }}) in the configuration
- copy the corresponding public key to `sshd_on_foo_base`.
- create a temporary `.roster` file that sets the ip of `sshd_on_foo_base` as the target for deploying the `prod` variant.
- run `salt-ssh` on a docker container called `salt_deploy_to_foo_base`. This docker container uses the key forwarded by the `ssh-agent` container.

If you don't supply the `--src` or `--docker-image` argument, the command will use the values of `${/SALT/src_dir}` and `${/SALT/docker_image}`.
