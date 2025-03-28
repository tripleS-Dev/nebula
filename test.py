import pickle
import os
import re

register = {}
register2 = {}

# Function to save the register dictionary to a file
def save_register():
    with open('register.pkl', 'wb') as f:
        pickle.dump(register2, f)


# Function to load the register dictionary from a file
def load_register():
    global register
    if os.path.exists('register.pkl'):
        with open('register.pkl', 'rb') as f:
            register = pickle.load(f)

load_register()
register2 = register.copy()

print(register)
for i in register:
    ad = register2[i].get('cosmo_address')
    if ad:
        if not ad.startswith('('):
            pass
        else:
            #print(ad)
            register2[i]['cosmo_address'] = re.findall(r'0x[a-fA-F0-9]+', ad)[0]
    else:
        print(i)
        if i.startswith('('):
            ar = re.findall(r'0x[a-fA-F0-9]+', i)[0]
            register2[ar] = register2.pop(i)
print(register2)
save_register()


# Convert the entire dictionary into a JSON-compatible format
import json

# Convert dictionary keys to strings to ensure JSON compatibility
json_ready_dict = {str(key): value for key, value in register2.items()}

# Save to a JSON file
json_path = "register.json"
with open(json_path, "w") as json_file:
    json.dump(json_ready_dict, json_file, indent=2)















