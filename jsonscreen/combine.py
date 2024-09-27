import json
import os


json_dir = '/Users/westyu/Desktop/cccjson'  


output_file = os.path.join(json_dir, 'merged_unique_apps.json')


all_apps = []
seen_ids = set()

for file_name in os.listdir(json_dir):
    if file_name.endswith('_apps.json'):  
        file_path = os.path.join(json_dir, file_name)
        
       
        with open(file_path, 'r') as f:
            apps = json.load(f)
            
            
            for app in apps:
                app_id = app['id']
                
                if app_id not in seen_ids:
                    all_apps.append(app)
                    seen_ids.add(app_id)  


with open(output_file, 'w') as f:
    json.dump(all_apps, f, indent=2)

print(f"Merged unique apps saved to: {output_file}")
print(f"Total unique apps: {len(all_apps)}")
