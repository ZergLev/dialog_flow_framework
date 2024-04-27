import git
import json

def generate_switcher():
    repo = git.Repo('./')
    
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    tags.reverse()
    latest_tag = tags[-1]
    
    switcher_json = []
    
    dev_data = {
        "version": "dev",
        "url": "https://deepavlov.github.io/dialog_flow_framework/dev/index.html",
    }
    switcher_json += [dev_data]
    
    for tag in tags:
        url = "https://deepavlov.github.io/dialog_flow_framework/" + str(tag) + "/index.html"
        tag_data = {
            "name": str(tag),
            "version": str(tag),
            "url": url,
        }
        if tag == tags[0]:
            tag_data["preferred"] = "true"
        # Only building for tags from v0.7.0
        if str(tag) >= "v0.7.0":
            switcher_json += [tag_data]
    
    switcher_json_obj = json.dumps(switcher_json, indent=4)
    
    # Write nested JSON data to the switcher.json file
    with open('_static/switcher.json', 'w') as f:
        f.write(switcher_json_obj)
