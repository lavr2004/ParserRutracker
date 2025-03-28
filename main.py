# main.py
import sys
from bin.gui import App, tk
from bin.settings.settings import logger

def main():
    if len(sys.argv) > 1:
        # Command-line execution with argument
        from bin.rutrackerParser import run_parser
        from bin.rutrackerHtmlGenerator import generate_html

        category_parameter = sys.argv[1]
        logger.info(f"Starting parser for category {category_parameter} via command line")
        run_parser(category_parameter)
        logger.info("Generating HTML...")
        generate_html(category_parameter)
        logger.info("Process completed successfully!")
    else:
        # GUI execution
        logger.info("Starting GUI mode")
        root = tk.Tk()
        app = App(root)
        root.mainloop()

if __name__ == "__main__":
    main()