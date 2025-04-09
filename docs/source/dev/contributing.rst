.. _contributing:

Contributor's Guide
===================

Welcome—and thank you for considering contributing to `geoenv`!

We're excited to have you here. Whether you're fixing a bug, improving docs, or proposing a new feature, your contributions make this project better.

Got a question or idea? Start a conversation in our `GitHub issues`_!

.. _GitHub issues: https://github.com/clnsmth/geoenv/issues

Be Respectful
-------------

We’re committed to creating a friendly, welcoming space for collaboration.

Please be kind and constructive in all interactions. Diversity of background, perspective, and experience strengthens our community.

See our :ref:`Code of Conduct <conduct>` for details.

.. _Code of Conduct: https://geoenv.readthedocs.io/en/latest/dev/conduct/

Is Your Idea a Good Fit?
------------------------

Not sure if your idea fits the project? Let’s talk!

Open a quick `GitHub issue`_ and we’ll help you assess it. While we thoughtfully review every suggestion, the maintainers ultimately determine what aligns with the project goals.

.. _GitHub issue: https://github.com/clnsmth/geoenv/issues

How to Contribute Code
----------------------

Here’s a simple guide to submitting a pull request:

1. Fork the repo.
2. Create a new feature branch off `development`.
3. Install the project:
   ``poetry install``
4. Run the tests:
   ``poetry run pytest``
   Investigate and fix any failures.
5. Add test cases to support your change.
6. Make your changes. Update docs where relevant (see :ref:`documentation-contributions`).
7. Re-run tests to confirm everything still works.
8. Format and lint your code (see :ref:`code-format-and-analysis`).
9. Build the docs:
   ``poetry run make --directory=docs clean html``
10. Build the package:
    ``poetry build``
11. Write a good commit message (see :ref:`commit-message`).
12. Open a Pull Request targeting the `development` branch.

.. _reStructuredText: https://thomas-cokelaer.info/tutorials/sphinx/docstring_python.html
.. _pytest: https://docs.pytest.org/en/latest/
.. _Angular commit style: https://github.com/angular/angular/blob/convert/CONTRIBUTING.md#-commit-message-format

We’ll review your submission and may offer suggestions. Once everything looks good—it’s in!

Code Style & Linting
~~~~~~~~~~~~~~~~~~~~

To keep the codebase consistent, we use:

- **`Black`** for automatic formatting
- **`Pylint`** for static code analysis

Run both with:

::

    poetry run black src/ tests/
    poetry run pylint src/ tests/

.. _Black: https://black.readthedocs.io/en/stable/
.. _Pylint: https://pylint.pycqa.org/en/latest/

.. _code-format-and-analysis:

.. _documentation-contributions:

Improving the Documentation
---------------------------

We love doc updates!

The docs live in the ``docs/`` directory and use `Sphinx`_ + `reStructuredText`_.

To build them locally:

::

    poetry run make --directory=docs clean html

API docs are generated from `PEP 287`_-style docstrings.

.. _reStructuredText: https://thomas-cokelaer.info/tutorials/sphinx/docstring_python.html
.. _Sphinx: http://sphinx-doc.org/index.html
.. _PEP 287: https://peps.python.org/pep-0287/

.. _documentation-contributions:

.. _bug-reports:

Bug Reports
-----------

If you find a bug, we want to hear about it! First, check the `GitHub issues`_ to see if it’s already been reported.

If it’s new, please use the `Bug report`_ issue template.

.. _Bug report: https://github.com/clnsmth/geoenv/issues/new/choose
.. _GitHub issues: https://github.com/clnsmth/geoenv/issues

Feature Requests
------------------

Got an idea for a feature? Let’s explore it! Before submitting, please search existing `GitHub issues`_.

To propose something new, use the `Feature request`_ template.

.. _Feature request: https://github.com/clnsmth/geoenv/issues/new/choose

.. _commit-message:

Writing Good Commit Messages
-------------------------------

A good commit message explains *what* changed and *why*.

We recommend:

- Limit the **header** to 52 characters or less.
- Wrap the **body** at 72 characters.
- Follow the `Angular style`_ format when possible.

.. _Angular style: https://github.com/angular/angular/blob/convert/CONTRIBUTING.md#-commit-message-format

.. _commit-message:

Thank you again for contributing to geoenv ❤️. You help make open science more powerful and more connected.