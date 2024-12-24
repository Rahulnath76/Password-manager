from cryptography.fernet import Fernet
from database import database
from dotenv import load_dotenv
import hashlib
import random
import os
load_dotenv()



class password_manager:
    def __init__(self):
        self.db = database()
        self.user_name = ""
        self.key = os.environ.get('FERNET_KEY')

    def user_login(self):
        print("-" * 60)
        print("\tPlease login before accessing our app: ".expandtabs(10))
        print("-" * 60)

        cond = input("\nIf you have an account press 1\n")
        if cond == '1':
            self.user_name = input("Enter your username:\n")
            password = input("Enter your password:\n")

            user = self.db["users"].find_one({"username": self.user_name})
            if user:
                password_check = hashlib.sha256(password.encode('utf-8')).hexdigest() == user["password"]
                if password_check:
                    print("Password is correct")
                    self.menu()
                else:
                    print("Password is incorrect")
        
        else:
            ran = input("Do you want to create an account? yes/no\n").lower()

            if ran == "yes":
                self.user_name = input("Please enter the username:\n")
                password = input("Please enter the password:\n")
                retype_pass = input("Please retype the password:\n")

                if password == retype_pass:
                    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
                    already_exist = self.db["users"].find_one({"username": self.user_name})
                    if not already_exist:
                        user = self.db["users"].insert_one({
                            "username": self.user_name,
                            "password": hashed_password,
                        })
                        print("Account created succesfully!\n")
                        self.menu()
                    else:
                        print("Username already exists")
                else:
                    print("Password do not match")
                    exit()

            
    def menu(self):
        while True:
            print("-" * 60)
            print("   Welcome this is our Password Manager App:")
            print("-" * 60)

            print("\n\t1. Add password for any website")
            print("\t2. Find the paasword for your website")
            print("\t3. List Websites")
            print("\t4. Remove websites")
            print("\t5. Generate unique password")
            print("\t6. Change your master password")
            print("\t7. Erase all data")
            print("\t8. Log out")
            print("Prees any other key to close")
            print("-" * 40)

            choice = input(": ").strip().lower()

            if choice == '1':
                self.add_password()
            elif choice == '2':
                self.find_password()
            elif choice == '3':
                self.list_all_websites()
            elif choice == '4':
                self.remove_password()
            elif choice == '5':
                self.generate_unique_password()
            elif choice == '6':
                self.change_master_pass()
            elif choice == '7':
                self.erase_all_pass()
            else:
                break

    def encrypt_password(self, password):
        cipher_suite = Fernet(self.key)
        password = password.encode()
        encrypted_pass = cipher_suite.encrypt(password)
        return encrypted_pass
    
    def decrypt_password(self, encrypted_pass):
        cipher_suite = Fernet(self.key)
        return cipher_suite.decrypt(encrypted_pass)
    
    def add_password(self):
        print("-" * 60)
        print("Add Password:")
        print("-" * 60)
        website_name = input("Enter the website name: \n").strip().replace(" ", "_")
        password = input("Enter the Password for the website\n")
        password_enc = self.encrypt_password(password)

        details = self.db["password"].find_one({
            "website_name": website_name,
            "username": self.user_name
        })

        if not details:
            self.db["password"].insert_one({
                "website_name": website_name,
                "password": password_enc,
                "username": self.user_name
            })
            print("Password added succesfully")
        else:
            print("Website name already exists")
            exit()
        
        return
    
    def remove_password(self):
        print("-" * 60)
        print("Remove Password:")
        print("-" * 60)

        website_name = input("Enter the website name: \n").strip().replace(" ", "_")

        details = self.db["password"].find_one({
            "website_name": website_name,
            "username": self.user_name
        })

        if details:
            self.db["password"].find_one_and_delete({"website_name": website_name})
            print(f"Password for the website {website_name.replace("_", " ")} removed succesfully")
        else:
            print("Website does not exist")

    def find_password(self):
        print("-" * 60)
        print("Find the Password:")
        print("-" * 60)

        website_name = input("Enter the website name: \n").strip().replace(" ", "_")
        details = self.db["password"].find_one({"website_name": website_name})

        if details:
            original_password = self.decrypt_password(details.password)
            print(f"The password for the website {website_name.replace("_", " ")} is {original_password}")
            print("\n")
        else:
            print("Website does not exists")
        
    def list_all_websites(self):
        print("-" * 60)
        print("Listing all the Passwords:")
        print("-" * 60)
        user_passwords = self.db["password"].find({"username": self.user_name})

        for password in user_passwords:
            decrypted_pass = self.decrypt_password(password["password"])
            print(f"{password["website_name"]} : {decrypted_pass}")

    
    def generate_unique_password(self):
        print("-" * 60)
        print("Generate a unique Password:")
        print("-" * 60)

        length = int(input("Enter the length of the password: \n"))

        lib = "qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM!@#$%&*()-=_+?/.,:;'"
        password = ""
        print(len(lib))
        for i in range(length):
            password += lib[random.randint(0, len(lib)-1)]
        
        print(f"Your generated password is : {password}")

    def change_master_pass(self):
        print("-" * 60)
        print("Change your master password: ")
        print("-" * 60)
        oldpass = input("Please enter your old password: \n")
        newpass = input("Please enter your new password: \n")

        user = self.db["users"].find_one({"username": self.user_name})

        if hashlib.sha256(oldpass.encode('utf-8')).hexdigest() == user["password"]:
            hashed_password = hashlib.sha256(newpass.encode('utf-8')).hexdigest()

            user["password"] = hashed_password
            self.db["users"].update_one({"_id": user["_id"]}, {"$set": user})
            print("Password changed sucessfully!\n")
        else:
            print("Incorrect old password")
        
    def erase_all_pass(self):
        check = input("Are you sure you want to erase all your passwords: (y/n)\n").lower()
        if check == 'y':
            passwords = self.db["password"]
            passwords.delete_many({"username": self.user_name})
            print("Passwords removed succesfully")

        


def main():
    manager = password_manager()
    manager.user_login()

if __name__ == '__main__':
    main()

