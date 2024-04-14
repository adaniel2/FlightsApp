# FlightsApp

## Introduction

It is often the case that when a prospective passenger looking to purchase flight tickets, they resort to online booking platforms such as Google Flights, Expedia, Kayak, Booking.com, and many more. It is then that they often find themselves asking how they can get to their destination in the fastest, cost-effective, most comfortable and reliable way possible. That is, each purchase should meet the individual’s or party’s travel needs and expectations accordingly. To this end, we intended to create a small application featuring a simple command line interface (CLI) designed to provide users with the ability to plan trips like that of Google Flights, but specifically for North American domestic & international flights. This would involve having the ability to lookup prices/routes based on desired travel class, number of passengers and other similar features. More interestingly, we also look to explore implementation of features not often readily available from the aforementioned platforms.

The data that will be used for such solution would be obtained by tailoring a combination of datasets from multiple sources to achieve the desired IO functionality. Such datasets include dozens of attributes like date, scheduled departure/arrival time, airline, ground/airtime, and many more, which could provide the basis for creating entities and relationships between such entities to be able to respond to user queries. The dataset will aim to be as recent as possible, however, we will also consider the possibility of associating less recent data with more up-to-date data (old routes with recent prices for example) if necessary.

## How to Use

### Prerequisites

- Python 3.x installed
- Git installed
- Access to a MySQL server (e.g., MySQL Workbench)
- Basic understanding of virtual environments and Python's packaging tools

### Setup Instructions

1. **Clone the Repository:**
   First, clone the FlightsApp repository from GitHub (or another version control system) onto your local machine.
   ```bash
   git clone https://github.com/yourusername/FlightsApp.git
   cd FlightsApp
   ```

2. **Setup MySQL Database:**
   - Open your MySQL Workbench or the MySQL command line tool.
   - Create a new database named `flights`.
   - Place the provided `.zip` file with database files into `C:\ProgramData\MySQL\MySQL Server 8.0\Uploads`
   - Import and run the `database.sql` file provided in the repository to set up tables and seed data.

3. **Create `.env` File:**
   Create a `.env` file in the root of your project directory. This file should contain all the necessary environment variables. Example:
   ```plaintext
   DB_HOST=localhost
   DB_USER=your_username
   DB_PASS=your_password
   DB_NAME=flights
   ```

4. **Install `pipenv` and Set Up the Virtual Environment:**
   - Ensure you are in the project directory (`FlightsApp`).
   - Install `pipenv` if it’s not already installed:
     ```bash
     pip install --user pipenv
     ```
   - Create a new virtual environment and install dependencies using:
     ```bash
     pipenv install
     ```
   This command will install all packages as specified in the `Pipfile.lock`, ensuring that you have all the required dependencies as per the locked versions.

5. **Activate the Virtual Environment:**
   - Activate the `pipenv` shell to use the virtual environment:
     ```bash
     pipenv shell
     ```
   Upon activation, your environment will have all the packages installed and available as specified in the `Pipfile.lock`, making your setup consistent with the project's requirements.

6. **Run the Backend Server:**
   - Navigate to the `backend` directory:
     ```bash
     cd backend
     ```
   - Run the Flask backend server:
     ```bash
     python app.py
     ```

7. **Run the Frontend GUI:**
   - Open another command prompt or terminal.
   - Navigate to the `frontend` directory:
     ```bash
     cd frontend
     ```
   - Activate the virtual environment again:
     ```bash
     pipenv shell
     ```
   - Start the Tkinter GUI application:
     ```bash
     python flight_gui.py
     ```

8. **Deactivate the Virtual Environment (when done):**
   - When you’re finished working, you can exit each virtual environment by typing:
     ```bash
     exit
     ```
