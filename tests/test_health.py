from testfm.advanced import Advanced
from testfm.constants import upstream_url
from testfm.health import Health
from testfm.log import logger


def test_positive_foreman_maintain_health_list(ansible_module):
    """List health check in foreman-maintain

    :id: 976ef4cd-e028-4545-91bb-72433d40d7ee

    :setup:
        1. foreman-maintain should be installed.

    :steps:
        1. Run foreman-maintain health list

    :expectedresults: Health check list should work.

    :CaseImportance: Critical
    """
    contacted = ansible_module.command(Health.list())
    for result in contacted.values():
        logger.info(result['stdout'])
        assert result["rc"] == 0


def test_positive_foreman_maintain_health_list_tags(ansible_module):
    """List tags for health check in foreman-maintain

    :id: d0a6c8c1-8266-464a-bfdf-01d405dd9bd2

    :setup:
        1. foreman-maintain should be installed.

    :steps:
        1. Run foreman-maintain health list-tags

    :expectedresults: Tags for health checks should list.

    :CaseImportance: Critical
    """
    contacted = ansible_module.command(Health.list_tags())
    for result in contacted.values():
        logger.info(result['stdout'])
        assert result["rc"] == 0


def test_positive_list_health_check_by_tags(ansible_module):
    """List health check in foreman-maintain by tags

    :id: 420d8e62-84d8-4496-8c24-037bd23febe9

    :setup:
        1. foreman-maintain should be installed.

    :steps:
        1. Run foreman-maintain health list --tags default

    :expectedresults: health checks according to tag should list.

    :CaseImportance: Critical
    """
    for tags in ['default', 'pre-upgrade']:
        contacted = ansible_module.command(Health.list({
            'tags': tags
        }))
        for result in contacted.values():
            logger.info(result['stdout'])
            assert result["rc"] == 0


def test_positive_foreman_maintain_health_check(ansible_module):
    """Verify foreman-maintain health check

    :id: bfff93dd-adde-4630-8411-1bb6b74daddd

    :setup:
        1. foreman-maintain should be installed.

    :steps:
        1. Run foreman-maintain health check

    :expectedresults: Health check should perform.

    :CaseImportance: Critical
    """
    contacted = ansible_module.command(Health.check())
    for result in contacted.values():
        logger.info(result['stdout'])
        assert "FAIL" not in result['stdout']


def test_positive_foreman_maintain_health_check_by_tags(ansible_module):
    """Verify foreman-maintain health check by tags

        :id: 518e19af-2dd4-4fb0-8c90-208cbd354107

        :setup:
            1. foreman-maintain should be installed.

        :steps:
            1. Run foreman-maintain health check --tags tag_name

        :expectedresults: Health check should perform.

        :CaseImportance: Critical
        """
    contacted = ansible_module.command(Health.list_tags())
    for result in contacted.values():
        output = result['stdout']
    output = [i.split(']\x1b[0m')[0] for i in output.split('\x1b[36m[') if i]
    for tag in output:
        contacted = ansible_module.command(Health.check({
            'tags': tag,
            'whitelist': 'disk-performance, packages-install'
        }))
        for result in contacted.values():
            logger.info(result['stdout'])
            assert "FAIL" not in result['stdout']
            assert result['rc'] == 0


def test_positive_check_hammer_ping(ansible_module):
    """Verify hammer ping check

    :id: b1eec8cb-9f94-439a-b5e7-8621cb35501f

    :setup:
        1. foreman-maintain should be installed.

    :steps:
        1. Run foreman-maintain health check --label hammer-ping

    :expectedresults: Health check should perform.

    :CaseImportance: Critical
    """
    contacted = ansible_module.command(Health.check({
        'label': 'hammer-ping'
    }))
    for result in contacted.values():
        logger.info(result['stdout'])
        assert "FAIL" not in result['stdout']


def test_negative_check_hammer_ping(ansible_module):
    """Verify hammer ping check

    :id: ecdc5bfb-2adf-49f6-948d-995dae34bcd3

    :setup:
        1. foreman-maintain should be installed.

    :steps:
        1. Run Katello-service stop
        2. Run foreman-maintain health check --label hammer-ping
        3. Run Katello-service start

    :expectedresults: Health check should perform.

    :CaseImportance: Critical
    """
    setup = ansible_module.command(Advanced.run_katello_service_stop())
    for result in setup.values():
        assert result['rc'] == 0
    contacted = ansible_module.command(Health.check({
        'label': 'hammer-ping'
    }))
    for result in contacted.values():
        logger.info(result['stdout'])
        assert "FAIL" in result['stdout']
    teardown = ansible_module.command(Advanced.run_service_start())
    for result in teardown.values():
        logger.info(result['stdout'])


def test_positive_pre_upgrade_health_check(ansible_module):
    """Verify pre-upgrade health checks

    :id: f52bd43e-79cd-488b-adbb-3c9e5bac32cc

    :setup:
        1. foreman-maintain should be installed.

    :steps:
        1. Run foreman-maintain health check --tags pre-upgrade

    :expectedresults: Pre-upgrade health checks should perform.

    :CaseImportance: Critical
    """
    contacted = ansible_module.command(Health.check({
        'tag': 'pre-upgrade'
    }))
    for result in contacted.values():
        logger.info(result['stdout'])
        assert "FAIL" not in result['stdout']


def test_positive_check_upstream_repository(ansible_module):
    """Verify upstream repository check

    :id: 349fcf33-2d25-4628-a6af-cff53e624b25

    :setup:
        1. foreman-maintain should be installed.

    :steps:
        1. Run foreman-maintain health check --label check-upstream-repository

    :expectedresults: Health check should perform.

    :CaseImportance: Critical
    """
    for name, url in upstream_url.items():
        ansible_module.yum_repository(
            name=name,
            description=name,
            file="upstream_repo",
            baseurl=url,
            enabled="yes",
            gpgcheck="no"
            )
    setup = ansible_module.file(
        path='/etc/yum.repos.d/upstream_repo.repo',
        state='present')
    assert setup.values()[0]["changed"] == 0
    contacted = ansible_module.command(Health.check([
            '--label', 'check-upstream-repository', '--assumeyes'
        ]))
    for result in contacted.values():
        logger.info(result['stdout'])
        assert result['rc'] == 0
    teardown = ansible_module.file(
        path='/etc/yum.repos.d/upstream_repo.repo',
        state='absent')
    assert teardown.values()[0]["changed"] == 1


def test_positive_available_space(ansible_module):
    """Verify available-space check

    :id: 7d8798ca-3334-4dda-a9b0-dc3d7c0903e9

    :setup:
        1. foreman-maintain should be installed.

    :steps:
        1. Run foreman-maintain health check --label available-space

    :expectedresults: Health check should perform.

    :CaseImportance: Critical
    """
    contacted = ansible_module.command(Health.check({
        'label': 'available-space'
    }))
    for result in contacted.values():
        logger.info(result['stdout'])
        assert "FAIL" not in result['stdout']
        assert result['rc'] == 0


def test_positive_check_hotfix_installed(ansible_module):
    """Verify check-hotfix-installed check

    :id: 3b6fbf3a-5c78-4283-996e-ca8da88a5d1b

    :setup:
        1. foreman-maintain should be installed.

    :steps:
        1. Run foreman-maintain health check --label check-hotfix-installed

    :expectedresults: Health check should perform.

    :CaseImportance: Critical
    """
    contacted = ansible_module.command(Health.check([
        '--label', 'check-hotfix-installed', '--assumeyes']))
    for result in contacted.values():
        logger.info(result['stdout'])
        assert "WARNING" not in result['stdout']
        assert result['rc'] == 0


def test_positive_check_hotfix_installed_with_file_changed(ansible_module):
    """Verify check-hotfix-installed check

    :id: d9023293-4173-4223-bbf5-328b41cf87cd

    :setup:
        1. foreman-maintain should be installed.
        2. modify some files of satellite

    :steps:
        1. Run foreman-maintain health check --label check-hotfix-installed

    :expectedresults: Health check should perform.

    :CaseImportance: Critical
    """
    file = ansible_module.find(
        paths='/opt/theforeman/tfm/root/usr/share/gems/gems/',
        patterns='fog-vsphere-*',
        file_type='directory')
    dpath = file.values()[0]['files'][0]['path']
    fpath = dpath + '/lib/fog/vsphere/requests/compute/list_clusters.rb'
    ansible_module.lineinfile(
        dest=fpath,
        insertafter='EOF',
        line="#modifying_file")
    setup = ansible_module.yum(
        name=['python-kitchen', 'yum-utils'],
        state='present')
    for result in setup.values():
        assert result['rc'] == 0
    contacted = ansible_module.command(Health.check({
        'label': 'check-hotfix-installed'
    }))
    for result in contacted.values():
        logger.info(result['stdout'])
        assert "WARNING" in result['stdout']
        assert result['rc'] == 1
    teardown = ansible_module.command(
        'yum -y reinstall tfm-rubygem-fog-vsphere')
    for result in teardown.values():
        assert result['rc'] == 0
