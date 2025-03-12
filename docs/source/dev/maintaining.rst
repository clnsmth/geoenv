.. _maintaining:

Maintainers Guide
=================

Many thanks for your help maintaining our project! Without your contribution, development would be considerably slower and the user community left waiting longer.

This document complements the `Contributor's Guide <contributing.html>`_ by providing additional steps for integrating contributions into the project's code base. As a maintainer, you are also a contributor, so please use the contributor guide when making changes in order to keep the development process open and consistent (note :ref:`developing-features-as-a-maintainer`).

Be Courteous
------------

Sometimes we need to meet contributors halfway. This means more work on our part but for benefit of the project and community. Please be courteous and patient.

If you are unable to respond fully to a pull request or issue in a timely manner, please let the contributor know that you will get to it as soon as you can.

Pull Request Review
-------------------

Pull request review facilitates refinement of a contribution before it's incorporated into the project. The goals are to ensure the contribution is consistent with the project's design, is well-documented, and is well-tested. We are not looking for perfection, but rather that the contribution does what it is intended to do.

*Though pull request review is required by the project's GitHub branch protection rules, maintainers are allowed to bypass review. Having said this, we generally encourage review in all cases.*

Here are a steps to help with your pull request review:

1. Start a GitHub review on the pull request.
2. Check that the :ref:`ci-workflow` passes. Even if successful, check the workflow run logs for Pylint related messages. Though not required, we recommend these messages be addressed.
3. New features or bug-fixes should include tests demonstrating the change.
4. Review the diffs of code and related documentation.
5. Check for compliance with our :ref:`commit-message` style.
6. Submit the review.

If collaboration on the pull request is needed, create a `feature branch` in GitHub, change the base branch of the pull request from `development` to the newly created `feature branch`, and merge. This allows the maintainer to lend a helpful hand.

When a pull request passes review, it is ready to be merged into the `development` branch (see :ref:`merging-features-into-development`).

Git and GitHub
--------------

We use a combination of git and GitHub features to version control and manage various aspects of our project. Generally, we prefer small, incremental changes that are easy to review and maintain.

.. _commit-message-style:

Commit Message Style
~~~~~~~~~~~~~~~~~~~~

Our project uses two different commit message styles. The first is used during feature development (see the Contributor's Guide :ref:`commit-message`). The second is used to convert a squash commit when merging a `feature branch` into `development`, and allows `Python Semantic Release`_ to streamline the reoccurring release process.

This second commit style is the `Angular commit style`_. Our project uses this style in full with the notable exceptions that the `commit message header`_ should not include the `scope` value, and that any related GitHub issues should be referenced. For example:

``feat: add framework for new feature (#3, #5)``

not

``feat(module): add framework for new feature``

.. _Python Semantic Release: https://python-semantic-release.readthedocs.io/en/latest/
.. _Angular commit style: https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit
.. _commit message header: https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit-message-header

Do your best to keep the commit message header from exceeding 52 characters in length, but no greater than 72 characters, and keep the commit message body from exceeding 72 characters.

*Note, Semantic Release may be bypassed in special circumstances. To do this, simply remove all Angular style "type" keywords from the commit message header.*



Branch Management
~~~~~~~~~~~~~~~~~

The `main` branch always reflects the current stable release, a `development` branch is used for incorporating new features, and `feature` branches implement changes. The `development` branch is always in a releasable state.

.. _feature-branches:

Feature Branches
^^^^^^^^^^^^^^^^

Any sort of change, including new features, documentation, refactors, and fixes, should be done on a `feature branch` to facilitate iterative collaboration. It can be helpful when feature branch names reference the issue and describes the feature, for example, ``30-release-workflow``.

.. _merging-features-into-development:

Merging Features into Development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When a feature is complete and ready for integration with the project, it should be merged into `development` following these steps:

1. Pull the remote `feature branch` into your local repository.
2. Rebase the `feature branch` onto the `development` branch.
3. Force push your local `feature branch` to the remote `feature branch`.
4. Ensure the :ref:`ci-workflow` passes.
5. Squash merge the `feature branch` into `development` using the GitHub pull request interface, and following the Angular commit style mentioned in the :ref:`commit-message-style` guidelines. To do this:
    i. Edit the commit message header.
    ii. Preserve the commit message body as is (now a squashed set of commits).
    iii. Add keywords in the `commit message footer`_ to close out or mention any related GitHub issues.
    iv. Merge the pull request.

.. _commit message footer: https://github.com/angular/angular/blob/convert/CONTRIBUTING.md#commit-message-footer

If at this point, part of the feature was forgotten, don't restore the `feature branch`, rather open a new pull request on `development`, and iterate back through the contributor process.

Merging Development into Main
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When it's time to create a new release, a project maintainer, with repository write access, will merge the `development` branch into `main` locally, and then push to the remote, which will then kick-start the automated release workflow (see :ref:`cd-workflow`). This approach to merging, is taken in order to preserve a linear commit history and to retain the Angular styled commit messages required by `Python Semantic Release`_.

Here's a sequence of steps for merging `development` into `main` and creating a new release:

1. Open a pull request from the `development` branch to `main`.
2. Check that the :ref:`ci-workflow` and other requirements pass.
3. Get a pull request review from another maintainer (if possible).
4. *Do not merge in GitHub!* Instead follow these steps:
    i. Pull the remote `development` and `main` branches into your local repository.
    ii. Merge the `development` branch into `main`.
    iii. Push your local `main` branch to the remote.
5. Ensure both the :ref:`ci-workflow` and :ref:`cd-workflow` complete successfully.
6. Ensure the docs build and deploy successfully on `readthedocs.io`_.
7. Check the pull request has been merged and closed out.
8. Pull the remote `main` and `development` branches back into your local repository. This will keep your local branches in sync with the remote, which the semantic release made modifications to during the release process.

.. _readthedocs.io: https://geoenv.readthedocs.io/en/latest/

.. _hot-fixes:

Hot Fixes
^^^^^^^^^

Hotfixes should always be implemented in a `feature branch`, which is merged into `development`, and then merged into `main` using the approaches outlined above. Implementing a hotfix in `main` and merging into `development` will create problems in the commit history.

Branch Protection Rules
~~~~~~~~~~~~~~~~~~~~~~~

GitHub branch protection rules are used to help ensure the integrity of the codebase. The following rules are enforced on the `development` and `main` branches:

* Require a pull request approval before merging
* Require status checks to pass before merging
* Require branches to be up to date before merging
* Require conversation resolution before merging
* Require linear history

*The only protection rule maintainers are allowed to ignore is the "pull request approval" requirement. Having said this, we generally encourage review in all cases.*

Secrets
~~~~~~~

A GitHub repository secret, containing the personal access token of one of the maintainers with write access, is required for the :ref:`cd-workflow` to complete. This token should be added to the project's repository secrets with the name ``RELEASE_TOKEN``. This authentication is used by `Python Semantic Release`_ to commit changes created during the release proces to the `main` branch, which are then merged into the `development` branch. This latter step ensures the two branches remain synchronized.

Workflows
~~~~~~~~~

GitHub Actions are used for continuous integration and delivery.

.. _ci-workflow:

CI Workflow
^^^^^^^^^^^

The CI workflow is run on each pull request and push to the `development` and `main` branches. It performs the following steps:

1. Formats code in *src/* and *tests/* using `Black`_. This check is strictly enforced and will fail the workflow.
2. Analyzes code in *src/* and *tests/* using the project's `Pylint`_ configuration (see :ref:`code-format-and-analysis`). This check is not strictly enforced and will not fail the workflow. However, generally, Pylint recommendations should be followed.
3. Runs tests in *tests/* using `Pytest`_. This check is strictly enforced and will fail the workflow.
4. Builds the documentation (see :ref:`documentation-contributions`). This check is strictly enforced and will fail the workflow.

.. _Black: https://black.readthedocs.io/en/stable/
.. _Pylint: https://pylint.pycqa.org/en/latest/
.. _Pytest: https://docs.pytest.org/en/latest/

.. _cd-workflow:

CD Workflow
^^^^^^^^^^^

The CD workflow is run on push to the `main` branch for releases. It performs the following steps:

1. Runs `Python Semantic Release`_ to build the changelog, convert the distributions, bump the version number, and tag the release.
2. Merges changes in the `main` branch back into `development` to keep the branches synchronized.

.. _developing-features-as-a-maintainer:

Developing Features as a Maintainer
-----------------------------------

As a maintainer, when developing a new feature, you don't have to fork the project repository to your personal GitHub, and submit pull requests via that route. Rather, you may create a `feature branch` in the project's remote repository, and submit a pull request to `development` from there.

Dependency and Environment Management
-------------------------------------

This project uses `Poetry`_ to manage dependencies for development and distribution. Poetry keeps track of necessary packages and their versions, ensuring a consistent development environment.

For those who prefer using `Conda`_ for environment management, we provide environment files to define the Conda environment. This means package dependencies need to be maintained with Conda as well as Poetry. Update the Conda environment definition using the following commands::

    conda env export --from-history --file environment-min.yml
    conda env export --no-builds --file environment.yml

While Poetry is the recommended method for installation, we offer users an option to install the package using `pip`_. To get a requirements.txt file listing::

    pip list --format=freeze > requirements.txt

.. _Poetry: https://python-poetry.org/
.. _Conda: https://conda.io/projects/conda/en/latest/
.. _pip: https://pip.pypa.io/en/stable/
