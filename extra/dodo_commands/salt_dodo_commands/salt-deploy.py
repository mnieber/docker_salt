# noqa
from dodo_commands.system_commands import DodoCommand
from plumbum.cmd import docker
import os


class SshServer:
    def __init__(self):
        self.ip = None
        self.roster_filename = None
        self.container_name = None


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument(
            "--src",
            dest="src_dir"
        )
        parser.add_argument(
            "--docker-image",
            dest="target_docker_image"
        )
        parser.add_argument(
            "hostname",
        )

    def run_ssh_server(self, docker_image, src_dir, hostname):
        ssh_server = SshServer()

        cleaned_docker_name = docker_image.replace(':', '_')
        ssh_server.container_name = "sshd_on_%s" % cleaned_docker_name

        # start ssh service on a new container based on docker_image
        self.runcmd(
            [
                'docker', 'run',
                '-d',
                '--rm',
                '--publish=0.0.0.0:22:22',
                '--name=%s' % ssh_server.container_name,
                docker_image,
                '/usr/sbin/sshd', '-D',
            ]
        )

        # copy public key to the docker container
        ssh_public_key = os.path.expandvars(
            '$HOME/.ssh/%s.pub' % self.get_config('/SSH/key_name')
        )
        self.runcmd(
            [
                'docker',
                'cp',
                ssh_public_key,
                '%s:/root/.ssh/authorized_keys' % ssh_server.container_name
            ]
        )

        # get the ip address
        ssh_server.ip = docker(
            'inspect',
            '-f',
            '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
            ssh_server.container_name
        )[:-1]

        # write the roster file
        ssh_server.roster_filename = os.path.join(
            src_dir, '.roster.%s' % ssh_server.container_name
        )
        with open(ssh_server.roster_filename, 'w') as ofs:
            ofs.write("%s:\n" % hostname)
            ofs.write("    host: %s\n" % ssh_server.ip)
            ofs.write("    priv: agent-forwarding\n")

        # try a simple ssh command
        self.runcmd(
            [
                'ssh',
                'root@%s' % ssh_server.ip,
                '-oStrictHostKeyChecking=no',
                '-oUserKnownHostsFile=/dev/null',
                'echo'
            ]
        )

        return ssh_server

    def commit_ssh_server(self, ssh_server, docker_image):
        # commit the container
        self.runcmd(
            [
                'docker',
                'commit',
                ssh_server.container_name,
                docker_image
            ]
        )

        # stop the container
        self.runcmd(
            [
                'docker',
                'stop',
                ssh_server.container_name
            ]
        )

        # remove roster
        os.unlink(ssh_server.roster_filename)

    def handle_imp(self, src_dir, target_docker_image, hostname, **kwargs):
        src_dir = src_dir or self.get_config('/SALT/src_dir')
        target_docker_image = target_docker_image or self.get_config(
            '/SALT/target_docker_image', None
        )

        if target_docker_image:
            ssh_server = self.run_ssh_server(
                target_docker_image, src_dir, hostname
            )
            salt_container_name = (
                'salt_deploy_to_%s' % ssh_server.container_name
            )
            roster_filename = os.path.basename(ssh_server.roster_filename)
        else:
            salt_container_name = 'salt_deploy_to_%s' % hostname
            roster_filename = "roster"

        # run salt-ssh
        srv_salt_src_dir = '/srv/salt/src'
        docker_args = [
            'docker', 'run',
            '--rm',
            '-it',
            '--volume=%s:%s' % (src_dir, srv_salt_src_dir),
            '--volumes-from=ssh-agent',
            '--env=SSH_AUTH_SOCK=/.ssh-agent/socket',
            '--workdir=%s' % srv_salt_src_dir,
            '--name=%s' % salt_container_name,
            self.get_config('/SALT/docker_image'),
        ]
        self.runcmd(
            docker_args +
            [
                'salt-ssh',
                # '-l', 'debug',
                '-i',
                '--roster-file=./%s' % roster_filename,
                hostname,
                'state.apply'
            ]
        )

        if target_docker_image:
            self.commit_ssh_server(ssh_server, target_docker_image)
