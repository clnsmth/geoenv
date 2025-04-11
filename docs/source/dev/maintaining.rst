.. _maintaining:

Maintainers Guide
=================

Welcome—and thank you for helping maintain `geoenv`! 🚀

Maintainers keep the engine running and the community thriving. This guide complements the :ref:`contributing` guide and includes everything you need to manage contributions and releases.

As a maintainer, you’re still a contributor—please follow the same steps when submitting code or documentation changes.

Collaboration Comes First
-------------------------

Sometimes we meet contributors halfway—cleaning up commits, refining docs, or offering extra help. That’s okay. A kind and helpful tone makes a big difference.

If you're short on time, it's totally fine—just leave a comment to let contributors know when you’ll be back.

Reviewing Pull Requests
-----------------------

Pull request reviews 🔍 help ensure contributions are:

- Aligned with project goals
- Tested and reliable
- Documented and understandable

Even though maintainers *can* bypass reviews, we encourage PR review in all cases.

Review Checklist
~~~~~~~~~~~~~~~~

When reviewing a pull request, please follow this checklist 📋:

1. Point the pull request to the `development` branch.
2. Open a GitHub review on the pull request.
3. Confirm that the :ref:`ci-workflow` passes.
4. Check the CI logs—look for any Pylint messages (even if not failing).
5. Ensure new features or bug fixes include meaningful test coverage.
6. Review the code and docs diffs.
7. Confirm commit messages follow :ref:`writing-good-commit-messages`.
8. Submit the review, or collaborate via a `feature branch` if needed.

Once reviewed, the PR is ready to merge into `development`. See :ref:`merging-features-into-development` for how.


Branch Strategy
---------------

- `main`: Current stable release
- `development`: In-progress features (always stable & releasable)
- `feature`: All new work starts here

.. _feature-branches:

Feature Branches
~~~~~~~~~~~~~~~~

Use `feature` branches for all changes—even docs or refactors. Include the issue number and a short description:
Example: ``30-release-workflow``

.. _merging--into-development:

Merging into Development
~~~~~~~~~~~~~~~~~~~~~~~~

When a feature is complete, merge the feature branch into `development` using GitHub:

1. Squash merge the pull request
2. Edit the commit message to follow :ref:`writing-good-commit-messages`
3. Delete the feature branch

Forgot something? Just open a new PR. Don’t resurrect merged branches.

.. _commit message footer: https://github.com/angular/angular/blob/convert/CONTRIBUTING.md#commit-message-footer

Merging Development into Main
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When releasing:

1. Open a PR from `development` → `main`
2. Ensure CI/CD checks pass
3. Get a review from another maintainer
4. **Do not merge in GitHub**

Instead:

5. Pull `development` and `main` locally
6. Merge `development` into `main`
7. Push to `main`

This preserves a clean, linear history with correct commit styling.

After merging:

8. CI/CD runs a release via `Python Semantic Release`_
9. Docs are deployed to `readthedocs.io`_
10. Pull `main` and `development` again to sync locally

.. _readthedocs.io: https://geoenv.readthedocs.io/en/latest/


.. _hot-fixes:

Hotfixes
~~~~~~~~

All hotfixes 🚑 go through the same flow:
`feature` → `development` → `main`

Never hotfix `main` directly.

Branch Protection & Secrets
---------------------------

Branch Rules
~~~~~~~~~~~~

The following GitHub branch rules ✅ are enforced on `main` and `development`:

- PR approval
- CI checks pass
- Branch is up-to-date
- Conversations resolved
- Linear commit history

Maintainers *can* skip PR approval, but it’s encouraged in most cases.

Release Token
~~~~~~~~~~~~~

A GitHub secret 🔐 named ``RELEASE_TOKEN`` (a maintainer’s personal access token) is required for :ref:`cd-workflow` to complete.


CI & CD Workflows
-----------------

GitHub Actions power our automation. 🤖

.. _ci-workflow:

CI Workflow
~~~~~~~~~~~~

Runs on PRs and pushes to `main` / `development`. It checks:

1. Code formatting with `Black`_ (required)
2. Linting with `Pylint`_ (optional but encouraged)
3. Testing with `Pytest`_ (required)
4. Docs build with `Sphinx`_ (required)

.. _cd-workflow:

CD Workflow
~~~~~~~~~~~~

Runs on push to `main`:

1. Builds, versions, and tags via `Python Semantic Release`_
2. Merges `main` → `development` automatically

.. _Black: https://black.readthedocs.io/en/stable/
.. _Pylint: https://pylint.pycqa.org/en/latest/
.. _Pytest: https://docs.pytest.org/en/latest/

.. _developing-features-as-a-maintainer:

Developing as a Maintainer
--------------------------

You don’t need to fork the repo—just create a `feature` branch directly in the upstream repository and open a pull request to `development`. 🏗

Dependency & Environment Management
-----------------------------------

We use `Poetry`_ for managing development and distribution dependencies. 📦

For users who prefer `Conda`_, we provide `environment.yml` files to help maintain compatibility.

Update them with:

::

    conda env export --from-history --file environment-min.yml
    conda env export --no-builds --file environment.yml

To generate `requirements.txt` for pip installs:

::

    pip list --format=freeze > requirements.txt

.. _Poetry: https://python-poetry.org/
.. _Conda: https://conda.io/projects/conda/en/latest/
.. _pip: https://pip.pypa.io/en/stable/
.. _Python Semantic Release: https://python-semantic-release.readthedocs.io/en/latest/
.. _Angular commit style: https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit
.. _Sphinx: https://www.sphinx-doc.org/en/master/
