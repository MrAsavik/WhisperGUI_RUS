import sys
from gui import WhisperGUI
from cli_handler import process_files_cli

if __name__ == '__main__':
    if '--cli' in sys.argv:
        process_files_cli()
    else:
        app = WhisperGUI()
        app.mainloop()
