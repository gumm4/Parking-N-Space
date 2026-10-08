# Parking-N-Space

A desktop parking lot management system built with Python, CustomTkinter and SQLite.

## Features

- **Customer management:** register, list, update and delete customers (name, CPF and license plate), with input validation
- **Vehicle movement:** register vehicle entry and exit; the system calculates the parking time and the amount to be paid (R$ 10.00 per hour)
- **Payments:** list open payments and mark them as received
- **Reports:** customer list, open payments, received payments (with total) and the top 5 most frequent customers

## Tech Stack

- Python 3
- CustomTkinter (user interface)
- SQLite (local database, created automatically on first run)
- Pyglet (custom font loading)

## Installation

```bash
git clone https://github.com/gumm4/Parking-N-Space.git
cd Parking-N-Space
pip install customtkinter pyglet
python main.py
```

> Replace `main.py` with the name of your main file.
> The `fonts/` folder (Oswald font) must be in the same directory as the script.


## Notes

The interface is currently in Portuguese (Brazil). The parking rate can be changed in the `VALOR_HORA` constant.

## Author

Gustavo ([@gumm4](https://github.com/gumm4))
