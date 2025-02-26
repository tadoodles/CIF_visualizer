#src/main.py

from src.cif_interface import CIFViewer

def main():
    app = CIFViewer()
    app.mainloop()

if __name__ == "__main__":
    main()