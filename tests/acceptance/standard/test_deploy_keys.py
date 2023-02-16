from tests.acceptance import (
    run_gitlabform,
)


def single_true(iterable):
    i = iter(iterable)
    # use the fact that thanks to iter() we will "consume"
    # all the elements of iterable up to the one that is True
    # so that there should be no other True in the rest
    return any(i) and not any(i)


class TestDeployKeys:
    def test__deploy_key_add(
        self, gitlab, group_and_project_for_function, public_ssh_key
    ):
        config_add = f"""
        projects_and_groups:
          {group_and_project_for_function}:
            deploy_keys:
              foobar:
                key: {public_ssh_key}
                title: some_key
        """
        run_gitlabform(config_add, group_and_project_for_function)

        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert single_true([key["title"] == "some_key" for key in deploy_keys])

    def test__deploy_key_add_delete(
        self, gitlab, group_and_project_for_function, public_ssh_key
    ):
        config_add = f"""
        projects_and_groups:
          {group_and_project_for_function}:
            deploy_keys:
              foobar:
                key: {public_ssh_key}
                title: some_key
        """
        run_gitlabform(config_add, group_and_project_for_function)

        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert single_true([key["title"] == "some_key" for key in deploy_keys])

        config_delete = f"""
        projects_and_groups:
          {group_and_project_for_function}:
            deploy_keys:
              foobar:
                title: some_key
                delete: true
        """
        run_gitlabform(config_delete, group_and_project_for_function)

        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert not any([key["title"] == "some_key" for key in deploy_keys])

    def test__deploy_key_add_delete_with_enforce(
        self, gitlab, group_and_project_for_function, public_ssh_key
    ):
        config_add = f"""
        projects_and_groups:
          {group_and_project_for_function}:
            deploy_keys:
              foobar:
                key: {public_ssh_key}
                title: some_key
        """
        run_gitlabform(config_add, group_and_project_for_function)

        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert len(deploy_keys) >= 1
        assert single_true([key["title"] == "some_key" for key in deploy_keys])

        config_delete = f"""
        projects_and_groups:
          {group_and_project_for_function}:
            deploy_keys:
              enforce: true
        """
        run_gitlabform(config_delete, group_and_project_for_function)

        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert len(deploy_keys) == 0

    def test__deploy_key_add_delete_readd(
        self, gitlab, group_and_project_for_function, public_ssh_key
    ):
        config_add = f"""
        projects_and_groups:
          {group_and_project_for_function}:
            deploy_keys:
              foobar:
                key: {public_ssh_key}
                title: some_key
        """
        run_gitlabform(config_add, group_and_project_for_function)

        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert single_true([key["title"] == "some_key" for key in deploy_keys])

        config_delete = f"""
        projects_and_groups:
          {group_and_project_for_function}:
            deploy_keys:
              foobar:
                title: some_key
                delete: true
        """
        run_gitlabform(config_delete, group_and_project_for_function)

        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert not any([key["title"] == "some_key" for key in deploy_keys])

        run_gitlabform(config_add, group_and_project_for_function)
        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert single_true([key["title"] == "some_key" for key in deploy_keys])

    def test__deploy_key_add_delete_readd_under_different_name(
        self, gitlab, group_and_project_for_function, public_ssh_key
    ):
        config_add = f"""
            projects_and_groups:
              {group_and_project_for_function}:
                deploy_keys:
                  foobar:
                    key: {public_ssh_key}
                    title: a_title
            """
        run_gitlabform(config_add, group_and_project_for_function)

        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert single_true([key["title"] == "a_title" for key in deploy_keys])

        config_delete = f"""
            projects_and_groups:
              {group_and_project_for_function}:
                deploy_keys:
                  foobar:
                    title: a_title
                    delete: true
            """
        run_gitlabform(config_delete, group_and_project_for_function)

        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert not any([key["title"] == "a_title" for key in deploy_keys])

        config_readd = f"""
            projects_and_groups:
              {group_and_project_for_function}:
                deploy_keys:
                  foobar:
                    key: {public_ssh_key}
                    title: another_title
            """
        run_gitlabform(config_readd, group_and_project_for_function)
        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert single_true([key["title"] == "another_title" for key in deploy_keys])

    def test__deploy_key_update_title(
        self, gitlab, group_and_project_for_function, public_ssh_key
    ):
        config = f"""
            projects_and_groups:
              {group_and_project_for_function}:
                deploy_keys:
                  foobar:
                    key: {public_ssh_key}
                    title: title_before
            """
        run_gitlabform(config, group_and_project_for_function)

        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert single_true([key["title"] == "title_before" for key in deploy_keys])

        config = f"""
            projects_and_groups:
              {group_and_project_for_function}:
                deploy_keys:
                  # because it's the title that defines the key, we cannot immediately change key's title in the config.
                  # we need two element config - 1. delete it under old title, 2. add it under new title
                  foo:
                    title: title_before
                    delete: true
                  bar:
                    key: {public_ssh_key}
                    title: title_after
            """
        run_gitlabform(config, group_and_project_for_function)

        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert single_true([key["title"] == "title_after" for key in deploy_keys])
        assert not any([key["title"] == "title_before" for key in deploy_keys])

    def test__deploy_key_update_value(
        self,
        gitlab,
        group_and_project_for_function,
        public_ssh_key,
        other_public_ssh_key,
    ):
        config = f"""
        projects_and_groups:
          {group_and_project_for_function}:
            deploy_keys:
              foobar:
                key: {public_ssh_key}
                title: a_key
        """
        run_gitlabform(config, group_and_project_for_function)

        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert any([key["key"] == public_ssh_key for key in deploy_keys])

        config = f"""
        projects_and_groups:
          {group_and_project_for_function}:
            deploy_keys:
              foobar:
                key: {other_public_ssh_key}
                title: a_key
        """
        run_gitlabform(config, group_and_project_for_function)

        deploy_keys = gitlab.get_deploy_keys(group_and_project_for_function)
        assert not any([key["key"] == public_ssh_key for key in deploy_keys])
        assert any([key["key"] == other_public_ssh_key for key in deploy_keys])
