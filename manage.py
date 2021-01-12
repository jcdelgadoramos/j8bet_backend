#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "j8bet_backend.settings")
    try:
        command = sys.argv[1]
    except IndexError:
        command = "help"

    # Adds support for automatic Coverage when launching "manage.py test"
    # running_test = command == "test"
    # if running_test:
    #     from coverage import Coverage

    #     cov = Coverage()
    #     cov.erase()
    #     cov.start()
    # End

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

    # Adds support for automatic Coverage when launching "manage.py test"
    # if running_test:
    #     cov.stop()
    #     cov.save()
    #     cov.xml_report(outfile="cov.xml")
    #     covered = cov.report()
    #     if covered < 100:
    #         sys.exit(1)
    # End


if __name__ == "__main__":
    main()
