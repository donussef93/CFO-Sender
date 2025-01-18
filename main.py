import os
from email.message import EmailMessage
import smtplib
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
import pyfiglet
from colorama import init, Fore, Style
import requests

init()

input_color = Fore.CYAN + Style.BRIGHT
success_color = Fore.GREEN + Style.BRIGHT
error_color = Fore.RED + Style.BRIGHT

load_dotenv()

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

def validate_license_key(license_key):
    paste_id = "45pUYdfb"  
    paste_url = f"https://pastebin.com/raw/{paste_id}"
    
    try:
        response = requests.get(paste_url)
        if response.status_code == 200:
            valid_licenses = response.text.split('\n')
            if license_key in valid_licenses:
                return True
        return False  
    except requests.RequestException as e:
        print(f"{error_color}Error fetching from try again: {str(e)}")
        return False
    except Exception as e:
        print(f"{error_color}Unexpected error in license validation: {str(e)}")
        return False


def get_leads(file_path):
    leads = []
    current_lead = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line == '====================================':
                leads.append(current_lead)
                current_lead = {}
            elif line:
                key, value = line.split(' ', 1)
                current_lead[key] = value.strip('{}')
        if current_lead:
            leads.append(current_lead)
    return leads

def setup_jinja_environment(template_dir='.'):
    return Environment(loader=FileSystemLoader(template_dir), autoescape=True)

def send_emails():
    jinja_env = setup_jinja_environment()
    template = jinja_env.get_template('Letter.txt')
    leads = get_leads('leads.txt')

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            print(f"\n{Fore.YELLOW}SMTP Server: Host:{SMTP_SERVER}:{SMTP_PORT}{Style.RESET_ALL}")

            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)

            for lead in leads:
                content = template.render(
                    FirstName=lead['Receiver_name'],
                    fullName=lead.get('Sender_name', 'Your Name Here'),
                    Sender_from_name=lead.get('Sender_from_name', 'Your Company'),
                    position=lead['Position']
                )
                subject, body = content.split('\n', 1)
                subject = subject.split(': ', 1)[1]  # Extract subject from "Subject: ..."

                msg = EmailMessage()
                msg.set_content(body)
                msg['Subject'] = subject
                msg['From'] = f"{lead.get('Sender_from_name', 'Your Company')} <{SMTP_USER}>"
                msg['To'] = lead['Receiver_email']

                try:
                    server.send_message(msg)
                    print(f"""{Fore.GREEN}
Subject: {subject}
From_name: {lead.get('Sender_from_name', 'Your Company')}
SMTP Server: Host:{SMTP_SERVER}:{SMTP_PORT}
Email Status: sent
========================================================{Style.RESET_ALL}""")
                except Exception as e:
                    print(f"""{Fore.RED}
Subject: {subject}
From_name: {lead.get('Sender_from_name', 'Your Company')}
SMTP Server: Host:{SMTP_SERVER}:{SMTP_PORT}
Email Status: failed - {str(e)}
========================================================{Style.RESET_ALL}""")
    except smtplib.SMTPException as smtp_error:
        print(Fore.RED + f"SMTP Connection Error: {str(smtp_error)}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An unexpected error occurred: {str(e)}" + Style.RESET_ALL)

if __name__ == "__main__":
    banner = pyfiglet.figlet_format("Payroll-Sender")
    print(Fore.GREEN + banner + Style.RESET_ALL)
    
    print(Fore.CYAN + " ======== CFO - CEO - PAYROLL SENDER  BY @donussef ========" + Style.RESET_ALL)

    if True:
        while True:
            print(f"\n{success_color}[+] 1. Send")
            print(f"[+] 2. Exit")
            choice = input(f"{input_color}Select an option: ")

            if choice == '1':
                send_emails()
            elif choice == '2':
                print(f"{success_color}Exiting program. Goodbye!")
                break
            else:
                print(f"{error_color}Invalid option. Please try again.")
    else:
        print(f"{error_color}Exiting due to license validation failure.")
