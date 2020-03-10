mir.anidb Release Notes
=======================

This project uses `semantic versioning <http://semver.org/>`_.

2.0.1 (2020-03-29)
------------------

Updated dependencies.

2.0.0 (2018-05-26)
------------------

Removed
^^^^^^^

- Removed async API.  It's not very useful and adds maintenance hassle and dependencies.

1.2.1 (2018-02-26)
------------------

Fixed
^^^^^

- Async APIs now correctly release client responses.

1.2.0 (2017-10-29)
------------------

Added
^^^^^

- The titles API is now `request_titles` and `async_request_titles`,
  the same as the anime API.
- Added `get_main_title`.

Deprecated
^^^^^^^^^^

- `CachedTitlesGetter` and all related classes and functions are
  deprecated.  This logic should be implemented by the client.
  Furthermore, the way it is implemented in `mir.anidb` is
  unnecessarily complex.

1.1.0 (2017-10-29)
------------------

Added
^^^^^

- Added asynchronous API.

Changed
^^^^^^^

- `request_anime` raises `MissingElementError` instead of `ValueError`.
- Use `pipenv` instead of `tox` for development.

1.0.1 (2017-06-17)
------------------

Fixed
^^^^^

- Fixed anime parsing failure due to missing date.

1.0.0 (2017-05-21)
------------------

Stable release (no functional changes).

0.1.0 (2017-03-27)
------------------

Initial release.
