import json

auth0_export_file = open('binary.json', 'r')
auth0_output_file = open('binary.csv', 'w')
lines = auth0_export_file.readlines()

for line in lines:
    data = json.loads(line)
    email = data['email']
    groups = ['none']
    if 'app_metadata' in data:
        if 'groups' in data['app_metadata']:
            groups = []
            for group in data['app_metadata']['groups']:
                groups.append(group)

    csv_line = email

    for group in groups:
        csv_line+=f",{group}"

    auth0_output_file.write(csv_line)
    auth0_output_file.write("\n")

auth0_output_file.close()
print('operation complete. output file is binary.csv')
