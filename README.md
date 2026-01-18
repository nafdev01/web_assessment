# Web Vulnerability Assessment Tool

Web Vulnerability Assessment Tool is a cutting-edge web application vulnerability assessment tool designed to identify, categorize, and provide remediation advice for various vulnerabilities in web applications. By leveraging the power of the Nuclei vulnerability scanner, Web Vulnerability Assessment Tool offers detailed analyses, including vulnerability descriptions, affected paths, and HTTP methods, along with actionable remediation guidance and external references for further information.

The platform is engineered to be intuitive and accessible, ensuring users of all technical levels can effectively assess the security posture of their web applications. With features like comprehensive PDF report generation and email notifications, Web Vulnerability Assessment Tool simplifies the process of understanding and addressing web application vulnerabilities.

## Tech Stack

- **Frontend**: HTML, Custom CSS, JavaScript
- **Backend**: Django
- **Task Queue**: Celery
- **Message Broker**: Redis
- **Database**: PostgreSQL
- **Web Vulnerability Scanner**: Nuclei
- **Supported Operating System**: Linux

## Features

- Detailed vulnerability analysis with descriptions, paths, and HTTP methods.
- Remediation advice and external links for further vulnerability information.
- Comprehensive PDF report generation for in-depth security assessments.
- Email notifications for assessment completions and alerts.
- Built on the Nuclei vulnerability scanner for robust scanning capabilities.
- Designed for Linux environments.

## Prerequisites

Ensure you have the following installed before setting up Web Vulnerability Assessment Tool:

- Python 3.8 or newer.
- Redis server (for Celery task queue).
- PostgreSQL database. in
- A Linux-based operating system.
- Nuclei vulnerability scanner. Install it using the following commands:

```bash
# Download the latest release (Linux AMD64)
curl -L -O https://github.com/projectdiscovery/nuclei/releases/download/v3.6.2/nuclei_3.6.2_linux_amd64.zip

# Unzip the downloaded file
unzip nuclei_3.6.2_linux_amd64.zip

# Move the binary to your executable path
sudo mv nuclei /usr/local/bin/

# Verify installation
nuclei -version
```

## Setting Up

1. **Clone the repository**:

```bash
git clone https://github.com/nafdev01/web_assessment.git
```

2. **Navigate to the project directory**

```bash
cd web_assessment
```

3. **Create a virtual environment**:

```bash
python3 -m venv .venv
```

4. **Activate the virtual environment**:

```bash
source .venv/bin/activate
```

5. **Install the dependencies**:

```bash
pip install -r requirements.txt
```

6. **Database setup**:

- Install the database server

```bash
sudo apt-get install postgresql
```

- Access the database server

```bash
sudo -u postgres psql
```

- Create a database and user

```bash
CREATE USER web_assessment_user WITH PASSWORD 'password';
```

- Create a database with the owner as the user created

```bash
CREATE DATABASE web_assessment owner web_assessment_user;
```

- Set up the database and user for compatibility with the application by running the following commands:

```bash
ALTER ROLE web_assessment_user SET client_encoding TO 'utf8';
ALTER ROLE web_assessment_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE web_assessment_user SET timezone TO 'UTC';
```

7. **Set up the environment variables**:

- Use the .env.example file to create a .env file in the root directory. Update the environment variables as needed.

8. **Run the migrations**:

```bash
python manage.py migrate
```

9. **Create a superuser account for the Django admin panel**

```bash
python manage.py createsuperuser
```

10. **Start the Django development server**:

```bash
python manage.py runserver
```

11. **Start the redis server**:

- Open a new terminal and run the following command to start the Redis server.

```bash
redis-server
```

- Alternatively you could start the redis service by running the following command:

```bash
sudo service redis-server start
```

12. **Start the celery worker**:

- Open a new terminal and activate the virtual environment then run the following command:

```bash
celery -A django_project worker -l info
```

Your Web Vulnerability Assessment Tool instance should now be running on [http://localhost:8000](http://localhost:8000).

## Usage

- Signup and login to the application in order to use the application. Once logged in click on the `Assess` button in the top right corner and enter the complete link of the url you want to assess. The scan will be initialized and once complete, a summary of the results will be sent to your email with a link to the site where you can get more detailed results and download a pdf report of the scan.
- Please note that the scan may take up to 15-20 minutes to complete depending on the size of the site being scanned and the scope of vulnerbilites found.

## Troubleshooting

Include common issues and their solutions. Example:

- **Celery Worker Not Starting**: Ensure Redis is running and that you are in the virtual environment where Web Vulnerability Assessment Tool dependencies are installed.
- **Database Connection Error**: Check that the database server is running and that the database credentials in the .env file are correct.
- **Nuclei Not Installed**: Install Nuclei using the commands provided in the prerequisites section.
- **Vulnerability Scan Not Starting**: Ensure the URL provided is correct and that the scan has been initialized successfully.

#### Note:

_If you encounter any issues not listed here, please reach out to us for assistance. For detailed feedback, error and traceback details will be stored in a ile called warning.log in the root project folder_

## Contributing

We welcome contributions! Please read our contribution guidelines for more information on how you can contribute to Web Vulnerability Assessment Tool. Let's make web applications more secure, together!

## Security Notice

- Make sure you obtain permission from the owner of the website before scanning it for vulnerabilities.
- This tool is meant for educational purposes only. Do not use it for malicious purposes.
- We do not condone any illegal activities and do not bare responsibility for any misuse of this tool.
- When creating a .env file
- If you discover a security issue within Web Vulnerability Assessment Tool, please don't disclose it publicly. Instead, contact us directly so we can work on a fix. Your efforts to responsibly disclose your findings are greatly appreciated.
- When creating a .env file, ensure that the `DEBUG` variable is set to `False` in production environments and that you never upload the .env file to a public repository or share its contents with anyone.
