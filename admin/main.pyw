import os
import sys
import runpy
import tempfile
import traceback


# // double-click THIS file instead of main.py to open the admin without
# // the black console window: Windows runs .pyw files with pythonw, which
# // has no console at all. It starts main.py exactly as before, nothing
# // else changes.
# //
# // with no console there's also nowhere for an error message to show
# // up, so any error is shown in a normal message box instead and also
# // written to a log file in the temp folder (not inside the project, so
# // it can never get committed by accident).

HERE = os.path.dirname(
    os.path.abspath(__file__)
)

os.chdir(
    HERE
)

sys.path.insert(
    0,
    HERE
)

LOG_PATH = os.path.join(
    tempfile.gettempdir(),
    "portfolio_admin_error.log"
)


def show_error(details):

    try:

        with open(
            LOG_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                details
            )

    except Exception:

        pass

    try:

        import ctypes

        ctypes.windll.user32.MessageBoxW(

            0,

            "The admin hit a problem.\n\n"
            + details[-900:]
            + "\n\n(also saved in " + LOG_PATH + ")",

            "website upload",

            0x10

        )

    except Exception:

        # // not on Windows (or no way to show a box): the log file
        # // above is all there is.
        pass


def handle_error(error_type, error, error_traceback):

    # // used for errors that happen later on, while the window is open
    # // (a button click that fails, for example).

    show_error(
        "".join(
            traceback.format_exception(
                error_type,
                error,
                error_traceback
            )
        )
    )


sys.excepthook = handle_error


try:

    runpy.run_path(
        os.path.join(
            HERE,
            "main.py"
        ),
        run_name="__main__"
    )

except SystemExit:

    # // the normal way the admin ends (closing the window).
    raise

except Exception:

    show_error(
        traceback.format_exc()
    )
